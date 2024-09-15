## はじめに
嫁がなかなか家計簿をつけてくれない...。家計簿アプリをいろいろと試してみたが入力するのが面倒だというので負担の少ない方法を模索しました。そこで思いついたのが、LINE Messaging APIを使って簡単に家計簿をつけられるシステムを作ること！AWSを使ってLINE経由でサクッと家計簿をつけられる仕組みを作ることにしました。

### システムの概要
この記事で紹介する家計簿アプリは、LINEのメッセージを使って品目と金額を送信するだけで、データが**AWS Lambda**経由で**Amazon DynamoDB**に保存するというシンプルな構成です。
- **AWS Lambda**: LINEから受け取ったデータを処理し、DynamoDBに保存する関数を実行。
- **Amazon DynamoDB**: 家計簿データを保存するためのNoSQLデータベース。

### 開発の流れ
1. **LINE Developersコンソールでチャネル作成**  
   まずは、LINEのAPIと連携するためにチャネルを作成。Webhook URLには、AWS Lambdaの関数URLを設定します。

2. **Lambda関数の実装**  
   LINEから送られた項目と金額をDynamoDBに保存するコードをLambdaで作成します。

```python
import os
import sys
import json
import boto3
import logging
import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# DynamoDBに接続し、テーブル 'household_account' を指定
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('household_account')

# ログ設定 (INFOレベル以上のメッセージを記録)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数からLINEチャネルアクセストークンとシークレットを取得
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

# トークンとシークレットがない場合エラーを表示して終了
if CHANNEL_ACCESS_TOKEN is None:
    logger.error('LINE_CHANNEL_ACCESS_TOKEN is not defined as environmental variables.')
    sys.exit(1)
if CHANNEL_SECRET is None:
    logger.error('LINE_CHANNEL_SECRET is not defined as environmental variables.')
    sys.exit(1)

# LineBotAPI と WebhookHandler の初期化
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 家計簿項目の初期データ
item_name = {
    'F': 'Food',
    'U': 'Utility',
    'I': 'Internet',
    'C': 'Clothing',
    'T': 'Transportation',
    'D': 'Daily necessities'
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
                        'date': str(datetime.datetime.today()),  # 日付を現在の日付に設定
                        'item_name': item_name[initial_letter],  # 項目名
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
```


#### **ここまでの設定は下記のブログを参考にしています。**
https://note.com/flymywife/n/n0fbcc1d8aaa7
https://note.com/flymywife/n/n89cb8671d478

3. **DynamoDBテーブルの設定**  
   DynamoDBでは、テーブル名とパーティションキーを設定して後はデフォルトでOKです。
<img width="1038" alt="スクリーンショット 2024-09-15 13 19 45" src="https://github.com/user-attachments/assets/e6240dba-086f-4cea-b02d-ac1478eeef66">
<img width="1146" alt="スクリーンショット 2024-09-15 13 20 47" src="https://github.com/user-attachments/assets/95953a53-15d8-45f3-b848-f20aca0b4c1a">

### LINEで入力
以下の入力を試してみました。
- hまたはhelpでヘルプメッセージを出力
- 項目と金額を入力
- 不正な値の入力
<img width="300" alt="スクリーンショット 2024-09-15 13 20 47" src="https://github.com/user-attachments/assets/04acfe40-31ba-47b9-b628-6a7450cc0fef">
<img width="300" alt="スクリーンショット 2024-09-15 13 20 47" src="https://github.com/user-attachments/assets/b755b910-ba31-4b14-a63e-c28d13887d03">

#### DynamoDBテーブルを確認する
DynamoDB>項目を探索>"テーブル名"を開くとテーブルにデータが保存されているのがわかります。
<img width="870" alt="スクリーンショット 2024-09-15 13 56 31" src="https://github.com/user-attachments/assets/28069196-0ba1-4afc-850c-49c6145b94fe">
<img width="864" alt="スクリーンショット 2024-09-15 15 15 30" src="https://github.com/user-attachments/assets/7e2895d7-0255-4caf-8d62-69fee8ba1720">

### 実際に使ってみて

この仕組みなら、品名と価格をLINEでサクッと送信するだけで家計簿が完成します。何より、LINEという普段使い慣れたツールを利用しているため、操作がとても簡単で、日常的に使いやすいのが大きな魅力です。家計簿の記入が手間と感じる方でも、気軽に継続できるのではないかと思います。

### まとめと今後

今回は非常にシンプルな構成に仕上げましたが、今後の展望としては以下のポイントに取り組んでいきたいです。
- **品目の追加**：多様な支出に対応できるように、家計簿の品目を増やす予定です。
- **データの集計機能**：合計金額や月別支出の集計などを自動化し、支出を一目で確認できるようにしたいです。
- **AWSサービス予算超過時の対策**：AWSのコスト管理の強化にも取り組み、予算超過時に自動でアラートを設定し、不要な出費を抑える仕組みを導入する予定です。
- **データの可視化**：集めたデータをよりわかりやすく視覚化して、グラフやチャートで表示する機能を追加し、家計の管理がさらに楽しくなるようにしたいと考えています。

このプロジェクトは、自分や家族が楽に家計簿を続けられるように改善し続けていきます。
