from fuzzywuzzy import fuzz

# =================================
# 2. KARŞILAŞTIRMA FONKSİYONU
# =================================
def compare_texts(target: str, user: str):
    # Normalize
    target_norm = target.lower().strip()
    user_norm   = user.lower().strip()

    # Benzerlik oranları
    ratio = fuzz.ratio(target_norm, user_norm)
    partial = fuzz.partial_ratio(target_norm, user_norm)
    token_sort = fuzz.token_sort_ratio(target_norm, user_norm)

    # Ortalama skor
    score = int((ratio + partial + token_sort) / 3)
    passed = score >= 80

    return {
        "score": score,
        "ratio": ratio,
        "partial": partial,
        "token_sort": token_sort,
        "passed": passed,
        "feedback": "Good work, keep Up!" if passed else "You have to practice more"
    }