import json
import os
import urllib.parse
import secrets

def lambda_handler(event, context):
    path = event.get("path", "")
    
    if "login" in path:
        state = secrets.token_urlsafe(16)
        scopes = "user-top-read user-read-private user-read-email"
        
        params = {
            "response_type": "code",
            "client_id": os.environ.get("SPOTIFY_CLIENT_ID"),
            "scope": scopes,
            "redirect_uri": os.environ.get("SPOTIFY_REDIRECT_URI"),
            "state": state
        }
        
        auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
        
        return {
            "statusCode": 302,
            "headers": {
                "Location": auth_url
            }
        }
        
    elif "callback" in path:
        query_params = event.get("queryStringParameters", {}) or {}
        code = query_params.get("code")
        error = query_params.get("error")
        
        if error or not code:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": error or "Missing authorization code"})
            }
            
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Authorization code received successfully",
                "code": code[:10] + "..."
            })
        }
        
    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "Not Found"})
    }