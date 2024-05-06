import paypayopa
import uuid
from dotenv import load_dotenv
import os 
load_dotenv()

API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
MERCHANT_ID =  os.getenv("MERCHANT_ID")

print(API_KEY, SECRET_KEY, MERCHANT_ID)


def create_payment(orders, total):

    client = paypayopa.Client(
        auth=(API_KEY, SECRET_KEY),
        production_mode=False,
    )
    client.set_assume_merchant(MERCHANT_ID)
    request = {
        "merchantPaymentId": str(uuid.uuid1()),
        "codeType": "ORDER_QR",
        "redirectUrl": "http://localhost:3000/bag",
        "redirectType": "WEB_LINK",
        "orderDescription": "TOKUYAMA - GAKUSHOKU",
        "orderItems": orders,
        "amount": {"amount": total, "currency": "JPY"},
    }

    response = client.Code.create_qr_code(request)
    url = response["data"]["url"]
    return url
