import os
import sys
import json
import boto3
import logging
import datetime
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

item_name = {
    'D': 'Daily necessities',
    'F': 'Food',
    'E': 'Eating out',
    'T': 'Transportation expenses'
}
help_message = 'Write the initial letter of the item name (lowercase or uppercase) on the first line and the price on the second line.\n[Item name]'
for i in item_name.values():
    help_message += '\n- ' + i

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text

    if message == 'h' or message == 'help':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_message))
    else:
        message_list = message.split()
        if len(message_list) != 2:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_message))
        else:
            initial_letter = message_list[0].upper()
            try:
                item_name[initial_letter]
                table.put_item(
                    Item={
                        'date': str(datetime.date.today()),
                        'item_name': item_name[initial_letter],
                        'price': message_list[1],
                        'user_id': event.source.user_id
                    }
                )
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message_list[0]))
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Enter the correct product name.'))

def lambda_handler(event, context):
    body = event['body']

    logger.info(body)
    if 'x-line-signature' in event['headers']:
        signature = event['headers']['x-line-signature']
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
