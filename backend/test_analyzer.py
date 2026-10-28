import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from .analyzer import analyze_text
except (ImportError, ValueError):
    from analyzer import analyze_text

examples = [
    "Mujhe kal college jaana hai bro",
    "Yaar ye movie bahut acchi thi",
    "I have exam kal",
]

for text in examples:
    result = analyze_text(text)
    print("\n" + "="*50)
    print("INPUT:", text)
    print("TYPE:", result["sentence_type"])
    print("SENTIMENT:", result["sentiment"]["badge"], f"(score: {result['sentiment']['polarity_score']})")
    print("TRANSLATION:", result["translation"]["translated_text"], f"[{result['translation']['method']}]")
    print("ENTITIES:", [(e["text"], e["label"]) for e in result["ner"]["entities"]])
    print("TOKENS & POS:")
    for row in result["tokens"]:
        print(" ", row)

# Test specific examples
print("\n" + "="*50)
print("TESTING NER SPECIFIC: 'Rahul kal Delhi office jayega'")
res_ner = analyze_text("Rahul kal Delhi office jayega")
print("Entities found:", [(e["text"], e["label"], e["description"]) for e in res_ner["ner"]["entities"]])

print("\nTESTING SENTIMENT SPECIFIC: 'Yaar aaj ka lecture bahut boring tha'")
res_sent = analyze_text("Yaar aaj ka lecture bahut boring tha")
print("Sentiment found:", res_sent["sentiment"]["sentiment"], res_sent["sentiment"]["explanation"])

