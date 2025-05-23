user_intent_prompt = """
You're an e-commerce search assistant. Given a user query that may be indirect or natural, rewrite it into a clear, intent-driven search query for an e-commerce site.

Example:
User: "I need a formal top for my beige pants"
Bad match: `Beige formal tops` or `formal pants` or `beige pants`
Correct intent: Tops that contrast beige, suitable for formal wear
Search query: "Women's formal tops in navy, maroon, or black"

Now do the same for:
User Query: {user_query}

ONLY return the JSON response, nothing else.
{{ "search_query": "..." }}
"""



generate_followup_questions_prompt = """You're an e-commerce assistant. Based on a user query and product reviews, generate 3–5 concise follow-up questions to refine their search.

Requirements:
- Focus on any negative or positive feedback from the reviews
- Be specific, actionable, and helpful for narrowing results

User Query: {user_query}
Product Reviews: {reviews}

ONLY return the JSON response, nothing else
{{
  "followup_questions": [
    "Question 1",
    "Question 2",
    "Question 3"
  ]
}}
"""

