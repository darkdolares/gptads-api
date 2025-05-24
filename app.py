from flask import Flask, jsonify
from google.ads.googleads.client import GoogleAdsClient
import os

app = Flask(__name__)

# Configuração via variáveis de ambiente
config = {
    "developer_token": os.getenv("DEVELOPER_TOKEN"),
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "refresh_token": os.getenv("REFRESH_TOKEN"),
    "login_customer_id": os.getenv("LOGIN_CUSTOMER_ID"),
    "use_proto_plus": True,
}

# Carregar cliente do Google Ads
client = GoogleAdsClient.load_from_dict(config)


@app.route("/")
def home():
    return jsonify({"status": "API do Google Ads rodando com dados completos!"})


@app.route("/campanhas")
def campanhas():
    try:
        customer_id = os.getenv("CUSTOMER_ID")
        if not customer_id:
            return jsonify({"error": "CUSTOMER_ID não definido nas variáveis de ambiente"}), 500

        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.start_date,
                campaign.end_date,
                campaign.bidding_strategy_type,
                campaign_budget.amount_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.average_cpm,
                metrics.average_position,
                metrics.conversions
            FROM campaign
            LIMIT 50
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        campanhas = []
        for row in response:
            campanhas.append({
                "id": str(row.campaign.id),
                "nome": row.campaign.name,
                "status": row.campaign.status.name,
                "tipo_canal": row.campaign.advertising_channel_type.name,
                "inicio": row.campaign.start_date,
                "fim": row.campaign.end_date,
                "estrategia_lance": row.campaign.bidding_strategy_type.name,
                "orcamento_diario": float(row.campaign_budget.amount_micros) / 1e6 if row.campaign_budget else None,
                "metricas": {
                    "impressoes": row.metrics.impressions,
                    "cliques": row.metrics.clicks,
                    "ctr": row.metrics.ctr,
                    "cpc_medio": row.metrics.average_cpc,
                    "cpm_medio": row.metrics.average_cpm,
                    "posicao_media": row.metrics.average_position,
                    "conversoes": row.metrics.conversions
                }
            })

        return jsonify(campanhas)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/palavras-chave")
def keywords():
    try:
        customer_id = os.getenv("CUSTOMER_ID")
        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.conversions
            FROM keyword_view
            WHERE ad_group_criterion.status != 'REMOVED'
            LIMIT 100
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        palavras = []
        for row in response:
            palavras.append({
                "campanha_id": str(row.campaign.id),
                "campanha_nome": row.campaign.name,
                "grupo_id": str(row.ad_group.id),
                "grupo_nome": row.ad_group.name,
                "palavra_chave": row.ad_group_criterion.keyword.text,
                "tipo_correspondencia": row.ad_group_criterion.keyword.match_type.name,
                "status": row.ad_group_criterion.status.name,
                "metricas": {
                    "impressoes": row.metrics.impressions,
                    "cliques": row.metrics.clicks,
                    "ctr": row.metrics.ctr,
                    "cpc_medio": row.metrics.average_cpc,
                    "conversoes": row.metrics.conversions
                }
            })

        return jsonify(palavras)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/segmentacao")
def segmentacao():
    try:
        customer_id = os.getenv("CUSTOMER_ID")
        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign_criterion.location.geo_target_constant,
                campaign_criterion.device.type,
                campaign_criterion.gender.type,
                campaign_criterion.age_range.type
            FROM campaign_criterion
            LIMIT 100
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        criterios = []
        for row in response:
            criterios.append({
                "campanha_id": str(row.campaign.id),
                "campanha_nome": row.campaign.name,
                "local": getattr(row.campaign_criterion.location, "geo_target_constant", None),
                "dispositivo": getattr(row.campaign_criterion.device, "type_", None),
                "genero": getattr(row.campaign_criterion.gender, "type_", None),
                "faixa_etaria": getattr(row.campaign_criterion.age_range, "type_", None)
            })

        return jsonify(criterios)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
