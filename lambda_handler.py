import os
import sys
import json
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from app.line_bot import process_message

# ログ設定 (INFOレベル以上のメッセージを記録)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数からLINEチャネルアクセストークンとシークレットを取得
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

# トークンとシークレットがない場合エラーを表示して終了
if CHANNEL_ACCESS_TOKEN is None:
    logger.error('CHANNEL_ACCESS_TOKEN is not defined as environmental variables.')
    sys.exit(1)
if CHANNEL_SECRET is None:
    logger.error('CHANNEL_SECRET is not defined as environmental variables.')
    sys.exit(1)

# LineBotAPI と WebhookHandler の初期化
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# メッセージを受け取った際の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    logger.info(event)  # メッセージ内容をログに記録
    message = process_message(event)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

# Lambda関数のエントリーポイント
def lambda_handler(event, context):
    # リクエストヘッダーから署名を取得
    signature = event['headers']['x-line-signature']
    body = event['body']  # リクエストのボディを取得

    # WebhookハンドラでLINEイベントの処理を実行
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名が不正な場合は400エラーを返す
        return {
                'statusCode': 400,
                'body': json.dumps('Invalid signature')
                }

    # 正常に処理が完了した場合、200ステータスコードを返す
    return {
            'statusCode': 200,
            'body': json.dumps('Success')
            }
