# Master list of genres supported by the Aether Vibe Engine
MASTER_GENRES = [
    "lofi-chill",
    "synthwave",
    "pop",
    "hip-hop",
    "r&b",
    "japanese-chill",
    "rock",
    "indie",
    "jazz",
    "classical"
]

def generate_taste_vector(user_genres):
    """
    Transforms a raw list of user music genres into a normalized binary vector
    based on the fixed MASTER_GENRES dictionary indexing layout.
    """
    # Initialize a vector of zeros matching our master dictionary length
    vector = [0] * len(MASTER_GENRES)
    
    # Normalize input items to prevent casing or spacing mismatches
    normalized_user_genres = [g.lower().strip() for g in user_genres]
    
    # Flip the index bit to 1 if the user possesses the matching profile trait
    for index, genre in enumerate(MASTER_GENRES):
        if genre in normalized_user_genres:
            vector[index] = 1
            
    return vector

def test_vectorizer():
    """Diagnostic helper to verify matrix integrity locally"""
    sample_traits = ["pop", "synthwave", "lofi-chill"]
    result_vector = generate_taste_vector(sample_traits)
    print(f"Sample Input:  {sample_traits}")
    print(f"Mapped Vector: {result_vector}")

if __name__ == "__main__":
    test_vectorizer()