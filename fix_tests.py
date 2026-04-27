import re

def count_negations(text, markers, lang='en'):
    """Count negation markers per sentence."""
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    counts = []
    for sent in sentences:
        sent_lower = sent.lower().strip()
        if not sent_lower:
            continue
        count = 0
        for marker in markers:
            count += len(re.findall(r'\b' + re.escape(marker) + r'\b', sent_lower))
        counts.append((sent.strip(), count))
    return counts

DUTCH_NEGATIONS = [
    'niet', 'geen', 'nooit', 'nimmer', 'niemand', 'niets',
    'geenszins', 'generlei', 'zonder',
    'in geen enkel', 'in geen enkele', 'in geenen',
    'noch', 'geensins',
]

ENGLISH_NEGATIONS = [
    'no', 'not', 'never', 'none', 'nothing', 'nobody',
    'neither', 'nor', 'without',
    'in no wise', 'in no respect', 'by no means',
    "n't",  # don't, won't, etc.
]

dutch = "Dit is niet goed. Niemand weet het."
english = "This is good. Nobody knows it."

dutch_counts = count_negations(dutch, DUTCH_NEGATIONS, 'nl')
english_counts = count_negations(english, ENGLISH_NEGATIONS, 'en')

print(f"Dutch counts: {dutch_counts}")
print(f"English counts: {english_counts}")
