import json
import os
import urllib.parse
import urllib.request
import base64
import secrets
import pymongo

from vectorizer import generate_taste_vector
from matcher import calculate_similarity

MONGO_URI = os.environ.get("MONGO_URI")

print(f"\n--- DEBUG DB --- MONGO_URI is: {'FOUND' if MONGO_URI else 'MISSING IN RENDER'}", flush=True)

db = None
if not MONGO_URI:
    print("CRITICAL ERROR: Render cannot see the MONGO_URI variable!", flush=True)
else:
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client["aether_db"]
        client.admin.command('ping')
        print("--- DEBUG DB --- Connected to MongoDB Atlas successfully!", flush=True)
    except Exception as e:
        print(f"--- DEBUG DB --- CONNECTION FAILED: {e}", flush=True)
        db = None

DUMMY_USERS = [
    {"id": "u1", "name": "Taylor", "traits": ["pop", "r&b", "hip-hop", "synthwave", "japanese-chill"]},
    {"id": "u2", "name": "Sam", "traits": ["lofi-chill", "synthwave", "pop", "hip-hop"]},
    {"id": "u3", "name": "Jordan", "traits": ["classical", "jazz", "pop"]},
    {"id": "u4", "name": "Alex", "traits": ["rock", "indie", "jazz", "classical"]}
]

base_auth = "https://" + "accounts" + ".spotify.com"
base_api = "https://" + "api" + ".spotify.com/v1"

def fetch_spotify_data(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"--- DEBUG SPOTIFY --- Failed fetching from {url}: {e}", flush=True)
        return {"error": str(e)}

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
        
        auth_url = f"{base_auth}/authorize?{urllib.parse.urlencode(params)}"
        
        return {
            "statusCode": 302,
            "headers": {"Location": auth_url}
        }
        
    elif "callback" in path:
        query_params = event.get("queryStringParameters", {}) or {}
        code = query_params.get("code")
        error = query_params.get("error")
        
        if error or not code:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": error or "Missing authorization code"})
            }
            
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI")
        
        auth_string = f"{client_id}:{client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        
        token_url = f"{base_auth}/api/token"
        token_data = urllib.parse.urlencode({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }).encode("ascii")
        
        req = urllib.request.Request(token_url, data=token_data, headers={
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        })
        
        try:
            with urllib.request.urlopen(req) as response:
                token_info = json.loads(response.read().decode("utf-8"))
            
            access_token = token_info.get("access_token")
            
            frontend_url = "https://aether-sand-three.vercel.app"
            react_app_url = f"{frontend_url}/?token={access_token}"
            
            return {
                "statusCode": 302,
                "headers": {"Location": react_app_url}
            }
            
        except urllib.error.URLError as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Failed token exchange"})
            }

    elif "profile" in path:
        headers = event.get("headers", {}) or {}
        auth_header = headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Unauthorized: Missing or invalid token format"})
            }
            
        access_token = auth_header.split(" ")[1]
        
        user_profile = fetch_spotify_data(f"{base_api}/me", access_token)
        spotify_id = user_profile.get("id")
        username = user_profile.get("display_name", "Aether Explorer")
        
        raw_artists = fetch_spotify_data(f"{base_api}/me/top/artists", access_token)
        
        top_artists = []
        all_genres = []
        
        if "items" in raw_artists and len(raw_artists["items"]) > 0:
            for item in raw_artists["items"]:
                top_artists.append(item.get("name"))
                all_genres.extend(item.get("genres", []))
            unique_genres = list(set(all_genres))[:15]
            profile_status = "live"
        else:
            top_artists = ["Lofi Fruits Music", "Chillhop Music", "The Weeknd", "Daft Punk", "Kendrick Lamar"]
            unique_genres = ["lofi-chill", "synthwave", "pop", "hip-hop", "r&b", "japanese-chill"]
            profile_status = "development_seed"
            
        taste_vector = generate_taste_vector(unique_genres)
        
        if db is not None and spotify_id:
            try:
                db.users.update_one(
                    {"spotify_id": spotify_id},
                    {
                        "$set": {
                            "spotify_id": spotify_id,
                            "name": username,
                            "traits": unique_genres,
                            "top_artists": top_artists,
                            "taste_vector": taste_vector
                        }
                    },
                    upsert=True
                )
                print(f"--- DEBUG DB --- Saved profile for {username} to Atlas!", flush=True)
            except Exception as e:
                print(f"--- DEBUG DB --- Failed to save profile: {e}", flush=True)
        else:
            print(f"--- DEBUG DB --- SKIPPED DB SAVE! db: {db}, spotify_id: {spotify_id}", flush=True)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "username": username,
                "profile_status": profile_status,
                "top_artists": top_artists,
                "genres": unique_genres,
                "taste_vector": taste_vector
            }, indent=2)
        }

    elif "matches" in path:
        headers = event.get("headers", {}) or {}
        auth_header = headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Unauthorized: Missing or invalid token format"})
            }
            
        access_token = auth_header.split(" ")[1]
        
        user_profile = fetch_spotify_data(f"{base_api}/me", access_token)
        current_spotify_id = user_profile.get("id")
        
        raw_artists = fetch_spotify_data(f"{base_api}/me/top/artists", access_token)
        
        all_genres = []
        if "items" in raw_artists and len(raw_artists["items"]) > 0:
            for item in raw_artists["items"]:
                all_genres.extend(item.get("genres", []))
            unique_genres = list(set(all_genres))[:15]
        else:
            unique_genres = ["lofi-chill", "synthwave", "pop", "hip-hop", "r&b", "japanese-chill"]
            
        current_vector = generate_taste_vector(unique_genres)
        results = []
        
        if db is not None and current_spotify_id:
            query = {"spotify_id": {"$ne": current_spotify_id}}
            
            try:
                already_swiped = [doc["target_id"] for doc in db.interactions.find({"user_id": current_spotify_id})]
                if already_swiped:
                    query["spotify_id"]["$nin"] = already_swiped
                    
                real_users = list(db.users.find(query))
                
                for user in real_users:
                    score = calculate_similarity(current_vector, user.get("taste_vector", []))
                    shared_traits = list(set(unique_genres) & set(user.get("traits", [])))
                    
                    results.append({
                        "user_id": user["spotify_id"],
                        "name": user.get("name", "Explorer"),
                        "match_percentage": round(score * 100, 2),
                        "shared_traits": shared_traits
                    })
            except Exception as e:
                print(f"--- DEBUG DB --- Error fetching matches: {e}", flush=True)
                
        if not results:
            for user in DUMMY_USERS:
                target_vector = generate_taste_vector(user["traits"])
                score = calculate_similarity(current_vector, target_vector)
                shared_traits = list(set(unique_genres) & set(user["traits"]))
                
                results.append({
                    "user_id": user["id"],
                    "name": user["name"],
                    "match_percentage": round(score * 100, 2),
                    "shared_traits": shared_traits
                })
            
        results.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"status": "success", "matches": results}, indent=2)
        }

    elif "connect" in path:
        headers = event.get("headers", {}) or {}
        auth_header = headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Unauthorized: Missing token"})
            }
            
        access_token = auth_header.split(" ")[1]
        
        user_profile = fetch_spotify_data(f"{base_api}/me", access_token)
        current_spotify_id = user_profile.get("id")

        body = event.get("body", "{}")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {}

        target_id = payload.get("target_user_id")
        action = payload.get("action")

        if not target_id or not action:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Missing target_user_id or action in payload"})
            }

        mutual_match = False
        
        if db is not None and current_spotify_id:
            try:
                db.interactions.update_one(
                    {"user_id": current_spotify_id, "target_id": target_id},
                    {"$set": {"user_id": current_spotify_id, "target_id": target_id, "action": action}},
                    upsert=True
                )
                
                if action == "like":
                    reverse_swipe = db.interactions.find_one({
                        "user_id": target_id,
                        "target_id": current_spotify_id,
                        "action": "like"
                    })
                    if reverse_swipe:
                        mutual_match = True
            except Exception as e:
                print(f"--- DEBUG DB --- Error saving swipe: {e}", flush=True)
        else:
            if action == "like" and target_id == "u1":
                mutual_match = True

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "status": "success",
                "message": f"Action '{action}' recorded for user {target_id}",
                "mutual_match": mutual_match
            }, indent=2)
        }
            
    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"error": "Endpoint Not Found"})
    }