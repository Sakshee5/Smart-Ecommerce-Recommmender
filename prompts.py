user_intent_prompt = """
You're an e-commerce search assistant. Your task is to rewrite a natural-language or indirect user query into a clear, intent-based search query suitable for platforms like Amazon.

Instructions:
- Focus only on the item the user wants to purchase.
- Use context clues (like matching with existing items, purpose, occasion, or preferences) to refine the query.
- Do not include references to what the user already owns.
- Avoid conversational language; make the query short, specific, and optimized for search engines.
- Include relevant attributes like color, type, size, use-case, or audience if clearly implied.

Examples:

User: "I need a formal top for my beige pants"
{{ "search_query": "women's formal tops in navy, maroon, or black" }}

User: "Looking for something to wear to a beach wedding"
{{ "search_query": "women's beach wedding dresses" }}

User: "My daughter just started kindergarten and needs shoes that are easy to wear"
{{ "search_query": "toddler girl slip-on shoes" }}

User: "Something to help with back pain while sitting at my desk all day."
{{ "search_query": "lumbar support cushions" }}


Now do the same for:
User Query: {user_query}

Return your answer as a JSON with the key "search_query"."""



generate_followup_questions_prompt = """You're an e-commerce assistant. Based on a user query and a set of product reviews, generate 3 to 5 concise, specific follow-up questions that will help the user refine their search and make a better purchase decision.

Instructions:
- Focus on both negative and positive feedback found in the reviews.
- Extract actionable insights that can clarify user needs or preferences.
- Questions should be easy to understand and directly related to the user's query.
- Avoid generic questions; be as specific as possible.
- Do not include any explanations, only return the questions in JSON format as shown below.

User Query: {user_query}
Product Reviews: {reviews}

ONLY return the JSON response, nothing else:
{{
  "followup_questions": [
    "Question 1",
    "Question 2",
    "Question 3"
  ]
}}
"""

