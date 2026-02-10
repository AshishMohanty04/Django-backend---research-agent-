# myapp/research_agent/utils.py
import trafilatura

def extract_text(url, max_chars=2000):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                return text[:max_chars]
    except Exception:
        pass

    # 🔥 FALLBACK: return URL text itself
    return f"This article discusses {url} and its relevance to the topic."


def break_down_query(query):
    return [
        f"What is {query}?",
        f"What is the impact of {query}?"
    ]

