import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Smart Search Assistant",
    page_icon="🧠",
    layout="wide"
)

from datetime import datetime
from typing import List, Dict, Any, Tuple
from data_handler import ProductDataManager
from llm_handler import process_user_intent, generate_followup_questions, get_openai_embedding, generate_review_summary

product_manager = ProductDataManager()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'products' not in st.session_state:
    st.session_state.products = []
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0
if 'current_recommendations' not in st.session_state:
    st.session_state.current_recommendations = None
if 'processed_query' not in st.session_state:
    st.session_state.processed_query = None
if 'product_summaries' not in st.session_state:
    st.session_state.product_summaries = {}
if 'current_product_summaries' not in st.session_state:
    st.session_state.current_product_summaries = {}

def add_message(role: str, content: str):
    """Add a message to the chat history."""
    st.session_state.chat_history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now().strftime("%H:%M")
    })

def process_query(query: str, is_followup: bool = False) -> Tuple[Dict[str, str], List[Tuple]]:
    """Process the user query and return products."""

    query_embedding = get_openai_embedding(query)
    
    if is_followup and st.session_state.current_recommendations is not None:
        top_k_recommendations = product_manager.rerank_recommendations(
            query_embedding,
            st.session_state.current_recommendations
        )
    else:
        top_k_recommendations = product_manager.get_recommendations(query_embedding)
        st.session_state.current_recommendations = top_k_recommendations

    return top_k_recommendations


def get_product_recos(top_k_recommendations: List[Tuple]) -> List[Dict[str, Any]]:
    """Convert recommendations to product details."""

    return [{
        'product_name': rec[0],
        'product_image': rec[4],
        'rating': rec[5],
    } for rec in top_k_recommendations]

def get_followup_questions(
    processed_query: Dict[str, str],
    top_k_recommendations: List[Tuple],
    is_followup: bool = False
) -> List[str]:
    """Generate follow-up questions based on recommendations."""

    reviews = [{
        'product_name': rec[0],
        'review_titles': rec[2],
        'review_contents': rec[3]
    } for rec in top_k_recommendations]

    if is_followup:
        return generate_followup_questions(
            st.session_state.chat_history,
            reviews,
        )
    else:
        return generate_followup_questions(
            processed_query,
            reviews,
        ) 

def generate_product_summaries(
    top_k_recommendations: List[Tuple],
) -> List[str]:
    """Generate follow-up questions based on recommendations."""

    st.session_state.current_product_summaries = {}

    reviews = [{
        'product_name': rec[0],
        'review_titles': rec[2],
        'review_contents': rec[3]
    } for rec in top_k_recommendations]

    for i, prod_details in enumerate(reviews):
        print(i)
        if prod_details['product_name'] not in st.session_state.product_summaries.keys():
            prod_summary = generate_review_summary(prod_details)
            st.session_state.product_summaries[prod_details['product_name']] = prod_summary
            st.session_state.current_product_summaries[prod_details['product_name']] = prod_summary
        else:
            st.session_state.current_product_summaries[prod_details['product_name']] = st.session_state.product_summaries[prod_details['product_name']]

def render_chat_interface():
    """Render the chat interface."""
    st.subheader("🧠 Chat with Assistant")
    
    query = st.text_input(
        "Describe what you're looking for...",
        key=f"query_input_{st.session_state.input_key}",
        placeholder="e.g., 'I need formal tops for beige formal pants I already own'"
    )
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div style="font-weight: bold;">👤 You ({message['timestamp']})</div>
                    <div>{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div style="font-weight: bold;">🧠 Assistant ({message['timestamp']})</div>
                    <div>{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    input_col1, input_col2 = st.columns([3, 1])
    with input_col1:
        if st.button("Search", key="send_button", use_container_width=True):
            if query:
                add_message('user', query)
                is_followup = len(st.session_state.chat_history) > 1

                if is_followup:
                    processed_query = st.session_state.processed_query + "\n" + query
                    print("Followup query: ", processed_query)
                    
                else:
                    with st.spinner("Processing User Intent..."):
                        processed_query = process_user_intent(query)
                    st.session_state.processed_query = processed_query
                    print("Processed query: ", processed_query)

                with st.spinner("Generating Recommendations..."):
                    top_k_recommendations = process_query(processed_query, is_followup)
                st.session_state.products = get_product_recos(top_k_recommendations)

                with st.spinner("Generating Follow-up Questions..."):
                    followup_questions = get_followup_questions(processed_query, top_k_recommendations)

                with st.spinner("Generating Product Review Summaries..."):
                    generate_product_summaries(top_k_recommendations)
                
                add_message('assistant', followup_questions)
                
                st.session_state.input_key += 1
                st.rerun()
    
    with input_col2:
        if st.button("Clear Chat", key="clear_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.products = []
            st.session_state.input_key += 1
            st.rerun()

def render_product_recommendations():
    """Render the product recommendations section."""
    st.subheader("Recommended Items")
    print(st.session_state.current_product_summaries)
    
    for i in range(0, len(st.session_state.products), 3):
        row_products = st.session_state.products[i:i+3]
        summaries = list(st.session_state.current_product_summaries.values())[i:i+3]
        cols = st.columns(len(row_products))
        
        for idx, (product, summary) in enumerate(zip(row_products, summaries)):
            with cols[idx]:
                with st.container():
                    st.image(product['product_image'], width=100)
                    st.markdown(f"{product['product_name']}")
                    
                    if product.get('rating'):
                        rating = float(product['rating'])
                        stars = '⭐' * int(rating) + '☆' * (5 - int(rating))
                        st.markdown(f"**Rating:** {stars} ({rating})")

                    st.write(summary)

def main():
    """Main application entry point."""
    
    _, mid_col, _ = st.columns([2, 3, 1])
    with mid_col:
        st.title("Smart Search Assistant")
    st.markdown('---')
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_chat_interface()
    
    with col2:
        render_product_recommendations()
    
    # Add custom styling
    st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        
        .stContainer {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stContainer:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .chat-message {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .user-message {
            background-color: rgb(0, 0, 0);
            margin-left: 20%;
        }
        .assistant-message {
            background-color: rgb(0, 0, 0);
            margin-right: 20%;
        }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 