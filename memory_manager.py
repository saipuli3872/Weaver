# memory_manager.py (Definitive Fix for Stubborn AI)

import json
import os
from datetime import datetime
import google.generativeai as genai

# --- Configuration ---
MEMORY_DIR = "memory"
EPISODIC_JOURNAL_PATH = os.path.join(MEMORY_DIR, "episodic_journal.json")
SEMANTIC_KB_PATH = os.path.join(MEMORY_DIR, "semantic_knowledge_base.json")

try:
    knowledge_extractor_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"FATAL ERROR: Could not initialize knowledge_extractor_model. Reason: {e}")
    knowledge_extractor_model = None

# --- Initialization ---
def initialize_memory():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if not os.path.exists(EPISODIC_JOURNAL_PATH):
        with open(EPISODIC_JOURNAL_PATH, 'w') as f: json.dump([], f)
    if not os.path.exists(SEMANTIC_KB_PATH):
        with open(SEMANTIC_KB_PATH, 'w') as f: json.dump({}, f)

# --- Journal & Formatting Functions (No Changes) ---
def log_interaction_to_journal(user_input, ai_response):
    new_entry = {"timestamp": datetime.now().isoformat(), "user": user_input, "ai": ai_response}
    with open(EPISODIC_JOURNAL_PATH, 'r+') as f:
        journal = json.load(f)
        journal.append(new_entry)
        f.seek(0)
        json.dump(journal, f, indent=4)

def get_recent_interactions(count=5):
    try:
        with open(EPISODIC_JOURNAL_PATH, 'r') as f: return json.load(f)[-count:]
    except (FileNotFoundError, json.JSONDecodeError): return []

def format_journal_for_prompt(journal_entries):
    if not journal_entries: return ""
    formatted_string = "This is a summary of our recent conversation (your journal):\n"
    for entry in journal_entries:
        formatted_string += f"- User said: \"{entry['user']}\"\n"
        formatted_string += f"- You (the AI) responded: \"{entry['ai']}\"\n"
    formatted_string += "\n---\n"
    return formatted_string

def get_knowledge_base():
    try:
        with open(SEMANTIC_KB_PATH, 'r') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def save_knowledge_base(knowledge_data):
    with open(SEMANTIC_KB_PATH, 'w') as f: json.dump(knowledge_data, f, indent=4)

def format_knowledge_base_for_prompt(knowledge_data):
    if not knowledge_data: return ""
    formatted_string = "This is your permanent knowledge base of key facts:\n"
    formatted_string += json.dumps(knowledge_data, indent=2)
    formatted_string += "\n---\n"
    return formatted_string

def _extract_json_from_string(text):
    try:
        start_index = text.find('{')
        end_index = text.rfind('}') + 1
        if start_index != -1 and end_index != -1:
            json_str = text[start_index:end_index]
            return json.loads(json_str)
        return None
    except json.JSONDecodeError:
        return None

# --- REBUILT: Knowledge Synthesizer Engine ---
def synthesize_knowledge_from_interaction(last_interaction):
    """
    This new version demotes the AI. Its only job is to extract a list of actions.
    The Python code then executes those actions reliably.
    """
    print("--- [INFO] Starting knowledge synthesis process... ---")
    if not knowledge_extractor_model:
        print("--- [ERROR] Knowledge Extractor model is not available. Skipping synthesis. ---")
        return

    # This new prompt asks the AI to identify actions, not to update the DB itself.
    extractor_prompt = f"""
    You are an information extraction system. Your job is to read a conversation
    and identify any specific facts that should be recorded.

    Analyze the conversation below. Extract a list of actions to update a knowledge base.
    Possible actions are: 'add_fact' or 'add_to_list'.

    Example:
    Conversation: "The project deadline is tomorrow."
    Output:
    {{
      "actions": [
        {{"action": "add_fact", "key_path": ["ProjectA", "deadline"], "value": "tomorrow"}}
      ]
    }}
    
    Conversation: "Add two developers, Alice and Bob."
    Output:
    {{
      "actions": [
        {{"action": "add_to_list", "key_path": ["ProjectA", "developers"], "value": "Alice"}},
        {{"action": "add_to_list", "key_path": ["ProjectA", "developers"], "value": "Bob"}}
      ]
    }}

    Analyze this conversation:
    User: "{last_interaction['user']}"
    AI: "{last_interaction['ai']}"

    Return ONLY a JSON object with a single key, "actions".
    """
    
    try:
        response = knowledge_extractor_model.generate_content(
            extractor_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        extracted_data = _extract_json_from_string(response.text)

        if extracted_data and 'actions' in extracted_data:
            # --- PYTHON TAKES CONTROL ---
            # Now, our reliable Python code performs the update.
            knowledge_base = get_knowledge_base()
            
            for item in extracted_data['actions']:
                action = item.get('action')
                key_path = item.get('key_path', [])
                value = item.get('value')

                if not all([action, key_path, value]):
                    continue # Skip malformed actions

                # Navigate the dictionary path
                current_level = knowledge_base
                for i, key in enumerate(key_path[:-1]):
                    current_level = current_level.setdefault(key, {})

                final_key = key_path[-1]

                if action == "add_fact":
                    current_level[final_key] = value
                elif action == "add_to_list":
                    # Ensure the list exists, then add the item if it's not already there.
                    if final_key not in current_level:
                        current_level[final_key] = []
                    if not isinstance(current_level[final_key], list):
                         current_level[final_key] = [current_level[final_key]] # Convert to list if it's not
                    if value not in current_level[final_key]:
                        current_level[final_key].append(value)
            
            save_knowledge_base(knowledge_base)
            print("--- [INFO] Knowledge base updated successfully by Python logic. ---")
        else:
            print(f"--- [INFO] No actions extracted from conversation. ---")

    except Exception as e:
        print(f"--- [ERROR] An exception occurred during knowledge synthesis: {e} ---")
        if 'response' in locals():
            print(f"--- [DEBUG] Raw AI output was: {response.text} ---")

# --- Initial call ---
initialize_memory()