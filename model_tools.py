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

BECKN_BASE_URL = os.getenv("BECKN_BASE_URL")
WORLD_ENGINE_BASE_URL = os.getenv("WORLD_ENGINE_BASE_URL")
BECKN_BAP_ID = os.getenv("BECKN_BAP_ID")
BECKN_BAP_URI = os.getenv("BECKN_BAP_URI")
BECKN_BPP_ID = os.getenv("BECKN_BPP_ID")
BECKN_BPP_URI = os.getenv("BECKN_BPP_URI")

@tool
def beckn_connection_search(bap_id: str, bap_uri: str, bpp_id: str, bpp_uri: str) -> dict:
    """
    Triggers the Search API for Beckn Connection to find available services.
    Requires bap_id, bap_uri, bpp_id, bpp_uri.
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
def beckn_solar_retail_search(bap_id: str, bap_uri: str, bpp_id: str, bpp_uri: str) -> dict:
    """
    Triggers the Search API for Beckn Solar-Retail to find solar product and service offerings.
    Requires bap_id, bap_uri, bpp_id, bpp_uri.
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
def beckn_solar_retail_select(bap_id: str, bap_uri: str, bpp_id: str, bpp_uri: str, provider_id: str, item_id: str) -> dict:
    """
    Triggers the Select API for Beckn Solar-Retail to select a specific solar offering.
    Requires bap_id, bap_uri, bpp_id, bpp_uri, provider_id, and item_id.
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
def beckn_solar_retail_init(bap_id: str, bap_uri: str, bpp_id: str, bpp_uri: str, provider_id: str, item_id: str) -> dict:
    """
    Triggers the Init API for Beckn Solar-Retail to initialize the order/process.
    Requires bap_id, bap_uri, bpp_id, bpp_uri, provider_id, and item_id.
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
def beckn_solar_retail_confirm(bap_id: str, bap_uri: str, bpp_id: str, bpp_uri: str, provider_id: str, item_id: str, fulfillment_id: str, customer_name: str, customer_phone: str, customer_email: str) -> dict:
    """
    Triggers the Confirm API for Beckn Solar-Retail to confirm the order/process.
    Requires bap_id, bap_uri, bpp_id, bpp_uri, provider_id, item_id, fulfillment_id, customer_name, customer_phone, and customer_email.
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
def beckn_solar_retail_status(bap_id: str, bap_uri: str, bpp_id: str, bpp_uri: str, order_id: str) -> dict:
    """
    Triggers the Status API for Beckn Solar-Retail to get the status of an order.
    Requires bap_id, bap_uri, bpp_id, bpp_uri, and order_id.
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
def beckn_subsidy_search(bap_id: str, bap_uri: str, bpp_id: str, bpp_uri: str) -> dict:
    """
    Triggers the Search API for Beckn Subsidy to find available incentives.
    Requires bap_id, bap_uri, bpp_id, bpp_uri.
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
def beckn_subsidy_confirm(bap_id: str, bap_uri: str, bpp_id: str, bpp_uri: str, provider_id: str, item_id: str, fulfillment_id: str, customer_name: str, customer_phone: str, customer_email: str) -> dict:
    """
    Triggers the Confirm API for Beckn Subsidy to apply for an incentive.
    Requires bap_id, bap_uri, bpp_id, bpp_uri, provider_id, item_id, fulfillment_id, customer_name, customer_phone, and customer_email.
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
def world_engine_create_energy_resource(name: str, type: str, meter: Optional[int] = None) -> dict:
    """
    Creates a new energy resource (e.g., Household) in the World Engine.
    Requires name and type (e.g., "CONSUMER"). Optional: meter (Meter ID).
    """
    url = f"{WORLD_ENGINE_BASE_URL}/energy-resources"
    headers = { "Content-Type": "application/json" }
    payload = {
        "data": {
            "name": name,
            "type": type,
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
