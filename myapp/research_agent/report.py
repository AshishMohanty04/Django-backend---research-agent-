from fpdf import FPDF


def _clean_text(text: str) -> str:
    """
    Clean text for FPDF (latin-1 safe).
    Replaces unsupported Unicode characters.
    """
    if not text:
        return ""

    replacements = {
        "•": "-",
        "–": "-",
        "—": "-",
        "’": "'",
        "“": '"',
        "”": '"',
        "…": "...",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.encode("latin-1", errors="ignore").decode("latin-1")


def generate_citation(title: str, url: str) -> str:
    """
    Generate a simple reference entry.
    """
    title = title or "Untitled Source"
    url = url or ""
    return f"{title}. Available at: {url}"


def generate_pdf_report(data: dict) -> bytes:
    """
    Generate a structured research-style PDF report.
    Sections:
    - Introduction
    - Literature Review
    - Methodology
    - Results
    - Discussion
    - References
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ===== TITLE =====
    pdf.set_font("Arial", style="B", size=16)
    pdf.multi_cell(0, 12, _clean_text(data.get("title", "")))
    pdf.ln(4)

    # ===== INTRODUCTION =====
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Introduction", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, _clean_text(data.get("introduction", "")))
    pdf.ln(2)

    # ===== LITERATURE REVIEW =====
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Literature Review", ln=True)
    pdf.set_font("Arial", size=11)

    for item in data.get("literature_review", []):
        pdf.multi_cell(0, 8, _clean_text(item))
        pdf.ln(1)

    pdf.ln(1)

    # ===== METHODOLOGY =====
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Methodology", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, _clean_text(data.get("methodology", "")))
    pdf.ln(2)

    # ===== RESULTS =====
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Results", ln=True)
    pdf.set_font("Arial", size=11)

    for result in data.get("results", []):
        pdf.multi_cell(0, 8, _clean_text(result))
        pdf.ln(1)

    pdf.ln(1)

    # ===== DISCUSSION =====
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Discussion", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, _clean_text(data.get("discussion", "")))
    pdf.ln(2)

    # ===== REFERENCES =====
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "References", ln=True)
    pdf.set_font("Arial", size=10)

    for ref in data.get("references", []):
        pdf.multi_cell(0, 7, _clean_text(ref))
        pdf.ln(1)

    # Return PDF as bytes
    return pdf.output(dest="S").encode("latin-1")
