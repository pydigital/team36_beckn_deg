
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import copy
import traceback
import datetime

# --- Call st.set_page_config() as the FIRST Streamlit command ---
st.set_page_config(page_title="AI Chatbot", layout="wide", initial_sidebar_state="collapsed")

class StreamlitChatApp:
    def __init__(self):
        """
        Initializes the chat application, loading LangGraph components and setting up initial state.
        """
        self.app = None
        self.initial_state = {"chat_history": [], "input": None} # Default placeholder
        self.langgraph_available = self._load_langgraph_components()
        self._initialize_session_state()

    def _load_langgraph_components(self):
        """
        Loads the LangGraph application and initial state from langgraph_parts.py.
        Returns True if successful, False otherwise.
        """
        try:
            from langgraph_parts import app as lg_app # Use an alias to avoid conflict
            self.app = lg_app
            try:
                from langgraph_parts import INITIAL_STATE as lg_initial_state
                self.initial_state = copy.deepcopy(lg_initial_state) # Use a copy
                if 'input' not in self.initial_state:
                    st.warning("Warning: 'input' key not found in INITIAL_STATE from langgraph_parts. Adding it with None value.")
                    self.initial_state['input'] = None
            except ImportError:
                st.warning("INITIAL_STATE not found in langgraph_parts.py. Using a basic placeholder. Ensure all state keys are present.")
                # Basic INITIAL_STATE already set in __init__, ensure 'input' is there.
                if 'input' not in self.initial_state:
                     self.initial_state['input'] = None
            return True
        except ImportError as e:
            st.error(f"Error importing from langgraph_parts.py: {e}")
            # Define a dummy app for UI to function without backend
            def dummy_app(state):
                state["chat_history"].append(AIMessage(content="LangGraph backend error: Components not loaded."))
                return state
            self.app = dummy_app
            return False

    def _initialize_session_state(self):
        """
        Initializes Streamlit's session state for persistent data across reruns.
        """
        if "persistent_state" not in st.session_state:
            st.session_state.persistent_state = copy.deepcopy(self.initial_state)

    def _render_css(self):
        """
        Injects custom CSS for the phone screen view.
        """
        phone_styles_css = """
        <style>
        body {
            background-color: #F0F2F5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; padding: 0;
        }
        .phone-wrapper {
            display: flex; justify-content: center; align-items: center;
            padding: 20px 10px; min-height: 95vh; box-sizing: border-box;
        }
        .phone-container {
            width: 375px; height: 812px; border: 10px solid black;
            border-radius: 44px; 
            box-shadow: 0px 0px 0px 11px #1c1c1e, 0px 0px 0px 13px #1c1c1e, 0px 20px 40px rgba(0, 0, 0, 0.4);
            background-color: #FFF; display: flex; flex-direction: column;
            overflow: hidden; position: relative;
        }
        .phone-container::before { /* Notch/Island */
            content: ''; position: absolute; top: 10px; left: 50%;
            transform: translateX(-50%); width: 120px; height: 28px;
            background-color: black; border-radius: 14px; z-index: 100;
        }
        .status-bar {
            height: 44px; background-color: #FFF; display: flex;
            justify-content: space-between; align-items: center; padding: 0 20px;
            font-size: 13px; font-weight: 600; color: #000;
            flex-shrink: 0; position: relative; z-index: 50;
            box-sizing: border-box; padding-top: 10px; /* Below notch */
        }
        .status-bar .time { position: absolute; left: 50%; transform: translateX(-50%); }
        .status-bar .right-icons { display: flex; align-items: center; gap: 5px; }
        .chat-area-wrapper {
            flex-grow: 1; overflow-y: auto; padding: 0px 10px 10px 10px;
            background-color: #FFF; display: flex; flex-direction: column-reverse;
        }
        .message-bubble-container { display: flex; width: 100%; margin-bottom: 2px; }
        .user-bubble .message-bubble-container { justify-content: flex-end; }
        .assistant-bubble .message-bubble-container { justify-content: flex-start; }
        .message-bubble {
            max-width: 75%; padding: 8px 14px; border-radius: 18px;
            word-wrap: break-word; line-height: 1.4; font-size: 15px;
        }
        .user-bubble .message-bubble { background-color: #007AFF; color: white; border-bottom-right-radius: 4px;}
        .assistant-bubble .message-bubble { background-color: #E5E5EA; color: black; border-bottom-left-radius: 4px;}
        .chat-input-container {
            padding: 8px 10px 15px 10px; background-color: #F0F2F5;
            border-top: 1px solid #DCDCDC; flex-shrink: 0;
        }
        div[data-testid="stChatInput"] { /* Style Streamlit's chat input */
            background-color: white !important; border-radius: 20px !important;
            border: 1px solid #DCDCDC !important; padding: 0 5px !important;
        }
        </style>
        """
        st.markdown(phone_styles_css, unsafe_allow_html=True)

    def _render_status_bar_js(self):
        """
        Injects JavaScript for the dynamic time in the status bar.
        """
        now = datetime.datetime.now()
        current_time_str = now.strftime("%-I:%M") # e.g., "9:41"

        status_bar_js = f"""
        <script>
        function updateStatusBarTime() {{
            const timeElement = document.getElementById('status-bar-time');
            if (timeElement) {{
                const now = new Date();
                const hours = now.getHours();
                const minutes = now.getMinutes().toString().padStart(2, '0');
                const ampmHours = hours % 12 || 12;
                timeElement.textContent = `${{ampmHours}}:${{minutes}}`;
            }}
        }}
        // Ensure this runs after the element exists
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', function() {{
                updateStatusBarTime();
                setInterval(updateStatusBarTime, 10000); // Update every 10 secs to reduce load
            }});
        }} else {{
            updateStatusBarTime();
            setInterval(updateStatusBarTime, 10000);
        }}
        </script>
        """
        st.markdown(status_bar_js, unsafe_allow_html=True)

    def _render_status_bar_html(self):
        """
        Renders the HTML for the status bar.
        """
        now = datetime.datetime.now()
        current_time_str = now.strftime("%-I:%M")
        st.markdown(f"""
            <div class="status-bar">
                <span id="status-bar-time">{current_time_str}</span>
                <div class="right-icons">
                    <span>📶</span>
                    <span>Wi-Fi</span>
                    <span>🔋</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    def _display_messages_in_phone(self, chat_history):
        """
        Renders chat messages within the phone UI using custom HTML bubbles.
        """
        for msg_idx, msg in enumerate(reversed(chat_history)):
            unique_key_suffix = f"msg_{len(chat_history) - 1 - msg_idx}"
            bubble_class = ""
            if isinstance(msg, HumanMessage):
                bubble_class = "user-bubble"
                content = msg.content
            elif isinstance(msg, AIMessage):
                if msg.content and str(msg.content).strip():
                    bubble_class = "assistant-bubble"
                    content = msg.content
                else:
                    continue # Skip empty AI messages
            else:
                continue # Skip other message types

            st.markdown(f"""
                <div class="{bubble_class} message-bubble-container" key="{unique_key_suffix}_container">
                    <div class="message-bubble" key="{unique_key_suffix}">
                        {content}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    def _handle_user_input(self, user_query):
        """
        Processes user input, calls the LangGraph app, and updates session state.
        """
        if not user_query:
            return

        st.session_state.persistent_state["chat_history"].append(HumanMessage(content=user_query))

        current_graph_state = copy.deepcopy(st.session_state.persistent_state)
        if "input" in current_graph_state:
            current_graph_state["input"] = user_query
        else:
            # This should ideally not happen if INITIAL_STATE is correctly set up
            st.error("Critical error: 'input' key missing in graph state. Check INITIAL_STATE setup.")
            current_graph_state['input'] = user_query # Fallback

        try:
            response_state = self.app.invoke(current_graph_state)
            st.session_state.persistent_state = response_state
        except Exception as e:
            error_message_for_chat = f"Sorry, an error occurred: {str(e)[:100]}..."
            st.error(f"An error occurred: {str(e)}. Check console for full traceback.")
            print(f"--- ERROR Encountered during app.invoke: {str(e)} ---")
            traceback.print_exc()
            st.session_state.persistent_state["chat_history"].append(
                AIMessage(content=error_message_for_chat)
            )
        st.rerun()

    def run(self):
        """
        Main method to render the Streamlit UI and handle interactions.
        """
        self._render_css()

        if not self.langgraph_available:
            st.error("The LangGraph backend is not available. Please fix the import issues.")
            st.stop()

        # --- Phone UI Structure ---
        st.markdown('<div class="phone-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="phone-container">', unsafe_allow_html=True)

        self._render_status_bar_html()
        self._render_status_bar_js() # JS needs to be rendered after HTML elements

        # --- Chat Area ---
        # The st.container() itself doesn't take a class, so we wrap our styled div inside it.
        with st.container():
            st.markdown('<div class="chat-area-wrapper" id="chat-area-wrapper-id">', unsafe_allow_html=True)
            if "persistent_state" in st.session_state and "chat_history" in st.session_state.persistent_state:
                self._display_messages_in_phone(st.session_state.persistent_state["chat_history"])
            st.markdown('</div>', unsafe_allow_html=True)

        # --- Chat Input ---
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        # Key for chat_input must be unique and stable.
        user_query = st.chat_input("Message", key="chat_input_field_main")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True) # End phone-container and phone-wrapper

        if user_query:
            self._handle_user_input(user_query)

if __name__ == "__main__":
    chat_app = StreamlitChatApp()
    chat_app.run()
