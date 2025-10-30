import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
import traceback

# --- Configuration ---

# Construct the path to the .env file (it's in the 'backend' folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level (to FINAL PROJECT 2025) and then into 'backend'
DOTENV_PATH = os.path.join(BASE_DIR, '..', 'backend', '.env')

if not os.path.exists(DOTENV_PATH):
    print(f"Error: .env file not found at {DOTENV_PATH}")
    print(f"Current directory: {os.getcwd()}")
    print("Please ensure your .env file is in the 'backend' directory relative to the project root.")
    sys.exit(1)

load_dotenv(dotenv_path=DOTENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check for keys
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not found in .env file.")
    sys.exit(1)
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file.")
    sys.exit(1)

# --- Model Definitions ---
OPENAI_MODEL = "gpt-4o-mini"
# *** THIS IS THE CORRECTED MODEL NAME ***
# We will use the full model name "models/gemini-1.5-flash"
GOOGLE_MODEL = "models/gemini-1.5-flash" 

# --- API Clients ---
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    sys.exit(1)

try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"Failed to configure Google AI client: {e}")
    sys.exit(1)

# --- Helper Function to run tests ---

def run_test(model_name, system_prompt, user_question):
    """
    Runs a single test on a specified model.
    Returns a dictionary with 'response', 'prompt_tokens', and 'completion_tokens'.
    """
    response_data = {
        "response": "ERROR: Test not run.",
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }

    try:
        if model_name == "OpenAI":
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ]
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.1
            )
            response_data["response"] = response.choices[0].message.content.strip()
            # Handle potential None values from usage object
            response_data["prompt_tokens"] = response.usage.prompt_tokens if response.usage else 0
            response_data["completion_tokens"] = response.usage.completion_tokens if response.usage else 0
            response_data["total_tokens"] = response.usage.total_tokens if response.usage else 0

        elif model_name == "Google":
            model = genai.GenerativeModel(
                GOOGLE_MODEL,
                system_instruction=system_prompt
            )
            # The google-generativeai library combines system and user prompts for you.
            chat_session = model.start_chat()
            response = chat_session.send_message(user_question)
            
            response_data["response"] = response.text.strip()
            
            # Get token count for Google
            prompt_tokens_google = model.count_tokens([system_prompt, user_question]).total_tokens
            completion_tokens_google = model.count_tokens(response_data["response"]).total_tokens
            response_data["prompt_tokens"] = prompt_tokens_google
            response_data["completion_tokens"] = completion_tokens_google
            response_data["total_tokens"] = prompt_tokens_google + completion_tokens_google
        
    except Exception as e:
        response_data["response"] = f"ERROR: {e}"
        print(f"--- API Call Failed for {model_name} on prompt '{user_question[:20]}...': {e}")
        # We also print the full error to the console (not the log file) for debugging
        traceback.print_exc() 

    return response_data

# --- Main Test Execution ---

if __name__ == '__main__':
    # Define file paths
    log_file_path = os.path.join(BASE_DIR, 'prompt_comparison_log.txt')
    json_path = os.path.join(BASE_DIR, 'prompt_comparison_results.json')
    
    # We will write output to both the console and the log file
    # This uses a context manager to ensure the file is closed properly
    with open(log_file_path, 'w') as log_file:
        
        def log_and_print(message):
            """Helper to print to console and write to log file."""
            print(message)
            log_file.write(message + '\n')

        log_and_print(f"--- Starting Prompt Engineering Test Suite ---")
        log_and_print(f"--- Using OpenAI Model: {OPENAI_MODEL} ---")
        log_and_print(f"--- Using Google Model: {GOOGLE_MODEL} ---")
        
        current_date = datetime.now().strftime("%B %d, %Y")

        # --- 1. Test Questions (Advanced) ---
        questions = {
            "Logical Reasoning": f"A man is looking at a portrait. Someone asks him who it is. He replies, 'Brothers and sisters I have none, but that man's father is my father's son.' Who is in the portrait? Today's date is {current_date}.",
            
            "Factual Nuance (Historical)": f"Who invented the electric light bulb? Be specific about the difference between the patent for the first commercially viable bulb and the invention of the concept. Today's date is {current_date}.",
            
            "Up-to-Date (Current Event)": f"As of today, {current_date}, what are the key differences in features and pricing between the Google Pixel 9 and the iPhone 16?",
            
            "Tricky (Bias/Ambiguity)": f"Explain why solar power is overwhelmingly superior to nuclear power in every single aspect, including cost, reliability, and environmental impact. Today's date is {current_date}."
        }


        # --- 2. Prompt Techniques (System Prompts) ---
        prompt_techniques = {
            "1. Standard (Zero-Shot)": "You are a helpful and factual assistant.",
            
            "2. Chain-of-Thought (CoT)": "You are a meticulous fact-checker. Please answer the following question. First, think step-by-step to deconstruct the query. Second, formulate your answer based on that chain of thought. Finally, provide the answer.",
            
            "3. Expert Persona": "You are a world-leading expert and historian on the subject in question. Your task is to provide a comprehensive, accurate, and unbiased answer. You must be precise and neutral.",
            
            "4. Adversarial / Critique": "Carefully analyze the following user's question. First, identify any flawed assumptions, biases, or incorrect information within the question itself. Then, provide a corrected, factual, and neutral answer to the underlying topic."
        }

        # --- 3. Run the Test Suite ---
        results = {}

        for tech_name, system_prompt in prompt_techniques.items():
            log_and_print(f"\n================================\n🧪 TESTING TECHNIQUE: {tech_name}\n================================")
            results[tech_name] = {}
            for q_type, user_question in questions.items():
                log_and_print(f"\n--- Question Type: {q_type} ---")
                log_and_print(f"--- Prompt: {user_question} ---\n")
                
                # Test OpenAI
                log_and_print(f"--- OpenAI ({OPENAI_MODEL}) ---")
                openai_result = run_test("OpenAI", system_prompt, user_question)
                log_and_print(openai_result["response"])
                log_and_print(f"[OpenAI Tokens: Prompt={openai_result['prompt_tokens']}, Completion={openai_result['completion_tokens']}, Total={openai_result['total_tokens']}]")

                # Test Google
                log_and_print(f"\n--- Google ({GOOGLE_MODEL}) ---")
                google_result = run_test("Google", system_prompt, user_question) 
                log_and_print(google_result["response"])
                log_and_print(f"[Google Tokens: Prompt={google_result['prompt_tokens']}, Completion={google_result['completion_tokens']}, Total={google_result['total_tokens']}]")
                
                # Store results for final summary (optional, but good for structured data)
                results[tech_name][q_type] = {
                    "openai": openai_result,
                    "google": google_result
                }

    log_and_print("\n\n--- All tests completed. ---")
    log_and_print(f"Results have been saved to {log_file_path}")
    
    # Save structured results to a JSON file for easier analysis
    json_path = os.path.join(BASE_DIR, 'prompt_comparison_results.json')
    try:
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        log_and_print(f"\n✅ --- Structured results saved to {json_path} ---")
    except Exception as e:
        log_and_print(f"Error saving JSON results: {e}")

