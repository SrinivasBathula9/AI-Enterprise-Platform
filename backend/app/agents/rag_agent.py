from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState
from app.services.llm_service import get_llm
from app.services.rag_service import retrieve_context

RAG_SYSTEM_PREFIX = """You are a helpful AI assistant with access to a knowledge base.
Use the following retrieved context to answer the user's question accurately.
If the context does not contain relevant information, say so and answer from your own knowledge.

--- RETRIEVED CONTEXT ---
{context}
--- END CONTEXT ---
"""


class RAGAgent(BaseAgent):
    """RAG-augmented agent: retrieves relevant docs from Qdrant before calling the LLM."""

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("call_llm", self._call_llm)
        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "call_llm")
        graph.add_edge("call_llm", END)
        return graph.compile()

    async def _retrieve(self, state: AgentState) -> dict:
        last_user_message = next(
            (m.content for m in reversed(state["messages"]) if m.type == "human"), ""
        )
        chunks = retrieve_context(
            query=last_user_message,
            user_id=state["user_id"],
            workspace_id=state["workspace_id"],
            top_k=5,
        )
        return {"context": chunks}

    async def _call_llm(self, state: AgentState) -> dict:
        llm = get_llm(
            provider=state.get("provider"),
            model=state.get("model"),
            streaming=True,
        )

        context_text = "\n\n".join(state.get("context", []))
        system_content = RAG_SYSTEM_PREFIX.format(context=context_text or "No context retrieved.")
        if state.get("system_prompt"):
            system_content = state["system_prompt"] + "\n\n" + system_content

        messages = [SystemMessage(content=system_content)] + list(state["messages"])
        
        # Use astream to ensure on_chat_model_stream events are triggered
        response = None
        async for chunk in llm.astream(messages):
            if response is None:
                response = chunk
            else:
                response += chunk

        return {"messages": [response]}
