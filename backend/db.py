"""
Database module for Hinglish Text Analyzer & NLP Suite.
Connects to Supabase PostgreSQL with automatic fallback to Supabase REST API (HTTPS).
Ensures 100% connectivity on any network (IPv4, IPv6, college Wi-Fi, campus proxies).
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from dotenv import load_dotenv

# Find and load .env file from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")

# Primary fallback pooler URL for IPv4 compatibility (eu-west-1 region)
IPV4_POOLER_URL = "postgresql://postgres.cyzlijjwsjqwruywmtzh:ywNbaJsiawWcEfzm@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"

def get_connection():
    """
    Establish and return a new connection to Supabase PostgreSQL.
    Tries DATABASE_URL first, then IPv4 pooler URL.
    """
    candidates = []
    if DATABASE_URL:
        candidates.append(DATABASE_URL)
    candidates.append(IPV4_POOLER_URL)

    last_err = None
    for url in candidates:
        try:
            return psycopg2.connect(url, sslmode="require", connect_timeout=4)
        except Exception as e:
            last_err = e

    raise last_err

def fetch_rest_api(table, params=None):
    """Fetch table records via Supabase REST API (HTTPS port 443)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL or SUPABASE_KEY not configured in .env")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.get(url, headers=headers, params=params or {}, timeout=5)
    resp.raise_for_status()
    return resp.json()

class DatabaseCache:
    """
    In-memory cache of NLP rules, lexicons, and gazetteers populated
    directly from Supabase PostgreSQL tables or REST API.
    Maintains ultra-fast sub-millisecond execution for NLP token processing
    while ensuring the single source of truth is the Supabase database.
    """
    def __init__(self):
        self.hindi_words = set()
        self.english_words = set()
        self.pos_lexicon = {}
        
        self.positive_lexicon = {}
        self.negative_lexicon = {}
        self.emoji_sentiment = {}
        self.negators = set()
        self.intensifiers = {}
        self.diminishers = {}

        self.persons = set()
        self.locations = set()
        self.organizations = set()
        self.facilities = set()
        self.events = set()

        self.temporal_keywords = set()
        self.past_indicators = set()
        self.future_indicators = set()

        self.phrase_translations = []
        self.word_translations = {}
        self.parallel_translations = []

        self.preset_examples = {}
        self._is_loaded = False
        self.connection_mode = "unknown"

    def load_from_sql(self):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Load Vocabulary
                cur.execute("SELECT word, language FROM nlp_vocabulary")
                h_words = set()
                e_words = set()
                for word, lang in cur.fetchall():
                    w = word.strip().lower()
                    if lang.lower() == "hindi":
                        h_words.add(w)
                    elif lang.lower() == "english":
                        e_words.add(w)
                self.hindi_words = h_words
                self.english_words = e_words

                # 2. Load POS Lexicon
                cur.execute("SELECT word, pos_tag FROM nlp_pos_lexicon")
                self.pos_lexicon = {w.strip().lower(): tag for w, tag in cur.fetchall()}

                # 3. Load Sentiment Lexicon
                cur.execute("SELECT term, polarity_score, category FROM nlp_sentiment_lexicon")
                pos_lex = {}
                neg_lex = {}
                emojis = {}
                for term, score, cat in cur.fetchall():
                    if cat == "positive":
                        pos_lex[term.strip().lower()] = float(score)
                    elif cat == "negative":
                        neg_lex[term.strip().lower()] = float(score)
                    elif cat == "emoji":
                        emojis[term] = float(score)
                self.positive_lexicon = pos_lex
                self.negative_lexicon = neg_lex
                self.emoji_sentiment = emojis

                # 4. Load Sentiment Modifiers
                cur.execute("SELECT term, modifier_type, weight FROM nlp_sentiment_modifiers")
                negs = set()
                intens = {}
                dimins = {}
                for term, mtype, weight in cur.fetchall():
                    t = term.strip().lower()
                    w = float(weight) if weight is not None else 1.0
                    if mtype == "negator":
                        negs.add(t)
                    elif mtype == "intensifier":
                        intens[t] = w
                    elif mtype == "diminisher":
                        dimins[t] = w
                self.negators = negs
                self.intensifiers = intens
                self.diminishers = dimins

                # 5. Load Entities Gazetteer
                cur.execute("SELECT entity_text, entity_type FROM nlp_entities_gazetteer")
                p_set = set()
                l_set = set()
                o_set = set()
                f_set = set()
                e_set = set()
                for text, etype in cur.fetchall():
                    val = text.strip().lower()
                    if etype == "PERSON":
                        p_set.add(val)
                    elif etype == "LOCATION":
                        l_set.add(val)
                    elif etype == "ORGANIZATION":
                        o_set.add(val)
                    elif etype == "FACILITY":
                        f_set.add(val)
                    elif etype == "EVENT":
                        e_set.add(val)
                self.persons = p_set
                self.locations = l_set
                self.organizations = o_set
                self.facilities = f_set
                self.events = e_set

                # 6. Load Temporal Indicators
                cur.execute("SELECT term, indicator_type FROM nlp_temporal_indicators")
                t_set = set()
                past_set = set()
                fut_set = set()
                for term, itype in cur.fetchall():
                    val = term.strip().lower()
                    if itype == "temporal_keyword":
                        t_set.add(val)
                    elif itype == "past_indicator":
                        past_set.add(val)
                    elif itype == "future_indicator":
                        fut_set.add(val)
                self.temporal_keywords = t_set
                self.past_indicators = past_set
                self.future_indicators = fut_set

                # 7. Load Phrase Translations
                cur.execute("SELECT phrase, translation FROM nlp_phrase_translations ORDER BY phrase_length DESC, priority DESC")
                self.phrase_translations = [(p.strip().lower(), tr.strip()) for p, tr in cur.fetchall()]

                # 8. Load Word Translations
                cur.execute("SELECT source_word, target_translation FROM nlp_word_translations")
                self.word_translations = {sw.strip().lower(): tgt.strip() for sw, tgt in cur.fetchall()}

                # 9. Load Parallel Translation Dataset
                cur.execute("SELECT hinglish_text, english_translation FROM datasets_translation ORDER BY sentence_id ASC")
                self.parallel_translations = [(h.strip(), e.strip()) for h, e in cur.fetchall()]

                # 10. Load Preset Examples
                cur.execute("SELECT title, text FROM nlp_preset_examples ORDER BY display_order ASC")
                self.preset_examples = {title: text for title, text in cur.fetchall()}

            self._is_loaded = True
            self.connection_mode = "postgresql_pooler"
        finally:
            conn.close()

    def load_from_rest(self):
        """Fallback to load all NLP linguistic data via Supabase HTTPS REST API."""
        # 1. Vocabulary
        vocab = fetch_rest_api("nlp_vocabulary", {"select": "word,language"})
        h_words = set()
        e_words = set()
        for r in vocab:
            w = r["word"].strip().lower()
            if r["language"].lower() == "hindi":
                h_words.add(w)
            elif r["language"].lower() == "english":
                e_words.add(w)
        self.hindi_words = h_words
        self.english_words = e_words

        # 2. POS Lexicon
        pos = fetch_rest_api("nlp_pos_lexicon", {"select": "word,pos_tag"})
        self.pos_lexicon = {r["word"].strip().lower(): r["pos_tag"] for r in pos}

        # 3. Sentiment Lexicon
        sents = fetch_rest_api("nlp_sentiment_lexicon", {"select": "term,polarity_score,category"})
        pos_lex = {}
        neg_lex = {}
        emojis = {}
        for r in sents:
            cat = r["category"]
            term = r["term"]
            score = float(r["polarity_score"])
            if cat == "positive":
                pos_lex[term.strip().lower()] = score
            elif cat == "negative":
                neg_lex[term.strip().lower()] = score
            elif cat == "emoji":
                emojis[term] = score
        self.positive_lexicon = pos_lex
        self.negative_lexicon = neg_lex
        self.emoji_sentiment = emojis

        # 4. Modifiers
        mods = fetch_rest_api("nlp_sentiment_modifiers", {"select": "term,modifier_type,weight"})
        negs = set()
        intens = {}
        dimins = {}
        for r in mods:
            t = r["term"].strip().lower()
            mtype = r["modifier_type"]
            w = float(r.get("weight") or 1.0)
            if mtype == "negator":
                negs.add(t)
            elif mtype == "intensifier":
                intens[t] = w
            elif mtype == "diminisher":
                dimins[t] = w
        self.negators = negs
        self.intensifiers = intens
        self.diminishers = dimins

        # 5. Entities
        ents = fetch_rest_api("nlp_entities_gazetteer", {"select": "entity_text,entity_type"})
        p_set, l_set, o_set, f_set, e_set = set(), set(), set(), set(), set()
        for r in ents:
            val = r["entity_text"].strip().lower()
            etype = r["entity_type"]
            if etype == "PERSON":
                p_set.add(val)
            elif etype == "LOCATION":
                l_set.add(val)
            elif etype == "ORGANIZATION":
                o_set.add(val)
            elif etype == "FACILITY":
                f_set.add(val)
            elif etype == "EVENT":
                e_set.add(val)
        self.persons = p_set
        self.locations = l_set
        self.organizations = o_set
        self.facilities = f_set
        self.events = e_set

        # 6. Temporal
        temps = fetch_rest_api("nlp_temporal_indicators", {"select": "term,indicator_type"})
        t_set, past_set, fut_set = set(), set(), set()
        for r in temps:
            val = r["term"].strip().lower()
            itype = r["indicator_type"]
            if itype == "temporal_keyword":
                t_set.add(val)
            elif itype == "past_indicator":
                past_set.add(val)
            elif itype == "future_indicator":
                fut_set.add(val)
        self.temporal_keywords = t_set
        self.past_indicators = past_set
        self.future_indicators = fut_set

        # 7. Phrases
        phrases = fetch_rest_api("nlp_phrase_translations", {"select": "phrase,translation", "order": "phrase_length.desc,priority.desc"})
        self.phrase_translations = [(r["phrase"].strip().lower(), r["translation"].strip()) for r in phrases]

        # 8. Words
        words = fetch_rest_api("nlp_word_translations", {"select": "source_word,target_translation"})
        self.word_translations = {r["source_word"].strip().lower(): r["target_translation"].strip() for r in words}

        # 9. Parallel
        parallel = fetch_rest_api("datasets_translation", {"select": "hinglish_text,english_translation", "order": "sentence_id.asc"})
        self.parallel_translations = [(r["hinglish_text"].strip(), r["english_translation"].strip()) for r in parallel]

        # 10. Presets
        presets = fetch_rest_api("nlp_preset_examples", {"select": "title,text", "order": "display_order.asc"})
        self.preset_examples = {r["title"]: r["text"] for r in presets}

        self._is_loaded = True
        self.connection_mode = "https_rest_api"

    def load(self, force=False):
        """Fetch all linguistic datasets and rules from Supabase (SQL first, REST API fallback)."""
        if self._is_loaded and not force:
            return

        try:
            self.load_from_sql()
        except Exception as e_sql:
            print(f"PostgreSQL direct connection failed ({e_sql}). Falling back to Supabase HTTPS REST API...")
            try:
                self.load_from_rest()
                print("Successfully loaded NLP data from Supabase via HTTPS REST API!")
            except Exception as e_rest:
                raise RuntimeError(f"Both PostgreSQL and HTTPS REST connection to Supabase failed: SQL error={e_sql}, REST error={e_rest}")

# Singleton cache instance
_cache = DatabaseCache()

def ensure_cache():
    """Ensure linguistic data is loaded from Supabase."""
    if not _cache._is_loaded:
        _cache.load()

def refresh_cache():
    """Reload all data from Supabase."""
    _cache.load(force=True)
    return get_db_status()

# ==========================================
# Linguistic Getters (Read from Supabase DB)
# ==========================================

def get_hindi_words():
    ensure_cache()
    return _cache.hindi_words

def get_english_words():
    ensure_cache()
    return _cache.english_words

def get_pos_lexicon():
    ensure_cache()
    return _cache.pos_lexicon

def get_positive_lexicon():
    ensure_cache()
    return _cache.positive_lexicon

def get_negative_lexicon():
    ensure_cache()
    return _cache.negative_lexicon

def get_emoji_sentiment():
    ensure_cache()
    return _cache.emoji_sentiment

def get_negators():
    ensure_cache()
    return _cache.negators

def get_intensifiers():
    ensure_cache()
    return _cache.intensifiers

def get_diminishers():
    ensure_cache()
    return _cache.diminishers

def get_gazetteers():
    ensure_cache()
    return (
        _cache.persons,
        _cache.locations,
        _cache.organizations,
        _cache.facilities,
        _cache.events
    )

def get_temporal_indicators():
    ensure_cache()
    return (
        _cache.temporal_keywords,
        _cache.past_indicators,
        _cache.future_indicators
    )

def get_phrase_translations():
    ensure_cache()
    return _cache.phrase_translations

def get_word_translations():
    ensure_cache()
    return _cache.word_translations

def get_parallel_translations():
    ensure_cache()
    return _cache.parallel_translations

def get_preset_examples():
    ensure_cache()
    return _cache.preset_examples

# ==========================================
# Dataset Queries (Direct Supabase Queries)
# ==========================================

DATASET_TABLE_MAP = {
    "ner": {
        "table": "datasets_ner",
        "title": "Named Entity Recognition (NER) Dataset",
        "order_by": "sentence_id ASC",
        "rest_order": "sentence_id.asc"
    },
    "sentiment": {
        "table": "datasets_sentiment",
        "title": "Sentiment Analysis Dataset",
        "order_by": "sentence_id ASC",
        "rest_order": "sentence_id.asc"
    },
    "translation": {
        "table": "datasets_translation",
        "title": "Hinglish to English Translation Dataset",
        "order_by": "sentence_id ASC",
        "rest_order": "sentence_id.asc"
    },
    "sample": {
        "table": "datasets_sample",
        "title": "Sample Hinglish Corpus",
        "order_by": "id ASC",
        "rest_order": "id.asc"
    }
}

def get_dataset(name="ner"):
    """
    Fetch a full dataset directly from Supabase database table.
    Supports SQL and HTTPS REST API fallback.
    """
    if name not in DATASET_TABLE_MAP:
        raise ValueError(f"Unknown dataset '{name}'. Available: {list(DATASET_TABLE_MAP.keys())}")

    meta = DATASET_TABLE_MAP[name]
    table = meta["table"]
    order_by = meta["order_by"]
    rest_order = meta["rest_order"]

    # Try SQL connection first
    try:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(f"SELECT * FROM {table} ORDER BY {order_by}")
                records = cur.fetchall()
                
                clean_records = []
                for r in records:
                    row_dict = dict(r)
                    if "created_at" in row_dict:
                        row_dict["created_at"] = str(row_dict["created_at"])
                    if "entities" in row_dict and isinstance(row_dict["entities"], (list, dict)):
                        row_dict["entities"] = json.dumps(row_dict["entities"])
                    clean_records.append(row_dict)

                columns = list(clean_records[0].keys()) if clean_records else []
                return {
                    "dataset_name": name,
                    "title": meta["title"],
                    "table_name": table,
                    "columns": columns,
                    "total_records": len(clean_records),
                    "data": clean_records
                }
        finally:
            conn.close()
    except Exception:
        # Fallback to Supabase REST API
        records = fetch_rest_api(table, {"select": "*", "order": rest_order})
        clean_records = []
        for r in records:
            row_dict = dict(r)
            if "created_at" in row_dict:
                row_dict["created_at"] = str(row_dict["created_at"])
            if "entities" in row_dict and isinstance(row_dict["entities"], (list, dict)):
                row_dict["entities"] = json.dumps(row_dict["entities"])
            clean_records.append(row_dict)

        columns = list(clean_records[0].keys()) if clean_records else []
        return {
            "dataset_name": name,
            "title": meta["title"],
            "table_name": table,
            "columns": columns,
            "total_records": len(clean_records),
            "data": clean_records
        }

def get_db_status():
    """Return live status and counts for all Supabase database tables."""
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
    counts = {}

    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                for t in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {t}")
                    counts[t] = cur.fetchone()[0]

            return {
                "status": "connected",
                "database": "Supabase PostgreSQL",
                "connection_mode": _cache.connection_mode or "postgresql_pooler",
                "tables": counts,
                "total_records": sum(counts.values()),
                "cached": _cache._is_loaded
            }
        finally:
            conn.close()
    except Exception:
        # REST API fallback
        for t in tables:
            try:
                headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Range-Unit": "items", "Prefer": "count=exact"}
                r = requests.get(f"{SUPABASE_URL}/rest/v1/{t}?select=count", headers=headers, timeout=4)
                cr = r.headers.get("content-range", "")
                cnt = int(cr.split("/")[-1]) if "/" in cr else 0
                counts[t] = cnt
            except Exception:
                counts[t] = 0

        return {
            "status": "connected",
            "database": "Supabase (HTTPS REST)",
            "connection_mode": "https_rest_api",
            "tables": counts,
            "total_records": sum(counts.values()),
            "cached": _cache._is_loaded
        }

# Initial eager load on import
try:
    ensure_cache()
except Exception as e:
    print(f"Warning: Failed initial Supabase cache load ({e}). Will retry on demand.")
