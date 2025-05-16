# app.py (Flask Backend)
from flask import Flask, request, jsonify
from flask_cors import CORS # For handling Cross-Origin Resource Sharing if frontend and backend are on different ports during development
import copy
from langgraph_parts import create_beckn_context # Assuming this is a function in your langgraph_parts.py


# --- Import your LangGraph components ---
# Ensure langgraph_parts.py is in the same directory or accessible in PYTHONPATH
try:
    from langgraph_parts import app as langgraph_app
    try:
        from langgraph_parts import INITIAL_STATE as LANGGRAPH_INITIAL_STATE
    except ImportError:
        
        LANGGRAPH_INITIAL_STATE = {
            'chat_history': [],
            'input': None,
            'user_info': {},
            'solar_options': [],
            'selected_solar_option': None,
            'order_id': None,
            'subsidy_search_results': None,
            'applied_subsidy_order_id': None,
            'world_engine_data': None,
            'meter_id': None,
            'energy_resource_id': None,
            'der_ids': [],
            'beckn_context': create_beckn_context(),
            'error_message': None,
            'latest_tool_output_summary': None
        }
    # Ensure 'input' key is in INITIAL_STATE
    if 'input' not in LANGGRAPH_INITIAL_STATE:
        print("Warning: 'input' key missing from langgraph_parts.INITIAL_STATE. Adding default 'input': None.")
        LANGGRAPH_INITIAL_STATE['input'] = None
    print("LangGraph components loaded successfully.")
except ImportError as e:
    print(f"Critical Error: Could not import from langgraph_parts.py: {e}")
    print("Please ensure langgraph_parts.py exists and defines 'app' and 'INITIAL_STATE'.")
    # Define dummy components if import fails, so Flask can still start (but chat won't work)
    def dummy_langgraph_app(state):
        state["chat_history"].append({"type": "ai", "content": "LangGraph backend components not loaded."}) # Simplified message structure
        return state
    langgraph_app = dummy_langgraph_app
    LANGGRAPH_INITIAL_STATE = {"chat_history": [], "input": None}


flask_app = Flask(__name__)
CORS(flask_app) # Enable CORS for all routes

# In-memory store for session states (for demonstration purposes)
# For a production app, use a more robust session store (e.g., Redis, database)
session_states = {}

@flask_app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_message_content = data.get('user_message')
    session_id = data.get('session_id')

    if not user_message_content:
        return jsonify({"error": "user_message is required"}), 400
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    # Retrieve or initialize session state for LangGraph
    if session_id not in session_states:
        print(f"Initializing new session for ID: {session_id}")
        # Deepcopy INITIAL_STATE to prevent modification of the global template
        session_states[session_id] = copy.deepcopy(LANGGRAPH_INITIAL_STATE)
    
    current_persistent_state = session_states[session_id]

    # --- Prepare state for LangGraph ---
    # 1. Add HumanMessage to chat_history
    #    Ensure your langgraph_parts.py expects message objects (e.g., HumanMessage)
    #    or adapt this to the structure it expects (e.g., simple dicts).
    #    For this example, assuming it expects LangChain Core message objects.
    try:
        from langchain_core.messages import HumanMessage
        current_persistent_state["chat_history"].append(HumanMessage(content=user_message_content))
    except ImportError:
        # Fallback if langchain_core is not available where Flask runs, use dicts
        print("Warning: langchain_core.messages.HumanMessage not found. Using dictionary for message.")
        current_persistent_state["chat_history"].append({"role": "user", "content": user_message_content})


    # 2. Set the 'input' field if your graph uses it
    if "input" in current_persistent_state:
        current_persistent_state["input"] = user_message_content
    
    print(f"\n--- Invoking LangGraph for session {session_id} ---")

    try:
        # Invoke the LangGraph app
        updated_state = langgraph_app.invoke(current_persistent_state)
        session_states[session_id] = updated_state # Store the updated state for the session


        # Extract AI responses
        # This logic assumes new AI messages are appended to chat_history by the graph.
        # It tries to find messages that are new since the user's last message.
        ai_responses_content = []
        num_messages_before_invoke = len(current_persistent_state["chat_history"]) # Count before invoke, user message is last
        
        for msg_idx in range(num_messages_before_invoke -1, len(updated_state["chat_history"])):
            msg = updated_state["chat_history"][msg_idx]
            # Check if it's an AIMessage (from langchain_core) or a dict with role 'ai'
            is_ai_message_obj = False
            try:
                from langchain_core.messages import AIMessage
                if isinstance(msg, AIMessage):
                    is_ai_message_obj = True
            except ImportError:
                pass # AIMessage not available, rely on dict check

            if is_ai_message_obj:
                if msg.content and str(msg.content).strip():
                    ai_responses_content.append(str(msg.content))
            elif isinstance(msg, dict) and msg.get("role") == "ai": # Or "assistant" depending on your graph
                if msg.get("content") and str(msg.get("content")).strip():
                    ai_responses_content.append(str(msg["content"]))
            # Add more checks if your AIMessage structure is different

        # If no specific new AI messages found, check the last message if it's AI
        if not ai_responses_content and updated_state["chat_history"]:
            last_msg = updated_state["chat_history"][-1]
            is_ai_message_obj_last = False
            try:
                from langchain_core.messages import AIMessage
                if isinstance(last_msg, AIMessage): is_ai_message_obj_last = True
            except ImportError: pass

            if is_ai_message_obj_last and last_msg.content and str(last_msg.content).strip():
                ai_responses_content.append(str(last_msg.content))
            elif isinstance(last_msg, dict) and last_msg.get("role") == "ai" and last_msg.get("content"):
                 ai_responses_content.append(str(last_msg.get("content")))


        if not ai_responses_content:
            print("No new AI messages extracted. Sending a default or checking last message.")
            # This might happen if the graph doesn't add a new message or modifies existing ones.
            # For simplicity, we'll send an empty list if nothing new is clearly identified.
            # A more robust solution would depend on how your graph signals completion/response.

        return jsonify({"ai_responses": ai_responses_content, "session_id": session_id})

    except Exception as e:
        print(f"Error during LangGraph invocation for session {session_id}: {e}")
        # traceback.print_exc()
        return jsonify({"error": "An internal error occurred while processing your message.", "detail": str(e)}), 500

if __name__ == '__main__':
    # Make sure langgraph_parts.py is in the same directory or in PYTHONPATH
    # Run this Flask app. Example: python app.py
    # The frontend (index.html) should then be opened in a browser.
    # If running locally, frontend might be at file:///path/to/your/project/index.html
    # and it will try to connect to [http://127.0.0.1:5000/api/chat](http://127.0.0.1:5000/api/chat)
    flask_app.run(debug=True, port=5000)