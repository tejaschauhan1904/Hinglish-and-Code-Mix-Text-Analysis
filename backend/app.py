import os
import streamlit as st
import pandas as pd
try:
    from .analyzer import (
        analyze_text,
        analyze_ner,
        analyze_sentiment,
        translate_hinglish_to_english
    )
except (ImportError, ValueError):
    from analyzer import (
        analyze_text,
        analyze_ner,
        analyze_sentiment,
        translate_hinglish_to_english
    )

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data") if os.path.exists(os.path.join(BASE_DIR, "data")) else os.path.abspath("data")

st.set_page_config(
    page_title="Hinglish Text Analyzer & NLP Suite",
    page_icon="🇮🇳",
    layout="wide"
)

# Custom styling for entity tags and badges
st.markdown(
    """
    <style>
    .entity-tag {
        display: inline-block;
        padding: 3px 8px;
        margin: 2px 4px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.88rem;
    }
    .entity-person { background-color: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
    .entity-location { background-color: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
    .entity-org { background-color: #ede9fe; color: #5b21b6; border: 1px solid #c4b5fd; }
    .entity-datetime { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .entity-facility { background-color: #cffafe; color: #155e75; border: 1px solid #a5f3fc; }
    .entity-event { background-color: #fce7f3; color: #9d174d; border: 1px solid #fbcfe8; }
    
    .sentiment-card {
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .sentiment-positive { background-color: #ecfdf5; border-left: 5px solid #10b981; }
    .sentiment-negative { background-color: #fef2f2; border-left: 5px solid #ef4444; }
    .sentiment-neutral { background-color: #f9fafb; border-left: 5px solid #6b7280; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🇮🇳 Hinglish Text Analyzer & NLP Suite")
st.caption("Comprehensive Natural Language Processing for Hindi-English code-mixed text in Roman script.")

# Sidebar Feature Navigation
with st.sidebar:
    st.header("⚙️ Feature Navigation")
    feature_mode = st.radio(
        "Select Feature Module:",
        options=[
            "🌐 All-in-One Analysis",
            "🏷️ Rule-based POS & Language ID",
            "🔍 Named Entity Recognition (NER)",
            "🎭 Sentiment Analysis",
            "🔄 Hinglish to English Translation",
            "📚 Dataset Explorer"
        ],
        index=0
    )

    st.markdown("---")
    st.header("💡 Try an Example")

    # Diverse examples tailored to features
    preset_examples = {
        "Hinglish Code-Mix": "Mujhe kal college jaana hai bro",
        "NER (Person + City + Office)": "Rahul kal Delhi office jayega",
        "Negative Sentiment": "Yaar aaj ka lecture bahut boring tha",
        "Positive Sentiment": "Ye movie sach me bahut acchi thi",
        "Negated Sentiment": "Khana bilkul accha nahi tha aur staff rude tha",
        "Multi-Entity & Translation": "Kal subah 9 baje meeting hai TCS ke office me",
        "Casual Chat Translation": "Mera laptop slow hai but theek ho jayega"
    }

    for label, ex_text in preset_examples.items():
        if st.button(f"{label}: \"{ex_text[:28]}...\"", use_container_width=True):
            st.session_state["text"] = ex_text

# If Dataset Explorer is selected, handle separately
if feature_mode == "📚 Dataset Explorer":
    st.subheader("📁 Curated Datasets for Hinglish NLP")
    st.markdown("Explore the custom large datasets created specifically for Hinglish text analysis, NER, Sentiment, and Translation.")

    dataset_option = st.selectbox(
        "Choose Dataset to Inspect:",
        options=[
            "🏷️ Named Entity Recognition (NER) Dataset",
            "🎭 Sentiment Analysis Dataset",
            "🔄 Hinglish-to-English Translation Dataset",
            "📝 General Sample Hinglish Corpus"
        ]
    )

    path_map = {
        "🏷️ Named Entity Recognition (NER) Dataset": os.path.join(DATA_DIR, "hinglish_ner_dataset.csv"),
        "🎭 Sentiment Analysis Dataset": os.path.join(DATA_DIR, "hinglish_sentiment_dataset.csv"),
        "🔄 Hinglish-to-English Translation Dataset": os.path.join(DATA_DIR, "hinglish_translation_dataset.csv"),
        "📝 General Sample Hinglish Corpus": os.path.join(DATA_DIR, "sample_hinglish.csv")
    }

    selected_file = path_map[dataset_option]
    if os.path.exists(selected_file):
        df_dataset = pd.read_csv(selected_file)
        c1, c2 = st.columns([1, 3])
        c1.metric("Total Records", len(df_dataset))
        c2.write(f"**File Location:** `{selected_file}`")

        # Search filter
        search_kw = st.text_input("Filter dataset by keyword:", "")
        if search_kw.strip():
            filtered_df = df_dataset[df_dataset.apply(lambda row: row.astype(str).str.contains(search_kw, case=False).any(), axis=1)]
            st.write(f"Showing **{len(filtered_df)}** matching records:")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_dataset, use_container_width=True)
    else:
        st.error(f"Dataset file `{selected_file}` not found.")

    st.stop()

# Main Text Input Area
default_input = st.session_state.get("text", "Mujhe kal college jaana hai bro")
text = st.text_area(
    "Enter Hinglish / Code-Mixed Text:",
    value=default_input,
    height=100,
    placeholder="Example: Rahul kal Delhi office jayega OR Yaar aaj ka lecture bahut boring tha"
)

col_btn, _ = st.columns([1, 4])
with col_btn:
    analyze_clicked = st.button("🔍 Run Analysis", type="primary", use_container_width=True)

if not text.strip():
    st.warning("Please enter some Hinglish text above to analyze.")
    st.stop()

# Run unified analysis
result = analyze_text(text)


def render_pos_language_section(res):
    """Renders the original Rule-based POS & Language ID feature."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Words", res["total_words"])
    c2.metric("Hindi Words", res["hindi_count"])
    c3.metric("English Words", res["english_count"])
    c4.metric("Other/Punct", res["other_count"])

    st.subheader("📊 Language Analysis")
    st.write(f"**Sentence classification:** `{res['sentence_type']}`")
    st.progress(res["hindi_percentage"] / 100)
    st.write(
        f"Hindi / Roman-Hindi: **{res['hindi_percentage']:.1f}%** | "
        f"English: **{res['english_percentage']:.1f}%**"
    )

    st.subheader("🏷️ Token & Rule-Based POS Analysis")
    df = pd.DataFrame(res["tokens"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("🧾 Summary")
    st.info(res["summary"])


def render_ner_section(ner_data, sentence_text):
    """Renders the Named Entity Recognition section."""
    st.subheader("🔍 Named Entity Recognition (NER)")
    st.caption("Identifies Persons, Locations, Organizations, Facilities, Events, and context-dependent Date/Time expressions.")

    entities = ner_data["entities"]
    if not entities:
        st.info("No named entities recognized in the input text. Try names of people, cities, companies, or days (e.g. *Rahul*, *Delhi*, *Google*, *kal*, *9 baje*).")
        return

    # Metrics
    summary = ner_data["labels_summary"]
    cols = st.columns(len(summary) + 1)
    cols[0].metric("Total Entities", ner_data["entity_count"])
    for i, (label, count) in enumerate(summary.items(), start=1):
        cols[i].metric(label, count)

    # Annotated visual representation
    st.markdown("#### Annotated Entity Chips")
    badge_classes = {
        "PERSON": "entity-person",
        "LOCATION": "entity-location",
        "ORGANIZATION": "entity-org",
        "DATE_TIME": "entity-datetime",
        "FACILITY": "entity-facility",
        "EVENT": "entity-event"
    }

    chips_html = []
    for ent in entities:
        cls = badge_classes.get(ent["label"], "entity-person")
        chips_html.append(f"<span class='entity-tag {cls}'>{ent['text']} &nbsp;<b>[{ent['label']}]</b></span>")
    st.markdown(" ".join(chips_html), unsafe_allow_html=True)

    st.write("")
    st.markdown("#### Entity Details & Context Resolution")
    df_ner = pd.DataFrame([
        {
            "Entity Token": e["text"],
            "Entity Type": e["label"],
            "Contextual Meaning / Description": e["description"],
            "Character Span": f"{e['start']} : {e['end']}"
        }
        for e in entities
    ])
    st.dataframe(df_ner, use_container_width=True, hide_index=True)

    # Context note for kal
    if any(e["text"].lower() == "kal" for e in entities):
        st.caption("💡 **Temporal Resolution for 'kal':** Automatically infers *Yesterday (Past)* or *Tomorrow (Future)* based on verb inflections (e.g. *jayega* vs *tha*).")


def render_sentiment_section(sentiment_data):
    """Renders the keyword-based Sentiment Analysis section."""
    st.subheader("🎭 Keyword-Based Sentiment Analysis")
    st.caption("Calculates message polarity using curated Hinglish & English sentiment lexicons, negation inversion, and intensifier scaling.")

    polarity = sentiment_data["polarity_score"]
    sentiment = sentiment_data["sentiment"]
    card_class = f"sentiment-{sentiment.lower()}"

    st.markdown(
        f"""
        <div class="sentiment-card {card_class}">
            <h3 style="margin: 0; padding-bottom: 4px;">{sentiment_data['badge']}</h3>
            <p style="margin: 0; font-size: 1.05rem;"><b>Polarity Score:</b> {polarity:+.2f} &nbsp;|&nbsp; <b>Interpretation:</b> {sentiment} emotional tone.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Polarity Score", f"{polarity:+.2f}")
    c2.metric("Sentiment Class", sentiment)
    c3.metric("Key Signals Found", len(sentiment_data["positive_keywords"]) + len(sentiment_data["negative_keywords"]))

    col_pos, col_neg = st.columns(2)
    with col_pos:
        st.markdown("**🟢 Positive Signals Detected:**")
        if sentiment_data["positive_keywords"]:
            for item in sentiment_data["positive_keywords"]:
                st.write(f"- `{item}`")
        else:
            st.caption("None detected.")

    with col_neg:
        st.markdown("**🔴 Negative Signals Detected:**")
        if sentiment_data["negative_keywords"]:
            for item in sentiment_data["negative_keywords"]:
                st.write(f"- `{item}`")
        else:
            st.caption("None detected.")

    # Modifiers & Linguistic Justification
    st.markdown("#### 🔍 Linguistic Mechanics & Justification")
    if sentiment_data["negations"]:
        st.info(f"🔄 **Negation Inversion Active:** Detected negation construct: **{', '.join(sentiment_data['negations'])}**. Polarity was inverted accordingly.")
    if sentiment_data["intensifiers"]:
        st.info(f"⚡ **Intensifier Active:** Amplified by: **{', '.join(sentiment_data['intensifiers'])}**.")

    st.write(f"**Explanation:** {sentiment_data['explanation']}")


def render_translation_section(trans_data):
    """Renders the Hinglish to English translation section."""
    st.subheader("🔄 Hinglish to English Translation")
    st.caption("Converts Roman-script Hinglish into standard, fluent English using dataset matching and multi-word phrase substitution.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🇮🇳 Original Hinglish")
        st.info(trans_data["source_text"])

    with col2:
        st.markdown("#### 🇬🇧 English Translation")
        st.success(trans_data["translated_text"])

    c_m1, c_m2 = st.columns(2)
    c_m1.metric("Translation Pipeline", trans_data["method"])
    c_m2.metric("Confidence Score", f"{trans_data['confidence']}%")
    st.caption(f"ℹ️ {trans_data['description']}")

    # Alignment breakdown
    alignments = trans_data.get("word_alignments", [])
    if alignments and trans_data["method"] != "Dataset Direct Match":
        with st.expander("🔎 View Word / Phrase Alignment Details", expanded=False):
            df_align = pd.DataFrame(alignments)
            df_align.columns = ["Hinglish Token", "Translated English Token"]
            st.dataframe(df_align, use_container_width=True, hide_index=True)


# Render Content Based on Selected Feature
if feature_mode == "🏷️ Rule-based POS & Language ID":
    render_pos_language_section(result)

elif feature_mode == "🔍 Named Entity Recognition (NER)":
    render_ner_section(result["ner"], text)

elif feature_mode == "🎭 Sentiment Analysis":
    render_sentiment_section(result["sentiment"])

elif feature_mode == "🔄 Hinglish to English Translation":
    render_translation_section(result["translation"])

elif feature_mode == "🌐 All-in-One Analysis":
    # Master dashboard with overview and tabs
    st.markdown("### 🌐 Unified Hinglish Analysis Dashboard")

    t1, t2, t3, t4 = st.tabs([
        "🏷️ POS & Language Tagging",
        "🔍 Named Entities (NER)",
        "🎭 Sentiment Analysis",
        "🔄 English Translation"
    ])

    with t1:
        render_pos_language_section(result)
    with t2:
        render_ner_section(result["ner"], text)
    with t3:
        render_sentiment_section(result["sentiment"])
    with t4:
        render_translation_section(result["translation"])

st.markdown("---")
