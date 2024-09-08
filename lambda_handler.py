import json
import logging
import os
import sys
import uuid
import boto3
import datetime

#split_list = [x for x in text.split('\n') if x]

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('test2')

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

help_message = "D : Daily necessities\nF : Food\nE : Eating out\nT : Transportation expenses"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text

    if message == 'help':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_message))
    else:
        mes = message.split()
        table.put_item(
            Item={
                'date': str(datetime.date.today()),
                'item_name': mes[0],
                'price': mes[1]
            }
        )
        # list = event.message.text.split()
        # res = ''
        # for s in list:
        #     res += s + '\n'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

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
