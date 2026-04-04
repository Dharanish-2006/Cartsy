import requests
from django.conf import settings
from datetime import datetime

ZOHO_CLIENT_ID     = settings.ZOHO_CLIENT_ID
ZOHO_CLIENT_SECRET = settings.ZOHO_CLIENT_SECRET
ZOHO_REFRESH_TOKEN = settings.ZOHO_REFRESH_TOKEN
ZOHO_API_DOMAIN    = settings.ZOHO_API_DOMAIN


def get_access_token():
    url = "https://accounts.zoho.in/oauth/v2/token"
    params = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id":     ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type":    "refresh_token",
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]


def zoho_headers():
    return {
        "Authorization": f"Zoho-oauthtoken {get_access_token()}",
        "Content-Type":  "application/json",
    }


def create_zoho_contact(user, order=None):
    """
    Creates (or updates) a Zoho CRM Contact.
    If an order is supplied, shipping address fields are included.
    """
    url = f"{ZOHO_API_DOMAIN}/crm/v2/Contacts"

    contact = {
        "Last_Name": user.username,
        "Email":     user.email,
    }

    if order:
        if order.full_name:
            parts = order.full_name.strip().split(" ", 1)
            contact["First_Name"] = parts[0]
            contact["Last_Name"]  = parts[1] if len(parts) > 1 else parts[0]

        contact["Mailing_Street"]  = order.address    or ""
        contact["Mailing_City"]    = order.city       or ""
        contact["Mailing_Zip"]     = order.postal_code or ""
        contact["Mailing_Country"] = order.country    or ""

    data = {"data": [contact]}
    response = requests.post(url, json=data, headers=zoho_headers())
    response.raise_for_status()
    return response.json()


def create_zoho_deal(order):
    """Creates a Zoho CRM Deal for an Order."""
    url = f"{ZOHO_API_DOMAIN}/crm/v2/Deals"

    data = {
        "data": [
            {
                "Deal_Name":    f"Order #{order.id}",
                "Stage":        "Qualification",
                "Amount":       float(order.total_amount),
                "Closing_Date": datetime.now().strftime("%Y-%m-%d"),
                "Description": (
                    f"Payment Method: {order.payment_method}\n"
                    f"Status: {order.payment_status}\n"
                    f"Ship to: {order.full_name}, {order.address}, "
                    f"{order.city} {order.postal_code}, {order.country}"
                ),
            }
        ]
    }

    response = requests.post(url, json=data, headers=zoho_headers())
    response.raise_for_status()
    return response.json()