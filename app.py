from flask import Flask, jsonify
from google.ads.googleads.client import GoogleAdsClient
import os

app = Flask(__name__)

# Carrega configurações da API a partir das variáveis de ambiente
config = {
    "developer_token": os.environ.get("DEVELOPER_TOKEN"),
    "client_id": os.environ.get("CLIENT_ID"),
    "client_secret": os.environ.get("CLIENT_SECRET"),
    "refresh_token": os.environ.get("REFRESH_TOKEN"),
    "login_customer_id": os.environ.get("LOGIN_CUSTOMER_ID"),
    "use_proto_plus": True
}

client = GoogleAdsClient.load_from_dict(config)

@app.route("/campanhas", methods=["GET"])
def campanhas():
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status
        FROM campaign
        LIMIT 100
    """

    # ID da conta com campanhas (sem traços)
    customer_id = os.environ.get("CUSTOMER_ID")

    response = ga_service.search(customer_id=customer_id, query=query)

    resultado = []
    for row in response:
        resultado.append({
            "id": int(row.campaign.id),
            "nome": row.campaign.name,
            "status": row.campaign.status.name
        })

    return jsonify(resultado)

if __name__ == "__main__":
    app.run(port=3000)
