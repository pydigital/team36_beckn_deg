import requests
import json

class WorldEngineClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_utilities_detailed(self):
        """
        Get detailed data for utilities, substations, and transformers.
        """
        url = f"{self.base_url}/utility/detailed"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def reset_data(self):
        """
        Reset the data of the World Engine.
        """
        url = f"{self.base_url}/utility/reset"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def get_grid_loads(self):
        """
        Get grid loads data.
        """
        url = f"{self.base_url}/grid-loads"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def create_meter(self, data):
        """
        Create a new meter.

        Args:
            data (dict): The data for the new meter.
                         Example: {
                                    "code": "METER003",
                                    "parent": null,
                                    "energyResource":null,
                                    "consumptionLoadFactor": 1.0,
                                    "productionLoadFactor": 0.0,
                                    "type": "SMART",
                                    "city": "San Francisco",
                                    "state": "California",
                                    "latitude": 37.7749,
                                    "longitude": -122.4194,
                                    "pincode": "94103"
                                  }
        """
        url = f"{self.base_url}/meters"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "data": data
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def get_all_meters(self, page=1, pageSize=100, populate_parent=True, populate_energy_resource=True, populate_children=True, populate_appliances=True, sort_children_desc=True):
        """
        Get all meters with pagination and population options.

        Args:
            page (int): The page number for pagination.
            pageSize (int): The number of items per page.
            populate_parent (bool): Whether to populate parent information.
            populate_energy_resource (bool): Whether to populate energy resource information.
            populate_children (bool): Whether to populate children information.
            populate_appliances (bool): Whether to populate appliances information.
            sort_children_desc (bool): Whether to sort children by code in descending order.
        """
        url = f"{self.base_url}/meters"
        params = {
            "pagination[page]": page,
            "pagination[pageSize]": pageSize,
        }
        if populate_parent:
            params["populate[0]"] = "parent"
        if populate_energy_resource:
            params["populate[1]"] = "energyResource"
        if populate_children:
            params["populate[2]"] = "children"
        if populate_appliances:
            params["populate[3]"] = "appliances"
        if sort_children_desc:
             params["sort[0]"] = "children.code:desc"

        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def delete_meter(self, meter_id):
        """
        Delete a meter by ID.

        Args:
            meter_id (int): The ID of the meter to delete.
        """
        url = f"{self.base_url}/meters/{meter_id}"
        response = requests.delete(url)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def get_meter_by_id(self, meter_id, populate_parent=True, populate_children=True):
        """
        Get a meter by ID with population options.

        Args:
            meter_id (int): The ID of the meter to retrieve.
            populate_parent (bool): Whether to populate parent information.
            populate_children (bool): Whether to populate children information.
        """
        url = f"{self.base_url}/meters/{meter_id}"
        params = {}
        if populate_parent:
            params["populate[0]"] = "parent"
        if populate_children:
            params["populate[1]"] = "children"
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()


    def get_meter_historical_data(self, meter_dataset_id):
        """
        Get historical data for a meter dataset by ID.

        Args:
            meter_dataset_id (int): The ID of the meter dataset to retrieve historical data for.
        """
        url = f"{self.base_url}/meter-datasets/{meter_dataset_id}"
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def create_energy_resource(self, data):
        """
        Create a new energy resource (household).

        Args:
            data (dict): The data for the new energy resource.
                         Example: {
                                    "name": "Jonathon's Home",
                                    "type": "CONSUMER",
                                    "meter": 1361
                                  }
        """
        url = f"{self.base_url}/energy-resources"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "data": data
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def get_energy_resource_by_id(self, energy_resource_id, populate_meter_parent=True, populate_meter_children=True, populate_meter_appliances=True):
        """
        Get an energy resource by ID with population options.

        Args:
            energy_resource_id (int): The ID of the energy resource to retrieve.
            populate_meter_parent (bool): Whether to populate meter parent information.
            populate_meter_children (bool): Whether to populate meter children information.
            populate_meter_appliances (bool): Whether to populate meter appliances information.
        """
        url = f"{self.base_url}/energy-resources/{energy_resource_id}"
        params = {}
        if populate_meter_parent:
            params["populate[0]"] = "meter.parent"
        if populate_meter_children:
            params["populate[1]"] = "meter.children"
        if populate_meter_appliances:
            params["populate[2]"] = "meter.appliances"
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def delete_energy_resource(self, energy_resource_id):
        """
        Delete an energy resource by ID.

        Args:
            energy_resource_id (int): The ID of the energy resource to delete.
        """
        url = f"{self.base_url}/energy-resources/{energy_resource_id}"
        response = requests.delete(url)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def create_der(self, energy_resource_id, appliance_id):
        """
        Create a new Distributed Energy Resource (DER).

        Args:
            energy_resource_id (int): The ID of the energy resource the DER belongs to.
            appliance_id (int): The ID of the appliance associated with the DER.
        """
        url = f"{self.base_url}/der"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "energy_resource": energy_resource_id,
            "appliance": appliance_id
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def toggle_der_switching(self, der_id):
        """
        Toggle the switching status of a DER by ID.

        Args:
            der_id (int): The ID of the DER to toggle.
        """
        url = f"{self.base_url}/toggle-der/{der_id}"
        response = requests.post(url)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()