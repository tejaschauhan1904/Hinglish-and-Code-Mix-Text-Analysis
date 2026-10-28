import re
import os
import csv

# Positive keywords with base polarity weights
POSITIVE_LEXICON = {
    # Hindi / Hinglish
    "mast": 0.85, "badhiya": 0.85, "badiya": 0.85, "shandar": 0.9, "kamaal": 0.9,
    "accha": 0.75, "acchi": 0.75, "acche": 0.75, "achha": 0.75, "achhi": 0.75, "acha": 0.75,
    "lajawab": 0.9, "swadisht": 0.85, "sundar": 0.8, "khush": 0.85, "khushi": 0.8,
    "shaant": 0.7, "zabardast": 0.9, "maza": 0.85, "chill": 0.7, "energetic": 0.8,
    "fresh": 0.75, "pyaar": 0.85, "pasand": 0.75, "sahi": 0.65, "faadu": 0.9,
    "dhansu": 0.85, "gazab": 0.85, "sukoon": 0.8, "masti": 0.75, "raahat": 0.7,
    "tareef": 0.75, "jeet": 0.8, "asli": 0.6, "soothing": 0.75, "vibes": 0.5,
    # English
    "good": 0.7, "great": 0.85, "awesome": 0.9, "nice": 0.7, "love": 0.85,
    "happy": 0.85, "excellent": 0.9, "satisfied": 0.8, "clear": 0.6, "fast": 0.5,
    "polite": 0.7, "smooth": 0.7, "grand": 0.75, "colourful": 0.65, "best": 0.9,
    "brilliant": 0.85, "fun": 0.75, "enjoy": 0.8, "fantastic": 0.9, "amazing": 0.9,
    "wonderful": 0.9, "perfect": 0.9, "clean": 0.6, "friendly": 0.75, "glad": 0.75,
    "cool": 0.7, "superb": 0.9, "sweet": 0.7, "delicious": 0.85
}

# Negative keywords with base polarity weights (negative values)
NEGATIVE_LEXICON = {
    # Hindi / Hinglish
    "boring": -0.8, "bekaar": -0.85, "bekar": -0.85, "kharab": -0.8, "faltu": -0.85,
    "gussa": -0.85, "bura": -0.8, "buri": -0.8, "bure": -0.8, "thanda": -0.5,
    "mushkil": -0.65, "ganda": -0.75, "bakwas": -0.9, "ghatiya": -0.9, "pareshan": -0.8,
    "dukh": -0.8, "sad": -0.75, "tension": -0.7, "scam": -0.9, "puncture": -0.6,
    "jhooth": -0.8, "lut": -0.85, "barbaad": -0.9, "dard": -0.75, "beemar": -0.7,
    "dhokha": -0.9, "tang": -0.7, "third class": -0.9, "slow": -0.55, "drain": -0.6,
    # English
    "bad": -0.75, "terrible": -0.9, "horrible": -0.95, "irritating": -0.8, "annoying": -0.75,
    "rude": -0.85, "unprofessional": -0.85, "useless": -0.85, "fail": -0.85, "tough": -0.6,
    "waste": -0.75, "damaged": -0.8, "crash": -0.7, "late": -0.5, "hate": -0.85,
    "ugly": -0.7, "poor": -0.75, "problem": -0.6, "worst": -0.95, "broken": -0.75,
    "delay": -0.55, "loss": -0.7, "weak": -0.6, "dirty": -0.7, "mess": -0.65, "fault": -0.6
}

NEGATORS = {
    "nahi", "nahin", "nhi", "na", "mat", "not", "never", "no", "neither", "nor", "bina"
}

INTENSIFIERS = {
    "bahut": 1.6, "bohot": 1.6, "ekdum": 1.5, "bilkul": 1.5, "zyada": 1.4,
    "super": 1.5, "very": 1.6, "too": 1.4, "extremely": 1.8, "so": 1.3,
    "itna": 1.3, "itni": 1.3, "really": 1.4, "huge": 1.3, "completely": 1.5
}

DIMINISHERS = {
    "thoda": 0.6, "thodi": 0.6, "thode": 0.6, "kam": 0.6, "slightly": 0.6,
    "little": 0.6, "bit": 0.6, "somewhat": 0.7
}

# Basic emojis
EMOJI_SENTIMENT = {
    "😊": 0.7, "😃": 0.8, "🔥": 0.8, "❤️": 0.9, "👍": 0.7, "✨": 0.6, "🎉": 0.8,
    "😢": -0.7, "😭": -0.8, "😡": -0.9, "💔": -0.85, "👎": -0.7, "🤮": -0.9, "😞": -0.7
}

def analyze_sentiment(text):
    """
    Keyword-based sentiment analysis for Hinglish and English text.
    Uses polarity lexicons, negation inversion, and intensifier/diminisher scaling.
    No external libraries or API keys required.
    """
    words = re.findall(r"[A-Za-z]+|[^\w\s]", text)
    tokens_lower = [w.lower() for w in words]
    n = len(tokens_lower)

    positive_hits = []
    negative_hits = []
    negations_detected = []
    intensifiers_detected = []
    
    total_score = 0.0
    matched_count = 0

    # 1. Emoji checks
    for char, score in EMOJI_SENTIMENT.items():
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

        if phrase2 in POSITIVE_LEXICON:
            target = phrase2
            base_score = POSITIVE_LEXICON[phrase2]
            advance = 2
        elif phrase2 in NEGATIVE_LEXICON:
            target = phrase2
            base_score = NEGATIVE_LEXICON[phrase2]
            advance = 2
        elif word in POSITIVE_LEXICON:
            target = word
            base_score = POSITIVE_LEXICON[word]
        elif word in NEGATIVE_LEXICON:
            target = word
            base_score = NEGATIVE_LEXICON[word]

        if target:
            # Check context window of 3 preceding words for intensifiers and negations
            window_start = max(0, i - 3)
            preceding_window = tokens_lower[window_start:i]
            
            # Also check immediate next word for post-positioned negation (e.g., "accha nahi hai")
            following_negation = False
            if i + advance < n and tokens_lower[i + advance] in NEGATORS:
                following_negation = True

            # Determine multiplier
            multiplier = 1.0
            for w in preceding_window:
                if w in INTENSIFIERS:
                    multiplier *= INTENSIFIERS[w]
                    intensifiers_detected.append(w)
                elif w in DIMINISHERS:
                    multiplier *= DIMINISHERS[w]

            # Determine negation
            is_negated = any(w in NEGATORS for w in preceding_window) or following_negation
            if is_negated:
                neg_word = [w for w in preceding_window if w in NEGATORS] or ["nahi/not"]
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
