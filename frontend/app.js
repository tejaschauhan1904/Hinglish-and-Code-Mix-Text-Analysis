// Hinglish AI Studio - Interactive Frontend Logic

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const inputText = document.getElementById("inputText");
    const charCount = document.getElementById("charCount");
    const wordCount = document.getElementById("wordCount");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const clearBtn = document.getElementById("clearBtn");
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const themeIcon = document.getElementById("themeIcon");
    const copyTranslationBtn = document.getElementById("copyTranslationBtn");
    const toast = document.getElementById("toast");
    const currentFeatureTitle = document.getElementById("currentFeatureTitle");
    
    // View sections
    const sectionTranslation = document.getElementById("sectionTranslation");
    const sectionNER = document.getElementById("sectionNER");
    const sectionSentiment = document.getElementById("sectionSentiment");
    const sectionPOS = document.getElementById("sectionPOS");
    const datasetView = document.getElementById("datasetView");
    const consoleCard = document.querySelector(".console-card");
    const statsGrid = document.getElementById("statsGrid");

    let currentFeature = "all";
    let cachedDatasetData = [];

    // ==========================================
    // 1. Text & Stats Counting
    // ==========================================
    function updateInputStats() {
        const text = inputText.value;
        charCount.textContent = `${text.length} characters`;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        wordCount.textContent = `${words} words`;
    }

    inputText.addEventListener("input", updateInputStats);
    updateInputStats();

    // ==========================================
    // 2. Theme Toggling
    // ==========================================
    themeToggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("light-theme");
        const isLight = document.body.classList.contains("light-theme");
        themeIcon.textContent = isLight ? "🌙" : "☀️";
    });

    // ==========================================
    // 3. Toast Notifications
    // ==========================================
    function showToast(msg) {
        toast.textContent = msg;
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 2500);
    }

    copyTranslationBtn.addEventListener("click", () => {
        const text = document.getElementById("targetDisplay").textContent;
        navigator.clipboard.writeText(text).then(() => {
            showToast("Copied translation to clipboard!");
        });
    });

    // ==========================================
    // 4. Feature Navigation & Toggling
    // ==========================================
    const featureTitles = {
        all: "All-in-One Studio",
        pos: "Part-of-Speech & Language ID",
        ner: "Named Entity Recognition (NER)",
        sentiment: "Sentiment Analysis",
        translation: "Hinglish to English Translation",
        datasets: "Dataset Explorer"
    };

    function switchFeature(feature) {
        currentFeature = feature;
        currentFeatureTitle.textContent = featureTitles[feature] || "Hinglish Suite";

        // Update nav items active state
        document.querySelectorAll(".nav-item").forEach(item => {
            if (item.dataset.feature === feature) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        if (feature === "datasets") {
            // Hide normal input & result cards
            consoleCard.style.display = "none";
            statsGrid.style.display = "none";
            sectionTranslation.style.display = "none";
            sectionNER.style.display = "none";
            sectionSentiment.style.display = "none";
            sectionPOS.style.display = "none";
            datasetView.style.display = "block";
            loadDataset("ner");
            return;
        }

        // Show normal input & result cards
        consoleCard.style.display = "block";
        statsGrid.style.display = "grid";
        datasetView.style.display = "none";

        if (feature === "all") {
            sectionTranslation.style.display = "block";
            sectionNER.style.display = "block";
            sectionSentiment.style.display = "block";
            sectionPOS.style.display = "block";
        } else if (feature === "pos") {
            sectionTranslation.style.display = "none";
            sectionNER.style.display = "none";
            sectionSentiment.style.display = "none";
            sectionPOS.style.display = "block";
        } else if (feature === "ner") {
            sectionTranslation.style.display = "none";
            sectionNER.style.display = "block";
            sectionSentiment.style.display = "none";
            sectionPOS.style.display = "none";
        } else if (feature === "sentiment") {
            sectionTranslation.style.display = "none";
            sectionNER.style.display = "none";
            sectionSentiment.style.display = "block";
            sectionPOS.style.display = "none";
        } else if (feature === "translation") {
            sectionTranslation.style.display = "block";
            sectionNER.style.display = "none";
            sectionSentiment.style.display = "none";
            sectionPOS.style.display = "none";
        }
    }

    document.querySelectorAll(".nav-item").forEach(btn => {
        btn.addEventListener("click", () => {
            switchFeature(btn.dataset.feature);
        });
    });

    // ==========================================
    // 5. Preset Buttons & Quick Pills
    // ==========================================
    function setInputAndAnalyze(text) {
        inputText.value = text;
        updateInputStats();
        if (currentFeature === "datasets") {
            switchFeature("all");
        }
        runAnalysis();
    }

    document.querySelectorAll(".preset-btn, .pill").forEach(el => {
        el.addEventListener("click", () => {
            setInputAndAnalyze(el.dataset.text);
        });
    });

    clearBtn.addEventListener("click", () => {
        inputText.value = "";
        updateInputStats();
        inputText.focus();
    });

    // Ctrl+Enter shortcut
    inputText.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            runAnalysis();
        }
    });

    analyzeBtn.addEventListener("click", runAnalysis);

    // ==========================================
    // 6. NLP Analysis API Call & Render
    // ==========================================
    async function runAnalysis() {
        const text = inputText.value.trim();
        if (!text) {
            showToast("Please enter some Hinglish text first.");
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.querySelector(".btn-text").textContent = "Analyzing...";

        try {
            const resp = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });

            if (!resp.ok) throw new Error("Analysis failed");
            const data = await resp.json();
            renderResults(data);
        } catch (err) {
            console.error(err);
            showToast("Error connecting to analysis engine.");
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.querySelector(".btn-text").textContent = "Analyze Text";
        }
    }

    function renderResults(res) {
        // 1. Top Summary Stat Cards
        document.getElementById("statSentenceType").textContent = res.sentence_type;
        document.getElementById("statLangRatio").textContent = `Hindi: ${res.hindi_percentage.toFixed(1)}% | English: ${res.english_percentage.toFixed(1)}%`;
        
        const sent = res.sentiment;
        document.getElementById("statSentiment").textContent = sent.sentiment;
        document.getElementById("statPolarity").textContent = `Polarity: ${sent.polarity_score > 0 ? '+' : ''}${sent.polarity_score.toFixed(2)}`;
        
        const ner = res.ner;
        document.getElementById("statEntityCount").textContent = `${ner.entity_count} detected`;
        const entityTypes = Object.keys(ner.labels_summary).join(", ") || "None";
        document.getElementById("statEntityTypes").textContent = entityTypes;

        const trans = res.translation;
        document.getElementById("statTransMethod").textContent = trans.method;
        document.getElementById("statTransConf").textContent = `Confidence: ${trans.confidence}%`;

        // 2. Translation View
        document.getElementById("sourceDisplay").textContent = trans.source_text;
        document.getElementById("targetDisplay").textContent = trans.translated_text;
        document.getElementById("transMethodBadge").textContent = trans.method;
        document.getElementById("transDesc").textContent = trans.description;

        // 3. Named Entity Recognition (NER)
        document.getElementById("nerCounterBadge").textContent = `${ner.entity_count} Entities Found`;
        const chipsContainer = document.getElementById("entityChipsContainer");
        const nerTbody = document.getElementById("nerTableBody");
        chipsContainer.innerHTML = "";
        nerTbody.innerHTML = "";

        if (ner.entities.length === 0) {
            chipsContainer.innerHTML = `<span class="no-signals">No prominent named entities detected in this sentence.</span>`;
            nerTbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--text-muted);">No named entities identified.</td></tr>`;
        } else {
            ner.entities.forEach(ent => {
                // Chip
                const chip = document.createElement("span");
                chip.className = `entity-chip ${ent.label}`;
                chip.innerHTML = `${ent.text} <span class="chip-tag">${ent.label}</span>`;
                chipsContainer.appendChild(chip);

                // Table row
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${ent.text}</strong></td>
                    <td><span class="entity-chip ${ent.label}" style="font-size:11px; padding:2px 8px;">${ent.label}</span></td>
                    <td>${ent.description}</td>
                    <td><span style="font-family: monospace; color: var(--text-muted);">${ent.start} : ${ent.end}</span></td>
                `;
                nerTbody.appendChild(tr);
            });
        }

        // Check for 'kal' context
        const kalEntity = ner.entities.find(e => e.text.toLowerCase() === "kal");
        const kalBanner = document.getElementById("kalContextBanner");
        if (kalEntity) {
            kalBanner.style.display = "flex";
            document.getElementById("kalContextExplanation").textContent = kalEntity.description;
        } else {
            kalBanner.style.display = "none";
        }

        // 4. Sentiment View
        const pill = document.getElementById("sentimentPill");
        pill.textContent = sent.badge;
        pill.className = `sentiment-pill ${sent.sentiment.toLowerCase()}`;

        document.getElementById("polarityNumber").textContent = `${sent.polarity_score > 0 ? '+' : ''}${sent.polarity_score.toFixed(2)}`;
        
        // Indicator position: -1 -> 5%, 0 -> 50%, +1 -> 95%
        const leftPercent = 50 + (sent.polarity_score * 45);
        document.getElementById("spectrumIndicator").style.left = `${leftPercent}%`;

        // Signal tags
        const posTags = document.getElementById("positiveSignals");
        posTags.innerHTML = sent.positive_keywords.length > 0
            ? sent.positive_keywords.map(k => `<span class="signal-chip" style="color:#34d399;">+ ${k}</span>`).join("")
            : `<span class="no-signals">None</span>`;

        const negTags = document.getElementById("negativeSignals");
        negTags.innerHTML = sent.negative_keywords.length > 0
            ? sent.negative_keywords.map(k => `<span class="signal-chip" style="color:#fb7185;">- ${k}</span>`).join("")
            : `<span class="no-signals">None</span>`;

        // Banners
        const alertsContainer = document.getElementById("sentimentAlerts");
        alertsContainer.innerHTML = "";
        if (sent.negations && sent.negations.length > 0) {
            alertsContainer.innerHTML += `
                <div class="alert-banner negation">
                    <span>🔄</span>
                    <span><strong>Negation Inversion Active:</strong> Detected construct <em>${sent.negations.join(", ")}</em>. Polarity flipped.</span>
                </div>
            `;
        }
        if (sent.intensifiers && sent.intensifiers.length > 0) {
            alertsContainer.innerHTML += `
                <div class="alert-banner intensifier">
                    <span>⚡</span>
                    <span><strong>Intensifier Scaling Active:</strong> Amplified by <em>${sent.intensifiers.join(", ")}</em>.</span>
                </div>
            `;
        }

        document.getElementById("sentimentReasoning").textContent = sent.explanation;

        // 5. POS & Language ID
        document.getElementById("langPillSummary").innerHTML = `
            <span class="lang-pill hindi">Hindi: ${res.hindi_count}</span>
            <span class="lang-pill english">English: ${res.english_count}</span>
            <span class="lang-pill other">Other: ${res.other_count}</span>
        `;

        const tokenContainer = document.getElementById("tokenChipsDisplay");
        tokenContainer.innerHTML = "";
        const posTbody = document.getElementById("posTableBody");
        posTbody.innerHTML = "";

        res.tokens.forEach((tok, index) => {
            // Visual Token Badge
            const badge = document.createElement("div");
            badge.className = "token-badge";
            badge.innerHTML = `
                <span class="token-word">${tok.Token}</span>
                <span class="token-pos">${tok["POS Tag"]}</span>
            `;
            tokenContainer.appendChild(badge);

            // Table row
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><span style="color:var(--text-muted);">${index + 1}</span></td>
                <td><strong>${tok.Token}</strong></td>
                <td><span class="lang-pill ${tok.Language.toLowerCase().replace(/[^a-z]/g, '')}">${tok.Language}</span></td>
                <td><code>${tok["POS Tag"]}</code></td>
                <td>${getPosCategory(tok["POS Tag"])}</td>
            `;
            posTbody.appendChild(tr);
        });

        document.getElementById("posSummaryText").textContent = res.summary;
    }

    function getPosCategory(tag) {
        const categories = {
            NOUN: "Noun (Naming word)",
            VERB: "Verb (Action/State)",
            PRON: "Pronoun (Substitute)",
            ADJ: "Adjective (Modifier)",
            ADV: "Adverb (Degree/Time)",
            AUX: "Auxiliary Verb (Helping)",
            DET: "Determiner (Article/Demonstrative)",
            ADP: "Adposition (Preposition/Postposition)",
            CONJ: "Conjunction (Connector)",
            SCONJ: "Subordinating Conjunction",
            PART: "Particle (Discourse/Negation)",
            INTJ: "Interjection (Emotion/Greeting)",
            NUM: "Numeral (Number)",
            PUNCT: "Punctuation Mark",
            X: "Unclassified / Other"
        };
        return categories[tag] || "General";
    }

    // ==========================================
    // 7. Dataset Explorer Logic
    // ==========================================
    const datasetSelect = document.getElementById("datasetSelect");
    const datasetSearchInput = document.getElementById("datasetSearchInput");
    const datasetTableHead = document.getElementById("datasetTableHead");
    const datasetTableBody = document.getElementById("datasetTableBody");
    const datasetRecordCount = document.getElementById("datasetRecordCount");

    datasetSelect.addEventListener("change", () => {
        loadDataset(datasetSelect.value);
    });

    datasetSearchInput.addEventListener("input", () => {
        filterDatasetRows(datasetSearchInput.value);
    });

    async function loadDataset(name) {
        datasetTableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 24px;">Loading dataset...</td></tr>`;
        try {
            const resp = await fetch(`/api/datasets?name=${name}`);
            if (!resp.ok) throw new Error("Dataset failed to load");
            const res = await resp.json();
            
            cachedDatasetData = res.data;
            renderDatasetTable(res.columns, res.data);
            datasetRecordCount.textContent = `Total: ${res.total_records} records`;
        } catch (err) {
            console.error(err);
            datasetTableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: #ef4444;">Failed to load dataset.</td></tr>`;
        }
    }

    function renderDatasetTable(columns, rows) {
        // Render headers
        datasetTableHead.innerHTML = `<tr>${columns.map(c => `<th>${c}</th>`).join("")}</tr>`;
        
        // Render rows
        if (rows.length === 0) {
            datasetTableBody.innerHTML = `<tr><td colspan="${columns.length}" style="text-align:center; color: var(--text-muted);">No records found.</td></tr>`;
            return;
        }

        datasetTableBody.innerHTML = rows.map(r => `
            <tr>${columns.map(c => `<td>${escapeHtml(String(r[c] !== undefined ? r[c] : ''))}</td>`).join("")}</tr>
        `).join("");
    }

    function filterDatasetRows(query) {
        const q = query.toLowerCase().trim();
        if (!q) {
            const cols = cachedDatasetData.length > 0 ? Object.keys(cachedDatasetData[0]) : [];
            renderDatasetTable(cols, cachedDatasetData);
            datasetRecordCount.textContent = `Total: ${cachedDatasetData.length} records`;
            return;
        }

        const filtered = cachedDatasetData.filter(row => {
            return Object.values(row).some(val => String(val).toLowerCase().includes(q));
        });

        const cols = cachedDatasetData.length > 0 ? Object.keys(cachedDatasetData[0]) : [];
        renderDatasetTable(cols, filtered);
        datasetRecordCount.textContent = `Showing: ${filtered.length} of ${cachedDatasetData.length} records`;
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
    }

    // Auto-run initial analysis
    runAnalysis();
});
