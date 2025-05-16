from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import copy

from source.langgraph_parts import create_beckn_context

# --- Import LangGraph components ---
try:
    from source.langgraph_parts import app as langgraph_app
    try:
        from source.langgraph_parts import INITIAL_STATE as LANGGRAPH_INITIAL_STATE
    except ImportError:
        # Default INITIAL_STATE if not defined in source.langgraph_parts
        LANGGRAPH_INITIAL_STATE = {
            "chat_history": [],
            "input": None,
            "user_info": {},
            "solar_options": [],
            "selected_solar_option": None,
            "order_id": None,
            "subsidy_search_results": None,
            "applied_subsidy_order_id": None,
            "world_engine_data": None,
            "meter_id": None,
            "energy_resource_id": None,
            "der_ids": [],
            "beckn_context": create_beckn_context(),
            "error_message": None,
            "latest_tool_output_summary": None,
        }

    if "input" not in LANGGRAPH_INITIAL_STATE:
        print("Warning: 'input' key missing from INITIAL_STATE, adding default None.")
        LANGGRAPH_INITIAL_STATE["input"] = None

    print("LangGraph components loaded successfully.")

except ImportError as e:
    print(f"Critical Error importing LangGraph components: {e}")
    print("Ensure source.langgraph_parts.py exists and defines 'app' and 'INITIAL_STATE'.")

    # Fallback dummy app and initial state
    def dummy_langgraph_app(state):
        state["chat_history"].append({
            "type": "ai",
            "content": "LangGraph backend components not loaded."
        })
        return state

    langgraph_app = dummy_langgraph_app
    LANGGRAPH_INITIAL_STATE = {"chat_history": [], "input": None}

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# In-memory session state store (consider Redis/db for production)
session_states = {}


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.json or {}

    user_message = data.get("user_message")
    session_id = data.get("session_id")

    if not user_message:
        return jsonify({"error": "user_message is required"}), 400
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    # Initialize session state if new session
    if session_id not in session_states:
        print(f"Initializing new session: {session_id}")
        session_states[session_id] = copy.deepcopy(LANGGRAPH_INITIAL_STATE)

    state = session_states[session_id]

    # Append user message to chat history using langchain_core or fallback dict
    try:
        from langchain_core.messages import HumanMessage
        state["chat_history"].append(HumanMessage(content=user_message))
    except ImportError:
        print("Warning: langchain_core not available, using dict for message.")
        state["chat_history"].append({"role": "user", "content": user_message})

    # Update 'input' field if exists
    if "input" in state:
        state["input"] = user_message

    print(f"\n--- Invoking LangGraph for session {session_id} ---")

    try:
        updated_state = langgraph_app.invoke(state)
        session_states[session_id] = updated_state

        # Extract new AI responses from chat history
        ai_responses = []
        pre_invoke_len = len(state["chat_history"])

        for msg in updated_state["chat_history"][pre_invoke_len - 1:]:
            is_ai_message = False
            try:
                from langchain_core.messages import AIMessage
                if isinstance(msg, AIMessage):
                    is_ai_message = True
            except ImportError:
                pass

            if is_ai_message and msg.content and msg.content.strip():
                ai_responses.append(msg.content.strip())
            elif isinstance(msg, dict) and msg.get("role") == "ai" and msg.get("content"):
                ai_responses.append(msg["content"].strip())

        # Fallback: check last message if no new AI responses found
        if not ai_responses and updated_state["chat_history"]:
            last_msg = updated_state["chat_history"][-1]
            try:
                from langchain_core.messages import AIMessage
                if isinstance(last_msg, AIMessage) and last_msg.content.strip():
                    ai_responses.append(last_msg.content.strip())
            except ImportError:
                if isinstance(last_msg, dict) and last_msg.get("role") == "ai" and last_msg.get("content"):
                    ai_responses.append(last_msg["content"].strip())

        if not ai_responses:
            print("No AI responses found after LangGraph invocation.")

        return jsonify({"ai_responses": ai_responses, "session_id": session_id})

    except Exception as e:
        print(f"Error invoking LangGraph for session {session_id}: {e}")
        return (
            jsonify(
                {
                    "error": "Internal error processing your message.",
                    "detail": str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
