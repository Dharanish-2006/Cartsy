import requests
from django.conf import settings
from datetime import datetime

ZOHO_CLIENT_ID = settings.ZOHO_CLIENT_ID
ZOHO_CLIENT_SECRET = settings.ZOHO_CLIENT_SECRET
ZOHO_REFRESH_TOKEN = settings.ZOHO_REFRESH_TOKEN
ZOHO_API_DOMAIN = settings.ZOHO_API_DOMAIN

def get_access_token():
    url = "https://accounts.zoho.in/oauth/v2/token"

    params = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

    return response.json()["access_token"]

def zoho_headers():
    token = get_access_token()
    return {
        "Authorization": f"Zoho-oauthtoken {token}",
        "Content-Type": "application/json",
    }


def create_zoho_contact(user):
    """
    Creates a Zoho CRM Contact
    """
    url = f"{ZOHO_API_DOMAIN}/crm/v2/Contacts"

    data = {
        "data": [
            {
                "Last_Name": user.username,
                "Email": user.email,
            }
        ]
    }

    response = requests.post(url, json=data, headers=zoho_headers())
    response.raise_for_status()

    return response.json()


def create_zoho_deal(order):
    """
    Creates a Zoho CRM Deal for an Order
    """
    url = f"{ZOHO_API_DOMAIN}/crm/v2/Deals"

    data = {
        "data": [
            {
                "Deal_Name": f"Order #{order.id}",
                "Stage": "Qualification",
                "Amount": float(order.total_amount),
                "Closing_Date": datetime.now().strftime("%Y-%m-%d"),
                "Description": f"Payment Method: {order.payment_method}\nStatus: {order.payment_status}",
            }
        ]
    }

    response = requests.post(url, json=data, headers=zoho_headers())
    response.raise_for_status()

    return response.json()
