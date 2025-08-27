from langchain_google_genai import ChatGoogleGenerativeAI
from db.structured_database_manager import DatabaseManager
from langchain_core.tools import tool
from rag.rag_manager import RAGManager
import config


def initialize_llm():
    llm = ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        convert_system_message_to_human=True,
        api_key=config.GEMINI_API_KEY
    )
    return llm
            

    
def generate_llm_response(llm, prompt: str) -> str:
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        return "I apologize, but I'm having trouble generating a response right now. Please try again."
    

@tool(description="Generate responses for queries related to order status and tracking")
def get_product_status(order_id: str) -> str:
    try:
        db_manager = DatabaseManager(recreate=False)
        order_status = db_manager.get_order_status(order_id)
        if not order_status:
            return f"I'm sorry, I couldn't find any information for order ID: {order_id}. Please check the ID and try again."
        status_prompt = f"""
        You are a helpful customer support agent for ShopEZ, an e-commerce platform.
        The user is asking about the status of their order with ID: {order_id}.
        Provide a friendly and professional response regarding the order status.
        
        order status: {order_status}
        
        Response:
        [INST] Provide just the message without any additional commentary or startup message. [/INST]
        """
        
        return generate_llm_response(prompt=status_prompt, llm=initialize_llm())
        
    except Exception as e:
        print(f"Error generating order status response: {e}")
        return "I apologize, but I'm having trouble accessing your order information right now. Please try again or contact support."
    

@tool(description="Generate responses for queries related to returns, exchanges, payments, billing, shipping, and general policies")
def policy_related_answers(query: str) -> str:
    rag_manager = RAGManager()
    llm = initialize_llm()
    rag_result = rag_manager.get_context_for_query(query, llm)
    return rag_result.get("result")


@tool(description="Generate a conversational response for chitchat or any general questions/conversation that doesn't fit in other two. This is the default.")
def generate_chitchat_response(query: str) -> str:
    try:
        print("Generating chitchat response...")
        chitchat_prompt = f"""
        You are a friendly customer support agent for ShopEZ, an e-commerce platform.
        The user is asking a general question or making conversation.
        Respond in a helpful, friendly manner while keeping the focus on how you can assist them with their shopping needs.
        Keep responses concise and professional.
        
        User: {query}
        
        Response:
        """
        
        return generate_llm_response(prompt=chitchat_prompt, llm=initialize_llm())
        
    except Exception as e:
        print(f"Error generating chitchat response: {e}")
        return "Hello! I'm here to help you with any questions about your orders, returns, or our policies. How can I assist you today?"