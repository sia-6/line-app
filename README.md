Messaging API（双方向メッセージ送信API）
https://lineapiusecase.com/ja/api/msgapi.html
line / line-api-use-case-messaging-api
https://github.com/line/line-api-use-case-messaging-api?tab=readme-ov-file

Messaging API設定
lambda
 レイヤー
 環境変数
https://github.com/line/line-bot-sdk-python
https://note.com/flymywife/n/n0fbcc1d8aaa7
pythonディレクトリにする理由
https://repost.aws/ja/knowledge-center/lambda-import-module-error-python

```python
import json
import logging
import os
import sys

from linebot import (
        LineBotApi,
        WebhookHandler
        )
from linebot.exceptions import (
        InvalidSignatureError,
        LineBotApiError
        )
from linebot.models import (
        MessageEvent,
        TextMessage,
        TextSendMessage,
        )

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

if CHANNEL_ACCESS_TOKEN is None:
    logger.error('LINE_CHANNEL_ACCESS_TOKEN is not defined as environmental variables.')
    sys.exit(1)
if CHANNEL_SECRET is None:
    logger.error('LINE_CHANNEL_SECRET is not defined as environmental variables.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    answer = 'Hello World'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answer))

def lambda_handler(event, context):
    if 'x-line-signature' in event['headers']:
        signature = event['headers']['x-line-signature']

    body = event['body']
    logger.info(body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {
                'statusCode': 400,
                'body': json.dumps('Webhooks are accepted exclusively from the LINE Platform.')
                }
    except LineBotApiError as e:
        logger.error('Got exception from LINE Messaging API: %s\n' % e.message)
        for m in e.error.details:
            logger.error('  %s: %s' % (m.property, m.message))
    return {
            'statusCode': 200,
            'body': json.dumps('Success!')
            }

```
------------------
DynamoDBへ書き込む
権限設定
```python
import json
import logging
import os
import sys
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('test')

from linebot import (
        LineBotApi,
        WebhookHandler
        )
from linebot.exceptions import (
        InvalidSignatureError,
        LineBotApiError
        )
from linebot.models import (
        MessageEvent,
        TextMessage,
        TextSendMessage,
        )

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

if CHANNEL_ACCESS_TOKEN is None:
    logger.error('LINE_CHANNEL_ACCESS_TOKEN is not defined as environmental variables.')
    sys.exit(1)
if CHANNEL_SECRET is None:
    logger.error('LINE_CHANNEL_SECRET is not defined as environmental variables.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    table.put_item(
        Item={
            'id': 90,
            'price': 59,
            'item_name': 6
        }
    )
    list = event.message.text.split()
    res = ''
    for s in list:
        res += s + '\n'
    logger.info(res)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res))

def lambda_handler(event, context):
    if 'x-line-signature' in event['headers']:
        signature = event['headers']['x-line-signature']

    body = event['body']
    logger.info(body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {
                'statusCode': 400,
                'body': json.dumps('Webhooks are accepted exclusively from the LINE Platform.')
                }
    except LineBotApiError as e:
        logger.error('Got exception from LINE Messaging API: %s\n' % e.message)
        for m in e.error.details:
            logger.error('  %s: %s' % (m.property, m.message))
    return {
            'statusCode': 200,
            'body': json.dumps('Success!')
            }

```
レスポンス
**line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))**

以下は、LINE Messaging API→Amazon API Gateway→AWS Lambda と LINE Messaging API→AWS Lambda の構成それぞれのメリットとデメリットです。

### LINE Messaging API→Amazon API Gateway→AWS Lambda

**メリット**:
1. **セキュリティの向上**: API Gatewayはリクエストの認証やアクセス制御、レート制限を簡単に設定可能。
2. **追加のロギングや監視**: API Gatewayの統合により、リクエストのロギングやCloudWatchとの統合が強化される。
3. **プロトコル変換**: HTTPリクエストとLambda関数の間でプロトコル変換ができ、柔軟性が向上。

**デメリット**:
1. **追加コスト**: API Gatewayの利用に伴い、Lambdaのみの場合よりコストが増加する。
2. **設定の複雑化**: API Gatewayの設定や管理が必要となるため、導入と運用がやや複雑。

### LINE Messaging API→AWS Lambda

**メリット**:
1. **シンプルな構成**: 直接Lambdaを呼び出すことで、設定や運用の手間を削減。
2. **コスト効率**: API Gatewayを使用しないため、低コストで運用できる。

**デメリット**:
1. **セキュリティとアクセス制御の管理が手動**: API Gatewayほど簡単にアクセス制御や認証を設定できない。
2. **拡張性の制限**: API Gatewayほどのプロトコルサポートやリクエスト制限の設定は手動で行う必要がある。

### 結論:
- **API Gatewayあり**の構成は、セキュリティや制御が必要な大規模システム向け。
- **API Gatewayなし**の構成は、簡単かつ低コストな実装を求める小規模なシステムに最適です。
