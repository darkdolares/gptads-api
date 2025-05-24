from flask import Flask, jsonify
from google.ads.googleads.client import GoogleAdsClient
import os

app = Flask(__name__)

# Configuração
config = {
    "developer_token": os.getenv("DEVELOPER_TOKEN"),
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "refresh_token": os.getenv("REFRESH_TOKEN"),
    "login_customer_id": os.getenv("LOGIN_CUSTOMER_ID"),
    "use_proto_plus": True
}

client = GoogleAdsClient.load_from_dict(config)

# Healthcheck
@app.route("/")
def home():
    return jsonify({"status": "API do Vertex AI rodando!"})


# 🏷️ Campanhas
@app.route("/campanhas", methods=["GET"])
def campanhas():
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, campaign.start_date, campaign.end_date
        FROM campaign
        LIMIT 100
    """
    response = ga_service.search(customer_id=os.getenv("CUSTOMER_ID"), query=query)

    resultado = []
    for row in response:
        resultado.append({
            "id": row.campaign.id,
            "nome": row.campaign.name,
            "status": row.campaign.status.name,
            "tipo": row.campaign.advertising_channel_type.name,
            "inicio": row.campaign.start_date,
            "fim": row.campaign.end_date
        })
    return jsonify(resultado)


# 🎯 Palavras-chave
@app.route("/palavras-chave", methods=["GET"])
def palavras_chave():
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            metrics.impressions,
            metrics.clicks,
            metrics.average_cpc,
            metrics.conversions
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
        LIMIT 100
    """
    response = ga_service.search(customer_id=os.getenv("CUSTOMER_ID"), query=query)

    resultado = []
    for row in response:
        resultado.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "ad_group_id": row.ad_group.id,
            "ad_group_name": row.ad_group.name,
            "keyword": row.ad_group_criterion.keyword.text,
            "match_type": row.ad_group_criterion.keyword.match_type.name,
            "status": row.ad_group_criterion.status.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "avg_cpc": row.metrics.average_cpc.micros / 1_000_000 if row.metrics.average_cpc else 0,
            "conversions": row.metrics.conversions
        })
    return jsonify(resultado)


# 🔍 Termos de Pesquisa
@app.route("/termos-pesquisa", methods=["GET"])
def termos_pesquisa():
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            search_term_view.search_term,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.average_cpc
        FROM search_term_view
        WHERE segments.date DURING LAST_30_DAYS
        LIMIT 100
    """
    response = ga_service.search(customer_id=os.getenv("CUSTOMER_ID"), query=query)

    resultado = []
    for row in response:
        resultado.append({
            "search_term": row.search_term_view.search_term,
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "ad_group_id": row.ad_group.id,
            "ad_group_name": row.ad_group.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "avg_cpc": row.metrics.average_cpc.micros / 1_000_000 if row.metrics.average_cpc else 0,
            "conversions": row.metrics.conversions
        })
    return jsonify(resultado)


# 📍 Localização
@app.route("/locais", methods=["GET"])
def locais():
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            campaign.id,
            campaign.name,
            segments.geo_target_country,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        LIMIT 100
    """
    response = ga_service.search(customer_id=os.getenv("CUSTOMER_ID"), query=query)

    resultado = []
    for row in response:
        resultado.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "pais": row.segments.geo_target_country,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "conversions": row.metrics.conversions
        })
    return jsonify(resultado)


# 🧠 Demografia
@app.route("/demografia", methods=["GET"])
def demografia():
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            campaign.id,
            campaign.name,
            segments.age_range,
            segments.gender,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        LIMIT 100
    """
    response = ga_service.search(customer_id=os.getenv("CUSTOMER_ID"), query=query)

    resultado = []
    for row in response:
        resultado.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "age_range": row.segments.age_range.name,
            "gender": row.segments.gender.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "conversions": row.metrics.conversions
        })
    return jsonify(resultado)


# 🚀 Start
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
