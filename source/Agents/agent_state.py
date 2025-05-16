from typing import Annotated, List, Tuple, Union, TypedDict, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages.tool import ToolMessage

class AgentState(TypedDict):
    """
    Represents the state of the agentic solar adoption process.
    """
    input: str  # User input for the current turn
    chat_history: List[Union[AIMessage, HumanMessage, ToolMessage]] # Full conversation history
    tool_output: Optional[Union[str, List[dict], dict]]  # Output from the latest tool call
    current_stage: str  # e.g., "welcome", "gather_info", "search_solar", "present_options", "select_solar", "confirm_solar", "search_subsidies", "apply_subsidies", "setup_grid_flexibility", "provide_status", "end", "error"
    user_info: dict  # Stores collected user data (location, bill, etc.)
    solar_options: List[dict] # Stores results from solar search
    selected_solar_option: Optional[dict] # Stores the user's selected option
    order_id: Optional[str] # Beckn order ID after confirmation
    subsidy_search_results: Optional[List[dict]] # Stores results from subsidy search
    applied_subsidy_order_id: Optional[str] # Beckn subsidy order ID after confirmation
    world_engine_data: Optional[dict] # Stores data fetched from World Engine
    meter_id: Optional[int] # World Engine Meter ID created for the user
    energy_resource_id: Optional[int] # World Engine Energy Resource ID for the user
    der_ids: List[int] # List of DER IDs created/managed for the user
    beckn_context: dict # Stores Beckn context variables (bap_id, etc.)
    error_message: Optional[str] # Stores error messages from the current turn
    # Added for LLM context generation:
    latest_tool_output_summary: Optional[str] # Summary description of the latest tool output
