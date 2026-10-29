"""
Named Entity Recognition (NER) Engine for Hinglish Text.
Data Source: Supabase PostgreSQL (via backend.db)
Zero hardcoded gazetteers, lists, or CSV file dependencies.
"""

import re
try:
    from . import db
except (ImportError, ValueError):
    import db

def resolve_kal_context(text):
    """Determine whether 'kal' refers to tomorrow (future) or yesterday (past) using DB indicators."""
    _, past_indicators, future_indicators = db.get_temporal_indicators()
    words = set(re.findall(r"[A-Za-z]+", text.lower()))
    has_past = any(w in words for w in past_indicators)
    has_future = any(w in words for w in future_indicators)

    if has_future and not has_past:
        return "DATE_TIME (Future / Tomorrow - inferred from verb tense)"
    elif has_past and not has_future:
        return "DATE_TIME (Past / Yesterday - inferred from verb tense)"
    else:
        return "DATE_TIME (Context-dependent: Tomorrow / Yesterday)"

def extract_named_entities(text):
    """
    Extract Named Entities from Hinglish text.
    Identifies PERSON, LOCATION, ORGANIZATION, FACILITY, EVENT, and DATE_TIME expressions
    using gazetteers and temporal indicators loaded from Supabase database.
    """
    persons, locations, organizations, facilities, events = db.get_gazetteers()
    temporal_keywords, _, _ = db.get_temporal_indicators()

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

    # 2. Multi-word gazetteer matching from Supabase DB (sorted by length descending for greedy match)
    all_multi_gazetteers = [
        (persons, "PERSON"),
        (locations, "LOCATION"),
        (organizations, "ORGANIZATION"),
        (facilities, "FACILITY"),
        (events, "EVENT"),
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

        if w in temporal_keywords:
            if w == "kal":
                desc = resolve_kal_context(text)
                add_entity(start, end, "DATE_TIME", text[start:end], desc)
            elif w in ("aaj", "today"):
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

        if w in persons:
            add_entity(start, end, "PERSON", text[start:end], "Person name")
        elif w in locations:
            add_entity(start, end, "LOCATION", text[start:end], "Geographical location")
        elif w in organizations:
            add_entity(start, end, "ORGANIZATION", text[start:end], "Organization / Brand / Institute")
        elif w in facilities:
            add_entity(start, end, "FACILITY", text[start:end], "Facility / Venue")
        elif w in events:
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
