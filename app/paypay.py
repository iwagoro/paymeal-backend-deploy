import paypayopa
import uuid
from dotenv import load_dotenv
import os 
load_dotenv()

API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
MERCHANT_ID =  os.getenv("MERCHANT_ID")

# 支払いを作成する関数
def create_payment(payment_id,orders, total):

    client = paypayopa.Client(
        auth=(API_KEY, SECRET_KEY),
        production_mode=False,
    )
    client.set_assume_merchant(MERCHANT_ID)
    request = {
        "merchantPaymentId": payment_id,
        "codeType": "ORDER_QR",
        "redirectUrl": "http://localhost:3000/bag",
        "redirectType": "WEB_LINK",
        "orderDescription": "TOKUYAMA - GAKUSHOKU",
        "orderItems": orders,
        "amount": {"amount": total, "currency": "JPY"},
    }

    response = client.Code.create_qr_code(request)
    code_id = response["data"]["codeId"]
    url = response["data"]["url"]
    return url ,code_id

def delete_payment(code_id):
    client = paypayopa.Client(
        auth=(API_KEY, SECRET_KEY),
        production_mode=False,
    )
    client.set_assume_merchant(MERCHANT_ID)
    response = client.Code.delete_qr_code(code_id)
    return response['resultInfo']['code']

# 支払いの詳細を取得する関数
def get_payment_details(payment_id):
    client = paypayopa.Client(
        auth=(API_KEY, SECRET_KEY),
        production_mode=False,
    )
    client.set_assume_merchant(MERCHANT_ID)
    response = client.Payment.get_payment_details(payment_id)
    return response['resultInfo']['code']

# 決済をキャンセルする関数
def cancel_payment(payment_id):
    client = paypayopa.Client(
        auth=(API_KEY, SECRET_KEY),
        production_mode=False,
    )
    client.set_assume_merchant(MERCHANT_ID)
    response = client.Payment.cancel_payment(payment_id)
    return response['resultInfo']['code']