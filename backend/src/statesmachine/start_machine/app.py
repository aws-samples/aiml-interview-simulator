import os
import json
import boto3

STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]
step_functions = boto3.client("stepfunctions")


def lambda_handler(event, context):

    response = step_functions.start_execution(
        stateMachineArn=STATE_MACHINE_ARN, input=json.dumps(event)
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": json.dumps(
            {
                "results": "started",
            }
        ),
    }
