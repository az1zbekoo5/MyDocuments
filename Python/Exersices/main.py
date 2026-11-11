

def top_words(text, k):
    """Return up to k words ordered by frequency, then alphabetically."""
    counts = {}
    punctuation = ".,;:!?\"'()[]-"

    for word in text.split():
        word = word.strip(punctuation).lower()
        if word:
            counts[word] = counts.get(word, 0) + 1

    ranked_words = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked_words[:max(0, k)]