from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage

from app.tools.log_tools import analyze_error_spike


def create_agent():
    llm = ChatOllama(
        model="llama3.1",
        temperature=0
    ).bind_tools([analyze_error_spike])

    return llm


def run_agent(agent, user_input: str):
    messages = [HumanMessage(content=user_input)]

    # First LLM call
    response = agent.invoke(messages)

    # If tool call exists
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

        # Second LLM call with tool result
        final_response = agent.invoke(messages)
        return final_response.content

    return response.content
