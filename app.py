from flask import Flask, jsonify
from google.ads.googleads.client import GoogleAdsClient
import os

app = Flask(__name__)

# 🔐 Configuração via variáveis de ambiente
config = {
    "developer_token": os.getenv("DEVELOPER_TOKEN"),
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "refresh_token": os.getenv("REFRESH_TOKEN"),
    "login_customer_id": os.getenv("LOGIN_CUSTOMER_ID"),
    "use_proto_plus": True,
}

client = GoogleAdsClient.load_from_dict(config)

@app.route("/")
def home():
    return jsonify({"status": "API do Google Ads rodando com Vertex AI!"})


# 📊 Campanhas
@app.route("/campanhas")
def campanhas():
    try:
        customer_id = os.getenv("CUSTOMER_ID")
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
                metrics.conversions
            FROM campaign
            LIMIT 100
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        result = []
        for row in response:
            result.append({
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
                    "conversoes": row.metrics.conversions
                }
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔑 Palavras-chave
@app.route("/palavras-chave")
def palavras():
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

        result = []
        for row in response:
            result.append({
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

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🏹 Segmentação
@app.route("/publico")
def publico():
    try:
        customer_id = os.getenv("CUSTOMER_ID")
        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign_criterion.age_range.type,
                campaign_criterion.gender.type,
                campaign_criterion.device.type,
                campaign_criterion.location.geo_target_constant
            FROM campaign_criterion
            LIMIT 100
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        result = []
        for row in response:
            result.append({
                "campanha_id": str(row.campaign.id),
                "campanha_nome": row.campaign.name,
                "idade": getattr(row.campaign_criterion.age_range, "type_", None),
                "genero": getattr(row.campaign_criterion.gender, "type_", None),
                "dispositivo": getattr(row.campaign_criterion.device, "type_", None),
                "local": getattr(row.campaign_criterion.location, "geo_target_constant", None)
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🏆 Leilão
@app.route("/leilao")
def leilao():
    try:
        customer_id = os.getenv("CUSTOMER_ID")
        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                auction_insight.search_impression_share,
                auction_insight.absolute_top_impression_share,
                auction_insight.top_impression_share,
                auction_insight.outranking_share
            FROM auction_insight_view
            LIMIT 100
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        result = []
        for row in response:
            result.append({
                "campanha_id": str(row.campaign.id),
                "campanha_nome": row.campaign.name,
                "impressao_search": row.auction_insight.search_impression_share,
                "impressao_topo_absoluto": row.auction_insight.absolute_top_impression_share,
                "impressao_topo": row.auction_insight.top_impression_share,
                "outranking_share": row.auction_insight.outranking_share,
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
