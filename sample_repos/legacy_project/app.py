from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)
model = pickle.load(open("model_v3_final_FINAL.pkl", "rb"))

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    pred = model.predict([data["features"]])
    return jsonify({"prediction": pred.tolist()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
