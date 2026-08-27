from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(filename="predictions.log", level=logging.INFO)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json()
    prediction = {"score": 0.5}
    logging.info(f"prediction_logged input={payload} output={prediction}")
    return jsonify(prediction), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
