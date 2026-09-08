from flask import Flask, request, jsonify, render_template_string
import requests
import base64
from datetime import datetime
import os

app = Flask(__name__)

# =========================
# SAFARICOM SANDBOX
# =========================

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
PASSKEY = os.getenv("PASSKEY")

BUSINESS_SHORT_CODE = "174379"

CALLBACK_URL = "https://mpesa-payment-ambs.onrender.com/mpesa/callback"


# =========================
# GET ACCESS TOKEN
# =========================

def get_access_token():

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(
        url,
        auth=(CONSUMER_KEY, CONSUMER_SECRET)
    )

    response.raise_for_status()

    return response.json()["access_token"]


# =========================
# PAYMENT PAGE
# =========================

@app.route("/", methods=["GET"])
def home():

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>M-PESA Payment</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <style>

        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }

        .box {
            background: white;
            width: 90%;
            max-width: 400px;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }

        h1 {
            text-align: center;
        }

        input {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 16px;
        }

        button {
            width: 100%;
            padding: 14px;
            margin-top: 15px;
            border: none;
            border-radius: 8px;
            background: #1b8f3a;
            color: white;
            font-size: 18px;
            cursor: pointer;
        }

        button:hover {
            background: #14752f;
        }

    </style>
</head>

<body>

<div class="box">

    <h1>M-PESA Payment</h1>

    <form method="POST" action="/pay">

        <input
            type="text"
            name="phone"
            placeholder="Phone Number e.g. 254701807071"
            required
        >

        <input
            type="number"
            name="amount"
            placeholder="Amount"
            min="1"
            required
        >

        <button type="submit">
            PAY NOW
        </button>

    </form>

</div>

</body>
</html>
""")


# =========================
# INITIATE STK PUSH
# =========================

@app.route("/pay", methods=["POST"])
def pay():

    phone = request.form.get("phone")
    amount = request.form.get("amount")

    try:
        amount = int(amount)
    except:
        return "Invalid amount", 400

    # Convert Kenyan phone formats to 254XXXXXXXXX
    if phone.startswith("07") or phone.startswith("01"):
        phone = "254" + phone[1:]

    elif phone.startswith("+254"):
        phone = phone[1:]

    try:

        access_token = get_access_token()

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        password_string = (
            BUSINESS_SHORT_CODE
            + PASSKEY
            + timestamp
        )

        password = base64.b64encode(
            password_string.encode()
        ).decode()

        url = (
            "https://sandbox.safaricom.co.ke/"
            "mpesa/stkpush/v1/processrequest"
        )

        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json"
        }

        payload = {
            "BusinessShortCode": BUSINESS_SHORT_CODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": BUSINESS_SHORT_CODE,
            "PhoneNumber": phone,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": "Payment",
            "TransactionDesc": "Payment"
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        print("\n===== STK RESPONSE =====")
        print(response.json())
        print("========================\n")

        return jsonify(response.json())

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# M-PESA CALLBACK
# =========================

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


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
