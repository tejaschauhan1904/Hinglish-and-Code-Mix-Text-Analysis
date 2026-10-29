"""
Sentiment Analysis Engine for Hinglish & English Code-Mixed Text.
Data Source: Supabase PostgreSQL (via backend.db)
Zero hardcoded lexicons, weights, or emojis in Python code.
"""

import re
try:
    from . import db
except (ImportError, ValueError):
    import db

def analyze_sentiment(text):
    """
    Sentiment analysis for Hinglish and English text.
    Uses polarity lexicons, negation inversion, and intensifier/diminisher scaling
    retrieved dynamically from the Supabase PostgreSQL database.
    """
    positive_lexicon = db.get_positive_lexicon()
    negative_lexicon = db.get_negative_lexicon()
    emoji_sentiment = db.get_emoji_sentiment()
    negators = db.get_negators()
    intensifiers = db.get_intensifiers()
    diminishers = db.get_diminishers()

    words = re.findall(r"[A-Za-z]+|[^\w\s]", text)
    tokens_lower = [w.lower() for w in words]
    n = len(tokens_lower)

    positive_hits = []
    negative_hits = []
    negations_detected = []
    intensifiers_detected = []
    
    total_score = 0.0
    matched_count = 0

    # 1. Emoji checks from Supabase sentiment lexicon
    for char, score in emoji_sentiment.items():
        if char in text:
            total_score += score
            matched_count += 1
            if score > 0:
                positive_hits.append(f"{char} (+{score})")
            else:
                negative_hits.append(f"{char} ({score})")

    # 2. Token keyword analysis with contextual window
    i = 0
    while i < n:
        # Check two-word phrases first (e.g. "third class", "dimag kharab")
        phrase2 = " ".join(tokens_lower[i:i+2]) if i + 1 < n else ""
        word = tokens_lower[i]
        
        target = None
        base_score = 0.0
        advance = 1

        if phrase2 in positive_lexicon:
            target = phrase2
            base_score = positive_lexicon[phrase2]
            advance = 2
        elif phrase2 in negative_lexicon:
            target = phrase2
            base_score = negative_lexicon[phrase2]
            advance = 2
        elif word in positive_lexicon:
            target = word
            base_score = positive_lexicon[word]
        elif word in negative_lexicon:
            target = word
            base_score = negative_lexicon[word]

        if target:
            # Check context window of 3 preceding words for intensifiers and negations
            window_start = max(0, i - 3)
            preceding_window = tokens_lower[window_start:i]
            
            # Also check immediate next word for post-positioned negation (e.g., "accha nahi hai")
            following_negation = False
            if i + advance < n and tokens_lower[i + advance] in negators:
                following_negation = True

            # Determine multiplier
            multiplier = 1.0
            for w in preceding_window:
                if w in intensifiers:
                    multiplier *= intensifiers[w]
                    intensifiers_detected.append(w)
                elif w in diminishers:
                    multiplier *= diminishers[w]

            # Determine negation
            is_negated = any(w in negators for w in preceding_window) or following_negation
            if is_negated:
                neg_word = [w for w in preceding_window if w in negators] or ["nahi/not"]
                negations_detected.append(f"{neg_word[0]} + {target}")
                # Invert polarity
                effective_score = -0.75 * base_score * multiplier
            else:
                effective_score = base_score * multiplier

            total_score += effective_score
            matched_count += 1

            if effective_score > 0:
                positive_hits.append(f"{target} (+{effective_score:.2f})")
            elif effective_score < 0:
                negative_hits.append(f"{target} ({effective_score:.2f})")

            i += advance
        else:
            i += 1

    # Normalize score between -1.0 and 1.0
    if matched_count > 0:
        normalized_score = max(-1.0, min(1.0, total_score / (matched_count ** 0.5)))
    else:
        normalized_score = 0.0

    # Categorize sentiment
    if normalized_score > 0.15:
        sentiment = "Positive"
        badge = "🟢 Positive"
    elif normalized_score < -0.15:
        sentiment = "Negative"
        badge = "🔴 Negative"
    else:
        sentiment = "Neutral"
        badge = "⚪ Neutral"

    # Construct human readable justification
    reasons = []
    if positive_hits:
        reasons.append(f"Positive signals: {', '.join(positive_hits)}")
    if negative_hits:
        reasons.append(f"Negative signals: {', '.join(negative_hits)}")
    if intensifiers_detected:
        reasons.append(f"Intensifiers: {', '.join(set(intensifiers_detected))}")
    if negations_detected:
        reasons.append(f"Negation inversions: {', '.join(negations_detected)}")
    if not reasons:
        reasons.append("No strong positive or negative keywords detected; objective/factual tone.")

    return {
        "sentiment": sentiment,
        "badge": badge,
        "polarity_score": round(normalized_score, 2),
        "positive_keywords": positive_hits,
        "negative_keywords": negative_hits,
        "negations": negations_detected,
        "intensifiers": list(set(intensifiers_detected)),
        "explanation": " | ".join(reasons)
    }
