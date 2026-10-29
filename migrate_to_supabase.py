"""
Migration Script: Extract all data from Python code and CSV files,
create all required tables in Supabase PostgreSQL, and insert all data.
"""

import os
import sys
import json
import csv
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Ensure root and backend directory are in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Load environment variables
load_dotenv(os.path.join(BASE_DIR, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file!")

# Import data directly from existing code
import translation_engine
import sentiment_engine
import ner_engine
import analyzer

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

CREATE_TABLES_SQL = """
-- 1. Datasets: NER Dataset
CREATE TABLE IF NOT EXISTS datasets_ner (
    id SERIAL PRIMARY KEY,
    sentence_id INT,
    text TEXT NOT NULL,
    entities JSONB NOT NULL,
    entity_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Datasets: Sentiment Dataset
CREATE TABLE IF NOT EXISTS datasets_sentiment (
    id SERIAL PRIMARY KEY,
    sentence_id INT,
    text TEXT NOT NULL,
    sentiment VARCHAR(50) NOT NULL,
    polarity DOUBLE PRECISION NOT NULL,
    sentiment_keywords TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Datasets: Translation Dataset
CREATE TABLE IF NOT EXISTS datasets_translation (
    id SERIAL PRIMARY KEY,
    sentence_id INT,
    hinglish_text TEXT NOT NULL,
    english_translation TEXT NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Datasets: Sample Hinglish Corpus
CREATE TABLE IF NOT EXISTS datasets_sample (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    label VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. NLP Vocabulary (Language Identification)
CREATE TABLE IF NOT EXISTS nlp_vocabulary (
    id SERIAL PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    language VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_nlp_vocab UNIQUE (word, language)
);

-- 6. NLP POS Lexicon (Part of Speech tags)
CREATE TABLE IF NOT EXISTS nlp_pos_lexicon (
    id SERIAL PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    pos_tag VARCHAR(20) NOT NULL,
    language VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. NLP Sentiment Lexicon (Polarity keywords and emojis)
CREATE TABLE IF NOT EXISTS nlp_sentiment_lexicon (
    id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL UNIQUE,
    polarity_score DOUBLE PRECISION NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. NLP Sentiment Modifiers (Negators, Intensifiers, Diminishers)
CREATE TABLE IF NOT EXISTS nlp_sentiment_modifiers (
    id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL,
    modifier_type VARCHAR(50) NOT NULL,
    weight DOUBLE PRECISION DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_sent_modifier UNIQUE (term, modifier_type)
);

-- 9. NLP Entities Gazetteer (NER Entities)
CREATE TABLE IF NOT EXISTS nlp_entities_gazetteer (
    id SERIAL PRIMARY KEY,
    entity_text VARCHAR(200) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_entity_entry UNIQUE (entity_text, entity_type)
);

-- 10. NLP Temporal Indicators (Temporal keywords, past and future indicators)
CREATE TABLE IF NOT EXISTS nlp_temporal_indicators (
    id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL,
    indicator_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_temp_indicator UNIQUE (term, indicator_type)
);

-- 11. NLP Phrase Translations (Multi-word phrase replacements)
CREATE TABLE IF NOT EXISTS nlp_phrase_translations (
    id SERIAL PRIMARY KEY,
    phrase VARCHAR(255) NOT NULL UNIQUE,
    translation TEXT NOT NULL,
    phrase_length INT NOT NULL,
    priority INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. NLP Word Translations (Lexicon word-level translations)
CREATE TABLE IF NOT EXISTS nlp_word_translations (
    id SERIAL PRIMARY KEY,
    source_word VARCHAR(100) NOT NULL UNIQUE,
    target_translation TEXT NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. NLP Preset Examples (Examples for UI & Testing)
CREATE TABLE IF NOT EXISTS nlp_preset_examples (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL UNIQUE,
    text TEXT NOT NULL,
    feature VARCHAR(100),
    display_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Grant full permissions to standard roles
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;
"""

def create_tables(conn):
    print("Creating tables in Supabase PostgreSQL...")
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLES_SQL)
    conn.commit()
    print("Tables created successfully.")

def seed_datasets(conn):
    print("Seeding datasets from CSV files into database...")
    data_dir = os.path.join(BASE_DIR, "data")
    
    with conn.cursor() as cur:
        # 1. NER Dataset
        ner_path = os.path.join(data_dir, "hinglish_ner_dataset.csv")
        if os.path.exists(ner_path):
            with open(ner_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                ner_rows = []
                for row in reader:
                    # Parse entities string safely to json
                    raw_ent = row.get("entities", "[]")
                    try:
                        import ast
                        parsed_ent = json.dumps(ast.literal_eval(raw_ent))
                    except Exception:
                        parsed_ent = json.dumps([])
                    ner_rows.append((
                        int(row["sentence_id"]),
                        row["text"],
                        parsed_ent,
                        row.get("entity_summary", "")
                    ))
                execute_values(cur, """
                    INSERT INTO datasets_ner (sentence_id, text, entities, entity_summary)
                    VALUES %s
                """, ner_rows)
            print(f"  Inserted {len(ner_rows)} rows into datasets_ner")

        # 2. Sentiment Dataset
        sentiment_path = os.path.join(data_dir, "hinglish_sentiment_dataset.csv")
        if os.path.exists(sentiment_path):
            with open(sentiment_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                sent_rows = [
                    (
                        int(row["sentence_id"]),
                        row["text"],
                        row["sentiment"],
                        float(row["polarity"]),
                        row.get("sentiment_keywords", "")
                    )
                    for row in reader
                ]
                execute_values(cur, """
                    INSERT INTO datasets_sentiment (sentence_id, text, sentiment, polarity, sentiment_keywords)
                    VALUES %s
                """, sent_rows)
            print(f"  Inserted {len(sent_rows)} rows into datasets_sentiment")

        # 3. Translation Dataset
        trans_path = os.path.join(data_dir, "hinglish_translation_dataset.csv")
        if os.path.exists(trans_path):
            with open(trans_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                trans_rows = [
                    (
                        int(row["sentence_id"]),
                        row["hinglish_text"],
                        row["english_translation"],
                        row.get("category", "general")
                    )
                    for row in reader
                ]
                execute_values(cur, """
                    INSERT INTO datasets_translation (sentence_id, hinglish_text, english_translation, category)
                    VALUES %s
                """, trans_rows)
            print(f"  Inserted {len(trans_rows)} rows into datasets_translation")

        # 4. Sample Hinglish Corpus
        sample_path = os.path.join(data_dir, "sample_hinglish.csv")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                sample_rows = [
                    (
                        row["text"],
                        row["label"],
                        row.get("category", "general")
                    )
                    for row in reader
                ]
                execute_values(cur, """
                    INSERT INTO datasets_sample (text, label, category)
                    VALUES %s
                """, sample_rows)
            print(f"  Inserted {len(sample_rows)} rows into datasets_sample")

    conn.commit()

def seed_nlp_code_data(conn):
    print("Seeding NLP Lexicons, Rules, and Gazetteers from code...")
    with conn.cursor() as cur:
        # 5. nlp_vocabulary (Hindi and English words)
        vocab_rows = []
        for w in analyzer.HINDI_WORDS:
            vocab_rows.append((w.lower().strip(), "Hindi"))
        for w in analyzer.ENGLISH_WORDS:
            vocab_rows.append((w.lower().strip(), "English"))
        execute_values(cur, """
            INSERT INTO nlp_vocabulary (word, language)
            VALUES %s
            ON CONFLICT (word, language) DO NOTHING
        """, vocab_rows)
        print(f"  Inserted {len(vocab_rows)} vocabulary words into nlp_vocabulary")

        # 6. nlp_pos_lexicon
        pos_rows = []
        for word, tag in analyzer.POS_LEXICON.items():
            lang = "Hindi" if word in analyzer.HINDI_WORDS else "English"
            pos_rows.append((word.lower().strip(), tag, lang))
        execute_values(cur, """
            INSERT INTO nlp_pos_lexicon (word, pos_tag, language)
            VALUES %s
            ON CONFLICT (word) DO UPDATE SET pos_tag = EXCLUDED.pos_tag, language = EXCLUDED.language
        """, pos_rows)
        print(f"  Inserted {len(pos_rows)} POS tags into nlp_pos_lexicon")

        # 7. nlp_sentiment_lexicon (Positive, Negative, Emoji)
        sent_rows = []
        for term, score in sentiment_engine.POSITIVE_LEXICON.items():
            sent_rows.append((term.lower().strip(), float(score), "positive"))
        for term, score in sentiment_engine.NEGATIVE_LEXICON.items():
            sent_rows.append((term.lower().strip(), float(score), "negative"))
        for emoji, score in sentiment_engine.EMOJI_SENTIMENT.items():
            sent_rows.append((emoji, float(score), "emoji"))
        execute_values(cur, """
            INSERT INTO nlp_sentiment_lexicon (term, polarity_score, category)
            VALUES %s
            ON CONFLICT (term) DO UPDATE SET polarity_score = EXCLUDED.polarity_score, category = EXCLUDED.category
        """, sent_rows)
        print(f"  Inserted {len(sent_rows)} sentiment terms into nlp_sentiment_lexicon")

        # 8. nlp_sentiment_modifiers (Negators, Intensifiers, Diminishers)
        modifier_rows = []
        for neg in sentiment_engine.NEGATORS:
            modifier_rows.append((neg.lower().strip(), "negator", 0.0))
        for inte, weight in sentiment_engine.INTENSIFIERS.items():
            modifier_rows.append((inte.lower().strip(), "intensifier", float(weight)))
        for dim, weight in sentiment_engine.DIMINISHERS.items():
            modifier_rows.append((dim.lower().strip(), "diminisher", float(weight)))
        execute_values(cur, """
            INSERT INTO nlp_sentiment_modifiers (term, modifier_type, weight)
            VALUES %s
            ON CONFLICT (term, modifier_type) DO UPDATE SET weight = EXCLUDED.weight
        """, modifier_rows)
        print(f"  Inserted {len(modifier_rows)} modifiers into nlp_sentiment_modifiers")

        # 9. nlp_entities_gazetteer (PERSONS, LOCATIONS, ORGANIZATIONS, FACILITIES, EVENTS)
        gaz_rows = []
        for p in ner_engine.PERSONS:
            gaz_rows.append((p.lower().strip(), "PERSON", "Person name"))
        for loc in ner_engine.LOCATIONS:
            gaz_rows.append((loc.lower().strip(), "LOCATION", "Geographical location"))
        for org in ner_engine.ORGANIZATIONS:
            gaz_rows.append((org.lower().strip(), "ORGANIZATION", "Organization / Brand / Institute"))
        for fac in ner_engine.FACILITIES:
            gaz_rows.append((fac.lower().strip(), "FACILITY", "Facility / Venue"))
        for ev in ner_engine.EVENTS:
            gaz_rows.append((ev.lower().strip(), "EVENT", "Event / Festival"))
        execute_values(cur, """
            INSERT INTO nlp_entities_gazetteer (entity_text, entity_type, description)
            VALUES %s
            ON CONFLICT (entity_text, entity_type) DO NOTHING
        """, gaz_rows)
        print(f"  Inserted {len(gaz_rows)} entities into nlp_entities_gazetteer")

        # 10. nlp_temporal_indicators (TEMPORAL_KEYWORDS, PAST_INDICATORS, FUTURE_INDICATORS)
        temp_rows = []
        for tk in ner_engine.TEMPORAL_KEYWORDS:
            temp_rows.append((tk.lower().strip(), "temporal_keyword"))
        for pi in ner_engine.PAST_INDICATORS:
            temp_rows.append((pi.lower().strip(), "past_indicator"))
        for fi in ner_engine.FUTURE_INDICATORS:
            temp_rows.append((fi.lower().strip(), "future_indicator"))
        execute_values(cur, """
            INSERT INTO nlp_temporal_indicators (term, indicator_type)
            VALUES %s
            ON CONFLICT (term, indicator_type) DO NOTHING
        """, temp_rows)
        print(f"  Inserted {len(temp_rows)} temporal indicators into nlp_temporal_indicators")

        # 11. nlp_phrase_translations
        phrase_rows = []
        for idx, (phrase, trans) in enumerate(translation_engine.PHRASE_TRANSLATIONS):
            phrase_rows.append((
                phrase.lower().strip(),
                trans.strip(),
                len(phrase.strip().split()),
                len(translation_engine.PHRASE_TRANSLATIONS) - idx
            ))
        execute_values(cur, """
            INSERT INTO nlp_phrase_translations (phrase, translation, phrase_length, priority)
            VALUES %s
            ON CONFLICT (phrase) DO UPDATE SET translation = EXCLUDED.translation,
                                            phrase_length = EXCLUDED.phrase_length,
                                            priority = EXCLUDED.priority
        """, phrase_rows)
        print(f"  Inserted {len(phrase_rows)} phrase translations into nlp_phrase_translations")

        # 12. nlp_word_translations
        word_trans_rows = []
        for src, tgt in translation_engine.WORD_TRANSLATIONS.items():
            word_trans_rows.append((src.lower().strip(), tgt.strip(), "lexicon"))
        execute_values(cur, """
            INSERT INTO nlp_word_translations (source_word, target_translation, category)
            VALUES %s
            ON CONFLICT (source_word) DO UPDATE SET target_translation = EXCLUDED.target_translation
        """, word_trans_rows)
        print(f"  Inserted {len(word_trans_rows)} word translations into nlp_word_translations")

        # 13. nlp_preset_examples
        preset_examples = [
            ("Hinglish Code-Mix", "Mujhe kal college jaana hai bro", "all", 1),
            ("NER (Person + City + Office)", "Rahul kal Delhi office jayega", "ner", 2),
            ("Negative Sentiment", "Yaar aaj ka lecture bahut boring tha", "sentiment", 3),
            ("Positive Sentiment", "Ye movie sach me bahut acchi thi", "sentiment", 4),
            ("Negated Sentiment", "Khana bilkul accha nahi tha aur staff rude tha", "sentiment", 5),
            ("Multi-Entity & Translation", "Kal subah 9 baje meeting hai TCS ke office me", "all", 6),
            ("Casual Chat Translation", "Mera laptop slow hai but theek ho jayega", "translation", 7)
        ]
        execute_values(cur, """
            INSERT INTO nlp_preset_examples (title, text, feature, display_order)
            VALUES %s
            ON CONFLICT (title) DO UPDATE SET text = EXCLUDED.text, feature = EXCLUDED.feature, display_order = EXCLUDED.display_order
        """, preset_examples)
        print(f"  Inserted {len(preset_examples)} preset examples into nlp_preset_examples")

    conn.commit()

def verify_all_tables(conn):
    print("\n" + "="*60)
    print("VERIFYING DATABASE TABLES AND COUNTS IN SUPABASE:")
    print("="*60)
    tables = [
        "datasets_ner",
        "datasets_sentiment",
        "datasets_translation",
        "datasets_sample",
        "nlp_vocabulary",
        "nlp_pos_lexicon",
        "nlp_sentiment_lexicon",
        "nlp_sentiment_modifiers",
        "nlp_entities_gazetteer",
        "nlp_temporal_indicators",
        "nlp_phrase_translations",
        "nlp_word_translations",
        "nlp_preset_examples"
    ]
    with conn.cursor() as cur:
        for t in tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"  Table '{t}': {cnt} records")
    print("="*60 + "\n")

def main():
    print("Connecting to Supabase PostgreSQL...")
    conn = get_connection()
    try:
        create_tables(conn)
        seed_datasets(conn)
        seed_nlp_code_data(conn)
        verify_all_tables(conn)
        print("ALL DATA SUCCESSFULLY SHIFTED TO SUPABASE POSTGRESQL!")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

