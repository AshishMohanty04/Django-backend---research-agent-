import uuid
import json
import time
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .research_agent import models as ra_models
from .research_agent import agents as ra_agents
from .research_agent import utils as ra_utils
from .research_agent import memory as ra_memory
from .research_agent import report as ra_report


# -------------------------------
# In-memory PDF store
# -------------------------------
_REPORT_STORE = {}

# Hard time limit (2 minutes)
TIME_LIMIT = 110


@ensure_csrf_cookie
def research_home(request):
    return render(request, "myapp/research.html")


@require_POST
def run_research(request):
    start_time = time.time()

    # -------------------------------
    # Parse request
    # -------------------------------
    try:
        payload = json.loads(request.body.decode("utf-8"))
        query = payload.get("query", "").strip()
        max_results = int(payload.get("max_results", 2))
        if not query:
            return JsonResponse({"error": "query required"}, status=400)
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    # -------------------------------
    # Init memory & models
    # -------------------------------
    ra_memory.init_memory()
    summarizer, embedder = ra_models.load_models()

    # -------------------------------
    # Break query (LIMITED for speed)
    # -------------------------------
    sub_queries = ra_utils.break_down_query(query)[:2]

    source_notes = []
    citations = []
    seen_links = set()

    # -------------------------------
    # Retrieval + Source Summaries
    # -------------------------------
    for sub_query in sub_queries:
        if time.time() - start_time > TIME_LIMIT:
            break

        results = ra_agents.retriever_agent(sub_query, max_results=1)

        for r in results:
            if time.time() - start_time > TIME_LIMIT:
                break

            link = r.get("link")
            if not link or link in seen_links:
                continue

            seen_links.add(link)

            title = r.get("title") or link
            text = ra_utils.extract_text(link)

            if not text:
                continue

            # Short structured summary (source-level)
            summary = ra_agents.summarizer_agent(summarizer, text)
            confidence = ra_agents.critic_agent(summary, link)

            source_notes.append(summary)
            citations.append(ra_report.generate_citation(title, link))

            ra_memory.add_to_memory(embedder, sub_query, summary, url=link)

    if not source_notes:
        return JsonResponse(
            {"error": "No valid content could be extracted."},
            status=500,
        )

    # -------------------------------
    # SECTION-WISE SYNTHESIS (KEY FIX)
    # -------------------------------
    def synthesize(section_title, min_len=280, max_len=450):
        prompt = (
            f"Write a detailed academic section titled '{section_title}' "
            f"for a research report on '{query}'. "
            f"Ensure formal tone, logical flow, and depth. "
            f"Do NOT include bullet points or references.\n\n"
            f"Notes:\n" + "\n".join(source_notes)
        )

        result = summarizer(
            prompt,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            truncation=True,
        )

        return result[0]["summary_text"].strip()

    introduction = synthesize("Introduction")
    literature_review = synthesize("Literature Review")
    methodology = (
        "This research uses an AI-driven research agent that performs web-based "
        "information retrieval, automated content extraction, transformer-based "
        "text summarization, and credibility assessment. The system synthesizes "
        "information from multiple sources into a coherent academic narrative."
    )
    results = synthesize("Results")
    discussion = synthesize("Discussion")

    # -------------------------------
    # PDF Report Data
    # -------------------------------
    report_data = {
        "title": f"Research Report on {query}",
        "introduction": introduction,
        "literature_review": literature_review,
        "methodology": methodology,
        "results": results,
        "discussion": discussion,
        "references": citations,
    }

    pdf_bytes = ra_report.generate_pdf_report(report_data)

    token = uuid.uuid4().hex
    _REPORT_STORE[token] = pdf_bytes

    # -------------------------------
    # JSON Response for Web UI
    # -------------------------------
    return JsonResponse({
        "query": query,
        "introduction": introduction,
        "literature_review": literature_review,
        "methodology": methodology,
        "results": results,
        "discussion": discussion,
        "references": citations,
        "download_token": token,
        "time_taken_sec": round(time.time() - start_time, 2),
    })


def download_report(request, token):
    pdf = _REPORT_STORE.get(token)
    if not pdf:
        return HttpResponseBadRequest("Invalid or expired token")

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="research_report.pdf"'
    return response
