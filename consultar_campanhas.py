from google.ads.googleads.client import GoogleAdsClient
import os

config = {
    "developer_token": os.environ.get("DEVELOPER_TOKEN"),
    "client_id": os.environ.get("CLIENT_ID"),
    "client_secret": os.environ.get("CLIENT_SECRET"),
    "refresh_token": os.environ.get("REFRESH_TOKEN"),
    "login_customer_id": os.environ.get("LOGIN_CUSTOMER_ID"),
    "use_proto_plus": True
}

client = GoogleAdsClient.load_from_dict(config)

ga_service = client.get_service("GoogleAdsService")

query = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status
    FROM campaign
    LIMIT 10
"""

customer_id = os.environ.get("CUSTOMER_ID")
response = ga_service.search(customer_id=customer_id, query=query)

for row in response:
    print(f"Campanha: {row.campaign.name} | ID: {row.campaign.id} | Status: {row.campaign.status.name}")
