import os
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import Base, engine, get_db, ChatSession, ChatMessage

UPLOAD_DIR: str = "static/uploads"

# 1. Define the Async Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handles application startup and shutdown events cleanly.
    """
    # Startup: Ensure upload directories exist and create tables
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield  # The application runs here while yielding control
    
    # Shutdown: Clean up connections or file streams if necessary
    await engine.dispose()

# 2. Pass the lifespan handler directly into FastAPI initialization
app = FastAPI(title="Agent Chhotu Backend", lifespan=lifespan)

# Mount static folder for serving uploaded images to your UI
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/session/create", status_code=status.HTTP_201_CREATED)
async def create_session(user_id: str, db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """Generates a unique session token tied to a specific User ID."""
    token: str = str(uuid.uuid4())
    new_session = ChatSession(session_token=token, user_id=user_id)
    db.add(new_session)
    await db.commit()
    return {"session_token": token, "user_id": user_id}

@app.post("/chat/send")
async def send_message(
    session_token: str = Form(...),
    message_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Processes incoming chat turns. Supports text, images, or both."""
    
    # 1. Validate Session
    result = await db.execute(select(ChatSession).where(ChatSession.session_token == session_token))
    chat_session: Optional[ChatSession] = result.scalar_one_or_none()
    if not chat_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid session token.")

    if not message_content and not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send an empty message.")

    # 2. Process Image Upload asynchronously if present
    saved_image_path: Optional[str] = None
    if file:
        file_extension: str = os.path.splitext(file.filename or "")[1]
        unique_filename: str = f"{uuid.uuid4()}{file_extension}"
        saved_image_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Open and write the file payload
        with open(saved_image_path, "wb") as buffer:
            buffer.write(await file.read())

    # 3. Store Human Message in database
    human_msg = ChatMessage(
        session_id=chat_session.id,
        sender="human",
        content=message_content,
        image_path=saved_image_path
    )
    db.add(human_msg)

    # 4. Agent Execution Window
    # TODO: Pass `message_content` and `saved_image_path` down to Agent Chhotu here
    ai_response_text: str = "Chhotu is checking this for you right away!"

    # 5. Store AI Response in database
    ai_msg = ChatMessage(
        session_id=chat_session.id,
        sender="ai",
        content=ai_response_text,
        image_path=None
    )
    db.add(ai_msg)
    
    await db.commit()

    return {
        "human_message": {"content": message_content, "image": saved_image_path},
        "ai_response": {"content": ai_response_text}
    }

@app.get("/chat/history/{session_token}")
async def get_chat_history(session_token: str, db: AsyncSession = Depends(get_db)) -> list[Dict[str, Any]]:
    """Retrieves chronological message logs for a session."""
    query = (
        select(ChatMessage)
        .join(ChatSession)
        .where(ChatSession.session_token == session_token)
        .order_by(ChatMessage.timestamp.asc())
    )
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return [
        {
            "sender": msg.sender,
            "content": msg.content,
            "image_url": f"/{msg.image_path}" if msg.image_path else None,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]