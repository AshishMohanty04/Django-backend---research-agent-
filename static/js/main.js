(function () {

  function getCsrfToken() {
    const name = "csrftoken=";
    return document.cookie
      .split(";")
      .map(c => c.trim())
      .find(c => c.startsWith(name))
      ?.substring(name.length) || "";
  }

  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("runBtn");
    const status = document.getElementById("status");

    btn.addEventListener("click", async function () {
      const query = document.getElementById("query").value.trim();
      const maxResults = document.getElementById("max_results").value || 2;

      if (!query) {
        alert("Please enter a topic");
        return;
      }

      status.innerText = "Running research… Please wait.";

      // Clear previous results
      [
        "intro-content",
        "literature-content",
        "methodology-content",
        "results-content",
        "discussion-content",
        "references-content"
      ].forEach(id => document.getElementById(id).innerHTML = "");

      document.getElementById("downloadDiv").innerHTML = "";

      try {
        const res = await fetch(window.runResearchUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken()
          },
          body: JSON.stringify({
            query: query,
            max_results: maxResults
          })
        });

        if (!res.ok) {
          status.innerText = "Server error occurred.";
          return;
        }

        const data = await res.json();
        status.innerText = "Research complete.";

        /* -------- Introduction -------- */
        if (data.introduction) {
          document.getElementById("intro-content").innerHTML =
            `<p>${data.introduction}</p>`;
        }

        /* -------- Literature Review -------- */
        if (data.literature_review?.length) {
          let html = "";
          data.literature_review.forEach(item => {
            html += `<div class="card p-3 mb-2">${item}</div>`;
          });
          document.getElementById("literature-content").innerHTML = html;
        }

        /* -------- Methodology -------- */
        if (data.methodology) {
          document.getElementById("methodology-content").innerHTML =
            `<p>${data.methodology}</p>`;
        }

        /* -------- Results -------- */
        if (data.results?.length) {
          let html = "";
          data.results.forEach(r => {
            html += `<div class="card p-3 mb-2">${r}</div>`;
          });
          document.getElementById("results-content").innerHTML = html;
        }

        /* -------- Discussion -------- */
        if (data.discussion) {
          document.getElementById("discussion-content").innerHTML =
            `<p>${data.discussion}</p>`;
        }

        /* -------- References -------- */
        if (data.references?.length) {
          let html = "<ul>";
          data.references.forEach(ref => {
            html += `<li>${ref}</li>`;
          });
          html += "</ul>";
          document.getElementById("references-content").innerHTML = html;
        }

        /* -------- Download -------- */
        const dlUrl = window.downloadReportTemplate.replace(
          "TOKEN",
          data.download_token
        );

        document.getElementById("downloadDiv").innerHTML = `
          <a href="${dlUrl}" class="btn btn-success">
            📄 Download PDF Report
          </a>
        `;

      } catch (err) {
        status.innerText = "Network error.";
      }
    });
  });

})();
