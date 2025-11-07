import os
import sys
from openai import OpenAI, APIStatusError
from dotenv import load_dotenv
import httpx
from datetime import datetime

# ---  EXISTING CODE (UNCHANGED) ---

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("---")
    print("ERROR: Your OPENAI_API_KEY was not found.")
    sys.exit(1)

client = OpenAI(api_key=api_key)

def get_ai_chat_response(messages: list):
    """
    This function takes a list of messages (the conversation history)
    and gets a response from the OpenAI API.
    """
    print(f"--- AI ENGINE: Sending prompt: '{messages[-1]['content']}' ---")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=250,
            temperature=0.5 # Lower temperature for more factual responses
        )
        ai_message = response.choices[0].message.content.strip()
        print("--- AI ENGINE: Received response from OpenAI. ---")
        return ai_message
    except APIStatusError as e:
        print(f"[ERROR] OpenAI API status error: {e}")
        if e.status_code == 429:
            return "API call failed due to a billing issue."
        else:
            return "Sorry, the AI service returned an error."
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return "Sorry, I encountered an unexpected error."


# =====================================================================
# V V V V V V V V V    NEW PROMPT TESTING SUITE    V V V V V V V V V
# =====================================================================

def run_prompt_test(test_name, prompt):
    """A helper function to run and print a single test."""
    print(f"\n====================\n🧪 RUNNING TEST: {test_name}\n====================")
    
    # The 'system' message sets the AI's persona or instructions
    messages = [
        {"role": "system", "content": "You are a precise and neutral fact-checking assistant. If you don't know an answer, say so. Verify dates carefully."},
        {"role": "user", "content": prompt}
    ]
    
    response = get_ai_chat_response(messages)
    print(f"\n----------\n🤖 AI RESPONSE:\n{response}\n----------")

# This block runs when you execute `python engine.py` directly
if __name__ == '__main__':
    
    # Get the current date to use in prompts
    current_date = datetime.now().strftime("%A, %B %d, %Y")

    # --- 1. Basic Fact-Checking Prompts ---
    run_prompt_test("Simple Fact", "Who was the first person to walk on the moon?")
    run_prompt_test("Numerical Fact", "What is the approximate population of Japan as of 2024?")
    run_prompt_test("Common Misconception", "Is it true that humans only use 10% of their brains?")

    # --- 2. Date and Time Awareness Prompts ---
    run_prompt_test("Current Date Inquiry", f"What is today's date? For context, my system clock says it is {current_date}.")
    run_prompt_test("Specific Historical Date", "What major event happened on July 20, 1969?")
    run_prompt_test("Date Calculation", "What day of the week was January 1, 2000?")
    
    # --- 3. Recent & Future Events (Tests Knowledge Cutoff) ---
    # The AI's knowledge is not live. These tests see how it handles that limitation.
    run_prompt_test("Very Recent Event", "Who won the Best Picture Oscar in 2025?")
    run_prompt_test("Future Event", "When is the next solar eclipse visible from North America?")

    # --- 4. Ambiguous & Trick Questions ---
    run_prompt_test("Ambiguous Question", "Who is the president? Provide the country and the person's name.")
    run_prompt_test("Trick Question (Validity)", "What was the score of the final match of the 1950 FIFA World Cup between Brazil and Germany?")
    run_prompt_test("Nonsense Question", "What is the color of the number nine?")

    # --- 5. Context and Nuance Prompts ---
    run_prompt_test("Requesting a Source", "Who invented the telephone? Please cite a reliable source.")
    run_prompt_test("Comparing Two Facts", "Compare the reigns of Queen Elizabeth I and Queen Victoria in terms of length and major achievements.")