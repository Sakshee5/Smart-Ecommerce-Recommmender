import os
import boto3
from dotenv import load_dotenv
from typing import List, Dict, Any
import json

load_dotenv()

class ConversationMemory:
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history

class ConversationalAI:
    def __init__(self):
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.memory = ConversationMemory()
        # Using Claude Instant for cost-effectiveness
        self.model_id = 'anthropic.claude-instant-v1'

    def generate_response(self, user_input: str) -> str:
        try:
            # Add user message to memory
            self.memory.add_message("user", user_input)

            # Prepare the prompt with conversation history
            prompt = self._prepare_prompt()

            # Call Bedrock API with proper request format for Claude
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": 300,
                    "temperature": 0.7,
                    "top_p": 1,
                })
            )

            # Extract and process the response
            assistant_response = self._process_response(response)
            
            # Add assistant response to memory
            self.memory.add_message("assistant", assistant_response)
            
            return assistant_response

        except Exception as e:
            return f"Error: {str(e)}"

    def _prepare_prompt(self) -> str:
        # Format conversation history for the model
        history = self.memory.get_history()
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        return prompt

    def _process_response(self, response: Dict[str, Any]) -> str:
        # Process and extract the response from Bedrock
        response_body = json.loads(response['body'].read())
        return response_body['completion']

def main():
    ai = ConversationalAI()
    print("Welcome to the Conversational AI Assistant! Type 'q' to exit.")
    print("Using Claude Instant model for cost-effective responses.")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'q':
            break
            
        response = ai.generate_response(user_input)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    main() 