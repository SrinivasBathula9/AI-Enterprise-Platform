from app.agents.chat_agent import ChatAgent
from app.agents.rag_agent import RAGAgent
from app.agents.base_agent import BaseAgent

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "chat": ChatAgent,
    "rag": RAGAgent,
    "code_reviewer": ChatAgent,   # Uses ChatAgent with a specialized system prompt
    "copywriter": ChatAgent,
}


def get_agent(graph_type: str) -> BaseAgent:
    agent_class = AGENT_REGISTRY.get(graph_type, ChatAgent)
    return agent_class()
