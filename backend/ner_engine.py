import re
import os
import csv

# Default curated gazetteers
PERSONS = {
    "rahul", "priya", "amit", "rohit", "rohit sharma", "sharma", "ananya", "aarav",
    "simran", "vikram", "karan", "pooja", "sneha", "sachin", "rohan", "virat",
    "virat kohli", "kohli", "shreya", "manish", "aditi", "deepak", "tanvi", "varun",
    "mohit", "kavita", "siddharth", "natasha", "harshit", "kriti", "gaurav", "rishi",
    "meera", "raj", "aman", "kunal", "ayush", "aryan", "ishan", "riya", "divya",
    "khushi", "neha", "anil", "sunil", "ajay", "vijay", "suresh", "ramesh", "sharma ji"
}

LOCATIONS = {
    "delhi", "new delhi", "mumbai", "bangalore", "bengaluru", "pune", "goa",
    "hyderabad", "noida", "gurgaon", "gurugram", "jaipur", "kolkata", "chandigarh",
    "ahmedabad", "indore", "chennai", "varanasi", "bhopal", "manali", "lucknow",
    "shimla", "india", "wankhede stadium", "narendra modi stadium", "connaught place",
    "cp", "ganga", "hauz khas", "sector 62", "marine drive", "chandigarh highway"
}

ORGANIZATIONS = {
    "google", "microsoft", "tcs", "infosys", "wipro", "zomato", "swiggy",
    "amazon", "flipkart", "uber", "ola", "starbucks", "mcdonald", "netflix",
    "apple", "meta", "paytm", "aiims", "aiims delhi", "pvr", "reliance",
    "reliance trends", "isro", "hdfc", "sbi", "iit", "iit delhi", "du",
    "delhi university", "state bank"
}

FACILITIES = {
    "office", "library", "metro station", "hospital", "gym", "canteen",
    "cafe", "airport", "railway station", "school", "college"
}

EVENTS = {
    "durga puja", "diwali", "holi", "eid", "big billion days", "tech fest",
    "wedding", "sale", "ipl"
}

TEMPORAL_KEYWORDS = {
    "kal", "aaj", "parso", "today", "tomorrow", "yesterday", "tonight",
    "subah", "shaam", "sham", "dopehar", "dopahar", "raat", "din",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "weekend", "somwar", "mangalwar", "budhwar", "guruwar", "shukrawar", "shaniwar", "raviwar",
    "month", "week", "year", "saal", "mahina", "hafte", "night", "morning", "evening", "afternoon"
}

def load_dataset_entities(csv_path=None):
    """Load additional entities from dataset if available."""
    if csv_path is None:
        candidates = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "hinglish_ner_dataset.csv"),
            os.path.join("data", "hinglish_ner_dataset.csv"),
            os.path.join("..", "data", "hinglish_ner_dataset.csv"),
        ]
        for c in candidates:
            if os.path.exists(c):
                csv_path = c
                break

    if not csv_path or not os.path.exists(csv_path):
        return
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_entities = row.get("entities", "")
                # Pattern match token and label in CSV representation
                matches = re.findall(r"'token':\s*'([^']+)',\s*'label':\s*'([^']+)'", raw_entities)
                for token, label in matches:
                    t = token.strip().lower()
                    if label == "PERSON":
                        PERSONS.add(t)
                    elif label == "LOCATION":
                        LOCATIONS.add(t)
                    elif label == "ORGANIZATION":
                        ORGANIZATIONS.add(t)
                    elif label == "FACILITY":
                        FACILITIES.add(t)
                    elif label == "EVENT":
                        EVENTS.add(t)
    except Exception:
        pass

# Populate from dataset on module load
load_dataset_entities()

PAST_INDICATORS = {
    "tha", "thi", "the", "gaya", "gayi", "gaye", "aaya", "aayi", "diya", "kiya",
    "dekhi", "dekha", "suna", "mila", "bheja", "was", "were", "did", "had", "yesterday"
}

FUTURE_INDICATORS = {
    "hoga", "hogi", "honge", "jayega", "jayegi", "jayenge", "aayega", "aayegi", "aayenge",
    "karega", "karegi", "karenge", "milega", "milegi", "milenge", "dega", "nikalenge",
    "chalenge", "will", "shall", "going to", "tomorrow"
}

def resolve_kal_context(text):
    """Determine whether 'kal' refers to tomorrow (future) or yesterday (past)."""
    words = set(re.findall(r"[A-Za-z]+", text.lower()))
    has_past = any(w in words for w in PAST_INDICATORS)
    has_future = any(w in words for w in FUTURE_INDICATORS)

    if has_future and not has_past:
        return "DATE_TIME (Future / Tomorrow - inferred from verb tense)"
    elif has_past and not has_future:
        return "DATE_TIME (Past / Yesterday - inferred from verb tense)"
    else:
        return "DATE_TIME (Context-dependent: Tomorrow / Yesterday)"

def extract_named_entities(text):
    """
    Extract Named Entities from Hinglish text.
    Identifies PERSON, LOCATION, ORGANIZATION, FACILITY, EVENT, and DATE_TIME expressions.
    """
    entities = []
    text_lower = text.lower()
    occupied_spans = set()

    def add_entity(start, end, label, token_text, desc=""):
        # Check span collision
        span = set(range(start, end))
        if span & occupied_spans:
            return
        occupied_spans.update(span)
        entities.append({
            "text": token_text,
            "label": label,
            "start": start,
            "end": end,
            "description": desc or label
        })

    # 1. Multi-word and regex temporal expressions
    time_patterns = [
        (r"\b\d{1,2}(?::\d{2})?\s*(?:baje|am|pm|o'clock|hrs?|hours?)\b", "DATE_TIME (Specific Time)"),
        (r"\b(?:subah|shaam|sham|raat|dopehar|dopahar)\s+\d{1,2}(?::\d{2})?\s*(?:baje|am|pm)?\b", "DATE_TIME (Time of Day)"),
        (r"\b(?:agle|pichle|next|last)\s+(?:hafte|saal|mahine|week|month|year|weekend|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", "DATE_TIME (Relative Period)"),
        (r"\b\d+\s+(?:ghante|baje|minutes|days|dino)\s+(?:pehle|baad|later|ago)\b", "DATE_TIME (Time offset)")
    ]

    for pat, desc in time_patterns:
        for m in re.finditer(pat, text_lower):
            start, end = m.span()
            add_entity(start, end, "DATE_TIME", text[start:end], desc)

    # 2. Multi-word gazetteer matching (sorted by length descending for greedy match)
    all_multi_gazetteers = [
        (PERSONS, "PERSON"),
        (LOCATIONS, "LOCATION"),
        (ORGANIZATIONS, "ORGANIZATION"),
        (FACILITIES, "FACILITY"),
        (EVENTS, "EVENT"),
    ]

    for gazetteer, label in all_multi_gazetteers:
        sorted_terms = sorted([t for t in gazetteer if " " in t], key=len, reverse=True)
        for term in sorted_terms:
            pattern = r"\b" + re.escape(term) + r"\b"
            for m in re.finditer(pattern, text_lower):
                start, end = m.span()
                add_entity(start, end, label, text[start:end], f"Known {label.lower().replace('_', ' ')}")

    # 3. Single-word entity matching
    for m in re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)?", text):
        start, end = m.span()
        w = m.group(0).lower()

        if w in TEMPORAL_KEYWORDS:
            if w == "kal":
                desc = resolve_kal_context(text)
                add_entity(start, end, "DATE_TIME", text[start:end], desc)
            elif w == "aaj" or w == "today":
                add_entity(start, end, "DATE_TIME", text[start:end], "DATE_TIME (Current day / Today)")
            elif w == "parso":
                add_entity(start, end, "DATE_TIME", text[start:end], "DATE_TIME (Two days away)")
            elif w in ("subah", "morning"):
                add_entity(start, end, "DATE_TIME", text[start:end], "DATE_TIME (Morning)")
            elif w in ("shaam", "sham", "evening"):
                add_entity(start, end, "DATE_TIME", text[start:end], "DATE_TIME (Evening)")
            elif w in ("raat", "night"):
                add_entity(start, end, "DATE_TIME", text[start:end], "DATE_TIME (Night)")
            else:
                add_entity(start, end, "DATE_TIME", text[start:end], "Temporal expression")
            continue

        if w in PERSONS:
            add_entity(start, end, "PERSON", text[start:end], "Person name")
        elif w in LOCATIONS:
            add_entity(start, end, "LOCATION", text[start:end], "Geographical location")
        elif w in ORGANIZATIONS:
            add_entity(start, end, "ORGANIZATION", text[start:end], "Organization / Brand / Institute")
        elif w in FACILITIES:
            add_entity(start, end, "FACILITY", text[start:end], "Facility / Venue")
        elif w in EVENTS:
            add_entity(start, end, "EVENT", text[start:end], "Event / Festival")

    # Sort entities by occurrence position in the text
    entities.sort(key=lambda x: x["start"])

    # Aggregate counts by label
    labels_summary = {}
    for ent in entities:
        lbl = ent["label"]
        labels_summary[lbl] = labels_summary.get(lbl, 0) + 1

    return {
        "entities": entities,
        "entity_count": len(entities),
        "labels_summary": labels_summary
    }
