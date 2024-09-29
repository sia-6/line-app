import boto3

def disable_lambda_function(function_name):
    client = boto3.client('lambda')

    try:
        response = client.put_function_concurrency(
            FunctionName=function_name,
            ReservedConcurrentExecutions=0
        )
        print(f"Lambda関数 {function_name} を無効化しました。")
        return response
    except Exception as e:
        print(f"エラー: {e}")
        raise

def lambda_handler(event, context):
    function_name = "line-app" #停止するLambda関数を指定する
    disable_lambda_function(function_name)
    return {
        'statusCode': 200,
        'body': f"{function_name} の実行を停止しました。"
    }
