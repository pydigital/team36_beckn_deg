import json
import operator
import random
import uuid
import datetime
import os # Import the os module
from typing import Annotated, List, Tuple, Union, TypedDict, Optional

import requests
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages.tool import ToolMessage
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv # Import load_dotenv

# --- Load environment variables from .env file ---
load_dotenv()

from google.cloud import aiplatform
aiplatform.init(project="e-dragon-459817-h0")

# --- Get variables from environment ---
gcp_project = os.getenv("GCP_PROJECT")
BECKN_BASE_URL = os.getenv("BECKN_BASE_URL")
WORLD_ENGINE_BASE_URL = os.getenv("WORLD_ENGINE_BASE_URL")
BECKN_BAP_ID = os.getenv("BECKN_BAP_ID")
BECKN_BAP_URI = os.getenv("BECKN_BAP_URI")
BECKN_BPP_ID = os.getenv("BECKN_BPP_ID")
BECKN_BPP_URI = os.getenv("BECKN_BPP_URI")
bap_id = BECKN_BAP_ID
bap_uri = BECKN_BAP_URI
bpp_id = BECKN_BPP_ID
bpp_uri = BECKN_BPP_URI
# Check if essential variables are loaded
if not all([BECKN_BASE_URL, WORLD_ENGINE_BASE_URL, BECKN_BAP_ID, BECKN_BAP_URI, BECKN_BPP_ID, BECKN_BPP_URI]):
    raise EnvironmentError("Missing one or more required environment variables. Ensure .env file exists and contains all necessary variables.")


# --- Define API Functions as LangChain Tools ---
###====================================###
@tool
def beckn_connection_search() -> dict:
    """
    Triggers the Search API for Beckn Connection to find available services.
    Requires provider_id, item_id.
    """
    url = f"{BECKN_BASE_URL}/search"
    headers = { "Content-Type": "application/json" }
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    payload = {
        "context": {
            "domain": "deg:service",
            "action": "search",
            "location": { "country": { "code": "USA" } }, # Assuming USA for now, could be parameterized
            "version": "1.1.0",
            "bap_id": bap_id,
            "bap_uri": bap_uri,
            "bpp_id": bpp_id,
            "bpp_uri": bpp_uri,
            "transaction_id": transaction_id,
            "message_id": message_id,
            "timestamp": timestamp
        },
        "message": { "intent": { "item": { "descriptor": { "name": "Connection" } } } }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

@tool
def beckn_solar_retail_search() -> dict:
    """
    Triggers the Search API for Beckn Solar-Retail and Battery-Retail to find solar and battery product and service offerings.
    Requires provider_id, item_id.
    """
    url = f"{BECKN_BASE_URL}/search"
    headers = { "Content-Type": "application/json" }
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    payload = {
        "context": {
            "domain": "deg:retail",
            "action": "search",
            "location": { "country": { "code": "USA" }, "city": { "code": "NANP:628" } }, # Assuming specific city for now
            "version": "1.1.0",
            "bap_id": bap_id,
            "bap_uri": bap_uri,
            "bpp_id": bpp_id,
            "bpp_uri": bpp_uri,
            "transaction_id": transaction_id,
            "message_id": message_id,
            "timestamp": timestamp
        },
        "message": { "intent": { "item": { "descriptor": { "name": "solar" } } } }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}


@tool
def beckn_solar_retail_select(provider_id: str, item_id: str) -> dict:
    """
    Triggers the Select API for Beckn Solar-Retail and Battery-Retail to select a specific solar and battery offering.
    Requires provider_id, item_id.
    """
    url = f"{BECKN_BASE_URL}/select"
    headers = { "Content-Type": "application/json" }
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    payload = {
      "context": {
        "domain": "deg:retail",
        "action": "select",
        "location": { "country": { "code": "USA" }, "city": { "code": "NANP:628" } },
        "version": "1.1.0",
        "bap_id": bap_id,
        "bap_uri": bap_uri,
        "bpp_id": bpp_id,
        "bpp_uri": bpp_uri,
        "transaction_id": transaction_id,
        "message_id": message_id,
        "timestamp": timestamp
      },
      "message": {
       "order": {
                "provider": { "id": provider_id },
                "items": [ { "id": item_id } ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

@tool
def beckn_solar_retail_init(provider_id: str, item_id: str) -> dict:
    """
    Triggers the Init API for Beckn Solar-Retail to initialize the order/process.
    Requires provider_id, item_id.
    """
    url = f"{BECKN_BASE_URL}/init"
    headers = { "Content-Type": "application/json" }
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    payload = {
      "context": {
        "domain": "deg:retail",
        "action": "init",
        "location": { "country": { "code": "USA" }, "city": { "code": "NANP:628" } },
        "version": "1.1.0",
        "bap_id": bap_id,
        "bap_uri": bap_uri,
        "bpp_id": bpp_id,
        "bpp_uri": bpp_uri,
        "transaction_id": transaction_id,
        "message_id": message_id,
        "timestamp": timestamp
      },
      "message": {
       "order": {
                "provider": { "id": provider_id },
                "items": [ { "id": item_id } ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

@tool
def beckn_solar_retail_confirm(provider_id: str, item_id: str, fulfillment_id: str, customer_name: str, customer_phone: str, customer_email: str) -> dict:
    """
    Triggers the Confirm API for Beckn Solar-Retail to confirm the order/process.
    Requires provider_id, item_id, fulfillment_id, customer_name, customer_phone, and customer_email.
    """
    url = f"{BECKN_BASE_URL}/confirm"
    headers = { "Content-Type": "application/json" }
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    payload = {
      "context": {
        "domain": "deg:retail",
        "action": "confirm",
        "location": { "country": { "code": "USA" }, "city": { "code": "NANP:628" } },
        "version": "1.1.0",
        "bap_id": bap_id,
        "bap_uri": bap_uri,
        "bpp_id": bpp_id,
        "bpp_uri": bpp_uri,
        "transaction_id": transaction_id,
        "message_id": message_id,
        "timestamp": timestamp
      },
      "message": {
       "order": {
                "provider": { "id": provider_id },
                "items": [ { "id": item_id } ],
                  "fulfillments": [
                {
                  "id": fulfillment_id,
                  "customer": {
                    "person": { "name": customer_name },
                    "contact": { "phone": customer_phone, "email": customer_email }
                  }
                }
              ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

@tool
def beckn_solar_retail_status(order_id: str) -> dict:
    """
    Triggers the Status API for Beckn Solar-Retail to get the status of an order.
    Requires order_id.
    """
    url = f"{BECKN_BASE_URL}/status"
    headers = { "Content-Type": "application/json" }
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    payload = {
      "context": {
        "domain": "deg:retail",
        "action": "status",
        "location": { "country": { "code": "USA" }, "city": { "code": "NANP:628" } },
        "version": "1.1.0",
        "bap_id": bap_id,
        "bap_uri": bap_uri,
        "bpp_id": bpp_id,
        "bpp_uri": bpp_uri,
        "transaction_id": transaction_id,
        "message_id": message_id,
        "timestamp": timestamp
      },
      "message": { "order_id": order_id }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

@tool
def beckn_subsidy_search() -> dict:
    """
    Triggers the Search API for Beckn Subsidy to find available incentives.
    Requires no parameters.
    """
    url = f"{BECKN_BASE_URL}/search"
    headers = { "Content-Type": "application/json" }
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    payload = {
        "context": {
            "domain": "deg:schemes",
            "action": "search",
            "location": { "country": { "code": "USA" }, "city": { "code": "NANP:628" } }, # Assuming specific city for now
            "version": "1.1.0",
            "bap_id": bap_id,
            "bap_uri": bap_uri,
            "bpp_id": bpp_id,
            "bpp_uri": bpp_uri,
            "transaction_id": transaction_id,
            "message_id": message_id, # Note: message_id was missing in original JSON for this search
            "timestamp": timestamp
        },
        "message": { "intent": { "item": { "descriptor": { "name": "incentive" } } } }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}


@tool
def beckn_subsidy_confirm(provider_id: str, item_id: str, fulfillment_id: str, customer_name: str, customer_phone: str, customer_email: str) -> dict:
    """
    Triggers the Confirm API for Beckn Subsidy to apply for an incentive.
    Requires provider_id, item_id, fulfillment_id, customer_name, customer_phone, and customer_email.
    """
    url = f"{BECKN_BASE_URL}/confirm"
    headers = { "Content-Type": "application/json" }
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    payload = {
      "context": {
        "domain": "deg:schemes",
        "action": "confirm",
        "location": { "country": { "code": "USA" }, "city": { "code": "NANP:628" } },
        "version": "1.1.0",
        "bap_id": bap_id,
        "bap_uri": bap_uri,
        "bpp_id": bpp_id,
        "bpp_uri": bpp_uri,
        "transaction_id": transaction_id,
        "message_id": message_id,
        "timestamp": timestamp
      },
      "message": {
       "order": {
                "provider": { "id": provider_id },
                "items": [ { "id": item_id } ],
                 "fulfillments": [
                {
                  "id": fulfillment_id,
                  "customer": {
                    "person": { "name": customer_name },
                    "contact": { "phone": customer_phone, "email": customer_email }
                  }
                }
              ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

# Note: Beckn DFP APIs are similar to Subsidy APIs in the provided collection,
# so we can potentially reuse or adapt the subsidy functions if DFP uses the same structure.
# For now, let's focus on the core solar adoption and a simple DFP enrollment via World Engine.


# World Engine Sandbox API Functions
@tool
def world_engine_get_utilities_data() -> dict:
    """
    Retrieves detailed data about utilities, substations, transformers, and meters from the World Engine.
    """
    url = f"{WORLD_ENGINE_BASE_URL}/utility/detailed"
    headers = { "Content-Type": "application/json" }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

@tool
def world_engine_create_meter(code: str, type: str, city: str, state: str, latitude: float, longitude: float, pincode: str, parent: Optional[int] = None, energyResource: Optional[int] = None, consumptionLoadFactor: float = 1.0, productionLoadFactor: float = 0.0) -> dict:
    """
    Creates a new meter in the World Engine.
    Requires code, type, city, state, latitude, longitude, pincode.
    Optional: parent (Transformer ID), energyResource (Energy Resource ID), consumptionLoadFactor, productionLoadFactor.
    """
    url = f"{WORLD_ENGINE_BASE_URL}/meters"
    headers = { "Content-Type": "application/json" }
    payload = {
        "data": {
            "code": code,
            "parent": parent,
            "energyResource": energyResource,
            "consumptionLoadFactor": consumptionLoadFactor,
            "productionLoadFactor": productionLoadFactor,
            "type": type,
            "city": city,
            "state": state,
            "latitude": latitude,
            "longitude": longitude,
            "pincode": pincode
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

@tool
def world_engine_create_energy_resource(name: str, meter: Optional[int] = None) -> dict:
    """
    Creates a new energy resource (e.g., Household) in the World Engine.
    Requires name and optional: meter (Meter ID).
    """
    url = f"{WORLD_ENGINE_BASE_URL}/energy-resources"
    headers = { "Content-Type": "application/json" }
    payload = {
        "data": {
            "name": name,
            "type": 'CUSTOMER',
            "meter": meter
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}

@tool
def world_engine_create_der(energy_resource_id: int, appliance_id: int, switched_on: bool = True) -> dict:
    """
    Creates a new Distributed Energy Resource (DER) associated with an energy resource (e.g., a solar panel or smart charger for a household).
    Requires energy_resource_id and appliance_id. Optional: switched_on (default True).
    """
    url = f"{WORLD_ENGINE_BASE_URL}/der"
    headers = { "Content-Type": "application/json" }
    payload = {
        "energy_resource": energy_resource_id,
        "appliance": appliance_id,
        "switched_on": switched_on
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}


@tool
def world_engine_toggle_der_switching(der_id: int) -> dict:
    """
    Toggles the switched_on status of a DER in the World Engine.
    Requires der_id.
    """
    url = f"{WORLD_ENGINE_BASE_URL}/toggle-der/{der_id}"
    headers = { "Content-Type": "application/json" }
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}
###====================================###
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

def create_beckn_context():
     return {
        "bap_id": BECKN_BAP_ID,
        "bap_uri": BECKN_BAP_URI,
        "bpp_id": BECKN_BPP_ID,
        "bpp_uri": BECKN_BPP_URI
    }


# Initialize the LLM and tools
llm = ChatVertexAI(model="gemini-2.5-flash-preview-04-17", temperature=0) # Use the specified model
tools = [
    beckn_connection_search,
    beckn_solar_retail_search,
    beckn_solar_retail_select,
    beckn_solar_retail_init,
    beckn_solar_retail_confirm,
    beckn_solar_retail_status,
    beckn_subsidy_search,
    beckn_subsidy_confirm,
    world_engine_get_utilities_data,
    world_engine_create_meter,
    world_engine_create_energy_resource,
    world_engine_create_der,
    world_engine_toggle_der_switching,
]
llm_with_tools = llm.bind_tools(tools)

# --- Graph Nodes ---

def handle_user_input(state: AgentState) -> AgentState:
    """Processes the initial user input and adds it to chat history."""
    user_input = state['input']
    print(f"--- handle_user_input ---:\nUser: {user_input}\n")

    # Determine initial stage based on user intent (simple keyword check)
    # This stage is set *before* update_state processes it.
    initial_stage = 'initial'
    if "solar" in user_input.lower() or "rooftop" in user_input.lower() or "incentive" in user_input.lower() or "flexibility program" in user_input.lower():
         initial_stage = 'gather_info'
    else:
         initial_stage = 'welcome' # If initial input is not directly about solar, start with welcome

    return {
        **state,
        'chat_history': state['chat_history'] + [HumanMessage(content=user_input)],
        'current_stage': initial_stage,
        'input': None, # Clear input after processing it
    }

def agent(state: AgentState) -> AgentState:
    """
    The core agent node that uses the LLM to decide the next action
    (tool call or generate a response) and generate user-facing text.
    """
    print(f"--- agent (Stage: {state['current_stage']}) ---")
    chat_history = state['chat_history'][:] # Use a copy

    # Construct a dynamic system message for the LLM
    # system_prompt_parts = [
    #     "You are an AI assistant specialized in helping households adopt rooftop solar and join grid flexibility programs.",
    #     "Your goal is to guide the user through the process seamlessly, handle API interactions, and provide clear updates.",
    #     "Always provide transparent information and progress updates.",
    #     "Based on the current stage of the process, the conversation history, and any recent tool outputs, decide on the best next action:",
    #     "1. Generate a friendly, conversational response to the user (e.g., asking for info, confirming a step, presenting options, explaining an error, providing status).",
    #     "2. Determine if a tool needs to be called to move the process forward. If so, formulate the correct tool call with accurate parameters based on the state and history.",
    #     "3. If the goal is achieved or the user indicates they want to stop, signal the end of the process.",
    #     f"The current stage is: {state['current_stage']}.",
    # ]
    system_prompt_parts = [
        "You are Inergy, a friendly AI buddy here to help folks with rooftop solar and grid flexibility programs.",
        "Your main job is to make this whole process super easy and clear for the user. Keep your answers sweet, and friendly!",
        "Always be upfront and let the user know what's happening.",
        "Okay, Inergy, look at where we are in the conversation (the current stage), what we've talked about (chat history), and any recent tool results. Then, figure out the best next step:",
        "1. Chat with the user: Keep it friendly and to the point. This could be asking for info, confirming something, showing options, explaining a hiccup, or giving a quick status update.",
        "2. Use a tool if needed: If you need to use one of your tools to move things along, make sure you set it up right with all the info from our chat and current state.",
        "3. Wrap it up: If everything's done, or if the user wants to stop, just say goodbye nicely.",
        f"We're currently at this stage: {state['current_stage']}.",
        "Remember to keep your responses concise and use a casual, helpful tone!"
    ]

    if state.get('error_message'):
         system_prompt_parts.append(f"An error occurred in the previous step: {state['error_message']}. You must inform the user about the error clearly and suggest how to proceed (e.g., try again, contact support, or restart the process).")

    if state.get('latest_tool_output_summary'):
         system_prompt_parts.append(f"Summary of the previous tool output: {state['latest_tool_output_summary']}. Use this information to generate your response or decide the next step.")
         # Optionally, add full tool output if needed for complex processing (be mindful of context window)
         # system_prompt_parts.append(f"Full latest tool output: {json.dumps(state['tool_output'])}")


    # Add relevant state variables to the prompt for context, especially for generating responses
    context_info = {
         'user_info': state.get('user_info'),
         'solar_options_count': len(state.get('solar_options', [])),
         'selected_solar_option': state.get('selected_solar_option'),
         'order_id': state.get('order_id'),
         'subsidy_search_results_count': len(state.get('subsidy_search_results', []) if state.get('subsidy_search_results') else []),
         'applied_subsidy_order_id': state.get('applied_subsidy_order_id'),
         'world_engine_setup_status': {
             'meter_created': state.get('meter_id') is not None,
             'energy_resource_created': state.get('energy_resource_id') is not None,
             'ders_created': len(state.get('der_ids', [])) > 0
         }
    }
    system_prompt_parts.append(f"Current process state summary: {json.dumps(context_info)}")

    # Provide specific instructions based on stage for better control
    if state['current_stage'] == 'welcome':
        system_prompt_parts.append("Start by introducing yourself and offering help with solar adoption and grid flexibility.")
    elif state['current_stage'] == 'gather_info':
        system_prompt_parts.append("Ask the user for their location (city, state, pincode) and average monthly electricity bill or consumption.")
        system_prompt_parts.append("If you detect location and consumption info in the user's input, update the user_info in the state and indicate readiness to search for solar. Give them visibility on thier high costs on annual level")
    elif state['current_stage'] == 'search_solar':
        system_prompt_parts.append("Call the `beckn_solar_retail_search` tool to find solar options. Show all options in a short user-friendly list.")
    elif state['current_stage'] == 'present_options':
         system_prompt_parts.append("Present the solar options found to the user clearly, mentioning their names and prices if available. Ask the user to select one by ID or number.")
         system_prompt_parts.append(f"Here are the options found: {json.dumps(state.get('solar_options'))}") # Pass full options for formatting
    elif state['current_stage'] == 'confirm_solar':
         system_prompt_parts.append("Call the `beckn_solar_retail_confirm` tool to confirm the selected solar option. Ensure you have `provider_id`, `item_id` from the `selected_solar_option`, and `customer_name`, `customer_phone`, `customer_email`, `fulfillment_id` from `user_info`. Generate a `fulfillment_id` if not already in `user_info`.")
    elif state['current_stage'] == 'search_subsidies':
         system_prompt_parts.append("Call the `beckn_subsidy_search` tool to find applicable subsidies.")
    elif state['current_stage'] == 'apply_subsidies':
         system_prompt_parts.append("If subsidies were found, select the most relevant one (or the first one for simplicity) and call the `beckn_subsidy_confirm` tool. Ensure you have the required parameters from the subsidy item and user_info. If no subsidies were found, inform the user and move to the next step.")
    elif state['current_stage'] == 'setup_grid_flexibility':
         system_prompt_parts.append("Set up the user's system in the World Engine for grid flexibility. Check if Energy Resource, Meter, and DERs exist based on state. If not, call the `world_engine_create_energy_resource`, `world_engine_create_meter`, and `world_engine_create_der` tools in sequence. You may need to call `world_engine_get_utilities_data` to find a parent transformer for the meter.")
    elif state['current_stage'] == 'provide_status':
        system_prompt_parts.append("Provide a summary of the user's solar adoption and grid flexibility setup status based on the information in the state (order IDs, meter ID, ER ID, DER IDs).")
    elif state['current_stage'] == 'end':
        system_prompt_parts.append("Thank the user and indicate that the process is complete.")
    elif state['current_stage'] == 'error':
         system_prompt_parts.append(f"An error occurred: {state.get('error_message')}. Inform the user about the error and ask how they'd like to proceed (e.g., retry, try something else).")


    system_message = SystemMessage(content="\n".join(system_prompt_parts))

    # Invoke the LLM with the system prompt and chat history
    response = llm_with_tools.invoke([system_message] + chat_history)

    # The agent's direct response or tool call will be the last message
    return {'chat_history': state['chat_history'] + [response]}

def call_tool(state: AgentState) -> AgentState:
    """Executes the tool call(s) recommended by the agent and adds ToolMessage to history."""
    print("--- call_tool ---")
    last_message = state['chat_history'][-1]
    tool_calls = last_message.tool_calls
    tool_outputs = []
    latest_output_summary = ""
    error_occurred = False

    for tool_call in tool_calls:
        print(f"Attempting to call tool: {tool_call.get('name')} with args {tool_call.get('args')}")
        try:
            tool_name = tool_call.get('name')
            tool_args = tool_call.get('args', {})
            tool_call_id = tool_call.get('id')

            # Need to handle the case where the LLM generates arguments that don't match the tool signature
            # Basic argument validation can be added here if needed
            # For simplicity, directly invoke the tool
            tool_function = globals().get(tool_name) # Get function by name

            if tool_function:
                 # Special handling for `world_engine_create_meter` to find a parent if not provided by LLM
                 if tool_name == 'world_engine_create_meter' and tool_args.get('parent') is None and state.get('world_engine_data') is None:
                      print("Attempting to fetch utility data to find meter parent...")
                      utility_data = world_engine_get_utilities_data.invoke({})
                      if 'error' not in utility_data and utility_data.get('utilities'):
                            state['world_engine_data'] = utility_data # Store for future use
                            # Find a transformer ID (simplistic: take the first one found)
                            transformer_id = None
                            if utility_data['utilities'] and utility_data['utilities'][0].get('substations'):
                                 if utility_data['utilities'][0]['substations'][0].get('transformers'):
                                      transformer_id = utility_data['utilities'][0]['substations'][0]['transformers'][0].get('id')
                                      tool_args['parent'] = transformer_id # Add parent to args
                                      print(f"Found and added transformer parent: {transformer_id}")
                            if transformer_id is None:
                                 error_msg = "Could not find a parent transformer for the meter."
                                 tool_outputs.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
                                 print(error_msg)
                                 latest_output_summary += error_msg
                                 error_occurred = True
                                 continue # Skip this tool call

                      elif 'error' in utility_data:
                           error_msg = f"Error fetching utility data to find meter parent: {utility_data.get('error', 'Unknown error')}"
                           tool_outputs.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
                           print(error_msg)
                           latest_output_summary += error_msg
                           error_occurred = True
                           continue # Skip this tool call


                 # Special handling for `beckn_solar_retail_confirm` and `beckn_subsidy_confirm`
                 # Ensure required user info (name, phone, email, fulfillment_id) is in args
                 if tool_name in ['beckn_solar_retail_confirm', 'beckn_subsidy_confirm']:
                      user_info = state.get('user_info', {})
                      # Ensure required fields are present or add from state
                      if 'customer_name' not in tool_args and user_info.get('customer_name'):
                           tool_args['customer_name'] = user_info['customer_name']
                      if 'customer_phone' not in tool_args and user_info.get('customer_phone'):
                           tool_args['customer_phone'] = user_info['customer_phone']
                      if 'customer_email' not in tool_args and user_info.get('customer_email'):
                           tool_args['customer_email'] = user_info['customer_email']
                      if 'fulfillment_id' not in tool_args and user_info.get('fulfillment_id'):
                            tool_args['fulfillment_id'] = user_info['fulfillment_id']
                      elif 'fulfillment_id' not in tool_args:
                           # Generate a fulfillment_id if not present
                           fulfillment_id = str(random.randint(10000, 99999))
                           tool_args['fulfillment_id'] = fulfillment_id
                           state['user_info']['fulfillment_id'] = fulfillment_id # Store for next turns
                           print(f"Generated and added fulfillment_id: {fulfillment_id}")

                      # Ensure provider_id and item_id are present for confirm based on selected option
                      if 'provider_id' not in tool_args and state.get('selected_solar_option', {}).get('provider', {}).get('id'):
                            tool_args['provider_id'] = state['selected_solar_option']['provider']['id']
                      if 'item_id' not in tool_args and state.get('selected_solar_option', {}).get('id'):
                            tool_args['item_id'] = state['selected_solar_option']['id']

                      # For subsidy confirm, if item_id/provider_id is not in args, try using the first subsidy search result
                      if tool_name == 'beckn_subsidy_confirm' and ('provider_id' not in tool_args or 'item_id' not in tool_args) and state.get('subsidy_search_results'):
                           first_subsidy = state['subsidy_search_results'][0]
                           tool_args['provider_id'] = first_subsidy.get('provider', {}).get('id')
                           tool_args['item_id'] = first_subsidy.get('id')
                           print(f"Using first subsidy search result for confirm: Provider ID {tool_args.get('provider_id')}, Item ID {tool_args.get('item_id')}")


                 # Special handling for `world_engine_create_der`
                 # Ensure energy_resource_id is present from state
                 if tool_name == 'world_engine_create_der' and tool_args.get('energy_resource_id') is None and state.get('energy_resource_id'):
                      tool_args['energy_resource_id'] = state['energy_resource_id']
                      print(f"Added energy_resource_id to DER args: {state['energy_resource_id']}")

                 # Check if all required arguments are now present (basic check based on tool signature)
                 # This requires inspecting the function signature, which is complex.
                 # For this demo, rely on the LLM generating correct calls or basic checks above.
                 # A real system might use a tool spec validator.

                 # Invoke the actual tool function
                 output = tool_function.invoke(tool_args)

                 tool_outputs.append(ToolMessage(content=json.dumps(output), tool_call_id=tool_call_id))

                 # Generate a brief summary of the output for the agent
                 if 'error' not in output:
                     latest_output_summary += f"Tool '{tool_name}' succeeded. "
                     if isinstance(output, dict):
                          if output.get('message', {}).get('catalog'):
                               latest_output_summary += f"Found {len(output['message']['catalog'].get('items', []))} items."
                          elif output.get('message', {}).get('order'):
                               latest_output_summary += f"Order ID: {output['message']['order'].get('id')}."
                          elif output.get('data', {}).get('id'):
                                latest_output_summary += f"Created item with ID: {output['data'].get('id')}."
                          else:
                                latest_output_summary += "Output data received."
                     else:
                           latest_output_summary += "Output received."
                 else:
                      latest_output_summary += f"Tool '{tool_name}' failed: {output.get('error', 'Unknown error')}."
                      error_occurred = True


                 print(f"Tool '{tool_name}' called successfully.")
                 print(f"Output: {output}\n")
            else:
                 error_msg = f"Tool '{tool_name}' not found."
                 tool_outputs.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
                 print(error_msg)
                 latest_output_summary += error_msg
                 error_occurred = True # Indicate tool not found as error

        except Exception as e:
            error_msg = f"Error executing tool {tool_call.get('name')}: {e}"
            tool_outputs.append(ToolMessage(content=error_msg, tool_call_id=tool_call.get('id', 'unknown_id')))
            print(error_msg)
            latest_output_summary += error_msg
            error_occurred = True

    # Update state with tool outputs and a summary
    # If any error occurred in tool calls, transition to 'error' stage
    next_stage = state['current_stage'] # Default to staying in the current stage
    if error_occurred:
         next_stage = 'error'
         state['error_message'] = "One or more tool calls failed." # Generic error message

    return {**state, 'chat_history': state['chat_history'] + tool_outputs, 'tool_output': tool_outputs, 'latest_tool_output_summary': latest_output_summary, 'current_stage': next_stage}

def update_state(state: AgentState) -> AgentState:
    """
    Updates the state based on the chat history (user input, tool outputs, agent messages)
    and decides the next stage of the process.
    Relies on the agent node to generate user-facing responses based on the updated state.
    """
    print(f"--- update_state (Current Stage: {state.get('current_stage')}) ---")

    # The latest entry in chat_history contains the result of the previous node
    latest_message = state['chat_history'][-1]
    current_stage = state.get('current_stage', 'initial')
    updated_state = state.copy()
    updated_state['error_message'] = None # Clear error message at the start of update_state
    updated_state['latest_tool_output_summary'] = None # Clear tool output summary

    # Process state updates based on the current stage and latest message
    if current_stage == 'initial':
         # This stage is set by handle_user_input. Decide next stage based on initial intent.
         user_input = state['chat_history'][-1].content.lower() # Get input from history
         if "solar" in user_input or "rooftop" in user_input or "incentive" in user_input or "flexibility program" in user_input:
             updated_state['current_stage'] = 'gather_info'
         else:
             updated_state['current_stage'] = 'welcome' # If initial input is not directly about solar, start with welcome

    elif current_stage == 'welcome':
         # User has seen the welcome message and provided input.
         # Check if their new input indicates interest in solar.
         user_input = state['chat_history'][-1].content.lower()
         if "solar" in user_input or "rooftop" in user_input or "incentive" in user_input or "flexibility program" in user_input or "yes" in user_input or "tell me more" in user_input:
             updated_state['current_stage'] = 'gather_info'
             print("User expressed interest in solar, transitioning to gather_info.")
         else:
             # If not, stay in welcome, the agent will decide how to respond
             updated_state['current_stage'] = 'welcome' # Stay in welcome stage
             print("Staying in welcome stage.")


    elif current_stage == 'gather_info':
        # Process latest user input or agent's attempt to gather info
        # Expecting HumanMessage with user info
        if isinstance(latest_message, HumanMessage):
            user_input = latest_message.content.lower()
            user_info = updated_state.get('user_info', {}).copy()

            # Attempt to extract key info from user input (simplistic)
            # In a real application, use proper NER or form filling.
            # For demo, just mark fields as 'provided' if keywords are present.
            if 'location' not in user_info:
                 # Look for city/state/pincode keywords
                 if any(word in user_input for word in ['city', 'state', 'pincode', 'location', 'in']):
                      user_info['location'] = "Provided" # Mark as provided
                      print("Attempted to extract location info.") # Debugging

            if 'consumption' not in user_info:
                 # Look for bill/consumption keywords
                 if any(word in user_input for word in ['bill', 'consumption', 'usage', 'kwh', '$']):
                      user_info['consumption'] = "Provided" # Mark as provided
                      print("Attempted to extract consumption info.") # Debugging

            if 'customer_name' not in user_info and ('name is' in user_input or 'i am' in user_input):
                 try:
                      # Very basic name extraction after "name is" or "i am"
                      parts = user_input.split('name is') if 'name is' in user_input else user_input.split('i am')
                      if len(parts) > 1:
                          name_part = parts[1].strip()
                          user_info['customer_name'] = name_part.split('.')[0].split(',')[0].title() # Basic extraction
                          print(f"Extracted name: {user_info['customer_name']}")
                 except Exception as e:
                      print(f"Error extracting name: {e}")

            if 'customer_phone' not in user_info:
                 # Basic phone number pattern matching (very simple)
                 import re
                 phone_match = re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', user_input)
                 if phone_match:
                      user_info['customer_phone'] = phone_match.group(0)
                      print(f"Extracted phone: {user_info['customer_phone']}")


            if 'customer_email' not in user_info:
                 # Basic email pattern matching
                 email_match = re.search(r'\S+@\S+\.\S+', user_input)
                 if email_match:
                      user_info['customer_email'] = email_match.group(0)
                      print(f"Extracted email: {user_info['customer_email']}")


            updated_state['user_info'] = user_info

            # Decide next stage based on whether required info is present
            # Check if BOTH location and consumption are marked as 'Provided'
            if user_info.get('location') == 'Provided' and user_info.get('consumption') == 'Provided':
                 updated_state['current_stage'] = 'search_solar'
                 print("Sufficient info gathered, transitioning to search_solar.")
            else:
                 # Stay in gather_info. The agent will see the state and know to ask for missing info.
                 updated_state['current_stage'] = 'gather_info' # Keep stage as gather_info
                 print("Info still incomplete, staying in gather_info.")


        elif isinstance(latest_message, AIMessage):
            # Agent responded while in gather_info, means it likely asked for info.
            # Stay in gather_info to receive user's response.
            updated_state['current_stage'] = 'gather_info'
            print("Agent message received in gather_info, staying in stage.")


    elif current_stage == 'search_solar':
        # Expecting ToolMessage output from call_tool (beckn_solar_retail_search)
        if isinstance(latest_message, ToolMessage):
            tool_output = json.loads(latest_message.content)
            if 'error' not in tool_output:
                solar_options = tool_output.get('output', {}).get('message', {}).get('catalog', {}).get('items', []) # Access 'output' key from tool result
                updated_state['solar_options'] = solar_options
                if solar_options:
                     updated_state['current_stage'] = 'present_options'
                     print("Solar options found, transitioning to present_options.")
                else:
                     updated_state['current_stage'] = 'welcome' # Go back if no options
                     print("No solar options found, transitioning back to welcome.")
            else:
                 updated_state['current_stage'] = 'error'
                 updated_state['error_message'] = tool_output.get('error', 'Unknown search error')
                 print(f"Search solar error, transitioning to error: {updated_state['error_message']}")

    elif current_stage == 'present_options':
        # Expecting HumanMessage user input selecting an option.
        # The agent node will interpret the selection and potentially decide to call confirm_solar.
        # This node just stays in 'present_options'. The agent's subsequent tool_calls
        # or message will drive the transition via the next_node_from_stage.
        # Add parsing for user selection here to update state['selected_solar_option']
        if isinstance(latest_message, HumanMessage):
            user_selection_input = latest_message.content.lower()
            selected_option = None

            if updated_state.get('solar_options'):
                try:
                    # Attempt to parse selection by number (e.g., "select 1")
                    if "select" in user_selection_input:
                        parts = user_selection_input.split("select")
                        if len(parts) > 1:
                            selection_str = parts[1].strip()
                            try:
                                selected_index = int(selection_str) - 1
                                if 0 <= selected_index < len(updated_state['solar_options']):
                                    selected_option = updated_state['solar_options'][selected_index]
                                    print(f"Selected option by number: {selected_index}")
                            except ValueError:
                                # Try matching by name if not a number
                                for option in updated_state['solar_options']:
                                    if option.get('descriptor', {}).get('name', '').lower() in selection_str:
                                        selected_option = option
                                        print(f"Selected option by name: {option.get('descriptor', {}).get('name')}")
                                        break

                    # Handle cases where the user might just type the option number or name (less robust parsing)
                    if not selected_option:
                        # Check if input is just a number corresponding to an option
                        try:
                            selected_index = int(user_selection_input.strip()) - 1
                            if 0 <= selected_index < len(updated_state['solar_options']):
                                selected_option = updated_state['solar_options'][selected_index]
                                print(f"Selected option by number directly: {selected_index}")
                        except ValueError:
                             # Check if input is an exact match for an option name (case-insensitive)
                             for option in updated_state['solar_options']:
                                if option.get('descriptor', {}).get('name', '').lower() == user_selection_input.strip():
                                     selected_option = option
                                     print(f"Selected option by exact name match: {user_selection_input}")
                                     break


                except Exception as e:
                     print(f"Error during option selection parsing: {e}") # Debugging

            if selected_option:
                updated_state['selected_solar_option'] = selected_option
                # Set next stage to confirm. The agent will see selected_solar_option in state
                # and know to call the confirm tool.
                updated_state['current_stage'] = 'confirm_solar'
                print(f"Option selected, transitioning to confirm_solar: {selected_option.get('id')}")

            elif 'cancel' in user_selection_input or 'stop' in user_selection_input:
                 updated_state['current_stage'] = 'end' # User wants to stop
                 print("User cancelled, transitioning to end.")
            else:
                 # Invalid selection, stay in present_options. Agent will reprompt.
                 updated_state['current_stage'] = 'present_options'
                 print("Invalid selection, staying in present_options.")


        elif isinstance(latest_message, AIMessage):
             # Agent responded while in present_options, means it likely presented options or asked for selection
             # Stay in present_options to receive user's selection.
             updated_state['current_stage'] = 'present_options'
             print("Agent message received in present_options, staying in stage.")

    elif current_stage == 'confirm_solar':
        # Expecting ToolMessage output from call_tool (beckn_solar_retail_confirm)
        if isinstance(latest_message, ToolMessage):
            tool_output = json.loads(latest_message.content)
            if 'error' not in tool_output:
                order = tool_output.get('output', {}).get('message', {}).get('order', {}) # Access 'output' key
                if order:
                    updated_state['order_id'] = order.get('id')
                    updated_state['current_stage'] = 'search_subsidies' # Move to subsidy search
                    print(f"Solar confirmed (Order ID: {updated_state['order_id']}), transitioning to search_subsidies.")
                else:
                     updated_state['current_stage'] = 'provide_status' # Confirmation response unexpected
                     print("Solar confirmation response unexpected, transitioning to provide_status.")
            else:
                updated_state['current_stage'] = 'error'
                updated_state['error_message'] = tool_output.get('error', 'Unknown confirm error')
                print(f"Confirm solar error, transitioning to error: {updated_state['error_message']}")


    elif current_stage == 'search_subsidies':
        # Expecting ToolMessage output from call_tool (beckn_subsidy_search)
        if isinstance(latest_message, ToolMessage):
            tool_output = json.loads(latest_message.content)
            if 'error' not in tool_output:
                subsidy_options = tool_output.get('output', {}).get('message', {}).get('catalog', {}).get('items', []) # Access 'output' key
                updated_state['subsidy_search_results'] = subsidy_options
                if subsidy_options:
                    updated_state['current_stage'] = 'apply_subsidies' # Move to applying
                    print(f"Subsidies found ({len(subsidy_options)}), transitioning to apply_subsidies.")
                else:
                    updated_state['current_stage'] = 'setup_grid_flexibility' # Move to next stage if no subsidies
                    print("No subsidies found, transitioning to setup_grid_flexibility.")
            else:
                updated_state['current_stage'] = 'setup_grid_flexibility' # Continue despite error
                updated_state['error_message'] = tool_output.get('error', 'Unknown subsidy search error')
                print(f"Search subsidies error, transitioning to setup_grid_flexibility: {updated_state['error_message']}")

    elif current_stage == 'apply_subsidies':
        # Expecting ToolMessage output from call_tool (beckn_subsidy_confirm)
        if isinstance(latest_message, ToolMessage):
            tool_output = json.loads(latest_message.content)
            if 'error' not in tool_output:
                order = tool_output.get('output', {}).get('message', {}).get('order', {}) # Access 'output' key
                if order:
                    updated_state['applied_subsidy_order_id'] = order.get('id')
                    updated_state['current_stage'] = 'setup_grid_flexibility' # Move to grid flexibility setup
                    print(f"Subsidy applied (ID: {updated_state['applied_subsidy_order_id']}), transitioning to setup_grid_flexibility.")
                else:
                    updated_state['current_stage'] = 'setup_grid_flexibility' # Confirmation response unexpected
                    print("Subsidy confirmation response unexpected, transitioning to setup_grid_flexibility.")
            else:
                updated_state['current_stage'] = 'setup_grid_flexibility' # Continue despite error
                updated_state['error_message'] = tool_output.get('error', 'Unknown subsidy confirm error')
                print(f"Apply subsidies error, transitioning to setup_grid_flexibility: {updated_state['error_message']}")


    elif current_stage == 'setup_grid_flexibility':
        # Expecting ToolMessage outputs from World Engine calls or AIMessage from agent asking for info.
        # This node processes the results of the WE API calls and decides the *next WE step*
        # or if WE setup is complete. The agent will be called next to decide which WE tool to call.

        # Process tool outputs from WE calls
        if isinstance(latest_message, ToolMessage):
            tool_output = json.loads(latest_message.content)
            tool_name = latest_message.tool_call_id # Use full tool_call_id to infer tool name

            if 'error' not in tool_output:
                # Update state based on which WE tool succeeded
                if 'world_engine_create_energy_resource' in tool_name and tool_output.get('output', {}).get('data'):
                    updated_state['energy_resource_id'] = tool_output['output']['data'].get('id')
                    print(f"ER created (ID: {updated_state['energy_resource_id']}).")
                elif 'world_engine_create_meter' in tool_name and tool_output.get('output', {}).get('data'):
                    updated_state['meter_id'] = tool_output['output']['data'].get('id')
                    print(f"Meter created (ID: {updated_state['meter_id']}).")
                elif 'world_engine_create_der' in tool_name and tool_output.get('output', {}).get('data'):
                    der_id = tool_output['output']['data'].get('id')
                    if der_id not in updated_state['der_ids']:
                         updated_state['der_ids'].append(der_id)
                    print(f"DER created (ID: {der_id}).")
                elif 'world_engine_get_utilities_data' in tool_name and tool_output.get('output', {}).get('utilities'):
                    updated_state['world_engine_data'] = tool_output['output'] # Store fetched utility data
                    print("Utility data fetched.")

                # After processing a successful WE tool call, stay in this stage for the agent to decide the next WE step
                updated_state['current_stage'] = 'setup_grid_flexibility'
                print("Processed WE tool output, staying in setup_grid_flexibility.")

            else:
                 # If a WE tool call failed, transition to error
                 updated_state['current_stage'] = 'error'
                 updated_state['error_message'] = tool_output.get('error', f'Unknown error from {tool_name}')
                 print(f"WE tool error ({tool_name}), transitioning to error: {updated_state['error_message']}")

        # After processing a Human or AIMessage in this stage
        elif isinstance(latest_message, (HumanMessage, AIMessage)):
             # The agent generated a message or user responded,
             # the stage logic is handled by the agent node determining which WE tool to call next.
             # Stay in this stage.
             updated_state['current_stage'] = 'setup_grid_flexibility'
             print("Processed message in setup_grid_flexibility, staying in stage.")

        # Check if all required WE setup steps are complete based on the updated state
        # This check should happen *after* potential state updates from tool calls
        if updated_state.get('energy_resource_id') is not None and updated_state.get('meter_id') is not None and updated_state.get('der_ids'):
             updated_state['current_stage'] = 'provide_status'
             print("All WE setup steps complete, transitioning to provide_status.")


    elif current_stage == 'provide_status':
         # Status is provided (by agent message), move to end.
         updated_state['current_stage'] = 'end'
         print("Status provided, transitioning to end.")


    elif current_stage == 'error':
       
        pass # Stay in error stage until new user input triggers handle_user_input


    elif current_stage == END:
        # Process ending, signal END
        updated_state['current_stage'] = END
        print("Process ended, transitioning to END.")

    # Note: latest_tool_output_summary is cleared at the start of update_state

    return updated_state

# --- Define Conditional Edges ---

def should_continue_agent(state: AgentState) -> str:
    """
    Decides whether the agent node's output is a tool call (go to call_tool)
    or a regular message (go to update_state for processing and next stage decision).
    Returns keys 'call_tool_action' or 'process_message' for the conditional edge.
    """
    last_message = state['chat_history'][-1]
    # If the agent generated tool calls, execute them
    if last_message.tool_calls:
        print("Agent output had tool calls, moving to call_tool.")
        return "call_tool_action" # Return a key indicating tool call needed
    else:
        # The agent generated a regular message. This message needs to be
        # processed by update_state to potentially extract info or just
        # signal the agent has finished its turn for this stage.
        print("Agent output was a message, moving to update_state.")
        return "process_message" # Return a key indicating message processing needed

def next_node_from_stage(state: AgentState) -> str:
    """
    Decides the next node based on the 'current_stage' and the last message type.
    """
    current_stage = state.get('current_stage')
    # Ensure chat_history is not empty before accessing the last element
    latest_message = state['chat_history'][-1] if state['chat_history'] else None
    
    print(f"--- next_node_from_stage (Current Stage: {current_stage}, Last message type: {type(latest_message)}) ---")

    if current_stage == END: # This case means the overall process defined by your stages has reached its conclusion
        return "end_process"

    # If the last message in the history is an AIMessage generated by the agent
    # (i.e., it has no tool_calls), and we are in a stage where the agent
    # has likely just asked a question or presented information and is now
    # waiting for a user response, the current graph invocation should conclude.
    if isinstance(latest_message, AIMessage) and not latest_message.tool_calls:
        # Stages where the agent communicates and then should wait for user input
        if current_stage in ['welcome', 'gather_info', 'present_options', 'provide_status', 'error']:
            print(f"Agent has spoken in stage {current_stage}. Current invoke pass will now end to await user input.")
            return "awaiting_human_input" 
            
    # Default behavior: continue processing, likely by going back to the agent node
    return "continue_process"


# --- Build the Graph ---

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("handle_user_input", handle_user_input)
workflow.add_node("agent", agent)
workflow.add_node("call_tool", call_tool)
workflow.add_node("update_state", update_state)

# Set the entry point
workflow.set_entry_point("handle_user_input")

# Define the transitions
workflow.add_edge("handle_user_input", "update_state")

workflow.add_conditional_edges(
    "agent",
    should_continue_agent,
    {
        "call_tool_action": "call_tool", # Key now matches the function's output
        "process_message": "update_state",
    },
)

workflow.add_edge("call_tool", "update_state")

# After updating the state, decide the next node based on the current_stage value
workflow.add_conditional_edges(
    "update_state",
    next_node_from_stage, # This function can return "continue_process", "end_process", or "awaiting_human_input"
    {
        "continue_process": "agent",  # Continue to the agent node for further processing
        "end_process": END,           # The entire graph process is finished
        "awaiting_human_input": END   # The current invoke pass should stop, awaiting user's response
                                      # The graph will resume on the next invoke with the new input.
    },
)

# Compile the graph
app = workflow.compile()