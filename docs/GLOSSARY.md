# Glossary of Terms: Agent Chhotu 

This glossary defines the domain terminology, architectural patterns, schemas, and framework concepts utilized across the **Agent Chhotu** codebase.

---

## Quick Reference Index
- [Agent & Orchestration Terms](#agent--orchestration-terms)
- [Model Context Protocol (MCP) & Tooling Terms](#model-context-protocol-mcp--tooling-terms)
- [State & Data Modeling Terms](#state--data-modeling-terms)
- [Domain & Business Logic Terms](#domain--business-logic-terms)
- [Infrastructure, Observability & Runtime Terms](#infrastructure-observability--runtime-terms)

---

## Agent & Orchestration Terms

### Agent Chhotu
The internal moniker for the conversational AI system. It refers to the end-to-end multimodal assistant capable of resolving food and grocery shopping intents.

### Supervisor Pattern / Hierarchical Multi-Agent
An architectural design pattern where a central agent ([`MasterAgent`](agents/master_agent.py)) oversees execution, breaks down complex user goals, and delegates sub-tasks to domain-specific agents ([`SwiggyAgent`](agents/swiggy_subagent.py), [`InstaMartAgent`](agents/instamart_subagent.py)) via LangChain tools.

### BaseAgent
The abstract base class defined in [`agents/base_agent.py`](agents/base_agent.py). It standardizes LLM initialization via `init_chat_model`, dynamic tool attachment via [`ToolRegistry`](tools/tools_registry.py), and asynchronous streaming response generation.

### BaseStructuredAgent
A specialized subclass of [`BaseAgent`](agents/base_agent.py) designed for agents that must produce output strictly adhering to a Pydantic schema rather than unstructured text.

### MasterAgent
The top-level orchestrator agent located in [`agents/master_agent.py`](agents/master_agent.py). It interacts with the end user, identifies dishes from input text or images, verifies delivery contexts, and routes tasks via `manage_swiggy_order` and `manage_instamart_order`.

### SwiggyAgent
The specialized sub-agent in [`agents/swiggy_subagent.py`](agents/swiggy_subagent.py) focused on ready-to-eat restaurant discovery, menu navigation, utility-based ranking, and food order feasibility.

### InstaMartAgent
The specialized sub-agent in [`agents/instamart_subagent.py`](agents/instamart_subagent.py) that handles recipe ingredient lookup, quick-commerce product search, and cart composition.

### AgentType
An enumeration defined in [`schema/agent_type.py`](schema/agent_type.py) with values `MASTER`, `SWIGGY`, and `INSTAMART`. Used to partition tools, configurations, and prompts.

### ModelProvider
An enumeration defined in [`schema/model_provider.py`](schema/model_provider.py) encapsulating supported LLM backend providers (`GOOGLE`, `OPENAI`, `ANTHROPIC`, `OLLAMA`, `HF`).

---

## Model Context Protocol (MCP) & Tooling Terms

### Model Context Protocol (MCP)
An open protocol developed by Anthropic that standardizes how applications provide context, tools, and prompts to LLMs. In this repository, MCP is used to interface with Swiggy’s catalog and cart services without hardcoding static API clients.

### SwiggyMCPManager
The centralized class in [`mcp_client/mcp_client.py`](mcp_client/mcp_client.py) managing connections to Swiggy Food and Instamart MCP servers, maintaining connection caches, and intercepting tool calls.

### MultiServerMCPClient
A client from `langchain-mcp-adapters` that connects to one or more MCP servers (e.g. over HTTP or STDIO) and converts discovered MCP functions into LangChain-compatible `BaseTool` instances.

### Tool Interceptor
A middleware function that intercepts tool call requests and results before they reach the LLM or external server. 
- Example: [`im_filter_search_product`](mcp_client/mcp_client.py#L34-L70) filters Instamart product searches to the top 5 items and strips `imageUrl` fields, eliminating token bloat by 5x–10x.

### ToolRegistry
A centralized dictionary mapping each [`AgentType`](schema/agent_type.py) to its allowed sequence of callable tools ([`tools/tools_registry.py`](tools/tools_registry.py)). Prevents sub-agents from calling unauthorized functions.

### Streamable HTTP (`streamable_http`)
The network transport mechanism used by the MCP client to communicate with remote Swiggy MCP server endpoints via HTTP streams.

---

## State & Data Modeling Terms

### CustomAgentState
The primary shared memory contract defined in [`state/states.py`](state/states.py) using Python's `TypedDict`. It maintains message history, identified food metadata, active delivery locations, order modes, and cart stages.

### `Annotated[List[BaseMessage], operator.add]`
A LangGraph reducer pattern used in [`CustomAgentState`](state/states.py#L53). Instead of overwriting the message list on each node return, it instructs LangGraph to append newly produced messages to the existing conversation list.

### IdentifiedFood
A Pydantic data model ([`state/states.py`](state/states.py#L11-L16)) capturing dish details from visual or natural language inputs (`dish_name`, `components`, `is_food`, `description`).

### DeliveryContext
A Pydantic data model ([`state/states.py`](state/states.py#L18-L23)) representing the active user address (`address_id`, `address_label`, `full_address`, `is_verified`).

### ProductInfo
A Pydantic model ([`state/states.py`](state/states.py#L25-L31)) representing a purchasable Instamart catalog item, including `spin_id`, `name`, `price`, `quantity`, and dark `store_id`.

### Checkpointer
A persistence adapter (such as `InMemorySaver` or `PostgresStore`) that records snapshots of the agent state graph at each step. Enables multi-turn conversations, state rollback, and Human-in-the-Loop workflows.

### Thread ID (`thread_id`)
A unique key passed in the LangGraph invocation configuration (`config={"configurable": {"thread_id": ...}}`) to isolate and retrieve conversation history for a specific session.

### Human-in-the-Loop (HITL)
A pattern where the agent workflow pauses (controlled by `pending_confirmation: bool` in [`CustomAgentState`](state/states.py#L74)) to await explicit user confirmation before executing critical operations like payment or final checkout.

---

## Domain & Business Logic Terms

### Spin ID (`spin_id`)
Swiggy Instamart’s internal unique identifier for a specific product SKU in their catalog.

### Dark Store (`store_id`)
A micro-fulfillment warehouse dedicated exclusively to rapid online grocery order fulfillment, mapped to specific geographic coordinates.

### Order Mode (`order_mode`)
A high-level user intent classifier with three supported values:
- `"order"`: User wants prepared food delivered from a restaurant.
- `"make"`: User wants to cook at home and buy raw ingredients from Instamart.
- `"none"`: General inquiry or food discovery without immediate purchase intent.

### Utility Score (`utility_score`)
A mathematical score in [`tools/swiggy_tools.py`](tools/swiggy_tools.py#L8-L42) used to rank candidate restaurants based on weighted factors:
- **50% Rating**
- **30% Delivery Speed** (inverse of delivery time)
- **20% Price** (inverse of average price)

### Feasibility Verification
Validation performed by [`verify_order_feasibility`](tools/swiggy_tools.py#L44-L65) ensuring business guardrails are met before placing an order (e.g., cart total under ₹1000 limit, restaurant status is `OPEN`).

---

## Infrastructure, Observability & Runtime Terms

### Astral `uv`
An extremely fast, Rust-based Python package and virtual environment manager used across this project for dependency resolution, locking (`uv.lock`), and Docker multi-stage containerization.

### MLflow LangChain Autologging
A diagnostic feature (`mlflow.langchain.autolog()`) that automatically records LLM inputs, tool calls, token usages, and traces to the MLflow tracking server without manual instrumentation.

### MLflow Prompt Registry (`mlflow.genai.load_prompt`)
Centralized version-controlled prompt management. Prompts are maintained in MLflow and fetched dynamically at runtime by scripts in `prompts/`.

### `deep_make_hashable` & `deep_make_dict`
Utility functions in [`utils/common.py`](utils/common.py) that recursively convert nested dictionaries into `frozenset` tuples and vice versa. This enables caching factory functions with `@alru_cache` despite complex dictionary arguments.

### FastAPI Lifespan Manager
An asynchronous context manager in [`backend/app.py`](backend/app.py#L15-L29) managing startup (directory creation, database table migrations) and shutdown (connection pool disposal) lifecycles.

