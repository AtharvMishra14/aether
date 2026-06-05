import math

def calculate_similarity(vector_a, vector_b):
    if len(vector_a) != len(vector_b):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    
    sum_sq_a = sum(a * a for a in vector_a)
    sum_sq_b = sum(b * b for b in vector_b)
    
    if sum_sq_a == 0 or sum_sq_b == 0:
        return 0.0
        
    return dot_product / (math.sqrt(sum_sq_a) * math.sqrt(sum_sq_b))

if __name__ == "__main__":
    user_a = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    user_b = [0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    
    score = calculate_similarity(user_a, user_b)
    print(f"Calculated Vibe Match Score: {round(score * 100, 2)}%")