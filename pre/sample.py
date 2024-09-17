import json
import os
import boto3
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 環境変数からLINEチャンネルのトークンとシークレットを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# DynamoDBにアクセスするためのクライアントを作成
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YourDynamoDBTable')  # ここでDynamoDBテーブル名を指定

# メッセージイベントを処理するハンドラ
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ユーザーIDを取得
    user_id = event.source.user_id
    # 送信されたテキストを取得
    user_input = event.message.text

    # DynamoDBにデータを保存
    table.put_item(
        Item={
            'user_id': user_id,
            'message': user_input,
            'timestamp': int(event.timestamp)  # タイムスタンプを保存
        }
    )

    # LINEユーザーに確認メッセージを返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='データが記録されました!')
    )

# Lambdaのエントリーポイント
def lambda_handler(event, context):
    signature = event['headers']['x-line-signature']
    body = event['body']

    # Webhookハンドラでイベント処理を実行
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid signature')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
