import requests
import json
import uuid
from datetime import datetime

class BecknClient:
    def __init__(self, base_url, bap_id, bap_uri, bpp_id, bpp_uri):
        self.base_url = base_url
        self.bap_id = bap_id
        self.bap_uri = bap_uri
        self.bpp_id = bpp_id
        self.bpp_uri = bpp_uri

    def _generate_context(self, action, domain="deg:service", city_code="NANP:628"):
        return {
            "domain": domain,
            "action": action,
            "location": {
                "country": {
                    "code": "USA"
                },
                "city": {
                    "code": city_code
                }
            },
            "version": "1.1.0",
            "bap_id": self.bap_id,
            "bap_uri": self.bap_uri,
            "bpp_id": self.bpp_id,
            "bpp_uri": self.bpp_uri,
            "transaction_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'
        }

    def search_connection(self):
        url = f"{self.base_url}/search"
        context = self._generate_context(action="search")
        payload = {
            "context": context,
            "message": {
                "intent": {
                    "item": {
                        "descriptor": {
                            "name": "Connection"
                        }
                    }
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def select_connection(self, provider_id, item_id):
        url = f"{self.base_url}/select"
        context = self._generate_context(action="select")
        payload = {
            "context": context,
            "message": {
                "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def init_connection(self, provider_id, item_id):
        url = f"{self.base_url}/init"
        context = self._generate_context(action="init")
        payload = {
            "context": context,
            "message": {
                "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def confirm_connection(self, provider_id, item_id, fulfillment_id, customer_name, customer_phone, customer_email):
        url = f"{self.base_url}/confirm"
        context = self._generate_context(action="confirm")
        payload = {
            "context": context,
            "message": {
                "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ],
                    "fulfillments": [
                        {
                            "id": fulfillment_id,
                            "customer": {
                                "person": {
                                    "name": customer_name
                                },
                                "contact": {
                                    "phone": customer_phone,
                                    "email": customer_email
                                }
                            }
                        }
                    ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def status_connection(self, order_id):
        url = f"{self.base_url}/status"
        context = self._generate_context(action="status")
        payload = {
            "context": context,
            "message": {
                "order_id": order_id
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def confirm_subsidy(self, provider_id, item_id, fulfillment_id, customer_name, customer_phone, customer_email):
        url = f"{self.base_url}/confirm"
        context = self._generate_context(action="confirm", domain="deg:schemes")
        payload = {
          "context": context,
          "message": {
           "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id

                        }
                    ],
                                 "fulfillments": [
                {
                  "id": fulfillment_id,
                  "customer": {
                    "person": {
                      "name": customer_name
                    },
                    "contact": {
                      "phone": customer_phone,
                      "email": customer_email
                    }
                  }
                }
              ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()


    def search_subsidy(self):
        url = f"{self.base_url}/search"
        context = self._generate_context(action="search", domain="deg:schemes")
        payload = {
            "context": context,
            "message": {
                "intent": {
                    "item": {
                        "descriptor": {
                            "name": "incentive"
                        }
                    }
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def status_subsidy(self, order_id):
        url = f"{self.base_url}/status"
        context = self._generate_context(action="status", domain="deg:service") # Note: Domain is deg:service in the postman collection for subsidy status
        payload = {
          "context": context,
          "message": {
                "order_id": order_id
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def search_dfp(self):
        url = f"{self.base_url}/search"
        context = self._generate_context(action="search", domain="deg:schemes")
        payload = {
            "context": context,
            "message": {
                "intent": {
                    "item": {
                        "descriptor": {
                            "name": "Program"
                        }
                    }
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def confirm_dfp(self, provider_id, item_id, fulfillment_id, customer_name, customer_phone, customer_email):
        url = f"{self.base_url}/confirm"
        context = self._generate_context(action="confirm", domain="deg:schemes")
        payload = {
          "context": context,
          "message": {
           "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id

                        }
                    ],
                     "fulfillments": [
                {
                  "id": fulfillment_id,
                  "customer": {
                    "person": {
                      "name": customer_name
                    },
                    "contact": {
                      "phone": customer_phone,
                      "email": customer_email
                    }
                  }
                }
              ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def status_dfp(self, order_id):
        url = f"{self.base_url}/status"
        context = self._generate_context(action="status", domain="deg:schemes")
        payload = {
          "context": context,
          "message": {
            "order_id": order_id
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def search_solar_retail(self):
        url = f"{self.base_url}/search"
        context = self._generate_context(action="search", domain="deg:retail")
        payload = {
            "context": context,
            "message": {
                "intent": {
                    "item": {
                        "descriptor": {
                            "name": "solar"
                        }
                    }
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def select_solar_retail(self, provider_id, item_id):
        url = f"{self.base_url}/select"
        context = self._generate_context(action="select", domain="deg:retail")
        payload = {
          "context": context,
          "message": {
           "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()


    def init_solar_retail(self, provider_id, item_id):
        url = f"{self.base_url}/init"
        context = self._generate_context(action="init", domain="deg:retail")
        payload = {
          "context": context,
          "message": {
           "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def confirm_solar_retail(self, provider_id, item_id, fulfillment_id, customer_name, customer_phone, customer_email):
        url = f"{self.base_url}/confirm"
        context = self._generate_context(action="confirm", domain="deg:retail")
        payload = {
          "context": context,
          "message": {
           "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ],
                  "fulfillments": [
                {
                  "id": fulfillment_id,
                  "customer": {
                    "person": {
                      "name": customer_name
                    },
                    "contact": {
                      "phone": customer_phone,
                      "email": customer_email
                    }
                  }
                }
              ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def status_solar_retail(self, order_id):
        url = f"{self.base_url}/status"
        context = self._generate_context(action="status", domain="deg:retail")
        payload = {
          "context": context,
          "message": {
            "order_id": order_id
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def search_solar_service(self):
        url = f"{self.base_url}/search"
        context = self._generate_context(action="search", domain="deg:service")
        payload = {
            "context": context,
            "message": {
                "intent": {
                    "descriptor": {
                        "name": "resi"
                    }
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def select_solar_service(self, provider_id, item_id):
        url = f"{self.base_url}/select"
        context = self._generate_context(action="select", domain="deg:service")
        payload = {
            "context": context,
            "message": {
                "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def init_solar_service(self, provider_id, item_id):
        url = f"{self.base_url}/init"
        context = self._generate_context(action="init", domain="deg:service")
        payload = {
          "context": context,
          "message": {
           "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def confirm_solar_service(self, provider_id, item_id, fulfillment_id, customer_name, customer_phone, customer_email):
        url = f"{self.base_url}/confirm"
        context = self._generate_context(action="confirm", domain="deg:service")
        payload = {
            "context": context,
            "message": {
                "order": {
                    "provider": {
                        "id": provider_id
                    },
                    "items": [
                        {
                            "id": item_id
                        }
                    ],
                    "fulfillments": [
                        {
                            "id": fulfillment_id,
                            "customer": {
                                "person": {
                                    "name": customer_name
                                },
                                "contact": {
                                    "phone": customer_phone,
                                    "email": customer_email
                                }
                            }
                        }
                    ]
                }
            }
        }
        response = requests.post(url, json=payload)
        return response.json()

    def status_solar_service(self, order_id):
        url = f"{self.base_url}/status"
        context = self._generate_context(action="status", domain="deg:service")
        payload = {
            "context": context,
            "message": {
                "order_id": order_id
            }
        }
        response = requests.post(url, json=payload)
        return response.json()