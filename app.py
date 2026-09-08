from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json(silent=True)

    print("\n===== M-PESA CALLBACK =====")
    print(data)
    print("===========================\n")

    return jsonify({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })

@app.route("/", methods=["GET"])
def home():
    return "M-PESA Callback Server is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)