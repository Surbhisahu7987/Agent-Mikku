from langchain_core.prompts import PromptTemplate
from mlflow.genai import load_prompt

prompt = load_prompt("instamart-subagent-system-prompt")
system_prompt = PromptTemplate.from_template(prompt.to_single_brace_format()).template

print(system_prompt)