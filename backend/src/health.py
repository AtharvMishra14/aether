import json
import os

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "status": "healthy",
            "database_target": os.environ.get("USERS_TABLE", "unknown")
        })
    }