import paypayopa
from fastapi import HTTPException
import os


API_KEY = os.environ["API_KEY"]
SECRET_KEY = os.environ["SECRET_KEY"]
MERCHANT_ID = os.environ["MERCHANT_ID"]


client = paypayopa.Client(
    auth=(API_KEY, SECRET_KEY),
    production_mode=False,
)
client.set_assume_merchant(MERCHANT_ID)


#! 支払いを作成する関数
def create_payment(payment_id, orders, total):
    # ? 注文内容を作成
    request = {
        "merchantPaymentId": payment_id,
        "codeType": "ORDER_QR",
        "redirectUrl": "http://localhost:3000/cart",
        "redirectType": "WEB_LINK",
        "orderDescription": "Paymeal",
        "orderItems": orders,
        "amount": {"amount": total, "currency": "JPY"},
    }
    # ? QRコードを作成
    response = client.Code.create_qr_code(request)
    # ? urlが取得できなかった場合はエラーを返す
    if response["resultInfo"]["code"] != "SUCCESS":
        raise HTTPException(status_code=400, detail="PAYMENT CREATION FAILED")
    code_id = response["data"]["codeId"]
    url = response["data"]["url"]
    return url, code_id


#! 支払いを削除する関数
def delete_payment(code_id):
    # ? QRコードを削除
    response = client.Code.delete_qr_code(code_id)
    # ?削除に失敗した場合はエラーを返す
    if response["resultInfo"]["code"] != "SUCCESS":
        raise HTTPException(status_code=400, detail="PAYMENT DELETION FAILED")


#! 支払いの詳細を取得する関数
def get_payment_details(payment_id):
    # ? 支払いの詳細を取得
    response = client.Payment.get_payment_details(payment_id)
    # ? 支払いが成功しているか確認
    if response["resultInfo"]["code"] != "SUCCESS":
        raise HTTPException(status_code=400, detail="PAYMENT FAILED")


#! 決済をキャンセルする関数
def cancel_payment(payment_id):
    response = client.Payment.cancel_payment(payment_id)
    if response["resultInfo"]["code"] != "SUCCESS":
        raise HTTPException(status_code=400, detail="PAYMENT CANCELLATION FAILED")
