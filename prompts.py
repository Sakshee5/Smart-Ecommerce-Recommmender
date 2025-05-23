user_intent_prompt = """You will be provided with the raw user query which may be direct or indirect. Your aim is to understand the intent and context behind it.

E-commerce search engines are built for **literal** queries.

When a user types something like:
> "I need a formal top for my beige pants"

The system often misinterprets it and returns:
> Beige formal tops (WRONG: literal keyword match)

But the **user's actual intent** might be:
> "Show me tops that *contrast* well with beige pants, suitable for a formal setting"

so ideally, the search query should be: "Women's formal tops in navy, maroon, black"

Based on the above example, your task is to create the appropriate search query for the following user query if needed:

User Query: {user_query}

Return the search query in a json format.
{{
"search_query": "succinct search query for an ecommerce website like amazon"
}}"""


generate_followup_questions_prompt = """You are a e-commerce assistant helping users find the perfect items. Your task is to generate relevant follow-up questions based on the user's query and other users reviews to help refine their search.

Original User Query: {user_query}
Other users reviews for the recommended products: {reviews}

Generate 3-5 logical and helpful follow-up questions that will help narrow down the perfect product match. The questions should be:
- Succinct, Specific and actionable
- Based on real product attributes
- Helpful for refining the search

Return follow-up questions in the EXACT json format as shown below:
{{
    "followup_questions": [
        "question1",
        "question2",
        "question3",
    ]
}}

ONLY return the JSON response, nothing else."""
