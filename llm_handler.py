"""Module for handling LLM interactions."""
import json
from typing import Dict, List, Any
import ollama
from prompts import user_intent_prompt

def get_ollama_response(query: str, system_prompt: str = "Respond only in valid JSON format.") -> str:
    """Get response from Ollama LLM."""
    try:
        response = ollama.chat(
            model="llama3:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        return response.get("message", {}).get("content", "No content in response.")
    except Exception as e:
        return f"Error: {e}"

def process_user_intent(query: str) -> Dict[str, str]:
    """Process user query to understand intent and generate search query."""

    response = get_ollama_response(user_intent_prompt.format(user_query=query))
    response = response.strip()
    return json.loads(response)['search_query']

def generate_followup_questions(
    user_query: str,
    reviews: List[Dict[str, Any]],
    followup_prompt: str
) -> List[str]:
    """Generate follow-up questions based on user query and product reviews.
    
    Args:
        user_query: Original user query
        reviews: List of product reviews
        followup_prompt: Prompt template for generating follow-up questions
        
    Returns:
        List of follow-up questions
    """
    response = get_ollama_response(
        followup_prompt.format(user_query=user_query, reviews=reviews)
    )
    print(response)
    return json.loads(response)['followup_questions'] 