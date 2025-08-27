from typing import List, Dict
from helper.helpers import (
    initialize_llm, 
    generate_llm_response,
    get_product_status,
    policy_related_answers,
    generate_chitchat_response
)
from langchain_core.messages import ToolMessage

class GenerateResponseService:
    def __init__(self):
        pass
        
    def rewrite_query_with_context(self, current_query: str, conversation_history: List[Dict]) -> str:
        """Rewrite the current query with conversation context"""
        print("Rewriting query with context...")
        if not conversation_history:
            return current_query
            
        context_messages = []
        for msg in conversation_history[-6:]: 
            if msg["role"] == "user":
                context_messages.append(f"User: {msg['content']}")
            else:
                context_messages.append(f"Assistant: {msg['content']}")
                
        context = "\n".join(context_messages)
        
        rewrite_prompt = f"""
        Given the conversation history and the current user query, rewrite the query to include all necessary context.
        Make sure the rewritten query is self-contained and clear.
        
        Conversation History:
        {context}
        
        Current Query: {current_query}
        
        Rewritten Query (be concise and include context and avoid unnecessary pleasantries or information just revelant question):
        """
        
        try:
            print(f"rewrite_prompt: {rewrite_prompt}")
            llm = initialize_llm()
            rewritten_query = generate_llm_response(llm, rewrite_prompt)
            print(f"rewritten_query: {rewritten_query}")
            return rewritten_query.strip()
        except Exception as e:
            print(f"Error rewriting query: {e}")
            return current_query
    

    def evaluate_tool_usage(self, rewritten_query: str) -> bool:
        llm = initialize_llm()
        planner_llm = llm.bind_tools([
            get_product_status,
            policy_related_answers,
            generate_chitchat_response
        ])
        eval_tool = planner_llm.invoke(rewritten_query)
        return eval_tool


    def generate_response(self, user_query: str, conversation_history: List[Dict]) -> str:
        print("conversation_history",conversation_history)
        if len(conversation_history) > 1:
            rewritten_query = self.rewrite_query_with_context(user_query, conversation_history)
        else:
            rewritten_query = user_query
        print(f"rewritten_query: {rewritten_query}")
        evaluate_tool = self.evaluate_tool_usage(rewritten_query)
        if evaluate_tool.tool_calls:
            tool = evaluate_tool.tool_calls[0]
            param = tool.get("args")
            tool_name = tool.get("name")
            print(f"evaluate_tool: {tool}")
            
            if tool_name == "get_product_status":
                return ToolMessage(
                    content=get_product_status(param.get("order_id")),
                    tool_call_id=tool["id"],
                ).content
            elif tool_name == "policy_related_answers":
                return ToolMessage(
                        content=policy_related_answers(param.get("query")),
                        tool_call_id=tool["id"],
                    ).content
            elif tool.get("name") == "generate_chitchat_response":
                return ToolMessage(
                        content=generate_chitchat_response(param.get("query")),
                        tool_call_id=tool["id"],
                    ).content
    
        
        return "Could not determine the appropriate response. Please try rephrasing your query. And if you are trying to ask about order status please provide a valid order ID like ABC-123, XYZ-456 etc."