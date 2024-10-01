import boto3
import os
import logging

# DynamoDBのリソースにアクセス
dynamodb = boto3.resource('dynamodb')
# 環境変数またはハードコーディングでテーブル名を指定
table = dynamodb.Table('your-dynamodb-table-name')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # 削除するアイテムのパーティションキー（例: 'id'）を指定
    try:
        partition_key_value = event['id']  # eventからパーティションキーの値を取得
    except KeyError:
        return {
            'statusCode': 400,
            'body': 'Error: Missing required "id" in the event payload'
        }

    try:
        # DynamoDBからアイテムを削除
        response = table.delete_item(
            Key={
                'id': partition_key_value  # パーティションキー
            }
        )
        logger.info(f'Deleted item with id: {partition_key_value}')
        
        return {
            'statusCode': 200,
            'body': f'Successfully deleted item with id: {partition_key_value}'
        }

    except Exception as e:
        logger.error(f'Error deleting item from DynamoDB: {e}')
        return {
            'statusCode': 500,
            'body': f'Error deleting item: {str(e)}'
        }
