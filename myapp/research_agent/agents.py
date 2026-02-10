# myapp/research_agent/agents.py

from ddgs import DDGS   # ✅ NEW library (no warnings)
import math


def retriever_agent(query, max_results=3, region="us-en"):
    """
    Search web using DuckDuckGo and return title + link
    """
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results, region=region):
            results.append({
                "title": r.get("title"),
                "link": r.get("href")
            })
    return results


def summarizer_agent(summarizer, text, max_chunk_chars=1500):
    """
    ChatGPT-style structured summary:
    - Headings
    - Bullet points
    - Professional tone
    """
    if not text or len(text.strip()) < 100:
        return "Insufficient content to generate a structured summary."

    # Take a larger chunk for richer context
    chunk = text[:max_chunk_chars]

    # Prompt-style instruction embedded via input text
    prompt = (
        "Generate a professional, structured summary with headings and bullet points. "
        "Cover the following sections if possible:\n"
        "1. Overview\n"
        "2. Key Applications\n"
        "3. Benefits\n"
        "4. Challenges\n\n"
        f"Content:\n{chunk}"
    )

    word_count = len(chunk.split())
    max_len = min(220, max(120, word_count // 2))
    min_len = max(80, max_len // 2)

    try:
        result = summarizer(
            prompt,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            truncation=True,
        )

        raw = result[0]["summary_text"].strip()

        # -------- Post-processing for clean bullet points --------
        lines = raw.replace("•", "").split(". ")
        bullets = [f"• {line.strip()}." for line in lines if len(line.strip()) > 30]

        return "\n".join(bullets)

    except Exception:
        return "Structured summary generation failed for this source."





def critic_agent(summary, url):
    """
    Very lightweight credibility scoring
    """
    score = 0.1  # base confidence

    if url:
        url = url.lower()
        if ".edu" in url or ".gov" in url:
            score += 0.6
        elif "wikipedia.org" in url:
            score += 0.3
        elif ".org" in url:
            score += 0.2

    return round(min(score, 1.0), 2)



# ------------------------------------------------------------------
# 🔥 NEW: Long-form academic section writer
# ------------------------------------------------------------------

def write_research_section(
    summarizer,
    section_title: str,
    topic: str,
    evidence: str,
    min_words: int = 700
):
    """
    Generate a long, coherent, research-style section with proper flow.
    """

    if not evidence or len(evidence.strip()) < 200:
        return f"{section_title} could not be generated due to insufficient evidence."

    prompt = f"""
You are an academic research writer.

Write a detailed section titled "{section_title}" for a research paper on the topic:
"{topic}"

Use the following extracted evidence as reference material:
{evidence}

Writing requirements:
- Formal academic tone
- Well-structured paragraphs
- Logical flow between ideas
- No bullet points
- No repetition
- At least {min_words} words
- Do not mention sources explicitly in-text
"""

    try:
        result = summarizer(
            prompt,
            max_length=1024,
            min_length=800,
            do_sample=False,
            truncation=True,
        )

        return result[0]["summary_text"].strip()

    except Exception:
        return f"{section_title} generation failed due to model constraints."


# ------------------------------------------------------------------
# 🔥 NEW: Full research paper synthesizer
# ------------------------------------------------------------------

def synthesize_full_research(
    summarizer,
    topic: str,
    summaries: list
):
    """
    Generate a full research paper with proper structure and flow.
    Output size: ~4–5 pages (PDF).
    """

    # Combine evidence cleanly
    evidence_text = "\n".join(
        f"{s['title']}: {s['summary']}"
        for s in summaries
        if s.get("summary")
    )

    introduction = write_research_section(
        summarizer,
        "Introduction",
        topic,
        evidence_text,
        min_words=800
    )

    literature_review = write_research_section(
        summarizer,
        "Literature Review",
        topic,
        evidence_text,
        min_words=1200
    )

    methodology = write_research_section(
        summarizer,
        "Methodology",
        topic,
        (
            "This research uses an AI-driven pipeline consisting of "
            "web retrieval via DuckDuckGo, content extraction using "
            "Trafilatura, transformer-based summarization models, "
            "and vector similarity memory with FAISS."
        ),
        min_words=700
    )

    results = write_research_section(
        summarizer,
        "Results",
        topic,
        evidence_text,
        min_words=800
    )

    discussion = write_research_section(
        summarizer,
        "Discussion",
        topic,
        evidence_text,
        min_words=900
    )

    conclusion = write_research_section(
        summarizer,
        "Conclusion",
        topic,
        evidence_text,
        min_words=500
    )

    return {
        "introduction": introduction,
        "literature_review": literature_review,
        "methodology": methodology,
        "results": results,
        "discussion": discussion,
        "conclusion": conclusion,
    }


def synthesize_section(section_name, query, summaries, summarizer):
    """
    Create a long, coherent academic section from multiple summaries
    """
    joined_notes = "\n".join(summaries)

    prompt = (
        f"Write a detailed academic section titled '{section_name}' "
        f"for a research report on '{query}'. "
        f"Maintain formal tone, logical flow, and depth. "
        f"Do NOT include instructions, quizzes, or references to articles.\n\n"
        f"Notes:\n{joined_notes}"
    )

    result = summarizer(
        prompt,
        max_length=450,
        min_length=250,
        do_sample=False,
        truncation=True,
    )

    return result[0]["summary_text"].strip()
