import os
import sys
from openai import OpenAI, APIStatusError
from dotenv import load_dotenv
import httpx  # We need to import httpx to create a mock response

# This line loads the variables from your .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# This is a crucial check to make sure the key was found.
if not api_key:
    print("---")
    print("ERROR: Your OPENAI_API_KEY was not found.")
    print("Please make sure you have a file named '.env' in the 'axiom-app' directory,")
    print("and make sure it contains the line: OPENAI_API_KEY='sk-yourkey'")
    print("---")
    sys.exit(1) # This stops the program if the key is missing.


# This creates the official OpenAI client with your key.
client = OpenAI(api_key=api_key)

def get_ai_chat_response(messages: list):
    """
    This function takes a list of messages (the conversation history)
    and gets a response from the OpenAI API.
    """
    # --- SIMULATION LOGIC ---
    last_user_message = messages[-1]['content']
    if last_user_message == "simulate billing error":
        print("--- AI ENGINE: Simulating a billing error. ---")
        
        # FIX: Create a mock response object with the status code inside it.
        # This is how the real openai library structures its errors.
        mock_response = httpx.Response(
            status_code=429,
            json={"error": {"code": "insufficient_quota", "message": "Simulated billing error"}}
        )

        # Now, raise the error by passing the mock response object.
        # The constructor for APIStatusError does not take 'status_code' directly.
        raise APIStatusError(
            "Simulated billing error", 
            response=mock_response, 
            body={"error": {"code": "insufficient_quota"}}
        )
    # --- END OF SIMULATION LOGIC ---

    print(f"--- AI ENGINE: Sending {len(messages)} messages to OpenAI. ---")
    try:
        # This is the actual call to the OpenAI API.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        ai_message = response.choices[0].message.content.strip()
        print("--- AI ENGINE: Received response from OpenAI. ---")
        return ai_message
    except APIStatusError as e:
        # This error handling will now correctly catch our simulated error.
        print(f"[ERROR] OpenAI API status error: {e}")
        if e.status_code == 429:
            return "API call failed due to a billing issue. Please check your plan and billing details on the OpenAI website."
        else:
            return "Sorry, the AI service returned an error. Please try again later."
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return "Sorry, I encountered an unexpected error while processing your request."

# =====================================================================
# V V V V V V V V V    NEW TESTING BLOCK ADDED BELOW    V V V V V V V V
# =====================================================================

# This block only runs when you execute `python engine.py` directly.
# It will NOT run when this file is imported by app.py.
if __name__ == '__main__':
    print("--- Running AI Engine in direct test mode... ---")

    # 1. Create a sample conversation history, just like your app would.
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the theory of relativity in one simple sentence."}
    ]

    # 2. Call your function with the test data.
    response = get_ai_chat_response(test_messages)

    # 3. Print the results.
    print("\n--- TEST COMPLETE ---")
    print(f"Test Prompt: {test_messages[-1]['content']}")
    print(f"AI Response: {response}")
    print("---------------------\n")
    
    # You can also test your error simulation
    print("--- Testing error simulation... ---")
    error_test_messages = [{"role": "user", "content": "simulate billing error"}]
    error_response = get_ai_chat_response(error_test_messages)
    print(f"AI Response to simulated error: {error_response}")
    print("---------------------------------")