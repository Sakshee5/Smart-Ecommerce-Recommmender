# Conversational AI Assistant Documentation

## Overview
This project implements a conversational AI assistant using Amazon Bedrock's Claude model. It includes conversation memory management, error handling, and a simple command-line interface.

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials:
   - Create a `.env` file
   - Add your AWS credentials and region

3. Run the application:
```bash
python app.py
```

## Project Structure
- `app.py`: Main application file containing the conversational AI implementation
- `requirements.txt`: Project dependencies
- `tests/`: Test suite directory
- `.env`: Configuration file for AWS credentials (not tracked in git)

## Features
- Conversation memory management
- Error handling for API calls
- Simple command-line interface
- Configurable conversation history length

## Testing
Run tests with coverage:
```bash
pytest --cov=app tests/
```

## API Usage
The main class `ConversationalAI` provides the following methods:
- `generate_response(user_input: str) -> str`: Generate a response for user input
- `_prepare_prompt() -> str`: Format conversation history for the model
- `_process_response(response: Dict[str, Any]) -> str`: Process model response

## Error Handling
The application includes error handling for:
- AWS API connection issues
- Invalid responses
- Memory management errors