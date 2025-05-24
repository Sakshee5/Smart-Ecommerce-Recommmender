"""Module for handling LLM interactions."""
import json
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any
import ollama
from prompts import user_intent_prompt
import openai
import os
import dotenv

dotenv.load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    

def get_openai_response(query: str) -> str:
    """Get response from OpenAI LLM."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"
    

def get_sentence_transformer_embedding(query: str) -> str:
    """Get embedding from Sentence Transformer."""
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    return model.encode(query)


def get_openai_embedding(query: str) -> list[float]:
    """Get embedding from OpenAI."""
    response = client.embeddings.create(input=[query], model="text-embedding-3-small")
    return response.data[0].embedding


def get_embeddings(query: str, model: str = "openai"):
    if model == "openai":
        return get_openai_embedding(query)
    else:
        return get_sentence_transformer_embedding(query)
    

def process_user_intent(query: str, model: str = "openai") -> Dict[str, str]:
    """Process user query to understand intent and generate search query."""

    if model == "openai":
        response = get_openai_response(user_intent_prompt.format(user_query=query))
    else:
        response = get_ollama_response(user_intent_prompt.format(user_query=query))

    response = response.strip()

    return json.loads(response)['search_query']

def generate_followup_questions(
    user_query: str,
    reviews: List[Dict[str, Any]],
    followup_prompt: str,
    model: str = "openai"
) -> List[str]:
    """Generate follow-up questions based on user query and product reviews.
    
    Args:
        user_query: Original user query
        reviews: List of product reviews
        followup_prompt: Prompt template for generating follow-up questions
        
    Returns:
        List of follow-up questions
    """
    if model == "openai":
        response = get_openai_response(
            followup_prompt.format(user_query=user_query, reviews=reviews)
        )
    else:
        response = get_ollama_response(
            followup_prompt.format(user_query=user_query, reviews=reviews)
        )
        
    return json.loads(response)['followup_questions'] 


if __name__ == "__main__":
    print(process_user_intent("I am looking for light colored tops that may go well with the grey formal pants I already own"))