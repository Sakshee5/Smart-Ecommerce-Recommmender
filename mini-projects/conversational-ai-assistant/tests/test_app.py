from app import ConversationalAI, ConversationMemory

def test_conversation_memory():
    memory = ConversationMemory(max_history=2)
    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi there!")
    memory.add_message("user", "How are you?")
    
    history = memory.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "assistant"
    assert history[0]["content"] == "Hi there!"
    assert history[1]["role"] == "user"
    assert history[1]["content"] == "How are you?"

def test_conversational_ai_initialization():
    ai = ConversationalAI()
    assert ai.model_id == 'anthropic.claude-instant-v1'
    assert isinstance(ai.memory, ConversationMemory)