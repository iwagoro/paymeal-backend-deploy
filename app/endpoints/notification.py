from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..schema import submitNotificationSchema, sendNotificationSchema
from ..database import Users
from firebase_admin import messaging
from .util.util import get_db, verify_token

router = APIRouter()


# * ユーザに通知を行う
def send_to_individual(token, title, body):
    # メッセージを作成
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )

    # メッセージを送信
    response = messaging.send(message)


#! Notification tokenを登録するエンドポイント
@router.post("/notification", status_code=200)
async def add_notification_token(
    token: submitNotificationSchema, user=Depends(verify_token), db: Session = Depends(get_db)
):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.notification_token = token.token
    db.commit()
    return "Notification token added"


# ?管理者のみがアクセスできるエンドポイント
#! ユーザーに通知を送信するエンドポイント
@router.post("/notification/send", status_code=202)
async def sent_notification(target: sendNotificationSchema, user=Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(Users).filter_by(email=user["email"]).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    target_user = db.query(Users).filter(Users.id == target.target_id, Users.notification_token != "").first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    # 通知を送信
    send_to_individual(target_user.notification_token, target.title, target.body)
