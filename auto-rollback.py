import os
import boto3

lambda_client = boto3.client('lambda')
ssm_client = boto3.client('ssm')

def get_ssm_parameter(name):
    response = ssm_client.get_parameter(Name=name)
    return response['Parameter']['Value']

def lambda_handler(event, context):
    function_name = os.environ['FUNCTION_NAME']  # e.g., "app"
    alias_name    = os.environ['ALIAS_NAME']     # e.g., "ALIAS_PROD_ROLLBACK"

    # Dynamically fetch latest v1 version from SSM Parameter Store
    try:
        latest_v1 = get_ssm_parameter('/app/LATEST_V1')
        print(f"Fetched LATEST_V1 from SSM: {latest_v1}")
    except Exception as e:
        print(f"Failed to fetch LATEST_V1 from SSM: {e}")
        raise

    # Update the alias to point 100% traffic to the fetched v1 version
    response = lambda_client.update_alias(
        FunctionName=function_name,
        Name=alias_name,
        FunctionVersion=latest_v1,
        Description="Rolled back to 100% app v1",
        RoutingConfig={'AdditionalVersionWeights': {}}
    )

    print("Alias updated:", response)
    return response
