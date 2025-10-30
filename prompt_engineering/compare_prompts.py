import os
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# --- Load API Keys ---
# We load the .env file from the 'backend' folder
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(dotenv_path=env_path)

openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

if not openai_api_key or not google_api_key:
    print("ERROR: Make sure both OPENAI_API_KEY and GOOGLE_API_KEY are in '../backend/.env'")
    exit()

# --- Initialize API Clients ---
openai_client = OpenAI(api_key=openai_api_key)
genai.configure(api_key=google_api_key)

# --- Define Models to Compare ---
OPENAI_MODEL = "gpt-4o-mini"
GOOGLE_MODEL = "gemini-1.5-flash"

# =========================================================================
#  PROMPT TECHNIQUES (THE "SYSTEM PROMPTS" / ADAPTATIONS)
# =========================================================================
PROMPT_TECHNIQUES = {
    "1. Zero-Shot": "You are a helpful assistant. Answer the question accurately.",
    
    "2. Zero-Shot CoT": "You are a meticulous fact-checker. Analyze the following question. Let's think step-by-step to determine the most accurate and nuanced answer.",
    
    "3. Expert Persona": "You are a university professor with PhDs in History, Economics, and Political Science. Your answers must be precise, unbiased, and cite your reasoning. Provide a comprehensive, academic-level response.",
    
    "4. Adversarial Critique": "You are an advanced AI. The user's question might have hidden assumptions or be poorly phrased. First, critique the question itself for any ambiguities. Then, provide a corrected, highly accurate answer."
}

# =========================================================================
#  TEST QUESTIONS (THE 4 CATEGORIES)
# =========================================================================
TEST_QUESTIONS = {
    "Fact-Check": "Is the Great Wall of China visible from the moon with the naked eye? Explain the science behind the answer.",
    
    "Historical": "What were the primary economic and social consequences of the dissolution of the Soviet Union for its former member states in the 1990s?",
    
    "Up-to-Date": f"As of today, {datetime.now().strftime('%B %Y')}, what are the latest developments in the European Union's AI Act and its potential impact on global tech companies?",
    
    "Political/Tricky": "Analyze the 'median voter theorem' and discuss two historical examples where a political candidate successfully appealed to the median voter, and one example where this strategy failed."
}

# --- Helper functions to call the APIs ---

def call_openai(system_prompt, user_question):
    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            temperature=0.2 # Low temp for factual answers
        )
        content = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        return content, prompt_tokens, completion_tokens
    except Exception as e:
        return f"ERROR calling OpenAI: {e}", 0, 0

def call_google(system_prompt, user_question):
    try:
        model = genai.GenerativeModel(
            GOOGLE_MODEL,
            system_instruction=system_prompt
        )
        response = model.generate_content(user_question)
        
        # Get token count
        prompt_tokens = model.count_tokens(user_question).total_tokens
        completion_tokens = model.count_tokens(response.text).total_tokens
        return response.text, prompt_tokens, completion_tokens
    except Exception as e:
        return f"ERROR calling Google: {e}", 0, 0

# --- Main test execution ---
def run_experiment():
    for tech_name, system_prompt in PROMPT_TECHNIQUES.items():
        print(f"\n{'='*80}")
        print(f"🧪 TESTING PROMPT TECHNIQUE: {tech_name}")
        print(f"   System Prompt: \"{system_prompt}\"")
        print(f"{'='*80}")
        
        for q_type, user_question in TEST_QUESTIONS.items():
            print(f"\n\n--- Question Type: {q_type} ---\n--- Question: {user_question} ---\n")
            
            # --- OpenAI Call ---
            print(f"---------- OpenAI ({OPENAI_MODEL}) Response ----------")
            openai_response, oai_pt, oai_ct = call_openai(system_prompt, user_question)
            print(openai_response)
            print(f"(Tokens: Prompt={oai_pt}, Completion={oai_ct})\n")
            
            # --- Google AI Call ---
            print(f"---------- Google ({GOOGLE_MODEL}) Response ----------")
            google_response, goo_pt, goo_ct = call_google(system_prompt, user_question)
            print(google_response)
            print(f"(Tokens: Prompt={goo_pt}, Completion={goo_ct})\n")
            print("-" * 80)

if __name__ == "__main__":
    run_experiment()
