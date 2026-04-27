import json
import re

glossary = {
    "Hervormde": "Reformed (State Church)",
    "Gereformeerde": "Reformed (Free Church)"
}

dutch_text = "De Hervormde kerk en de Gereformeerde kerk."
english_text = "The Reformed church and the Reformed church."

violations = []
matched = 0
total = 0

for dutch_term, expected_english in glossary.items():
    # Check if Dutch term appears in source
    if re.search(r'\b' + re.escape(dutch_term) + r'\b', dutch_text, re.IGNORECASE):
        total += 1
        # Check if expected English rendering is used
        expected_words = expected_english.lower().split()
        english_lower = english_text.lower()
        
        # Check if any of the key expected words appear
        key_word = expected_words[0].lower()
        print(f"Checking for {key_word} in {english_lower}")
        if key_word in english_lower:
            matched += 1
        else:
            violations.append({
                'dutch_term': dutch_term,
                'expected': expected_english,
                'message': f"Dutch '{dutch_term}' should render as '{expected_english}'"
            })

score = (matched / total * 100) if total > 0 else 100
print(f"Score: {score}, Matched: {matched}, Total: {total}, Violations: {violations}")
