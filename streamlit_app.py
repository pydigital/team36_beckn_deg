# streamlit_app.py

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph_parts import create_beckn_context
# --- 1. Import LangGraph components ---
# Attempt to import from langgraph_parts.py
# You might need to adjust the path if langgraph_parts.py is in a different directory
# e.g., from . import langgraph_parts
st.set_page_config(page_title="LangGraph Chatbot", layout="centered")

try:
    from langgraph_parts import app # Your compiled LangGraph app
    # Try to import AgentState if defined (for clarity, not strictly used by this script directly for now)
    # from langgraph_parts import AgentState

    # Try to import an initial state definition. This is highly recommended.
    # If not present, a placeholder will be used, which you'll need to customize.
    try:
        from langgraph_parts import INITIAL_STATE
    except ImportError:
        st.warning(
            "INITIAL_STATE not found in langgraph_parts.py. Using a placeholder. "
            "Please ensure this matches your AgentState structure for all required fields."
        )
        INITIAL_STATE = {
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
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    st.error(
        f"Error importing from langgraph_parts.py: {e}. "
        "Please ensure 'langgraph_parts.py' exists in the same directory or in PYTHONPATH, "
        "and defines 'app' (your LangGraph instance) and preferably 'INITIAL_STATE'."
    )
    LANGGRAPH_AVAILABLE = False
    # Define dummy app and INITIAL_STATE for UI to load without crashing if LangGraph parts are missing
    def dummy_app(state):
        response_content = "LangGraph backend is not available. Please check langgraph_parts.py."
        if "chat_history" not in state:
            state["chat_history"] = []
        state["chat_history"].append(AIMessage(content=response_content))
        return state
    app = dummy_app
    INITIAL_STATE = {"chat_history": []}


# --- 2. Initialize and manage session state ---
def initialize_session():
    if "persistent_state" not in st.session_state:
        # Make a deep copy if INITIAL_STATE contains mutable objects like lists/dicts
        # For simple structures, .copy() is fine.
        import copy
        st.session_state.persistent_state = copy.deepcopy(INITIAL_STATE)

# --- 3. Display chat messages ---
def display_messages():
    if "persistent_state" in st.session_state and "chat_history" in st.session_state.persistent_state:
        for msg in st.session_state.persistent_state["chat_history"]:
            if isinstance(msg, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(msg.content)
            elif isinstance(msg, AIMessage):
                with st.chat_message("assistant"):
                    st.markdown(msg.content)
                    # Display tool calls if present (standard for OpenAI models)
                    if msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            st.markdown("🛠️ **Tool Call**")
                            st.caption(f"Tool: {tool_call.get('name', 'N/A')}")
                            st.code(str(tool_call.get('args', {})), language="json")
                    # You might have other ways tool calls/info are stored in AIMessage.additional_kwargs
                    # For example, if 'tool_calls' isn't directly on the message object but in additional_kwargs
                    elif "tool_calls" in msg.additional_kwargs:
                         for tool_call in msg.additional_kwargs["tool_calls"]:
                            st.markdown("🛠️ **Tool Call (from additional_kwargs)**")
                            st.caption(f"Tool: {tool_call.get('name', 'N/A')}") # Adjust based on actual structure
                            st.code(str(tool_call.get('args', {})), language="json") # Adjust based on actual structure

            elif isinstance(msg, ToolMessage):
                with st.chat_message("tool", avatar="🛠️"):
                    st.markdown(f"**Tool Result: {msg.name}**")
                    st.code(str(msg.content), language="text") # Or json, if applicable

# --- 4. Main Streamlit UI and Interaction Logic ---
st.title("💬 LangGraph Powered Chatbot")
st.markdown("Powered by LangGraph and Streamlit")

if not LANGGRAPH_AVAILABLE:
    st.error("The LangGraph backend is not available. Please fix the import issues above.")
    st.stop()

# Initialize session state for chat history and LangGraph state
initialize_session()

# Display chat messages from history
display_messages()

# Get user input
user_query = st.chat_input("Ask me anything...")

if user_query:
    # Add user message to session state and display it
    st.session_state.persistent_state['input'] = user_query
    st.session_state.persistent_state["chat_history"].append(HumanMessage(content=user_query))
    with st.chat_message("user"):
        st.markdown(user_query)

    # Prepare the input state for LangGraph
    # Make a copy to avoid modifying session state directly before the graph returns
    import copy
    current_graph_state = copy.deepcopy(st.session_state.persistent_state)

    # If your AgentState uses a specific 'input' field for the current query:
    # Ensure 'input' is a key in your INITIAL_STATE and AgentState definition
    if "input" in current_graph_state:
        current_graph_state["input"] = user_query
    # Otherwise, your graph might be designed to pick up the latest HumanMessage from chat_history

    # Call the LangGraph app
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # The LangGraph app is expected to modify and return the full state,
                # including appending its response(s) to 'chat_history'.
                print (current_graph_state)
                response_state = app.invoke(current_graph_state)
                print (response_state)

                # Update the session state with the new state from LangGraph
                st.session_state.persistent_state = response_state

                # Force a re-run to display the new messages from the updated state.
                # Streamlit's natural re-run after chat_input might also handle this,
                # but st.rerun() ensures it happens immediately after the graph call.
                st.rerun()

            except Exception as e:
                st.error(f"Error calling LangGraph: {str(e)}")
                # Optionally log the error to the chat display for the user
                st.session_state.persistent_state["chat_history"].append(
                    AIMessage(content=f"Sorry, an error occurred: {str(e)}")
                )
                st.rerun() # Rerun to show the error message in chat

else:
    # Add a small note if the history is empty to guide the user
    if not st.session_state.persistent_state.get("chat_history"):
        st.info("Type a message below to start the conversation!")