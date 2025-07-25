# main.py (Synchronized and Corrected)

import google.generativeai as genai
from config import GEMINI_API_KEY
import sys
import memory_manager

# --- Configuration ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
except AttributeError:
    print("Error: The API key is not configured. Please check your config.py file.")
    sys.exit(1)

# --- MODEL CONFIGURATION ---
SYSTEM_INSTRUCTION = "You are a helpful assistant with a perfect memory of past conversations. Use the provided conversation history and your knowledge base to inform your answers and maintain context. Be concise and helpful."
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

# --- Main Application Logic ---
def main():
    """
    Main function for the context-aware chatbot.
    """
    print("--- Contextual Weaver (Week 1: Corrected) ---")
    print("AI now understands context and facts. Type 'quit' to exit.")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break

        # --- THE CORRECTED CONTEXT WEAVER ENGINE ---
        
        # Calls the correctly named functions in memory_manager.py
        recent_interactions = memory_manager.get_recent_interactions(count=5)
        knowledge_base = memory_manager.get_knowledge_base()
        
        journal_context = memory_manager.format_journal_for_prompt(recent_interactions)
        knowledge_context = memory_manager.format_knowledge_base_for_prompt(knowledge_base)
        
        final_prompt = (
            knowledge_context + 
            journal_context + 
            "Based on your knowledge base and our recent conversation, please respond to this new prompt: " + 
            user_input
        )
        
        print("\n--- [DEBUG] Final prompt sent to AI ---")
        print(final_prompt)
        print("---------------------------------------\n")

        print("AI is thinking...")
        response = model.generate_content(final_prompt)
        
        try:
            ai_response = response.text
            print(f"\nAI: {ai_response}")
            
            last_interaction = {"user": user_input, "ai": ai_response}
            
            # Calls the correctly named logging and synthesis functions
            memory_manager.log_interaction_to_journal(user_input, ai_response)
            print("\n--- [INFO] Interaction logged to episodic journal. ---")
            
            memory_manager.synthesize_knowledge_from_interaction(last_interaction)

        except ValueError:
            print("\nAI: I'm sorry, I couldn't generate a response for that.")
            if response.prompt_feedback:
                 print("Blocked Reason:", response.prompt_feedback.block_reason)

# --- Entry Point ---
if __name__ == "__main__":
    main()