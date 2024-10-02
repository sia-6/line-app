import os
import boto3
import logging

# DynamoDBのリソースにアクセス
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('household-account-DB')

def lambda_handler(event, context):
    try:
        table.delete_item(
            Key={
                'item_name': 'Food',
                'date': '2024-09-29 04:32:49'
            }
        )
        return {
            'statusCode': 200,
            'body': "Successfully deleted."
        }
    except Exception as e:
        logging.error(f"Error deleting item: {e}")
        return {
            'statusCode': 500,
            'body': f"Failed to delete item. Error: {e}"
        }
