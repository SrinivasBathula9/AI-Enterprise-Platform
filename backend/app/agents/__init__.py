from app.agents.base_agent import BaseAgent
from app.agents.chat_agent import ChatAgent
from app.agents.customer_agent import CustomerAgent
from app.agents.email_agent import EmailAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.logistics_agent import LogisticsAgent
from app.agents.operations_agent import OperationsAgent
from app.agents.rag_agent import RAGAgent

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    # Core platform agents
    "chat": ChatAgent,
    "rag": RAGAgent,
    "code_reviewer": ChatAgent,   # Uses ChatAgent with a specialized system prompt
    "copywriter": ChatAgent,
    # Operational AI agents — e-commerce fashion brand
    "logistics_monitor": LogisticsAgent,
    "finance_monitor": FinanceAgent,
    "email_manager": EmailAgent,
    "customer_issue_monitor": CustomerAgent,
    "operations_dashboard": OperationsAgent,
}


def get_agent(graph_type: str) -> BaseAgent:
    agent_class = AGENT_REGISTRY.get(graph_type, ChatAgent)
    return agent_class()
