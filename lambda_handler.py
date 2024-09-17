import os
import sys
import json
import boto3
import logging
import datetime
from boto3.dynamodb.conditions import Key
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from boto3.dynamodb.conditions import Attr

# DynamoDBに接続し、テーブル 'household-account-DB' を指定
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('household-account-DB')

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

# 家計簿項目の初期データ
item_name = {
        'F': 'Food',
        'D': 'Daily necessities',
        'C': 'Clothing',
        'P': 'Pet',
        'T': 'Transportation',
        'U': 'Utility',
        'I': 'Internet',
        'O': 'Others',
        }

# ヘルプメッセージ作成 (項目リスト付き)
help_message = 'Write the initial letter of the item name (lowercase or uppercase) on the first line and the price on the second line.'
for i in item_name.values():
    help_message += '\n- ' + i

# メッセージを受け取った際の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    logger.info(event)  # メッセージ内容をログに記録
    message = event.message.text  # ユーザーのメッセージを取得

    # 'h' または 'help' が送信された場合、ヘルプメッセージを返信
    if message == 'h' or message == 'help':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_message))
    # 'l' が送信された場合、最新のアイテム10件のデータを返信
    elif message[0] == 'l' or message[0] == 'L':
        if len(message) != 2:
            # メッセージが不正な形式の場合、ヘルプメッセージを返信
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="There is an error in the command to get the latest 10 data items. For example, if the item is \"Food\", enter \"l\" or \"L\" plus the first letter of the item name."))
        else:
            item_name_key = message[1].upper()  # アイテム名の頭文字を大文字に変換
            try:
                # 項目の頭文字が正しいかチェック
                if item_name_key not in item_name:
                    raise ValueError("Invalid item name.")
                # Query操作で直近の10件のデータを取得
                response = table.query(
                    KeyConditionExpression=Key('item_name').eq(item_name[item_name_key]),
                    ScanIndexForward=False,  # 降順でソート (最新のデータから取得)
                    Limit=10  # 最新の10件のみ取得
                )
                items = response.get('Items', [])
                if not items:
                    raise ValueError("No recent data available for the selected item.")
                items_list = items[0]['date'].split(' ')[0]
                logger.info(items)  # 取得したアイテム内容をログに記録
                for item in items:
                    items_list += f"\n{item['item_name']} : {str(item['price'])}"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=items_list))
            except ValueError as e:
                # 無効な入力があった場合のエラーメッセージ
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(e)))
            except Exception as e:
                # その他のエラーが発生した場合の処理
                logger.error(f"Error occurred: {e}")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="An error occurred. Please try again."))     
    else:
        # メッセージを2つに分割 (項目と価格)
        message_list = message.split()
        if len(message_list) != 2:
            # メッセージが不正な形式の場合、ヘルプメッセージを返信
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_message))
        else:
            initial_letter = message_list[0].upper()  # 項目の頭文字を大文字に変換
            try:
                # 項目の頭文字が正しいかチェック
                if initial_letter not in item_name:
                    raise ValueError("Invalid item name.")

                price = int(message_list[1])  # 価格を整数に変換

                # DynamoDBにデータを保存
                table.put_item(
                        Item={
                            'item_name': item_name[initial_letter],  # 項目名
                            'date': str(datetime.datetime.today()),  # 日付を現在の日付に設定
                            'price': price,  # 価格
                            'user_id': event.source.user_id  # ユーザーID
                            }
                        )
                # 正常に追加された場合、ユーザーに通知
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{item_name[initial_letter]}: {price} has been added."))
            except ValueError as e:
                # 無効な入力があった場合のエラーメッセージ
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(e)))
            except Exception as e:
                # その他のエラーが発生した場合の処理
                logger.error(f"Error occurred: {e}")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="An error occurred. Please try again."))

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
