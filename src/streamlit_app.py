# streamlit_app.py

import streamlit as st
import copy
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph_parts import create_beckn_context
# --- 1. Import LangGraph components ---
# Attempt to import from langgraph_parts.py
# You might need to adjust the path if langgraph_parts.py is in a different directory
# e.g., from . import langgraph_parts
st.set_page_config(page_title="LangGraph Chatbot", layout="centered")

# --- Custom CSS for Phone Screen View ---
PHONE_SCREEN_CSS = """
<style>
body { /* Apply a background to the whole page if desired */
    background-color: #e0e0e0; /* Light grey background for the page */
}

.phone-wrapper { /* This div will contain the phone and center it */
    display: flex;
    justify-content: center;
    align-items: flex-start; /* Align phone to the top */
    padding-top: 20px; /* Some space from the top of the viewport */
    padding-bottom: 20px;
}

.phone-container {
    width: 390px;  /* iPhone 12/13 Pro width */
    height: 720px; /* Adjusted for a decent chat view + input */
    border: 12px solid #1c1c1e; /* Dark border similar to phone chassis */
    border-radius: 40px; /* Rounded corners */
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3); /* Phone shadow */
    background-color: #1c1c1e; /* Chassis color visible in padding */
    padding: 10px; /* Padding between outer border and "screen" */
    display: flex;
    flex-direction: column; /* Stack screen area and input area */
}

.chat-screen-area {
    background-color: #ffffff; /* White background for the chat screen */
    border-radius: 25px; /* Inner rounded corners for the screen */
    flex-grow: 1; /* Chat messages take up available space */
    padding: 15px; /* Padding inside the screen */
    overflow-y: auto; /* Allows scrolling of messages */
    margin-bottom: 10px; /* Space between messages and input field */
    display: flex;
    flex-direction: column; /* Messages stack vertically */
}

/* Styling for the chat input to make it look like it belongs */
/* Streamlit's st.chat_input is a bit hard to deeply customize without affecting all inputs.
   This focuses on the container it resides in if we place it inside the phone. */
div[data-testid="stChatInput"] {
    background-color: #ffffff; /* Match screen background */
    border-radius: 0 0 20px 20px; /* If it's the last element, round bottom corners */
    padding: 0 5px 5px 5px; /* Adjust padding if needed */
}

/* Ensure chat messages themselves don't have huge margins */
div[data-testid="stChatMessage"] {
    margin-bottom: 0.75rem; /* Spacing between messages */
}
</style>
"""
st.markdown(PHONE_SCREEN_CSS, unsafe_allow_html=True)



try:
    from langgraph_parts import app

    try:
        from langgraph_parts import INITIAL_STATE
    except ImportError:
        st.warning(
            "Creating a default INITIAL_STATE "
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
    INITIAL_STATE = {"chat_history": [], "input": None}

# --- 2. Initialize and manage session state ---
def initialize_session():
    if "persistent_state" not in st.session_state:
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
                    # if msg.tool_calls:
                    #     for tool_call in msg.tool_calls:
                    #         st.markdown("🛠️ **Tool Call**")
                    #         st.caption(f"Tool: {tool_call.get('name', 'N/A')}")
                    #         st.code(str(tool_call.get('args', {})), language="json")
                    # # You might have other ways tool calls/info are stored in AIMessage.additional_kwargs
                    # # For example, if 'tool_calls' isn't directly on the message object but in additional_kwargs
                    # elif "tool_calls" in msg.additional_kwargs:
                    #      for tool_call in msg.additional_kwargs["tool_calls"]:
                    #         st.markdown("🛠️ **Tool Call (from additional_kwargs)**")
                    #         st.caption(f"Tool: {tool_call.get('name', 'N/A')}") # Adjust based on actual structure
                    #         st.code(str(tool_call.get('args', {})), language="json") # Adjust based on actual structure

            # elif isinstance(msg, ToolMessage):
            #     with st.chat_message("tool", avatar="🛠️"):
            #         st.markdown(f"**Tool Result: {msg.name}**")
            #         st.code(str(msg.content), language="text") # Or json, if applicable

# --- 4. Main Streamlit UI and Interaction Logic ---
st.title("💬 LangGraph Powered Chatbot")
st.markdown("Powered by LangGraph and Streamlit")

if not LANGGRAPH_AVAILABLE:
    st.error("The LangGraph backend is not available. Please fix the import issues above.")
    st.stop()

# Initialize session state for chat history and LangGraph state
initialize_session()

# Create the phone UI
st.markdown('<div class="phone-wrapper">', unsafe_allow_html=True) # Outer wrapper for centering
st.markdown('<div class="phone-container">', unsafe_allow_html=True) # Start phone

# Area for messages
st.markdown('<div class="chat-screen-area">', unsafe_allow_html=True)
display_messages() # Renders messages here
st.markdown('</div>', unsafe_allow_html=True) # End chat-screen-area

# Chat input - now rendered *inside* the phone-container div
user_query = st.chat_input("Type your message...")

st.markdown('</div></div>', unsafe_allow_html=True) # End phone-container and phone-wrapper

if user_query:
    
    st.session_state.persistent_state['input'] = user_query
    st.session_state.persistent_state["chat_history"].append(HumanMessage(content=user_query))

    with st.chat_message("user"):
        st.markdown(user_query)
    
    current_graph_state = copy.deepcopy(st.session_state.persistent_state)

    if "input" in current_graph_state:
        current_graph_state["input"] = user_query

    # Call the LangGraph app
    with st.chat_message("assistant"):
        with st.spinner("Working on it..."):
            try:
                response_state = app.invoke(current_graph_state)
                st.session_state.persistent_state = response_state
                st.rerun()
            except Exception as e:
                st.error(f"Error calling LangGraph: {str(e)}")
                st.session_state.persistent_state["chat_history"].append(
                    AIMessage(content=f"Sorry, an error occurred: {str(e)}")
                )
                st.rerun()

else:
    if not st.session_state.persistent_state.get("chat_history"):
        st.info("Type a message below to start the conversation!")