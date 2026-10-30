# Hinglish NLP Studio: End-to-End Workflow Diagrams, Architecture & LLM Prompts

This document provides complete, exhaustive workflow diagrams, dataflow breakdowns, database table mappings, and production-grade LLM prompts for generating diagrams across any tool (Mermaid, PlantUML, Graphviz DOT, and ASCII/Unicode).

---

## Table of Contents
1. [End-to-End System Workflow Diagram](#1-end-to-end-system-workflow-diagram)
2. [Database Schema & Table Integration Map](#2-database-schema--table-integration-map)
3. [Deep-Dive Subsystem Pipelines](#3-deep-dive-subsystem-pipelines)
   - [Pipeline A: Tokenization, Language ID & POS Tagging](#pipeline-a-tokenization-language-id--pos-tagging)
   - [Pipeline B: Named Entity Recognition & Temporal Resolution](#pipeline-b-named-entity-recognition--temporal-resolution)
   - [Pipeline C: Sentiment Analysis & Negation Windowing](#pipeline-c-sentiment-analysis--negation-windowing)
   - [Pipeline D: 4-Tier Translation Engine](#pipeline-d-4-tier-translation-engine)
4. [Client-Server-Database Sequence Diagram](#4-client-server-database-sequence-diagram)
5. [Complete LLM Prompts to Generate Workflow Diagrams](#5-complete-llm-prompts-to-generate-workflow-diagrams)
   - [Prompt 1: Full System Dataflow Prompt](#prompt-1-full-system-dataflow-for-plantuml--mermaid)
   - [Prompt 2: Database Table Fetch & Cache Architecture Prompt](#prompt-2-database-table-fetch--cache-architecture)
   - [Prompt 3: Multi-Tier Translation Decision Tree Prompt](#prompt-3-multi-tier-translation-decision-tree)
   - [Prompt 4: Entity-Relationship & Schema Architecture Prompt](#prompt-4-entity-relationship--schema-architecture)

---

## 1. End-to-End System Workflow Diagram

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Client Layer"]
        UI["User enters Hinglish text in Glassmorphic Web UI"]
        JS["frontend/app.js captures input and validates length"]
        POST["HTTP POST /api/analyze with JSON payload"]
        UI --> JS --> POST
    end

    subgraph ServerLayer["Backend API Layer (Flask)"]
        SVR["backend/server.py: api_analyze() endpoint"]
        AZ["backend/analyzer.py: analyze_text() orchestrator"]
        POST --> SVR --> AZ
    end

    subgraph DataCacheLayer["Database & Cache Layer (backend/db.py)"]
        CACHE["In-Memory DatabaseCache"]
        CHECK{"Is Cache Loaded?"}
        POOLER["Supabase IPv4 Pooler (port 5432)"]
        REST["Supabase HTTPS REST API (port 443)"]
        
        AZ --> CHECK
        CHECK -- No --> POOLER
        POOLER -- Direct SQL Fails --> REST
        POOLER -- Success --> CACHE
        REST -- Success --> CACHE
        CHECK -- Yes --> CACHE
    end

    subgraph ProcessingLayer["NLP Processing Pipeline"]
        TOK["1. Regex Word Tokenizer"]
        LID["2. Language Identification Engine"]
        POS["3. Rule-Based POS Tagger"]
        NER["4. NER & Temporal Context Resolver"]
        SENT["5. Sentiment & Modifier Engine"]
        TRANS["6. 4-Tier Translation Engine"]

        CACHE --> TOK
        TOK --> LID
        TOK --> POS
        TOK --> NER
        TOK --> SENT
        TOK --> TRANS
    end

    subgraph ResponseLayer["Response & Visualization Layer"]
        JSON["Consolidated JSON Response Object"]
        RENDER["frontend/app.js: renderAnalysisResults()"]
        KPIS["Metric KPI Tiles: Language Ratio, Sentiment, Entities, Confidence"]
        CARDS["Result Panels: Translation Box, Entity Chips, POS Table"]

        LID & POS & NER & SENT & TRANS --> JSON
        JSON --> SVR
        SVR --> RENDER
        RENDER --> KPIS & CARDS
    end
```

---

## 2. Database Schema & Table Integration Map

This diagram specifies **every database table**, the exact columns retrieved, and how each module in memory utilizes that table.

```mermaid
flowchart LR
    subgraph SupabaseDB["Supabase PostgreSQL Cloud Database"]
        T_VOCAB[("nlp_vocabulary\n(word, language)")]
        T_POS[("nlp_pos_lexicon\n(word, pos_tag, language)")]
        T_SENT[("nlp_sentiment_lexicon\n(term, polarity_score, category)")]
        T_MOD[("nlp_sentiment_modifiers\n(term, modifier_type, weight)")]
        T_GAZ[("nlp_entities_gazetteer\n(entity_text, entity_type, description)")]
        T_TEMP[("nlp_temporal_indicators\n(term, indicator_type)")]
        T_PHRASE[("nlp_phrase_translations\n(phrase, translation, phrase_length)")]
        T_WORD[("nlp_word_translations\n(source_word, target_translation, category)")]
        T_DTRANS[("datasets_translation\n(hinglish_text, english_translation, category)")]
        T_DNER[("datasets_ner\n(sentence_id, text, entities, entity_summary)")]
        T_DSENT[("datasets_sentiment\n(sentence_id, text, sentiment, polarity)")]
        T_DSAMP[("datasets_sample\n(text, label, category)")]
        T_DPOS[("datasets_pos\n(token_id, token, pos_tag, language, example_sentence)")]
    end

    subgraph MemoryCache["In-Memory DatabaseCache (backend/db.py)"]
        C_HINDI["self.hindi_words"]
        C_ENG["self.english_words"]
        C_POS["self.pos_lexicon"]
        C_POS_SENT["self.positive_lexicon"]
        C_NEG_SENT["self.negative_lexicon"]
        C_NEGATORS["self.negators"]
        C_INTENS["self.intensifiers"]
        C_DIMIN["self.diminishers"]
        C_ENT["self.persons / locations /\norganizations / facilities / events"]
        C_TEMP["self.temporal_keywords /\npast_indicators / future_indicators"]
        C_PHRASE["self.phrase_translations"]
        C_WTRANS["self.word_translations"]
        C_PTRANS["self.parallel_translations"]
    end

    subgraph NLPModules["NLP Processing Engines"]
        M_LID["Language Identification (backend/analyzer.py)"]
        M_POS["POS Tagging (backend/analyzer.py)"]
        M_NER["NER Engine (backend/ner_engine.py)"]
        M_SENT["Sentiment Engine (backend/sentiment_engine.py)"]
        M_TRANS["Translation Engine (backend/translation_engine.py)"]
    end

    T_VOCAB --> C_HINDI & C_ENG --> M_LID
    T_POS --> C_POS --> M_POS
    T_SENT --> C_POS_SENT & C_NEG_SENT --> M_SENT
    T_MOD --> C_NEGATORS & C_INTENS & C_DIMIN --> M_SENT
    T_GAZ --> C_ENT --> M_NER
    T_TEMP --> C_TEMP --> M_NER
    T_PHRASE --> C_PHRASE --> M_TRANS
    T_WORD --> C_WTRANS --> M_TRANS
    T_DTRANS --> C_PTRANS --> M_TRANS
```

---

## 3. Deep-Dive Subsystem Pipelines

### Pipeline A: Tokenization, Language ID & POS Tagging

```mermaid
flowchart TD
    INPUT["Raw Input: 'Tejas kal library jayega'"] --> REGEX["re.findall(r'\b\w+\b', text)"]
    REGEX --> TOKENS["Tokens: ['Tejas', 'kal', 'library', 'jayega']"]

    subgraph LID_Step["Language Identification (LID)"]
        TOKENS --> FOR_EACH_LID["For each token (lowercased)"]
        FOR_EACH_LID --> CHK_HINDI{"In db.get_hindi_words()?\n(From nlp_vocabulary)"}
        CHK_HINDI -- Yes --> TAG_HI["Tag: Hindi"]
        CHK_HINDI -- No --> CHK_ENG{"In db.get_english_words()?\n(From nlp_vocabulary)"}
        CHK_ENG -- Yes --> TAG_EN["Tag: English"]
        CHK_ENG -- No --> TAG_OTH["Tag: Other / Proper Noun"]
        
        TAG_HI & TAG_EN & TAG_OTH --> RATIO["Compute Ratios: Hindi %, English %"]
        RATIO --> CODE_MIX{"Ratio > 0 for both?"}
        CODE_MIX -- Yes --> CLS_MIX["Classification: Hinglish / Code-Mixed"]
        CODE_MIX -- No --> CLS_MONO["Classification: Mostly Hindi / Mostly English"]
    end

    subgraph POS_Step["Part-of-Speech Tagging"]
        TOKENS --> FOR_EACH_POS["For each token"]
        FOR_EACH_POS --> CHK_LEX{"In db.get_pos_lexicon()?\n(From nlp_pos_lexicon)"}
        CHK_LEX -- Match --> DIRECT_POS["Assign DB POS Tag (e.g. NOUN, VERB)"]
        CHK_LEX -- Miss --> MORPH_RULES["Evaluate Morphological Suffixes"]
        
        MORPH_RULES --> R1{"Ends with -ega, -egi, -enge, -ta, -ti, -te, -kar?"}
        R1 -- Yes --> VERB_TAG["Tag: VERB"]
        R1 -- No --> R2{"Title Case and not first word?"}
        R2 -- Yes --> PROPN_TAG["Tag: PROPN"]
        R2 -- No --> NOUN_TAG["Tag: NOUN (Default fallback)"]
    end
```

---

### Pipeline B: Named Entity Recognition & Temporal Resolution

```mermaid
flowchart TD
    TOKENS["Input Tokens + Contextual Sentence"] --> GAZETTEER_SCAN["Scan 1-gram, 2-gram, 3-gram against Gazetteer"]

    subgraph GazetteerCheck["Gazetteer Matching (from nlp_entities_gazetteer)"]
        GAZETTEER_SCAN --> CHK_P{"In db.get_persons()?\n(e.g., Tejas, Rohan, Parth)"}
        CHK_P -- Yes --> E_PER["Entity: PERSON"]
        
        CHK_P -- No --> CHK_L{"In db.get_locations()?\n(e.g., Delhi, Bangalore, Goa)"}
        CHK_L -- Yes --> E_LOC["Entity: LOCATION"]
        
        CHK_L -- No --> CHK_O{"In db.get_organizations()?\n(e.g., Google, Microsoft, TCS)"}
        CHK_O -- Yes --> E_ORG["Entity: ORGANIZATION"]
        
        CHK_O -- No --> CHK_F{"In db.get_facilities()?\n(e.g., office, library, airport)"}
        CHK_F -- Yes --> E_FAC["Entity: FACILITY"]
        
        CHK_F -- No --> CHK_E{"In db.get_events()?\n(e.g., hackathon, IPL, Diwali)"}
        CHK_E -- Yes --> E_EVT["Entity: EVENT"]
    end

    subgraph TemporalResolution["Contextual Temporal Resolution (from nlp_temporal_indicators)"]
        GAZETTEER_SCAN --> CHK_T{"Token in db.get_temporal_keywords()?\n(e.g., 'kal', 'aaj', 'parso')"}
        CHK_T -- Yes --> WORD_KAL{"Word == 'kal'?"}
        
        WORD_KAL -- Yes --> VERB_INSPECT["Inspect Surrounding Verb Conjugation"]
        VERB_INSPECT --> TENSE{"Verb ends in -ega, -egi, -enge\nor includes 'jayega' / 'karega'?"}
        TENSE -- Yes --> FUT["Assign: DATE_TIME (Tomorrow / Future Context)"]
        TENSE -- No --> PAST{"Verb ends in -tha, -thi, -the\nor includes 'gaya' / 'kiya'?"}
        PAST -- Yes --> PST["Assign: DATE_TIME (Yesterday / Past Context)"]
        PAST -- Ambiguous --> DEF_TIME["Assign: DATE_TIME (Relative Context)"]
        
        WORD_KAL -- No --> STD_TIME["Assign: DATE_TIME from indicator category"]
    end

    E_PER & E_LOC & E_ORG & E_FAC & E_EVT & FUT & PST & STD_TIME --> MERGE["Deduplicate Spans & Build Entity Chip Summary"]
```

---

### Pipeline C: Sentiment Analysis & Negation Windowing

```mermaid
flowchart TD
    RAW_INPUT["Input Hinglish Text"] --> NORM["Normalize to lowercase & extract words"]
    NORM --> SCAN["Iterate through tokens with index i"]

    subgraph LexiconLookup["Lexicon Score Match (from nlp_sentiment_lexicon)"]
        SCAN --> CHK_POS{"Word in db.get_positive_lexicon()?\n(e.g., accha, shandar, kamaal, mast)"}
        CHK_POS -- Yes --> GET_POS_VAL["Base Polarity: +0.60 to +0.95"]
        
        CHK_POS -- No --> CHK_NEG{"Word in db.get_negative_lexicon()?\n(e.g., bekaar, ghatiya, kharab, slow)"}
        CHK_NEG -- Yes --> GET_NEG_VAL["Base Polarity: -0.50 to -0.95"]
        
        CHK_NEG -- No --> NEUT["No Base Polarity (0.0)"]
    end

    subgraph WindowInspection["3-Token Preceding Context Window [i-3 ... i-1]"]
        GET_POS_VAL & GET_NEG_VAL --> CHK_NEGATION{"Negator present in window?\n(From nlp_sentiment_modifiers: nahi, na, mat, bina)"}
        
        CHK_NEGATION -- Yes --> INVERT["Invert Polarity:\nScore = -1 * Score * 0.90\n(e.g., 'accha nahi' flips +0.80 to -0.72)"]
        CHK_NEGATION -- No --> CHK_INTENS{"Intensifier present in window?\n(From nlp_sentiment_modifiers: bahut, bohot, super, ekdum)"}
        
        CHK_INTENS -- Yes --> SCALE_UP["Scale Magnitude:\nScore = Score * Weight (1.25x to 1.40x)"]
        CHK_INTENS -- No --> CHK_DIMIN{"Diminisher present in window?\n(thoda, halka)"}
        
        CHK_DIMIN -- Yes --> SCALE_DOWN["Dampen Magnitude:\nScore = Score * 0.70x"]
        CHK_DIMIN -- No --> RAW_SCORE["Keep Base Score"]
    end

    subgraph EmojiAndAggregate["Aggregation & Thresholding"]
        INVERT & SCALE_UP & SCALE_DOWN & RAW_SCORE --> SUM["Aggregate all token scores + Emoji sentiment"]
        SUM --> NORMALIZE["Clip score to [-1.0, +1.0]"]
        
        NORMALIZE --> THRESH{"Final Polarity Score"}
        THRESH -- Score >= +0.15 --> L_POS["Tone: Positive (Green Badge)"]
        THRESH -- Score <= -0.15 --> L_NEG["Tone: Negative (Red Badge)"]
        THRESH -- -0.15 < Score < +0.15 --> L_NEU["Tone: Neutral (Muted Badge)"]
    end
```

---

### Pipeline D: 4-Tier Translation Engine

```mermaid
flowchart TD
    RAW_IN["Input Hinglish Text: e.g., 'Tejas kal Delhi office jayega'"] --> TIER1

    subgraph TIER1["Tier 1: Exact Parallel Dataset Matching (Confidence 100%)"]
        T1_LOOKUP{"Exact match in datasets_translation?\n(Filtered against 170+ curated rows)"}
        T1_LOOKUP -- Match Found --> T1_RET["Return Curated English Translation directly\nMethod: 'Database Direct Match'"]
        T1_LOOKUP -- No Match --> TIER2
    end

    subgraph TIER2["Tier 2: Multi-Word Phrase & Idiom Substitution (Confidence 90%)"]
        TIER2 --> T2_SCAN["Scan text against nlp_phrase_translations\nSorted descending by phrase_length and priority"]
        T2_SCAN --> T2_REP["Replace longest matched idioms:\ne.g., 'kya haal hai' -> 'how are you',\n'tension mat lo' -> 'do not worry'"]
        T2_REP --> TIER3
    end

    subgraph TIER3["Tier 3: Bilingual Lexical Word Substitution (Confidence 80%)"]
        TIER3 --> T3_SCAN["For each remaining Hindi word, query nlp_word_translations:"]
        T3_SCAN --> T3_DICT["e.g., 'kal' -> 'tomorrow', 'office' -> 'office',\n'naya' -> 'new', 'jayega' -> 'will go'"]
        T3_DICT --> TIER4
    end

    subgraph TIER4["Tier 4: Syntactic SOV to SVO Restructuring & Surface Polish"]
        TIER4 --> SYNTAX["Reorder Hindi SOV (Subject-Object-Verb) to English SVO (Subject-Verb-Object)"]
        SYNTAX --> POLISH["Apply Capitalization, Spacing, and Sentence-ending Period"]
        POLISH --> FINAL_COMP["Return Composed Translation\nMethod: 'Phrase & Lexical Composition (Supabase DB)'"]
    end

    T1_RET --> OUT["Final Translation Output Object with Word Alignments"]
    FINAL_COMP --> OUT
```

---

## 4. Client-Server-Database Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant AppJS as frontend/app.js
    participant Server as backend/server.py
    participant Analyzer as backend/analyzer.py
    participant DB as backend/db.py (Cache)
    participant Supabase as Supabase Cloud DB

    Note over User, AppJS: User types text and clicks 'Analyze Text'
    User->>AppJS: Click / Ctrl+Enter
    AppJS->>AppJS: Set loading spinner, disable button
    AppJS->>Server: POST /api/analyze { text: "..." }

    Server->>Analyzer: analyze_text(text)
    Analyzer->>DB: ensure_cache()
    
    alt Cache already loaded in memory
        DB-->>Analyzer: Cache Ready (< 1 ms)
    else Cache empty (Cold Start)
        DB->>Supabase: Connect via IPv4 Pooler (port 5432)
        alt Pooler connection succeeds
            Supabase-->>DB: SQL Result: Vocabulary, Lexicons, Gazetteers, Datasets
        else Direct SQL fails (Network/Proxy boundary)
            DB->>Supabase: Fallback to HTTPS REST API (port 443)
            Supabase-->>DB: JSON Records: /rest/v1/...
        end
        DB->>DB: Populate in-memory sets and dictionaries
        DB-->>Analyzer: Cache Populated & Ready
    end

    rect rgb(240, 248, 255)
        Note over Analyzer: Parallel NLP Subsystem Execution
        Analyzer->>Analyzer: 1. Tokenize & Classify Language (LID)
        Analyzer->>Analyzer: 2. Morphological + Lexicon POS Tagging
        Analyzer->>Analyzer: 3. Gazetteer NER + Temporal kal/parso resolution
        Analyzer->>Analyzer: 4. Sentiment Polarity + Windowed Negation
        Analyzer->>Analyzer: 5. 4-Tier Translation Resolution
    end

    Analyzer-->>Server: Return consolidated result dict
    Server-->>AppJS: HTTP 200 OK (JSON payload)

    AppJS->>AppJS: Update Metric Tiles (Hinglish ratio, Sentiment, Entity count)
    AppJS->>AppJS: Render Translation card & Confidence badge
    AppJS->>AppJS: Render Interactive Entity chips & Span table
    AppJS->>AppJS: Render Sentiment Meter and POS Breakdown table
    AppJS-->>User: Display rich UI results
```

---

## 5. Complete LLM Prompts to Generate Workflow Diagrams

Copy and paste the exact prompts below into any LLM (ChatGPT, Claude, Gemini, DeepSeek) to generate new diagrams in your preferred format.

---

### Prompt 1: Full System Dataflow (For PlantUML / Mermaid)

```text
Act as a Principal System Architect and NLP Systems Engineer. 
Generate a comprehensive, production-grade PlantUML / Mermaid architecture diagram showing the exact end-to-end dataflow of a Hinglish (Hindi-English code-mixed) Natural Language Processing suite.

The system consists of:
1. Client Layer: Glassmorphic Web frontend (app.js) sending JSON payload via HTTP POST /api/analyze.
2. Server Layer: Python Flask server (backend/server.py) delegating to an NLP orchestrator (backend/analyzer.py).
3. Data Layer: Supabase PostgreSQL database holding 13 tables:
   - datasets_ner (160 rows), datasets_sentiment (154 rows), datasets_translation (170 rows), datasets_sample (90 rows), datasets_pos (125 rows)
   - nlp_vocabulary, nlp_pos_lexicon, nlp_sentiment_lexicon, nlp_sentiment_modifiers, nlp_entities_gazetteer, nlp_temporal_indicators, nlp_phrase_translations, nlp_word_translations
4. Connection Resilience: Dual-connectivity strategy using an IPv4 Pooler on port 5432 with automatic fallback to HTTPS REST API on port 443 when direct SQL is blocked.
5. In-Memory Cache: DatabaseCache loaded on startup for sub-millisecond token lookups.
6. Processing Pipelines:
   - Word Tokenizer (Regex)
   - Language Identification Engine (Hindi/English ratio calculator)
   - POS Tagger (Lexicon + Suffix rules for -ega, -egi, -enge, -kar)
   - NER Engine (Gazetteer lookup + context-aware temporal resolution for 'kal')
   - Sentiment Analyzer (Lexicon score + 3-token window negation inversion + intensifier scaling)
   - 4-Tier Translation Engine (Exact DB Match -> Phrase/Idiom Replacement -> Lexical Translation -> SOV to SVO Restructuring)
7. Response Layer: JSON response updating 4 Metric KPI tiles, translation cards, interactive entity chips, and token tables.

Please output the complete diagram code with clear grouping, labels, and swimlanes.
```

---

### Prompt 2: Database Table Fetch & Cache Architecture

```text
Act as a Database Architect.
Create a detailed Mermaid flowchart that maps out the exact relationship between database tables in Supabase and the in-memory cache structures of an NLP application:

Tables to map:
1. 'nlp_vocabulary' (columns: word, language) -> Populates 'self.hindi_words' and 'self.english_words' sets. Used by: Language Identification Engine.
2. 'nlp_pos_lexicon' (columns: word, pos_tag, language) -> Populates 'self.pos_lexicon' dictionary. Used by: POS Tagger.
3. 'nlp_sentiment_lexicon' (columns: term, polarity_score, category) -> Populates 'self.positive_lexicon', 'self.negative_lexicon', 'self.emoji_sentiment'. Used by: Sentiment Analyzer.
4. 'nlp_sentiment_modifiers' (columns: term, modifier_type, weight) -> Populates 'self.negators', 'self.intensifiers', 'self.diminishers'. Used by: Sentiment Negation Windowing.
5. 'nlp_entities_gazetteer' (columns: entity_text, entity_type, description) -> Populates sets for PERSON, LOCATION, ORGANIZATION, FACILITY, EVENT. Used by: NER Engine.
6. 'nlp_temporal_indicators' (columns: term, indicator_type) -> Populates past/future indicators. Used by: Contextual 'kal' (Yesterday vs Tomorrow) Resolver.
7. 'nlp_phrase_translations' (columns: phrase, translation, phrase_length, priority) -> Populates 'self.phrase_translations'. Used by: Tier 2 Idiom Substitution.
8. 'nlp_word_translations' (columns: source_word, target_translation, category) -> Populates 'self.word_translations'. Used by: Tier 3 Lexical Substitution.
9. 'datasets_translation' (columns: hinglish_text, english_translation, category) -> Populates 'self.parallel_translations'. Used by: Tier 1 Direct Dataset Match.

Show the flow from SQL/REST query -> memory cache attribute -> NLP feature function. Ensure syntax is valid Mermaid.
```

---

### Prompt 3: Multi-Tier Translation Decision Tree

```text
Act as a Senior Computational Linguist and AI Engineer.
Create a comprehensive Decision Tree flowchart in Mermaid format illustrating the 4-tier translation algorithm used for converting Hinglish (code-mixed Hindi-English) into Standard English:

Rules to visualize:
- Step 1: Input text is sanitized and trimmed.
- Step 2 (Tier 1): Search 'datasets_translation' (170 parallel sentences). If exact match found, return immediately with Confidence = 100% and Method = 'Database Direct Match'.
- Step 3 (Tier 2): If no exact match, scan input for multi-word idioms and colloquial phrases from 'nlp_phrase_translations' (e.g. 'kya chal raha hai', 'tension mat lo', 'chai peene'). Replace matched spans with their English equivalents sorted by phrase length.
- Step 4 (Tier 3): For any remaining un-translated Hindi tokens, query 'nlp_word_translations' for direct bilingual dictionary mapping (e.g. 'kal' -> 'tomorrow', 'dost' -> 'friend').
- Step 5 (Tier 4): Syntactic Reordering. Detect Hindi SOV (Subject-Object-Verb) patterns using auxiliary verb markers and reorder into English SVO (Subject-Verb-Object).
- Step 6: Surface cleaning: Fix spacing around punctuation, ensure initial letter capitalization, and append appropriate terminating punctuation. Output with Confidence = 85% and Method = 'Phrase & Lexical Composition (Supabase DB)'.

Provide the complete Mermaid diagram code.
```

---

### Prompt 4: Entity-Relationship & Schema Architecture

```text
Act as a PostgreSQL Database Administrator.
Generate a complete Mermaid Entity-Relationship (ER) diagram representing the relational schema for a Hinglish NLP Suite hosted on Supabase:

Include all the following tables with their data types and primary/unique keys:
1. datasets_ner (id PK, sentence_id INT, text TEXT, entities JSONB, entity_summary TEXT, created_at TIMESTAMPTZ)
2. datasets_sentiment (id PK, sentence_id INT, text TEXT, sentiment VARCHAR, polarity FLOAT, sentiment_keywords TEXT, created_at TIMESTAMPTZ)
3. datasets_translation (id PK, sentence_id INT, hinglish_text TEXT, english_translation TEXT, category VARCHAR, created_at TIMESTAMPTZ)
4. datasets_sample (id PK, text TEXT, label VARCHAR, category VARCHAR, created_at TIMESTAMPTZ)
5. datasets_pos (id PK, token_id INT UNIQUE, token VARCHAR, pos_tag VARCHAR, language VARCHAR, example_sentence TEXT, created_at TIMESTAMPTZ)
6. nlp_vocabulary (id PK, word VARCHAR, language VARCHAR, created_at TIMESTAMPTZ) [UNIQUE(word, language)]
7. nlp_pos_lexicon (id PK, word VARCHAR UNIQUE, pos_tag VARCHAR, language VARCHAR, created_at TIMESTAMPTZ)
8. nlp_sentiment_lexicon (id PK, term VARCHAR UNIQUE, polarity_score FLOAT, category VARCHAR, created_at TIMESTAMPTZ)
9. nlp_sentiment_modifiers (id PK, term VARCHAR UNIQUE, modifier_type VARCHAR, weight FLOAT, created_at TIMESTAMPTZ)
10. nlp_entities_gazetteer (id PK, entity_text VARCHAR, entity_type VARCHAR, description TEXT, created_at TIMESTAMPTZ) [UNIQUE(entity_text, entity_type)]
11. nlp_temporal_indicators (id PK, term VARCHAR, indicator_type VARCHAR, created_at TIMESTAMPTZ) [UNIQUE(term, indicator_type)]
12. nlp_phrase_translations (id PK, phrase VARCHAR UNIQUE, translation TEXT, phrase_length INT, priority INT, created_at TIMESTAMPTZ)
13. nlp_word_translations (id PK, source_word VARCHAR UNIQUE, target_translation TEXT, category VARCHAR, created_at TIMESTAMPTZ)

Provide valid Mermaid 'erDiagram' syntax with descriptions.
```

