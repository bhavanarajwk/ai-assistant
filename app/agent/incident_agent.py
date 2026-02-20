from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage

from app.tools.log_tools import analyze_error_spike
from app.rag.retriever import get_retriever

def create_agent():
    llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0
    ).bind_tools([analyze_error_spike])

    retriever = get_retriever()

    return llm, retriever


def run_agent(agent_tuple, user_input: str):
    llm, retriever = agent_tuple

    # 🔥 STEP 1 — Retrieve relevant log context
    retrieved_docs = retriever.invoke(user_input)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # Inject context into user question
    enhanced_input = f"""
    Relevant logs from system:
    {context}

    User question:
    {user_input}
    """

    messages = [HumanMessage(content=enhanced_input)]

    # 🔥 STEP 2 — First LLM call
    response = llm.invoke(messages)

    # 🔥 STEP 3 — If tool is called
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]

            if tool_name == "analyze_error_spike":
                tool_result = analyze_error_spike.invoke({})

                messages.append(response)
                messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"],
                    )
                )

        # 🔥 STEP 4 — Final LLM call
        final_response = llm.invoke(messages)
        return final_response.content

    return response.content
