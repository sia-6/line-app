import boto3
import logging
import datetime
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

# DynamoDBに接続し、テーブル 'household-account-DB' を指定
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('household-account-DB')

# ログ設定 (INFOレベル以上のメッセージを記録)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
help_message = 'The initial letter of the item + amount.'
for i in item_name.values():
    help_message += '\n- ' + i

def process_message(event):
    # 'h' または 'help' が送信された場合、ヘルプメッセージを返信
    message = event.message.text  # ユーザーのメッセージを取得
    if message == 'h' or message == 'help':
        return help_message
    # 'l' が送信された場合、最新のアイテム10件のデータを返信
    elif message[0] == 'l' or message[0] == 'L':
        if len(message) != 2:
            # メッセージが不正な形式の場合、ヘルプメッセージを返信
            return "L or l + the initial letter of the item"
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
                items_list = item_name[item_name_key]
                logger.info(items)  # 取得したアイテム内容をログに記録
                for item in items:
                    items_list += f"\n{item['date'].split(' ')[0]} : {str(item['price'])}"
                return items_list
            except ValueError as e:
                # 無効な入力があった場合のエラーメッセージ
                return str(e)
            except Exception as e:
                # その他のエラーが発生した場合の処理
                logger.error(f"Error occurred: {e}")
                return "An error occurred. Please try again."
    else:
        # メッセージを2つに分割 (項目と価格)
        initial_letter = message[0].upper()  # 項目の頭文字を大文字に変換
        try:
            # 項目の頭文字が正しいかチェック
            if initial_letter not in item_name:
                raise ValueError("Invalid item name.")

            price = int(message[1:])  # 価格を整数に変換

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
            return f"{item_name[initial_letter]}: {price} has been added."
        except ValueError as e:
            # 無効な入力があった場合のエラーメッセージ
            return str(e)
        except Exception as e:
            # その他のエラーが発生した場合の処理
            logger.error(f"Error occurred: {e}")
            return "An error occurred. Please try again."
