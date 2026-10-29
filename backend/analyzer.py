"""
Hinglish Text Analyzer & Core NLP Orchestrator.
Data Source: Supabase PostgreSQL (via backend.db)
Zero hardcoded word lists, POS tags, or vocabularies in Python code.
"""

import re
try:
    from . import db
    from .ner_engine import extract_named_entities as analyze_ner
    from .sentiment_engine import analyze_sentiment
    from .translation_engine import translate_hinglish_to_english
except (ImportError, ValueError):
    import db
    from ner_engine import extract_named_entities as analyze_ner
    from sentiment_engine import analyze_sentiment
    from translation_engine import translate_hinglish_to_english

def tokenize(text):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?|[^\w\s]", text)

def classify_language(word):
    """Classifies token language based on Supabase database vocabulary."""
    w = word.lower()
    hindi_words = db.get_hindi_words()
    english_words = db.get_english_words()

    if w in hindi_words and w in english_words:
        return "English/Common"
    if w in hindi_words:
        return "Hindi"
    if w in english_words:
        return "English"
    if re.fullmatch(r"\d+(?:\.\d+)?", w):
        return "Number"
    if re.fullmatch(r"[^\w\s]", w):
        return "Punctuation"
    return "Unknown"

def guess_pos(word, language):
    """Assigns part-of-speech tag using Supabase DB POS lexicon and morphological heuristics."""
    w = word.lower()
    pos_lexicon = db.get_pos_lexicon()

    if w in pos_lexicon:
        return pos_lexicon[w]

    if re.fullmatch(r"\d+(?:\.\d+)?", w):
        return "NUM"
    if re.fullmatch(r"[^\w\s]", w):
        return "PUNCT"

    # Morphological heuristics for unseen words
    if language == "Hindi":
        if w.endswith(("na", "ne", "ni", "ta", "ti", "te", "kar", "gaya", "gayi")):
            return "VERB"
        if w.endswith(("wala", "wali", "wale")):
            return "NOUN"

    # Basic English morphology
    if w.endswith(("ing", "ed")):
        return "VERB"
    if w.endswith(("ly",)):
        return "ADV"
    if w.endswith(("ous", "ful", "able", "ive", "al")):
        return "ADJ"

    return "NOUN" if language in ("Hindi", "English", "English/Common") else "X"

def analyze_text(text):
    """
    Performs comprehensive multi-task NLP analysis on Roman-script Hinglish text:
    1. Tokenization & Supabase-backed Language Identification
    2. Rule & Database-based POS Tagging
    3. Named Entity Recognition (NER)
    4. Sentiment Analysis with Negation & Intensifier Resolution
    5. Context-aware Hinglish-to-English Translation
    """
    raw_tokens = tokenize(text)
    tokens = []

    for word in raw_tokens:
        language = classify_language(word)
        pos = guess_pos(word, language)
        tokens.append({
            "Token": word,
            "Language": language,
            "POS Tag": pos
        })

    word_rows = [r for r in tokens if r["Language"] not in ("Punctuation",)]
    total = len(word_rows)

    hindi = sum(r["Language"] == "Hindi" for r in word_rows)
    english = sum(r["Language"] in ("English", "English/Common") for r in word_rows)
    other = total - hindi - english

    if hindi > 0 and english > 0:
        sentence_type = "Hinglish / Code-Mixed"
    elif hindi > 0:
        sentence_type = "Mostly Hindi"
    elif english > 0:
        sentence_type = "Mostly English"
    else:
        sentence_type = "Unknown / Other"

    hp = (hindi / total * 100) if total else 0
    ep = (english / total * 100) if total else 0

    summary = (
        f"The text contains {hindi} Hindi word(s) and {english} English word(s). "
        f"It is classified as **{sentence_type}**. "
        f"The analyzer uses tokenization, a Supabase DB lexicon, and rule-based POS tagging."
    )

    ner_result = analyze_ner(text)
    sentiment_result = analyze_sentiment(text)
    translation_result = translate_hinglish_to_english(text)

    return {
        "tokens": tokens,
        "total_words": total,
        "hindi_count": hindi,
        "english_count": english,
        "other_count": other,
        "hindi_percentage": hp,
        "english_percentage": ep,
        "sentence_type": sentence_type,
        "summary": summary,
        "ner": ner_result,
        "sentiment": sentiment_result,
        "translation": translation_result
    }
