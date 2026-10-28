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

6. **Interactive Streamlit Web UI:**
   - Left sidebar navigation allowing smooth toggling between all individual feature modules or a unified **All-in-One Dashboard**.
   - Built-in **Dataset Explorer** to search and inspect all newly curated datasets.

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
Streamlit Interactive Dashboard (Feature Toggles in Sidebar)
```

---

## 📁 Project Structure

```text
Hinglish_text_analyzer/
│
├── run.py                             # Root application launcher
├── requirements.txt                   # Project dependencies
├── README.md                          # Project documentation
│
├── frontend/                          # Modern Web UI (HTML5, CSS3, JavaScript)
│   ├── index.html                     # Responsive glassmorphic layout
│   ├── style.css                      # Design system, tokens & animations
│   └── app.js                         # Dynamic client-side logic & API calls
│
├── backend/                           # Python NLP & API Architecture
│   ├── __init__.py                    # Package initialization & exports
│   ├── server.py                      # Flask REST API server (serves frontend)
│   ├── analyzer.py                    # Core pipeline orchestrator
│   ├── ner_engine.py                  # Named Entity Recognition engine
│   ├── sentiment_engine.py            # Keyword & rule-based sentiment engine
│   ├── translation_engine.py          # Hinglish-to-English translation engine
│   ├── app.py                         # Streamlit dashboard alternative
│   └── test_analyzer.py               # Comprehensive CLI test suite
│
└── data/                              # Curated NLP Datasets
    ├── hinglish_ner_dataset.csv        # 50 sentences with labeled NER entities
    ├── hinglish_sentiment_dataset.csv  # 50 sentences with sentiment polarities & keywords
    ├── hinglish_translation_dataset.csv# 55+ parallel Hinglish-to-English pairs
    └── sample_hinglish.csv             # 20 diverse sample Hinglish sentences
```

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Pandas, Regex (`re`)
- **Frontend:** Semantic HTML5, Vanilla CSS3 (Glassmorphism & Micro-animations), JavaScript (ES6+ Fetch)
- **Alternative UI:** Streamlit
- **NLP Methodology:** Lexical & rule-based NLP, gazetteers, morphology heuristics, parallel corpus retrieval

---

## ▶️ How to Run

### 1. Modern Web Studio (HTML/CSS/JS) — Recommended ⭐

```bash
# Starts on http://localhost:8000
python run.py

# Or specify a custom port:
python run.py 3000
```
Open **`http://localhost:8000`** in your browser.

### 2. Streamlit Dashboard (Alternative)

```bash
python run.py --streamlit
```
Open **`http://localhost:8501`** in your browser.

### 3. Run Command-Line Tests

```bash
python run.py --test
```

---

## 🧪 Examples

| Feature | Input Text | Output |
| :--- | :--- | :--- |
| **POS Tagging** | `Mujhe kal college jaana hai bro` | `Tokens: [Mujhe (PRON), kal (ADV), college (NOUN), jaana (VERB), hai (AUX), bro (NOUN)]` |
| **NER** | `Rahul kal Delhi office jayega` | `Rahul (PERSON), kal (DATE_TIME - Tomorrow), Delhi (LOCATION), office (FACILITY)` |
| **Sentiment** | `Yaar aaj ka lecture bahut boring tha` | `🔴 Negative (Polarity: -1.0, Signal: boring [-1.28], Intensifier: bahut)` |
| **Translation** | `Mujhe kal college jaana hai bro` | `I have to go to college tomorrow, bro.` |
| **Translation** | `Rahul kal Delhi office jayega` | `Rahul will go to the Delhi office tomorrow.` |

---

## 👩‍💻 NLP Course Project
**Hinglish Text Analyzer & NLP Suite — Sem 5 NLP Project**
