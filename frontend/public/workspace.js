// Predefined statutory database simulating backend response contract (SIH26045)
const STATUTORY_DB = {
  ashwagandha: {
    answer: "Under Section 3(p) of the Patents Act, 1970, an invention which in effect is traditional knowledge or an aggregation of known properties of traditional components is barred from patentability. Because Withania somnifera (Ashwagandha) is documented in classical Ayurvedic texts, raw extracts fail novelty tests unless synergistic non-obvious efficacy (§ 3(e)) is demonstrated. Additionally, approval from the National Biodiversity Authority (NBA) via Form III is mandatory prior to grant under BDA Rules 2024.",
    citations: [
      {
        document_id: "patents_act_1970",
        source_name: "The Patents Act, 1970",
        page_number: 42,
        section: "Section 3(p)",
        text: "an invention which in effect is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components.",
        bbox: [100, 200, 500, 240]
      },
      {
        document_id: "bda_rules_2024",
        source_name: "Biological Diversity Rules, 2024",
        page_number: 14,
        section: "Rule 18 / Form III",
        text: "Any person applying for any intellectual property right for an invention based on any biological resource obtained from India shall make an application in Form III to National Biodiversity Authority.",
        bbox: [80, 150, 480, 210]
      }
    ]
  },
  classical: {
    answer: "Classical Ayurvedic formulations listed in the First Schedule authoritative texts of the Drugs and Cosmetics Act, 1940 (e.g., Charaka Samhita, Sushruta Samhita) cannot be patented as they constitute established prior art (TKDL). Licensing must proceed through State Licensing Authorities (SLA) under Rule 153.",
    citations: [
      {
        document_id: "dc_act_1940",
        source_name: "Drugs & Cosmetics Act, 1940",
        page_number: 18,
        section: "Section 3(a) & First Schedule",
        text: "Ayurvedic, Siddha or Unani drug includes all medicines intended for internal or external use manufactured exclusively in accordance with the formulae in the authoritative books specified in the First Schedule.",
        bbox: [90, 180, 490, 230]
      }
    ]
  },
  abs: {
    answer: "Access and Benefit Sharing (ABS) compliance is mandatory for commercial exploitation or patenting involving Indian biological resources under BDA Rules 2024. Indian commercial entities must file Form I with the State Biodiversity Board (SBB), while foreign entities or IPR filers require National Biodiversity Authority clearance via Form III.",
    citations: [
      {
        document_id: "bda_rules_2024",
        source_name: "Biological Diversity Rules, 2024",
        page_number: 12,
        section: "Section 6(1) & Rule 18",
        text: "No person shall apply for any intellectual property right by whatever name called in or outside India for any invention based on any research or information on a biological resource obtained from India without previous approval of National Biodiversity Authority.",
        bbox: [110, 210, 520, 260]
      }
    ]
  },
 counsel: {
    answer: "Safe Abstention Protocol Activated: The submitted formulation demonstrates non-obvious synergistic extraction processes that cannot be summarily evaluated under standard TKDL prior-art exclusions (§ 3(p)). Your docket has been flagged for human evaluation and escalated to an empaneled AYUSH IP Facilitator under the SIPP Framework.",
    citations: [
      {
        document_id: "patents_act_1970",
        source_name: "The Patents Act, 1970",
        page_number: 1,
        section: "Section 77 / SIPP Guidelines",
        text: "Facilitators shall provide advisory, drafting, and statutory prosecution support for micro, small and start-up entities before the Patent Office."
      }
    ]
  },
  abstain: {
    answer: "The available statutory sources and TKDL databases do not provide sufficient evidence for a reliable regulatory determination for this query. Human review by an AYUSH patent facilitator is recommended.",
    citations: []
  }
};

// UI Zoom State
let currentZoom = 100;

// Update Right-Column PDF Viewer
function updateEvidenceViewer(cit) {
  const docTitle = document.getElementById("docTitle");
  const pdfEmbed = document.getElementById("pdfEmbed");
  const pageInput = document.getElementById("pageNumberInput");

  if (!cit) {
    if (docTitle) docTitle.innerText = "Safe Abstention Mode";
    if (pageInput) pageInput.value = 1;
    return;
  }

  // Update title text cleanly
  if (docTitle) docTitle.innerText = `${cit.source_name} (${cit.section})`;
  if (pageInput) pageInput.value = cit.page_number;

  // Jump real embedded PDF directly to cited page (forcing browser cache bypass)
  if (pdfEmbed) {
    const timestamp = Date.now();
    pdfEmbed.src = `/sample.pdf?t=${timestamp}#page=${cit.page_number}&view=FitH`;
  }
}

// Append exchange and keep prior messages
function appendExchange(queryText, scenario) {
  const chatFeed = document.getElementById("chatFeed");
  if (!chatFeed) return;

  // Append user bubble
  const userRow = document.createElement("div");
  userRow.className = "msg-row user";
  userRow.innerHTML = `<div class="msg-bubble user-bubble">${queryText}</div>`;
  chatFeed.appendChild(userRow);

  // Append bot bubble
  const botRow = document.createElement("div");
  botRow.className = "msg-row bot";

  let citationsHtml = "";
  if (scenario.citations && scenario.citations.length > 0) {
    citationsHtml = `
      <div class="citation-header"><i class="fa-solid fa-file-circle-check"></i> Statutory Evidence Citations (Click to inspect source)</div>
      <div class="citation-list"></div>
    `;
  }

  botRow.innerHTML = `
    <div class="msg-bubble bot-bubble">
      <p class="legal-summary">${scenario.answer}</p>
      ${citationsHtml}
    </div>
  `;
  chatFeed.appendChild(botRow);

  // Populate interactive citation cards for this bubble
  if (scenario.citations && scenario.citations.length > 0) {
    const list = botRow.querySelector(".citation-list");
    scenario.citations.forEach((cit, idx) => {
      const card = document.createElement("div");
      card.className = `citation-card ${idx === 0 ? "active" : ""}`;
      card.innerHTML = `
        <div class="citation-meta">
          <span>${cit.source_name}</span>
          <span>Page ${cit.page_number}</span>
        </div>
        <div class="citation-section">${cit.section}</div>
        <div class="citation-text">"${cit.text}"</div>
      `;

      card.addEventListener("click", () => {
        document.querySelectorAll(".citation-card").forEach(c => c.classList.remove("active"));
        card.classList.add("active");
        updateEvidenceViewer(cit);
      });

      list.appendChild(card);
    });

    // Default inspect first citation
    updateEvidenceViewer(scenario.citations[0]);
  } else {
    updateEvidenceViewer(null);
  }

  // Scroll smoothly down to newly appended messages
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

// Event Listeners Setup
document.addEventListener("DOMContentLoaded", () => {
  // Input Query Submission
  const chatForm = document.getElementById("chatForm");
  const queryInput = document.getElementById("queryInput");

  if (chatForm && queryInput) {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const query = queryInput.value.trim();
      if (!query) return;

      const q = query.toLowerCase();
      let matchedScenario = STATUTORY_DB.abstain;

      if (q.includes("ashwagandha") || q.includes("extract") || q.includes("patent")) {
        matchedScenario = STATUTORY_DB.ashwagandha;
      } else if (q.includes("classical") || q.includes("samhita") || q.includes("text") || q.includes("charaka")) {
        matchedScenario = STATUTORY_DB.classical;
      } else if (q.includes("abs") || q.includes("nba") || q.includes("biodiversity") || q.includes("form")) {
        matchedScenario = STATUTORY_DB.abs;
      }

      appendExchange(query, matchedScenario);
      queryInput.value = "";
    });
  }

  // PDF Viewer Toolbar: Zoom Controls
  const zoomInBtn = document.getElementById("zoomInBtn");
  const zoomOutBtn = document.getElementById("zoomOutBtn");
  const zoomLevel = document.getElementById("zoomLevel");
  const pageSheet = document.getElementById("pageSheet");

  if (zoomInBtn && pageSheet) {
    zoomInBtn.addEventListener("click", () => {
      if (currentZoom < 140) {
        currentZoom += 10;
        zoomLevel.innerText = `${currentZoom}%`;
        pageSheet.style.transform = `scale(${currentZoom / 100})`;
      }
    });
  }

  if (zoomOutBtn && pageSheet) {
    zoomOutBtn.addEventListener("click", () => {
      if (currentZoom > 70) {
        currentZoom -= 10;
        zoomLevel.innerText = `${currentZoom}%`;
        pageSheet.style.transform = `scale(${currentZoom / 100})`;
      }
    });
  }

  // PDF Viewer Toolbar: Page Navigation
  const prevPageBtn = document.getElementById("prevPageBtn");
  const nextPageBtn = document.getElementById("nextPageBtn");
  const pageInput = document.getElementById("pageNumberInput");
  const sheetPageNum = document.getElementById("sheetPageNum");
  const pdfEmbed = document.getElementById("pdfEmbed");

  if (prevPageBtn && pageInput) {
    prevPageBtn.addEventListener("click", () => {
      let cur = parseInt(pageInput.value, 10);
      if (cur > 1) {
        pageInput.value = cur - 1;
        if (sheetPageNum) sheetPageNum.innerText = `PAGE ${pageInput.value}`;
        if (pdfEmbed) pdfEmbed.src = `/sample.pdf#page=${pageInput.value}&view=FitH`;
      }
    });
  }

  if (nextPageBtn && pageInput) {
    nextPageBtn.addEventListener("click", () => {
      let cur = parseInt(pageInput.value, 10);
      if (cur < 120) {
        pageInput.value = cur + 1;
        if (sheetPageNum) sheetPageNum.innerText = `PAGE ${pageInput.value}`;
        if (pdfEmbed) pdfEmbed.src = `/sample.pdf#page=${pageInput.value}&view=FitH`;
      }
    });
  }

  // Jurisdiction Toggle
  const btnIndia = document.getElementById("btnIndia");
  const btnIntl = document.getElementById("btnIntl");

  if (btnIndia && btnIntl) {
    btnIndia.addEventListener("click", () => {
      btnIndia.classList.add("active");
      btnIntl.classList.remove("active");
    });
    btnIntl.addEventListener("click", () => {
      btnIntl.classList.add("active");
      btnIndia.classList.remove("active");
    });
  }

  // Dynamic Query Injection via Landing Page Mode
    const urlParams = new URLSearchParams(window.location.search);
    const currentMode = urlParams.get("mode") || "classifier";

    if (currentMode === "prior_art" || currentMode === "tkdl") {
      appendExchange(
        "Evaluate Section 3(p) prior-art conflict for classical formulation documented in TKDL.",
        STATUTORY_DB.classical
      );
    } else if (currentMode === "abs") {
      appendExchange(
        "What are the mandatory ABS clearance and Form III requirements under Biological Diversity Rules 2024?",
        STATUTORY_DB.abs
      );
    } else if (currentMode === "counsel" || currentMode === "facilitator") {
      appendExchange(
        "Request statutory evaluation by an empaneled AYUSH patent facilitator for complex poly-herbal extract.",
        STATUTORY_DB.abstain
      );
    } else {
      appendExchange(
        "Can I patent a modified Ashwagandha formulation in India?",
        STATUTORY_DB.ashwagandha
      );
    }
});