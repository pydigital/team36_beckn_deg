import gradio as gr
import json # For formatting tool arguments if necessary
from typing import List, Tuple, Sequence, Dict, Any, Union

# --- Part 1: Import your LangGraph components ---
# This section assumes your LangGraph code (app, AgentState, message types)
# is available. You might need to adjust imports based on your project structure.

# Example: from langgraph_parts import app, AgentState, HumanMessage, AIMessage, ToolMessage
# If they are in the same file, you don't need to import them like this.

# Placeholder for your LangGraph components (replace with actual imports/definitions)
# Example AgentState (ensure this matches your actual AgentState)
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
# from AIMessage import AIMessage # If AIMessage has tool_calls, it's usually from langchain_core.messages
# from langchain_core.messages import ToolMessage # If you use ToolMessage

# class AgentState(TypedDict):
#     chat_history: Annotated[Sequence[BaseMessage], operator.add]
#     current_stage: str
#     accumulated_info: Dict[str, Any]
#     original_query: str
#     options: List[Any]
#     selected_option_id: str | None
#     final_answer_generated: bool
#     # user_input: str # If your AgentState explicitly carries the current turn's user input
#     # Add any other fields your AgentState uses

# Placeholder for your compiled LangGraph app
# app = None # Replace with your actual compiled LangGraph application: app = workflow.compile()

# --- End of LangGraph component placeholders ---


# --- Part 2: Initial State and Helper Functions ---

# Define the initial structure of your persistent state for the LangGraph app
# This must match the structure your LangGraph app expects and manages.
INITIAL_STATE: Dict[str, Any] = {
    "chat_history": [],
    "current_stage": "welcome",  # Or your graph's actual initial stage
    "accumulated_info": {},
    "original_query": "",
    "options": [],
    "selected_option_id": None,
    "final_answer_generated": False,
    # Initialize other AgentState fields as needed
}

def format_aimessage_content_for_display(msg: AIMessage) -> str:
    """
    Formats AIMessage content, including text and tool calls, for display.
    """
    content_str = ""
    # AIMessage.content can be a string or a list of content blocks (e.g., for Anthropic models)
    if isinstance(msg.content, str):
        content_str = msg.content
    elif isinstance(msg.content, list):
        for block in msg.content:
            if isinstance(block, dict) and block.get("type") == "text":
                content_str += block.get("text", "") + "\n"
            elif isinstance(block, str): # Simpler list of strings
                content_str += block + "\n"

    # Append tool call information if present
    if hasattr(msg, 'tool_calls') and msg.tool_calls and len(msg.tool_calls) > 0:
        tool_calls_formatted = []
        for tc in msg.tool_calls:
            # Standard LangChain tool_calls are dicts with 'name', 'args', 'id'
            if isinstance(tc, dict) and 'name' in tc and 'args' in tc:
                try:
                    args_str = json.dumps(tc['args'])
                except TypeError:
                    args_str = str(tc['args']) # Fallback for non-serializable args
                tool_calls_formatted.append(f" দেখুনঃtool_code\n{tc['name']}({args_str})\nID: {tc.get('id', 'N/A')}\n")
            # Adapt if your tool_calls structure is different
        if tool_calls_formatted:
            content_str += "\n" + "\n".join(tool_calls_formatted)
    return content_str.strip()

def convert_langchain_history_to_gradio_chatbot_format(
    lc_history: Sequence[BaseMessage]
) -> List[Tuple[Union[str, None], Union[str, None]]]:
    """
    Converts LangChain message history to Gradio Chatbot's format.
    Gradio expects a list of (user_message, bot_message) tuples.
    """
    gradio_chat_history: List[Tuple[Union[str, None], Union[str, None]]] = []
    current_user_msg_content: Union[str, None] = None
    current_bot_responses: List[str] = []

    def flush_bot_responses_to_gradio_history():
        nonlocal current_user_msg_content, current_bot_responses, gradio_chat_history
        if current_bot_responses:
            gradio_chat_history.append((current_user_msg_content, "\n".join(current_bot_responses)))
            current_bot_responses = []
        elif current_user_msg_content:  # User message without any bot response text yet
            gradio_chat_history.append((current_user_msg_content, None))
        current_user_msg_content = None

    for msg in lc_history:
        if isinstance(msg, HumanMessage):
            flush_bot_responses_to_gradio_history()  # Finalize any previous bot turn
            current_user_msg_content = msg.content
        elif isinstance(msg, AIMessage):
            current_bot_responses.append(format_aimessage_content_for_display(msg))
        # elif isinstance(msg, ToolMessage): # Assuming ToolMessage content should be displayed as part of bot's turn
        #     tool_name = getattr(msg, 'name', 'N/A')
        #     tool_id = getattr(msg, 'tool_call_id', 'N/A')
        #     current_bot_responses.append(f"🛠️ Tool Result ({tool_name}, ID: {tool_id}):\n{msg.content}")
        # Note: ToolMessages are often processed by the graph and result in a subsequent AIMessage.
        # If your graph directly adds ToolMessages to chat_history for display, uncomment and adjust.

    flush_bot_responses_to_gradio_history()  # Finalize the last turn

    return gradio_chat_history

# --- Part 3: Gradio Interaction Logic ---

def chat_interaction_fn(
    user_input_text: str,
    # chat_display_history: List[Tuple[str | None, str | None]], # Current Gradio display history (can be useful)
    persistent_state_dict: Dict[str, Any]  # From gr.State, this is our LangGraph state
) -> Tuple[List[Tuple[Union[str, None], Union[str, None]]], Dict[str, Any], str]:
    """
    Handles a single turn of conversation.
    1. Updates LangGraph state with user input.
    2. Invokes the LangGraph app.
    3. Updates persistent_state_dict with the new state.
    4. Formats the full history for Gradio Chatbot.
    5. Returns new display history, new persistent state, and clears textbox.
    """
    # Add user's message to the LangGraph chat_history within the persistent state
    # Make sure persistent_state_dict is a mutable dictionary
    current_lc_history = persistent_state_dict.get("chat_history", [])
    if not isinstance(current_lc_history, list): # Ensure it's a list
        current_lc_history = list(current_lc_history) # Convert if it's a tuple from previous state
        
    current_lc_history.append(HumanMessage(content=user_input_text))
    persistent_state_dict["chat_history"] = current_lc_history
    
    # (Optional) If your AgentState has a specific 'user_input' field for the current turn:
    # persistent_state_dict["user_input"] = user_input_text

    # Invoke the LangGraph app with the current state
    # Ensure your `app` object is available in this scope
    if app is None: # Check if app is loaded
        # This case should ideally not be hit if app is initialized globally
        error_message = "LangGraph app not loaded!"
        updated_lc_history = persistent_state_dict["chat_history"] + [AIMessage(content=error_message)]
        gradio_history_to_display = convert_langchain_history_to_gradio_chatbot_format(updated_lc_history)
        return gradio_history_to_display, persistent_state_dict, ""

    # Create a copy of the state to pass to invoke, as some graph operations might mutate input
    # or if you want to ensure the original persistent_state_dict isn't directly modified by app.invoke
    # (though app.invoke should return a new state object).
    input_to_invoke = persistent_state_dict.copy()
    
    try:
        updated_persistent_state_from_graph = app.invoke(input_to_invoke)
    except Exception as e:
        print(f"Error during LangGraph app.invoke: {e}")
        # Add error message to chat history for the user to see
        error_response = f"An error occurred: {str(e)}"
        persistent_state_dict["chat_history"].append(AIMessage(content=error_response))
        updated_persistent_state_from_graph = persistent_state_dict # Use current state with error added
        
    # Convert the full updated LangGraph chat_history to Gradio's chatbot format
    gradio_history_to_display = convert_langchain_history_to_gradio_chatbot_format(
        updated_persistent_state_from_graph.get("chat_history", [])
    )
    
    # Return new display history, the fully updated state for gr.State, and clear the textbox
    return gradio_history_to_display, updated_persistent_state_from_graph, ""


# --- Part 4: Gradio UI Definition ---

# Custom CSS for a "phone screen" or "WhatsApp" like appearance
# You can expand this with more specific styling.
custom_css = """
body { font-family: 'Roboto', sans-serif; background-color: #E5DDD5; } /* WhatsApp-like background */
.gradio-container { 
    max-width: 450px !important; /* Phone screen width */
    margin: auto !important; 
    border-radius: 20px; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    background-color: #F0F0F0; /* Inner background */
    overflow: hidden; /* For rounded corners */
}
#chat_window_column { padding: 0px !important; }
#chatbot_display { 
    height: 600px !important; 
    overflow-y: auto; 
    background-color: #E5DDD5; /* Chat background */
    padding: 10px;
    border-bottom: 1px solid #D1D1D1;
}
#chatbot_display .message-wrap { /* Target the wrapper for message styling */
    display: flex;
    flex-direction: column;
    margin-bottom: 8px;
}
#chatbot_display .message-wrap .message { /* Common message styles */
    padding: 8px 12px;
    border-radius: 18px;
    max-width: 75%;
    word-wrap: break-word;
    box-shadow: 0 1px 1px rgba(0,0,0,0.05);
    font-size: 0.95em;
    line-height: 1.4;
}
#chatbot_display .message-wrap.user .message { /* User messages */
    background-color: #DCF8C6 !important; /* WhatsApp green */
    color: #303030;
    align-self: flex-end;
    border-bottom-right-radius: 4px; /* WhatsApp tail effect */
}
#chatbot_display .message-wrap.bot .message { /* Bot messages */
    background-color: #FFFFFF !important;
    color: #303030;
    align-self: flex-start;
    border-bottom-left-radius: 4px; /* WhatsApp tail effect */
}
#input_row { padding: 10px; background-color: #F0F0F0; border-top: 1px solid #D1D1D1;}
#input_textbox textarea { border-radius: 18px !important; padding: 10px !important; }
#send_button { border-radius: 18px !important; min-width: 60px !important; }
.gr-footer { display: none !important; } /* Hide Gradio footer for cleaner look */
"""

with gr.Blocks(theme=gr.themes.Soft(font=[gr.themes.GoogleFont("Roboto"), "Arial", "sans-serif"]), css=custom_css) as demo:
    gr.Markdown("<h1 style='text-align: center; color: #075E54; margin-top:10px;'>Solar Assistant ☀️</h1>") # WhatsApp Header Color

    # Initialize persistent_state using gr.State. Make a deep copy of INITIAL_STATE if it's complex.
    # Using .copy() for dicts is usually sufficient for one level.
    current_persistent_state = gr.State(INITIAL_STATE.copy())
    
    # Attempt to get an initial welcome message if your graph supports it
    # This would typically involve invoking the graph with an initial state.
    # For simplicity here, we'll start with an empty chat or a predefined welcome.
    # If your graph CAN start with an AI message (e.g., entry point is `update_state`):
    #   initial_gradio_history, initial_state_for_gr = get_initial_bot_message_and_state_on_load()
    # Else (user must speak first or use a canned welcome):
    initial_gradio_history = [] # Start with empty chat
    # Or, a canned welcome:
    # initial_gradio_history = [(None, "Hello! I'm your Solar Assistant. How can I help you today?")]
    # initial_persistent_state["chat_history"] = [AIMessage(content="Hello! I'm your Solar Assistant...")]


    with gr.Column(elem_id="chat_window_column"):
        chatbot_display = gr.Chatbot(
            value=initial_gradio_history,
            label="Conversation",
            bubble_full_width=False, # Important for styling individual bubbles
            height=600, # Adjust as needed
            elem_id="chatbot_display",
            show_copy_button=True,
        )

        with gr.Row(elem_id="input_row"):
            input_textbox = gr.Textbox(
                show_label=False,
                placeholder="Type a message...",
                lines=1,
                scale=4, # Relative width
                elem_id="input_textbox",
                autofocus=True,
            )
            send_button = gr.Button("Send", scale=1, variant="primary", elem_id="send_button")

    # Define what happens on submit (Enter in textbox or click Send button)
    def on_submit_message(user_text, persistent_state_val):
        if not user_text.strip(): # Prevent sending empty messages
            # To keep Gradio happy, return existing state if no action
            # This requires knowing the current chatbot display value.
            # A bit tricky with gr.State alone for chatbot.
            # Better to handle this by disabling button or just processing and returning same.
            # For now, let user send, chat_interaction_fn can handle empty if needed.
             pass # Let it go to chat_interaction_fn, or handle here.
        
        # Call the main interaction logic
        # Note: chatbot_display.value isn't directly passed here if we rely on full history re-render
        new_display, new_state, cleared_text = chat_interaction_fn(
            user_text,
            persistent_state_val
        )
        return new_display, new_state, cleared_text

    submit_action = [input_textbox, current_persistent_state] # Inputs to on_submit_message
    update_action = [chatbot_display, current_persistent_state, input_textbox] # Outputs to update

    input_textbox.submit(on_submit_message, inputs=submit_action, outputs=update_action)
    send_button.click(on_submit_message, inputs=submit_action, outputs=update_action)

    # You could add a demo.load() event here if you want the AI to send a welcome message
    # when the app loads, assuming your graph can generate it from an initial state.
    # Example:
    def on_load(persistent_state_val):
        # Invoke graph to get welcome message
        # initial_state_for_invoke = persistent_state_val.copy() # Or INITIAL_STATE.copy()
        # updated_state = app.invoke(initial_state_for_invoke) # Assuming this produces a welcome
        # welcome_history_display = convert_langchain_history_to_gradio_chatbot_format(updated_state["chat_history"])
        # return welcome_history_display, updated_state
        # For now, let's use a canned welcome message or empty.
        canned_welcome_text = "Hello! I'm your Solar Assistant. How can I help you today?"
        initial_state_on_load = INITIAL_STATE.copy()
        initial_state_on_load["chat_history"] = [AIMessage(content=canned_welcome_text)]
        display = convert_langchain_history_to_gradio_chatbot_format(initial_state_on_load["chat_history"])
        return display, initial_state_on_load
    
    demo.load(on_load, inputs=[current_persistent_state], outputs=[chatbot_display, current_persistent_state])
    # Note: on_load will use the initial value of current_persistent_state.

# --- Part 5: Launch the Gradio App ---

if __name__ == "__main__":
    # Ensure your LangGraph 'app' is compiled and available here
    # For example, if it's in langgraph_parts.py:
    try:
        from langgraph_parts import app, AgentState, HumanMessage, AIMessage #, ToolMessage
        # If your AgentState is also in langgraph_parts, this covers it.
        print("LangGraph app and components loaded successfully.")
        if app is None:
            raise ImportError("The 'app' object from langgraph_parts is None.")
    except ImportError as e:
        print(f"Error importing LangGraph components: {e}")
        print("Please ensure 'langgraph_parts.py' exists and 'app' is compiled.")
        print("Using placeholder app for UI demonstration purposes ONLY.")
        # Placeholder app for UI demonstration if main app fails to load
        class PlaceholderApp:
            def invoke(self, state_dict):
                response_text = f"Placeholder response to: {state_dict['chat_history'][-1].content if state_dict['chat_history'] else '...'}"
                state_dict["chat_history"].append(AIMessage(content=response_text))
                return state_dict
        app = PlaceholderApp()
        # Define placeholder messages if not imported
        if 'HumanMessage' not in globals(): HumanMessage = type('HumanMessage', (), {'content': ''})
        if 'AIMessage' not in globals(): AIMessage = type('AIMessage', (), {'content': '', 'tool_calls': []})


    demo.launch(share=True)
    # demo.launch(share=True) # If you want a public link (use with caution)
    # demo.launch(server_name="0.0.0.0", server_port=7860) # To run on network