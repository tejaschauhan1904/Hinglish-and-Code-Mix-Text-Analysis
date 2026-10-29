# 🇮🇳 Hinglish Text Analyzer & NLP Suite

A comprehensive NLP system that analyzes **Hindi-English code-mixed (Hinglish) text** written in Roman script (such as WhatsApp-style messages, social media comments, and chat conversations).

---

## 🎯 Key Features

1. **Tokenization & Language Identification (LID):**
   - Distinguishes Hindi (Roman Hindi), English, Numbers, Punctuation, and Common shared words.
   - Detects code-mixing and calculates Hindi/English ratios.

2. **Rule + Lexicon-Based POS Tagging:**
   - Universal POS tagging (`NOUN`, `VERB`, `PRON`, `ADJ`, `ADV`, `AUX`, `CONJ`, `ADP`, `INTJ`).
   - Morphological heuristics for unlisted Roman-Hindi verb inflections (`-na`, `-ne`, `-ta`, `-ti`, `-te`, `-kar`) and noun derivations (`-wala`, `-wali`).

3. **Named Entity Recognition (NER):**
   - Identifies `PERSON`, `LOCATION`, `ORGANIZATION`, `FACILITY`, `EVENT`, and `DATE_TIME` entities.
   - Context-dependent resolution for temporal expressions (e.g., automatically inferring whether *"kal"* refers to *Yesterday (Past)* or *Tomorrow (Future)* using verb inflections like *jayega* vs *tha*).
   - Powered by a dedicated 50-sentence annotated NER dataset (`data/hinglish_ner_dataset.csv`).

4. **Keyword-Based Sentiment Analysis:**
   - Detects **Positive**, **Negative**, or **Neutral** sentiment with normalized polarity scores (-1.0 to +1.0).
   - Operates **purely via keyword lexicons and linguistic rules** — no heavy external models or API keys required.
   - Features **negation inversion** (e.g., *"accha nahi"* flips to negative) and **intensifier scaling** (*"bahut boring"* $\rightarrow$ -1.0).
   - Supported by a dedicated 50-sentence sentiment dataset (`data/hinglish_sentiment_dataset.csv`).

5. **Hinglish to English Translation:**
   - Multi-tiered translation: Direct dataset lookup $\rightarrow$ Semantic similarity alignment $\rightarrow$ Multi-word phrase/idiom substitution $\rightarrow$ Bilingual lexicon $\rightarrow$ Fluency post-processing.
   - Backed by a 55+ sentence parallel translation dataset (`data/hinglish_translation_dataset.csv`).

6. **Dual User Interfaces:**
   - **Modern Web Studio (Recommended):** High-performance glassmorphic UI built with HTML5, CSS3, and JavaScript, backed by a Flask REST API.
   - **Streamlit Dashboard (Alternative):** Interactive multi-tab data science dashboard with feature navigation and built-in **Dataset Explorer**.

---

## 🧠 Architecture & Methodology

```text
User Hinglish Input
   ↓
Tokenization (Regex)
   ↓
├── Language Identification & Code-Mix Ratio
├── Rule + Lexicon POS Tagging
├── Named Entity Recognition (Gazetteers + Contextual Temporal Rules)
├── Sentiment Analysis (Keyword Lexicon + Negation Inversion + Intensifiers)
└── Hinglish-to-English Translation (Dataset Match + Phrase & Lexical Rules)
   ↓
Output Delivery (Flask REST API / Modern Web UI / Streamlit Dashboard)
```

---

## 📁 Project Structure

```text
Hinglish-and-Code-Mix-Text-Analysis/
│
├── .env                               # Supabase credentials (SUPABASE_URL, DATABASE_URL)
├── run.py                             # Root application launcher (Flask / Streamlit / Tests / DB)
├── migrate_to_supabase.py             # Database creation & seeding script (13 tables, 1,313 records)
├── requirements.txt                   # Project dependencies (Flask, psycopg2, python-dotenv, streamlit)
├── README.md                          # Comprehensive documentation & setup guide
│
├── frontend/                          # Modern Web UI (HTML5, Vanilla CSS3, JavaScript)
│   ├── index.html                     # Responsive glassmorphic layout
│   ├── style.css                      # Design system, tokens & animations
│   └── app.js                         # Dynamic client-side logic & API integration
│
├── backend/                           # Python NLP & API Architecture (100% DB-Powered)
│   ├── __init__.py                    # Package initialization & exports
│   ├── db.py                          # Supabase PostgreSQL client, queries & cache manager
│   ├── server.py                      # Flask REST API server (serves frontend & DB endpoints)
│   ├── analyzer.py                    # Core pipeline orchestrator (loads data from DB)
│   ├── ner_engine.py                  # Named Entity Recognition engine (gazetteers from DB)
│   ├── sentiment_engine.py            # Keyword & rule-based sentiment engine (lexicons from DB)
│   ├── translation_engine.py          # Hinglish-to-English translation engine (rules from DB)
│   ├── app.py                         # Streamlit dashboard alternative
│   └── test_analyzer.py               # Comprehensive CLI test suite
│
└── data/                              # Curated NLP Datasets (Seed Sources)
    ├── hinglish_ner_dataset.csv        # 50 sentences with labeled NER entities
    ├── hinglish_sentiment_dataset.csv  # 50 sentences with sentiment polarities & keywords
    ├── hinglish_translation_dataset.csv# 55+ parallel Hinglish-to-English pairs
    └── sample_hinglish.csv             # 20 diverse sample Hinglish sentences
```

---

## 🗄️ Database Architecture (Supabase PostgreSQL)

All datasets, lexicons, gazetteers, rules, and example queries have been **100% shifted from the code to Supabase PostgreSQL**. There is zero hardcoded data left in the Python codebase.

### Created Database Tables (13 Tables, 1,313 Records):
1. **`datasets_ner`** (50 records): Annotated sentences, JSON entity labels, and summaries.
2. **`datasets_sentiment`** (50 records): Sentiment classification sentences with polarity scores and cue keywords.
3. **`datasets_translation`** (55 records): Parallel Hinglish-English dataset for semantic lookup and training.
4. **`datasets_sample`** (20 records): Sample code-mixed text categorized by domain.
5. **`nlp_vocabulary`** (282 records): Hindi and English lexicons for Language Identification (LID).
6. **`nlp_pos_lexicon`** (227 records): Part-of-speech mappings (PRON, NOUN, VERB, ADJ, ADV, AUX, etc.).
7. **`nlp_sentiment_lexicon`** (135 records): Positive and negative sentiment words with base weights + emojis.
8. **`nlp_sentiment_modifiers`** (34 records): Negators, intensifiers, and diminishers with dynamic multipliers.
9. **`nlp_entities_gazetteer`** (133 records): PERSON, LOCATION, ORGANIZATION, FACILITY, and EVENT gazetteers.
10. **`nlp_temporal_indicators`** (81 records): Temporal cues, past indicators, and future indicators.
11. **`nlp_phrase_translations`** (55 records): Conversational Hinglish phrases and idioms mapped to English.
12. **`nlp_word_translations`** (184 records): Lexical Hindi-to-English translation mappings.
13. **`nlp_preset_examples`** (7 records): Preset test cases and demonstration queries for the UI.

---

## 🛠️ Tech Stack & Requirements

- **Python Version:** Python 3.8+ (tested on Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
- **Backend Framework:** Flask 3.0+
- **Data Processing:** Pandas 2.0+
- **Dashboard UI:** Streamlit 1.36+
- **Frontend:** Semantic HTML5, Vanilla CSS3 (Glassmorphism, CSS Grid/Flexbox), JavaScript (Fetch API)
- **Zero Heavy ML Bloat:** Fast, 100% offline, lexical & rule-based pipeline (no GPU or paid API keys needed)

---

## 📥 Installation & Setup

Follow these step-by-step instructions to clone and set up the repository on your local machine.

### Prerequisites

Ensure you have the following installed:
- [Git](https://git-scm.com/downloads)
- [Python 3.8 or higher](https://www.python.org/downloads/)
- `pip` (Python package installer, bundled with Python)

---

### Step 1: Clone the Repository

Open your terminal or command prompt and clone the repository:

```bash
git clone https://github.com/tejaschauhan1904/Hinglish-and-Code-Mix-Text-Analysis.git
cd Hinglish-and-Code-Mix-Text-Analysis
```

---

### Step 2: Create and Activate a Virtual Environment

It is strongly recommended to use a virtual environment to isolate project dependencies.

#### On Windows (PowerShell):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

> **Note for PowerShell users:** If you see an `Execution_Policies` script restriction error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> and re-run `.\venv\Scripts\Activate.ps1`.

#### On Windows (Command Prompt `cmd.exe`):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Running the Application

You can run the application in three different modes using `run.py`:

### 1. Modern Web Studio (Recommended ⭐)

Launches the fast Flask REST API server and serves the responsive glassmorphic web interface.

```bash
python run.py
```

- **Default URL:** Open **[http://localhost:8000](http://localhost:8000)** in your browser.
- **Custom Port:** You can optionally pass a custom port as an argument:
  ```bash
  python run.py 3000
  ```
  *(Then open [http://localhost:3000](http://localhost:3000))*

---

### 2. Streamlit Interactive Dashboard (Alternative UI)

Launches the multi-tab Streamlit data science application with built-in dataset explorer.

```bash
python run.py --streamlit
```

- **Default URL:** Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

### 3. Automated CLI Test Suite

Runs a suite of sanity checks and sample sentence validations across all modules:

```bash
python run.py --test
```

Expected output includes tokenization, language ratios, POS tags, NER tags (with temporal inference for words like *kal*), sentiment polarity scores, and parallel translations.

---

## 🌐 REST API Endpoints

When running the Flask backend (`python run.py`), the following REST endpoints are available:

| Endpoint | Method | Payload / Params | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | None | Serves the Modern Web Studio UI |
| `/api/analyze` | `POST` | `{"text": "Mujhe kal college jaana hai bro"}` | Complete unified NLP analysis (LID, POS, NER, Sentiment, Translation) |
| `/api/ner` | `POST` | `{"text": "Rahul kal Delhi office jayega"}` | Named Entity Recognition only |
| `/api/sentiment` | `POST` | `{"text": "Yaar movie bahut acchi thi"}` | Sentiment polarity, score, and keywords |
| `/api/translate` | `POST` | `{"text": "Khana khao aur so jao"}` | Hinglish to English translation |
| `/api/datasets` | `GET` | `?name=ner` \| `sentiment` \| `translation` \| `sample` | Fetches JSON records from curated CSV datasets |

---

## 🧪 Benchmark Examples

Try these sample inputs in the Web Studio or Streamlit dashboard:

| Feature | Sample Hinglish Input | Output Highlights |
| :--- | :--- | :--- |
| **POS Tagging** | `Mujhe kal college jaana hai bro` | `[Mujhe (PRON), kal (ADV), college (NOUN), jaana (VERB), hai (AUX), bro (NOUN)]` |
| **Temporal NER** | `Rahul kal Delhi office jayega` | `Rahul (PERSON), kal (DATE_TIME - Future/Tomorrow), Delhi (LOCATION), office (FACILITY)` |
| **Temporal NER** | `Rahul kal Delhi office gaya tha` | `Rahul (PERSON), kal (DATE_TIME - Past/Yesterday), Delhi (LOCATION), office (FACILITY)` |
| **Negated Sentiment** | `Khana bilkul accha nahi tha` | `🔴 Negative (Polarity: -0.75, Negation Inversion triggered by 'nahi')` |
| **Intensified Sentiment**| `Yaar aaj ka lecture bahut boring tha` | `🔴 Negative (Polarity: -1.0, Signal: boring, Intensifier: bahut)` |
| **Translation** | `Mujhe kal college jaana hai bro` | `I have to go to college tomorrow, bro.` *(Direct Dataset Match)* |
| **Translation** | `Mera laptop slow hai but theek ho jayega` | `My laptop is slow but it will be fine.` *(Phrase & Lexical Composition)* |

---

## ❓ Troubleshooting

- **`ModuleNotFoundError: No module named 'flask'` (or `streamlit` / `pandas`):**
  Ensure your virtual environment is activated before running `python run.py`. You should see `(venv)` in your terminal prompt.
- **Port 8000 already in use:**
  Run on a different port:
  ```bash
  python run.py 8080
  ```
- **Streamlit command not recognized:**
  Run `pip install -r requirements.txt` within your active virtual environment.

---

## 👩‍💻 NLP Course Project
**Hinglish Text Analyzer & NLP Suite — Semester 5 NLP Project**  
Created for Hindi-English code-mixed and Romanized text processing.
