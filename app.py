from flask import Flask, jsonify, request
from vertexai.language_models import TextGenerationModel
from vertexai import init
import os
import json
from google.oauth2 import service_account

app = Flask(__name__)

# Credenciais via variável de ambiente
creds_info = json.loads(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON"))
credentials = service_account.Credentials.from_service_account_info(creds_info)

# Inicializa Vertex
init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION"),
    credentials=credentials
)

model = TextGenerationModel.from_pretrained("text-bison")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API do Vertex AI rodando!"})


@app.route("/gerar", methods=["GET"])
def gerar():
    prompt = request.args.get("prompt")
    if not prompt:
        return jsonify({"erro": "Parâmetro 'prompt' é obrigatório"}), 400

    resposta = model.predict(
        prompt,
        temperature=0.2,
        max_output_tokens=256,
    )

    return jsonify({"resposta": resposta.text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
