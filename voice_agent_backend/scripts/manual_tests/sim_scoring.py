import math

def rrf_score(ranks, k=60):
    return sum(1.0 / (rank + k) for rank in ranks)

# Simulation: Chunk hit in 4 variants at ranks 1, 1, 2, 1
variants_ranks = [1, 1, 2, 1]
score = rrf_score(variants_ranks)
print(f"RRF Score (4 variants, top ranks): {score:.4f}")
print(f"Scaled RRF (x15): {score * 15:.4f}")

# Simulation: Chunk hit in 1 variant at rank 1
score_single = rrf_score([1])
print(f"RRF Score (1 variant, rank 1): {score_single:.4f}")
print(f"Scaled RRF (x15): {score_single * 15:.4f}")

# Target combined score calculation
vector_score = 0.6
keyword_score = 1.0
rare_bonus = 0.1
noun_bonus = 0.1
rrf_contrib = score * 15

final = (vector_score * 0.4) + (rrf_contrib * 0.3) + (keyword_score * 0.2) + rare_bonus + noun_bonus
print(f"Final Combined Score Example: {final:.4f}")
