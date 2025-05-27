import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Tuple, Generator
from data_handler import ProductDataManager
from llm_handler import process_user_intent, generate_followup_questions, get_openai_embedding, generate_review_summary
from cache_handler import CacheManager

# Initialize managers
try:
    product_manager = ProductDataManager()
    cache_manager = CacheManager()
except Exception as e:
    st.error(f"Failed to initialize managers: {str(e)}")
    st.stop()

# Session state initialization
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'chat_history': [],
        'products': [],
        'initial_query': None,
        'processed_query': None,
        'current_product_summaries': {},
        'buffer_recommendations': {},
        'input_key': 0
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def add_message(role: str, content: str):
    """Add a message to the chat history."""
    st.session_state.chat_history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now().strftime("%H:%M")
    })

def process_query(query: str, is_followup: bool = False, k: int = 6, buffer_size: int = 30) -> Tuple[List[Tuple], List[Tuple]]:
    """Process the user query and return products with buffer."""
    query_embedding = get_openai_embedding(query)
    
    if is_followup:
        top_k_recommendations = product_manager.rerank_recommendations(
            query_embedding,
            st.session_state.buffer_recommendations,
            k=k
        )
    else:
        # Get both display recommendations and buffer
        st.session_state.buffer_recommendations = product_manager.get_recommendations(query_embedding, k=buffer_size)
        top_k_recommendations = st.session_state.buffer_recommendations[:k]

    return top_k_recommendations

def get_product_recos(top_k_recommendations: List[Tuple]) -> List[Dict[str, Any]]:
    """Convert recommendations to product details."""
    return [{
        'product_name': rec[0],
        'product_image': rec[4],
        'rating': rec[5],
        'similarity_score': rec[1]
    } for rec in top_k_recommendations]

def generate_followup(processed_query: str, recommendations: List[Tuple]) -> str:
    """Generate follow-up questions synchronously."""
    try:
        reviews = [{
            'product_name': rec[0],
            'review_titles': rec[2],
            'review_contents': rec[3]
        } for rec in recommendations]

        questions = generate_followup_questions(
            processed_query,
            reviews,
        ) 
        
        return questions
    except Exception as e:
        return f"Error generating questions: {str(e)}"

def generate_product_summaries(recommendations: List[Tuple]):
    """
    Generates product reviews summaries
    """
    try:
        reviews = [{
            'product_name': rec[0],
            'review_titles': rec[2],
            'review_contents': rec[3]
        } for rec in recommendations]

        for review in reviews:
            product_name = review['product_name']
            cached_summary = None
            
            # Check cache first
            try:
                cached_summary = cache_manager.get_summary(product_name)
                if cached_summary:  # Found in cache
                    st.session_state.current_product_summaries[product_name] = cached_summary
                    continue  # Skip to next product
            except Exception as e:
                print(f"Cache lookup failed for {product_name}: {str(e)}")
                # cached_summary remains None, so will generate new summary below
            
            # Generate new summary (either cache miss or cache error)
            if not cached_summary:  # Only generate if not found in cache
                try:
                    summary = generate_review_summary(review)
                    
                    # Cache the summary
                    try:
                        cache_manager.save_summary(product_name, summary)
                    except Exception as e:
                        print(f"Failed to cache summary for {product_name}: {str(e)}")
                    
                    st.session_state.current_product_summaries[product_name] = summary
                    
                except Exception as e:
                    print(f"Failed to generate summary for {product_name}: {str(e)}")
                    # Provide fallback content
                    st.session_state.current_product_summaries[product_name] = "Summary unavailable"

    except Exception as e:
        print(f"Failed to generate summaries: {str(e)}")
        # Ensure all products have some content to prevent KeyError in display
        for rec in recommendations:
            product_name = rec[0]
            if product_name not in st.session_state.current_product_summaries:
                st.session_state.current_product_summaries[product_name] = "Summary unavailable"
            

def handle_search_query(query: str):
    """Handle the search query processing."""
    add_message(role='user', content=query)
    is_followup = len(st.session_state.chat_history) > 1

    # Process user intent
    if is_followup:
        st.session_state.processed_query += f"\n{query}"
    else:
        with st.spinner("Processing User Intent..."):
            print(f"Original Query: {query}")
            st.session_state.processed_query = process_user_intent(query)

    print(f"Processed Query: {st.session_state.processed_query}")

    # Get recommendations immediately
    with st.spinner("Generating Recommendations..."):
        top_k_recommendations = process_query(st.session_state.processed_query, is_followup)
    
    # Update products immediately for display
    st.session_state.products = get_product_recos(top_k_recommendations)
    print(f"Recommendations: {st.session_state.products}")
    
    # Generate follow-up questions synchronously
    with st.spinner("Generating follow-up questions..."):
        followup_questions = generate_followup(
            st.session_state.processed_query, top_k_recommendations
        )
        add_message('assistant', followup_questions)
    print(f"Follow Up Questions: {followup_questions}")
    
    with st.spinner("Generating Product Review Summaries..."):
        generate_product_summaries(top_k_recommendations)
        


def render_product_recommendations():
    """Render the product recommendations section with streaming summaries."""
    
    # Create containers for each product
    for i, product in enumerate(st.session_state.products):
        product_name = product['product_name']
        
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                try:
                    st.image(product['product_image'], width=150)
                except Exception as e:
                    st.write("Image unavailable")
            
            with col2:
                st.markdown(f"**{product['product_name']}**")
                
                if product.get('rating'):
                    try:
                        rating = float(product['rating'])
                        stars = '⭐' * int(rating) + '☆' * (5 - int(rating))
                        st.markdown(stars)
                    except (ValueError, TypeError):
                        st.write("Rating unavailable")
                
                # Summary with fallback
                summary = st.session_state.current_product_summaries.get(
                    product_name, 
                    "Loading summary..." if product_name not in st.session_state.current_product_summaries 
                    else "Summary unavailable"
                )
                st.info(summary)


def add_custom_css():
    """Add custom CSS styling."""
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
            border: 1px solid rgba(0,0,0,0.1);
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
            background-color:rgba(0,0,0,0.1);
            margin-left: 20%;
        }
        .assistant-message {
            background-color: rgba(0,0,0,0.1);
            margin-right: 20%;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Smart Search Assistant",
        page_icon="🧠",
        layout="wide"
    )
    
    init_session_state()
    add_custom_css()
    
    # Header
    _, mid_col, _ = st.columns([2, 3, 1])
    with mid_col:
        st.title("Smart Search Assistant")
    st.markdown('---')
    
    # Main layout
    col1, col2 = st.columns([1, 2])
    
    # Create containers for dynamic content
    with col1:
        input_container = st.container()
        chat_container = st.container()
    
    with col2:
        reco_container = st.container()
    
    # Handle input first
    with input_container:
        st.subheader("🧠 Chat with Assistant")
        
        st.session_state.input_key += 1
        query = st.text_input(
            "Describe what you're looking for...",
            key="search_input",
            placeholder="e.g., 'I need formal tops for beige formal pants I already own'"
        )
        
        input_col1, input_col2 = st.columns([3, 1])
        with input_col1:
            if st.button("Search", key="send_button", use_container_width=True) and query:
                handle_search_query(query)
        
        with input_col2:
            if st.button("Clear Chat", key="clear_chat", use_container_width=True):
                init_session_state()
    
    # Render chat history (this will include any new messages)
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
    
    # Render recommendations
    with reco_container:
        st.subheader("Recommended Items")
        
        if not st.session_state.current_product_summaries:
            st.info("Search for products to see recommendations here.")
        else:
            render_product_recommendations()


if __name__ == "__main__":
    main()