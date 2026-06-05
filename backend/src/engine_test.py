from vectorizer import generate_taste_vector
from matcher import calculate_similarity

# Simulating a DynamoDB table scan of potential matches
DUMMY_USERS = [
    {"name": "Alex", "traits": ["rock", "indie", "jazz", "classical"]},
    {"name": "Sam", "traits": ["lofi-chill", "synthwave", "pop", "hip-hop"]},
    {"name": "Jordan", "traits": ["classical", "jazz", "pop"]},
    {"name": "Taylor", "traits": ["pop", "r&b", "hip-hop", "synthwave", "japanese-chill"]}
]

def run_matchmaking(current_user_traits):
    print(f"--- AETHER MATCHMAKING INITIATED ---")
    print(f"Your Music DNA: {current_user_traits}\n")

    # 1. Vectorize the current user
    current_vector = generate_taste_vector(current_user_traits)
    
    results = []
    
    # 2. Iterate through the database and calculate scores
    for user in DUMMY_USERS:
        target_vector = generate_taste_vector(user["traits"])
        score = calculate_similarity(current_vector, target_vector)
        
        # Find exactly which genres overlap for the UI
        shared_traits = list(set(current_user_traits) & set(user["traits"]))
        
        results.append({
            "name": user["name"],
            "match_percentage": round(score * 100, 2),
            "shared_traits": shared_traits
        })
        
    # 3. Sort the feed by highest match percentage
    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    # 4. Print the final UI feed
    for rank, match in enumerate(results, 1):
        print(f"#{rank} Match: {match['name']} - {match['match_percentage']}%")
        print(f"    Vibe Overlap: {match['shared_traits']}\n")

if __name__ == "__main__":
    # Injecting the exact seed data your auth.py script generated earlier
    my_traits = ["lofi-chill", "synthwave", "pop", "hip-hop", "r&b", "japanese-chill"]
    
    run_matchmaking(my_traits)