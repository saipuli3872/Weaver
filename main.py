# main.py (Week 2 - Robust Tool Parsing Fix)

import google.generativeai as genai
from config import GEMINI_API_KEY
import sys
import memory_manager
import tools
import json

# --- Configuration (No Changes) ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
except AttributeError:
    print("Error: The API key is not configured. Please check your config.py file.")
    sys.exit(1)

TOOL_MANIFEST = """
**TOOLBOX:**
You have access to the following tools. To use a tool, you MUST respond with a special JSON object by itself in a single response.

[
    {
        "tool_name": "list_files",
        "description": "Lists all files and directories in the workspace.",
        "arguments": {}
    },
    {
        "tool_name": "read_file",
        "description": "Reads the entire content of a specified file.",
        "arguments": {
            "filename": "<The name of the file to read>"
        }
    },
    {
        "tool_name": "write_file",
        "description": "Writes content to a specified file. Creates the file if it doesn't exist, and overwrites it if it does.",
        "arguments": {
            "filename": "<The name of the file to write to>",
            "content": "<The content to write into the file>"
        }
    }
]
"""
SYSTEM_INSTRUCTION = (
    "You are a helpful and autonomous AI agent. "
    "Your goal is to complete the user's request, using the tools provided in your TOOLBOX if necessary. "
    "1. First, think step-by-step about how to solve the user's request. "
    "2. If a tool is needed, respond with ONLY the single JSON object for that tool call. "
    "3. After the tool is executed, I will provide you with the result. Use that result to continue your task. "
    "4. Once the task is complete, provide the final answer to the user."
    + TOOL_MANIFEST
)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={"candidate_count": 1, "max_output_tokens": 1024}
)

# --- Tool Functions (No Changes) ---
def execute_tool_call(tool_call):
    tool_name = tool_call.get("tool_name")
    arguments = tool_call.get("arguments", {})
    if tool_name == "read_file":
        return tools.read_file(arguments.get("filename"))
    elif tool_name == "write_file":
        return tools.write_file(arguments.get("filename"), arguments.get("content"))
    elif tool_name == "list_files":
        return tools.list_files()
    else:
        return f"Error: Unknown tool '{tool_name}'."

# --- NEW: Robust JSON Extractor for Tool Calls ---
def _extract_tool_call(text: str):
    """
    Finds and parses the first valid JSON tool call from within a larger string.
    Returns the parsed JSON object or None if not found.
    """
    try:
        # Find the first '[' or '{' to start the search for a JSON object
        start_brace = text.find('{')
        start_bracket = text.find('[')
        
        # Determine the actual start index
        if start_brace == -1 and start_bracket == -1: return None
        if start_brace == -1: start_index = start_bracket
        elif start_bracket == -1: start_index = start_brace
        else: start_index = min(start_brace, start_bracket)

        # Find the corresponding closing character
        if text[start_index] == '{':
            end_index = text.rfind('}') + 1
        else:
            end_index = text.rfind(']') + 1
            
        if start_index != -1 and end_index != -1:
            json_str = text[start_index:end_index]
            return json.loads(json_str)
        return None
    except json.JSONDecodeError:
        return None


# --- Main Agentic Loop (Now More Robust) ---
def main():
    print("--- Contextual Weaver (Week 2: Robust Agent) ---")
    print("AI can now read, write, and list files. Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit': break

        # Context Weaving
        recent_interactions = memory_manager.get_recent_interactions(count=5)
        knowledge_base = memory_manager.get_knowledge_base()
        journal_context = memory_manager.format_journal_for_prompt(recent_interactions)
        knowledge_context = memory_manager.format_knowledge_base_for_prompt(knowledge_base)
        final_prompt = (knowledge_context + journal_context + user_input)
        
        print("\n--- [DEBUG] Prompt sent to AI ---")
        print(final_prompt)
        print("-----------------------------------\n")

        print("AI is thinking...")
        response = model.generate_content(final_prompt)
        ai_response_text = response.text
        
        while True:
            # --- THE FIX IS HERE ---
            # Use our new robust function to find a tool call.
            tool_call = _extract_tool_call(ai_response_text)
            
            # If no valid tool_call is found, it must be a final answer.
            if not tool_call:
                break
            
            # If a tool call IS found, execute it.
            print(f"--- [TOOL CALL] AI wants to use {tool_call.get('tool_name')} ---")
            tool_result = execute_tool_call(tool_call)
            print(f"--- [TOOL RESULT] {tool_result} ---")
            
            # Send the result back to the AI.
            print("AI is thinking about the tool result...")
            # This is the corrected block
            tool_feedback_prompt = (
                f"I have used the tool '{tool_call.get('tool_name')}' for you. "
                f"The result was: '{tool_result}'. "
                "Now, what is the next step? Do you need to use another tool, or can you give the final answer?"
            )           
            print(f"--- [TOOL FEEDBACK PROMPT]\n{tool_feedback_prompt}\n--------------------------")
            response = model.generate_content(tool_feedback_prompt)
            ai_response_text = response.text

        # The loop has finished, so this is the final answer.
        print(f"\nAI: {ai_response_text}")
        
        # Memory & Logging
        last_interaction = {"user": user_input, "ai": ai_response_text}
        memory_manager.log_interaction_to_journal(user_input, ai_response_text)
        memory_manager.synthesize_knowledge_from_interaction(last_interaction)

if __name__ == "__main__":
    main()