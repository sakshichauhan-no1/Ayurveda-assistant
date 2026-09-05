document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------------------------------------
  // 1. JURISDICTION CONTROLLER (India vs International)
  // -------------------------------------------------------------
  const btnIn = document.getElementById("btn-in");
  const btnIntl = document.getElementById("btn-intl");
  const viewDomestic = document.getElementById("view-domestic");
  const viewIntl = document.getElementById("view-international");
  const banner = document.getElementById("status-banner");
  const bannerTitle = document.getElementById("banner-title");
  const bannerDesc = document.getElementById("banner-desc");

  function setJurisdiction(scope) {
    const isDomestic = scope === "domestic";

    if (btnIn && btnIntl) {
      btnIn.classList.toggle("active", isDomestic);
      btnIntl.classList.toggle("active", !isDomestic);
    }

    if (viewDomestic && viewIntl) {
      viewDomestic.classList.toggle("active-view", isDomestic);
      viewIntl.classList.toggle("active-view", !isDomestic);
    }

    if (banner && bannerTitle && bannerDesc) {
      banner.classList.toggle("intl-mode", !isDomestic);
      if (isDomestic) {
        bannerTitle.textContent = "Current Scope: Indian Domestic Framework";
        bannerDesc.textContent = "Grounded in Patents Act (2024 Rules), Biological Diversity Act (2023/2024), TKDL prior-art defenses, and Drugs & Cosmetics Act First Schedule.";
      } else {
        bannerTitle.textContent = "Current Scope: International Treaties & Foreign Market Access";
        bannerDesc.textContent = "Grounded in WIPO GRATK Treaty (2024 mandatory origin disclosure), Nagoya Protocol ABS, Budapest Treaty, and target market botanical drug rules.";
      }
    }
  }

  if (btnIn) btnIn.addEventListener("click", () => setJurisdiction("domestic"));
  if (btnIntl) btnIntl.addEventListener("click", () => setJurisdiction("international"));

  // -------------------------------------------------------------
  // 2. SIGN IN MODAL CONTROLLER (User vs Admin Login)
  // -------------------------------------------------------------
  const openSignInBtn = document.getElementById("signInNavBtn");
  const authOverlay = document.getElementById("authOverlay");
  const modalCloseBtn = document.getElementById("modalCloseBtn");
  const roleStep = document.getElementById("authRoleStep");
  const formStep = document.getElementById("authFormStep");
  const chooseUserBtn = document.getElementById("chooseUserBtn");
  const chooseAdminBtn = document.getElementById("chooseAdminBtn");
  const backToRolesBtn = document.getElementById("backToRolesBtn");

  const activeRoleBadge = document.getElementById("activeRoleBadge");
  const formTitle = document.getElementById("formTitle");
  const formSub = document.getElementById("formSub");
  const identityLabel = document.getElementById("identityLabel");

  function openModal() {
    if (!authOverlay) return;
    authOverlay.classList.add("open");
    showStep("role");
  }

  function closeModal() {
    if (!authOverlay) return;
    authOverlay.classList.remove("open");
  }

  function showStep(step) {
    if (!roleStep || !formStep) return;
    if (step === "role") {
      roleStep.classList.add("active-step");
      formStep.classList.remove("active-step");
    } else {
      roleStep.classList.remove("active-step");
      formStep.classList.add("active-step");
    }
  }

  function selectRole(role) {
    if (role === "admin") {
      if (activeRoleBadge) {
        activeRoleBadge.textContent = "Admin / Official Access";
        activeRoleBadge.style.color = "#c29b38";
      }
      if (formTitle) formTitle.textContent = "Ministry Officer Login";
      if (formSub) formSub.textContent = "Access designated regulatory & verification modules";
      if (identityLabel) identityLabel.textContent = "Govt Email ID / Employee ID";
    } else {
      if (activeRoleBadge) {
        activeRoleBadge.textContent = "Practitioner / Innovator";
        activeRoleBadge.style.color = "#005a9c";
      }
      if (formTitle) formTitle.textContent = "Applicant Sign In";
      if (formSub) formSub.textContent = "Access your IPR formulation repository";
      if (identityLabel) identityLabel.textContent = "Email Address / Registered Mobile";
    }
    showStep("form");
  }

  // Event Listeners for Modal
  if (openSignInBtn) openSignInBtn.addEventListener("click", openModal);
  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);
  if (backToRolesBtn) backToRolesBtn.addEventListener("click", () => showStep("role"));
  if (chooseUserBtn) chooseUserBtn.addEventListener("click", () => selectRole("user"));
  if (chooseAdminBtn) chooseAdminBtn.addEventListener("click", () => selectRole("admin"));
// -------------------------------------------------------------
  // 3. STATUTORY TICKER CONTROLLER (Play / Pause Accessibility)
  // -------------------------------------------------------------
  const tickerBtn = document.getElementById("tickerPauseBtn");
  const tickerContent = document.querySelector(".ticker-content");

  if (tickerBtn && tickerContent) {
    tickerBtn.addEventListener("click", () => {
      const isPaused = tickerContent.classList.toggle("paused");
      tickerBtn.innerHTML = isPaused 
        ? '<i class="fa-solid fa-play"></i>' 
        : '<i class="fa-solid fa-pause"></i>';
    });
  }
  // -------------------------------------------------------------
  // 4. HERO SEARCH & FORMULATION LOOKUP SIMULATOR
  // -------------------------------------------------------------
  const searchInput = document.getElementById("formulationSearchInput");
  const searchBtn = document.getElementById("searchExecBtn");
  const resultCard = document.getElementById("quickResultCard");
  const closeResBtn = document.getElementById("closeResultBtn");
  const resTitle = document.getElementById("resTitle");
  const resDesc = document.getElementById("resDesc");
  const resTypeBadge = document.getElementById("resTypeBadge");
  const tagBtns = document.querySelectorAll(".tag-btn");

  const formulationDB = {
    "ashwagandha": {
      title: "Withania somnifera (Ashwagandha) Root Formulation",
      badge: "Classical / First Schedule",
      desc: "Recorded across multiple First Schedule authoritative Ayurvedic texts. Barred from direct composition patents under Section 3(p). Commercial use of cultivated biological resources requires notification to State Biodiversity Board (SBB) under BDA Rules 2024."
    },
    "triphala": {
      title: "Triphala Churna (Emblica, Terminalia chebula, Terminalia bellirica)",
      badge: "Classical Formulation",
      desc: "Subject to complete prior-art defenses logged in CSIR-TKDL. Any modification must prove unexpected non-obvious synergistic therapeutic activity under Section 3(e) to overcome Indian Patent Office objections."
    },
    "curcumin": {
      title: "Curcumin Enriched Bio-Enhanced Delivery System",
      badge: "Patent & Proprietary / Phytopharmaceutical Candidate",
      desc: "Eligible for patent protection under Section 2(1)(j) if an inventive step in extraction or bioavailability is established. Mandatory NBA Form III filing required before grant of patent."
    }
  };

  function executeSearch(query) {
    const cleanQuery = (query || (searchInput ? searchInput.value : "")).trim().toLowerCase();
    if (!cleanQuery || !resultCard) return;

    let match = null;
    for (const key in formulationDB) {
      if (cleanQuery.includes(key)) {
        match = formulationDB[key];
        break;
      }
    }

    if (!match) {
      match = {
        title: `Statutory Check: "${searchInput.value}"`,
        badge: "Under Legal Review",
        desc: "Requires formulation classification. Must be mapped against the 54 First Schedule texts to determine Section 3(p) patentability bar and BDA 2024 Access & Benefit-Sharing rules."
      };
    }

    if (resTitle) resTitle.textContent = match.title;
    if (resTypeBadge) resTypeBadge.textContent = match.badge;
    if (resDesc) resDesc.textContent = match.desc;
    resultCard.style.display = "block";
  }

  if (searchBtn) searchBtn.addEventListener("click", () => executeSearch());
  if (searchInput) {
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") executeSearch();
    });
  }
  if (closeResBtn) {
    closeResBtn.addEventListener("click", () => {
      resultCard.style.display = "none";
    });
  }

  tagBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const q = btn.getAttribute("data-query");
      if (searchInput) searchInput.value = q;
      executeSearch(q);
    });
  });
  // -------------------------------------------------------------
  // 5. METRIC STATS NUMBER TICKER ANIMATION
  // -------------------------------------------------------------
  const counters = document.querySelectorAll(".counter");
  let animated = false;

  function runCounters() {
    counters.forEach(counter => {
      const target = +counter.getAttribute("data-target");
      const duration = 1200; // 1.2s total duration
      const stepTime = 20;
      const steps = duration / stepTime;
      const increment = target / steps;
      let current = 0;

      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          counter.textContent = target.toLocaleString() + (target === 100 ? "%" : "+");
          clearInterval(timer);
        } else {
          counter.textContent = Math.ceil(current).toLocaleString();
        }
      }, stepTime);
    });
  }

  // Trigger on scroll or immediate load if in view
  window.addEventListener("scroll", () => {
    const section = document.querySelector(".metrics-section");
    if (!section || animated) return;
    const rect = section.getBoundingClientRect();
    if (rect.top <= window.innerHeight - 50) {
      runCounters();
      animated = true;
    }
  });

  // Run on page load if visible
  setTimeout(() => {
    if (!animated) {
      runCounters();
      animated = true;
    }
  }, 300);
  // -------------------------------------------------------------
  // 6. AI REGULATORY ASSISTANT CONTROLLER
  // -------------------------------------------------------------
  const chatToggleBtn = document.getElementById("chatToggleBtn");
  const chatWindow = document.getElementById("chatWindow");
  const closeChatBtn = document.getElementById("closeChatBtn");
  const sendChatBtn = document.getElementById("sendChatBtn");
  const userChatInput = document.getElementById("userChatInput");
  const chatMessages = document.getElementById("chatMessages");

  // Toggle chat widget visibility
  if (chatToggleBtn && chatWindow) {
    chatToggleBtn.addEventListener("click", () => {
      const isHidden = chatWindow.style.display === "none" || chatWindow.style.display === "";
      chatWindow.style.display = isHidden ? "flex" : "none";
      if (isHidden && userChatInput) {
        userChatInput.focus();
      }
    });
  }

  if (closeChatBtn && chatWindow) {
    closeChatBtn.addEventListener("click", () => {
      chatWindow.style.display = "none";
    });
  }

  function appendChatMessage(sender, text) {
    if (!chatMessages) return;
    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${sender}`;
    msgDiv.innerHTML = `<div class="msg-bubble">${text}</div>`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function handleUserMessage() {
    if (!userChatInput) return;
    const query = userChatInput.value.trim();
    if (!query) return;

    // Append user query
    appendChatMessage("user", query);
    userChatInput.value = "";

    // Simulated RAG & statutory reasoning responses
    setTimeout(() => {
      const lower = query.toLowerCase();
      let reply = "Under Section 3(p) of the Patents Act, 1970, an invention which in effect is traditional knowledge or an aggregation of known properties of traditionally known components is not patentable. You must establish non-obvious synergistic efficacy under Section 3(e).";

      if (lower.includes("ashwagandha") || lower.includes("somnifera")) {
        reply = "<strong>Statutory Assessment (Withania somnifera):</strong><br>1. <strong>Patent Bar:</strong> Direct extracts fall under Section 3(p) as cited in classical texts (First Schedule).<br>2. <strong>Novelty Exception:</strong> Only modified delivery systems or proven synergistic combinations (§ 3(e)) are patent-eligible.<br>3. <strong>ABS Obligation:</strong> Commercial use requires intimation to the State Biodiversity Board (SBB) under BDA Rules 2024.";
      } else if (lower.includes("abs") || lower.includes("biodiversity") || lower.includes("nba")) {
        reply = "<strong>Biological Diversity Act (2024 Compliance):</strong><br>• Indian entities require prior intimation to the SBB for commercial utilization.<br>• Foreign entities or entities with foreign shareholding require <strong>Form I approval</strong> from the National Biodiversity Authority (NBA).<br>• Applying for an IPR requires <strong>Form III approval</strong> prior to the grant of patent.";
      } else if (lower.includes("tkdl") || lower.includes("prior art")) {
        reply = "The <strong>Traditional Knowledge Digital Library (TKDL)</strong> acts as prior art under Section 13 read with Section 64 of the Patents Act. Ensure your claims specifically distinguish over citations from authoritative Ayurveda treatises.";
      }

      appendChatMessage("bot", reply);
    }, 500);
  }

  if (sendChatBtn) {
    sendChatBtn.addEventListener("click", handleUserMessage);
  }

  if (userChatInput) {
    userChatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleUserMessage();
      }
    });
  }
  window.addEventListener("click", (e) => {
    if (e.target === authOverlay) closeModal();
  });
});