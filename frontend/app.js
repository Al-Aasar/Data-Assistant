/**
 * Data Assistant - Frontend Application Logic
 * Integrates with FastAPI Backend (/api/health, /api/upload, /api/chat, /api/sample)
 */

(function () {
    "use strict";

    // ==========================================
    // 1. Translations & Localization (i18n)
    // ==========================================
    const i18n = {
        ar: {
            subtitle: "مساعد البيانات متعدد الوكلاء (DuckDB & LangGraph)",
            apiConnecting: "جاري الاتصال بالـ API...",
            apiConnected: "الـ API متصل وجاهز",
            apiDisconnected: "الـ API غير متصل (تأكد من تشغيل السيرفر)",
            loadSample: "عينة تجريبية",
            loadSampleTooltip: "تحميل ملف بيانات تجريبي",
            settingsTooltip: "إعدادات الـ API",
            removeFile: "إزالة الملف",
            uploadDataset: "تحميل مجموعة البيانات",
            dropzonePrompt: "اسحب الملف هنا أو <span class=\"browse-link\">تصفح ملفاتك</span>",
            dropzoneSubtext: "يدعم ملفات CSV, Excel (.xlsx, .xls)",
            processingFile: "جاري فحص وتوصيف البيانات...",
            generatingSchema: "يقوم Knowledge Agent باستخراج الدلالات والعلاقات",
            schemaInspector: "هيكل وتوصيف البيانات",
            noFileLoaded: "قم بتحميل ملف أو الضغط على \"عينة تجريبية\" لعرض الهيكل والأعمدة المقترحة",
            rowMeaningLabel: "دلالة كل سطر:",
            columnsCountUnit: "أعمدة",
            suggestedQuestions: "أسئلة تحليلية مقترحة",
            loadDataForSuggestions: "ستظهر هنا اقتراحات ذكية بمجرد تحليل الملف",
            chatTitle: "محادثة تحليل الأعمال (Business Intelligence)",
            chatDesc: "DuckDB In-Memory Execution + Multi-Agent Self-Correction",
            clearChat: "مسح",
            clearChatTooltip: "مسح المحادثة",
            heroBadge: "نظام تحليل البيانات باللغة الطبيعية",
            heroHeading: "اطرح أي سؤال عن بياناتك بالعربية أو الإنجليزية",
            heroText: "يقوم الوكلاء الذكيون بفحص أمان الاستعلام (Guardrails Agent)، وتوليد استعلام DuckDB SQL فائق السرعة، ومعالجة الأخطاء ذاتياً، وصياغة النتائج في تقرير تنفيذي مبسط لرواد الأعمال ومتخذي القرار.",
            guardrailTitle: "Guardrails Agent",
            guardrailDesc: "حماية البيانات ومنع التعديل أو الاختراق والتركيز فقط على التحليلات الآمنة.",
            duckdbTitle: "DuckDB SQL Engine",
            duckdbDesc: "تنفيذ استعلامات SQL متقدمة بسرعة فائقة في الذاكرة مع تصحيح ذاتي فوري.",
            executiveTitle: "Executive Explainer",
            executiveDesc: "تحويل الأرقام الخام إلى رؤى واستنتاجات تجارية واضحة قابلة للتنفيذ.",
            inputPlaceholder: "اكتب سؤالك هنا عن البيانات (مثال: ما هي أكثر 5 دول تحقيقاً للمبيعات؟)...",
            inputHint: "اضغط <kbd>Enter</kbd> للإرسال، أو <kbd>Shift + Enter</kbd> لسطر جديد",
            sendTitle: "إرسال السؤال (Enter)",
            settingsTitle: "إعدادات الاتصال بالـ API",
            apiUrlLabel: "رابط خادم الـ API (Base URL):",
            apiUrlHelp: "الافتراضي هو http://localhost:8000 أو الخادم المحلي الحالي.",
            testConnection: "اختبار الاتصال",
            saveSettings: "حفظ الإعدادات",
            searchColumns: "بحث في أسماء الأعمدة أو الأدوار...",
            agentThinking: "جاري تحليل السؤال والتحقق من الأمان عبر Guardrails Agent...",
            thinkingSteps: [
                "جاري فحص أمان السؤال عبر Guardrails Agent...",
                "يقوم Analysis Agent بتوليد استعلام DuckDB SQL الآمن...",
                "تنفيذ الاستعلام في محرك DuckDB واستخراج البيانات...",
                "يقوم Result Agent بصياغة التقرير التنفيذي للأعمال..."
            ],
            warnUploadFirst: "يرجى تحميل ملف بيانات (CSV أو Excel) أو الضغط على 'عينة تجريبية' أولاً.",
            queryEmpty: "يرجى كتابة سؤال للتحليل.",
            sqlQueryTitle: "استعلام SQL المُنفذ (DuckDB)",
            queryResultTitle: "جدول نتائج الاستعلام",
            copySql: "نسخ SQL",
            copiedSql: "تم النسخ!",
            exportCsv: "تصدير CSV",
            rowsCount: "عدد الصفوف:",
            connectionSuccess: "تم الاتصال بالـ API بنجاح!",
            connectionFailed: "فشل الاتصال بالـ API. تأكد من تشغيل السيرفر.",
            fileUploadedSuccess: "تم رفع وتحليل الملف بنجاح!",
            sampleLoadedSuccess: "تم تحميل ملف العينة التجريبية بنجاح!",
            tableSummary: "الجدول:",
            rowMeaning: "دلالة كل سطر:",
            noMatchingColumns: "لا توجد أعمدة مطابقة",
            chatCleared: "تم مسح المحادثة",
            csvExported: "تم تصدير ملف CSV بنجاح",
            unsupportedFile: "نوع الملف غير مدعوم. يدعم فقط CSV و Excel",
            failedLoadSample: "تعذر تحميل عينة البيانات تلقائياً. تأكد من تشغيل السيرفر."
        },
        en: {
            subtitle: "Multi-Agent Data Assistant (DuckDB & LangGraph)",
            apiConnecting: "Connecting to API...",
            apiConnected: "API Connected & Ready",
            apiDisconnected: "API Offline (Check if server is running)",
            loadSample: "Demo Data",
            loadSampleTooltip: "Load demo dataset",
            settingsTooltip: "API Settings",
            removeFile: "Remove File",
            uploadDataset: "Upload Dataset",
            dropzonePrompt: "Drop file here or <span class=\"browse-link\">browse files</span>",
            dropzoneSubtext: "Supports CSV, Excel (.xlsx, .xls)",
            processingFile: "Profiling & analyzing dataset...",
            generatingSchema: "Knowledge Agent is extracting semantic schema & metadata",
            schemaInspector: "Data Schema & Profiling",
            noFileLoaded: "Upload a file or click 'Demo Data' to inspect schema and suggested questions",
            rowMeaningLabel: "Row meaning:",
            columnsCountUnit: "columns",
            suggestedQuestions: "Suggested Business Questions",
            loadDataForSuggestions: "Smart question suggestions will appear here once data is analyzed",
            chatTitle: "Business Intelligence Conversation",
            chatDesc: "DuckDB In-Memory Execution + Multi-Agent Self-Correction",
            clearChat: "Clear",
            clearChatTooltip: "Clear chat",
            heroBadge: "Natural Language Data Analysis System",
            heroHeading: "Ask any business question about your data in Arabic or English",
            heroText: "Autonomous agents check safety guardrails, generate optimized DuckDB SQL, self-correct errors, and formulate executive findings for decision-makers.",
            guardrailTitle: "Guardrails Agent",
            guardrailDesc: "Guards against injections, unauthorized mutations, and keeps queries on scope.",
            duckdbTitle: "DuckDB SQL Engine",
            duckdbDesc: "Executes blazing-fast in-memory analytical queries with auto-correction.",
            executiveTitle: "Executive Explainer",
            executiveDesc: "Translates raw numbers and metrics into clear, actionable business findings.",
            inputPlaceholder: "Ask a question about the data (e.g. Which country generated the highest revenue?)...",
            inputHint: "Press <kbd>Enter</kbd> to send, or <kbd>Shift + Enter</kbd> for a new line",
            sendTitle: "Send question (Enter)",
            settingsTitle: "API Connection Settings",
            apiUrlLabel: "API Server Base URL:",
            apiUrlHelp: "Default is http://localhost:8000 or current local host.",
            testConnection: "Test Connection",
            saveSettings: "Save Settings",
            searchColumns: "Search column names or roles...",
            agentThinking: "Analyzing query and verifying safety via Guardrails Agent...",
            thinkingSteps: [
                "Checking safety guardrails with Guardrails Agent...",
                "Analysis Agent is generating safe DuckDB SQL...",
                "Executing SQL query in DuckDB sandbox engine...",
                "Result Agent is crafting the executive business report..."
            ],
            warnUploadFirst: "Please upload a dataset (CSV or Excel) or click 'Demo Data' first.",
            queryEmpty: "Please enter a question to analyze.",
            sqlQueryTitle: "Executed DuckDB SQL Query",
            queryResultTitle: "Query Result Rows",
            copySql: "Copy SQL",
            copiedSql: "Copied!",
            exportCsv: "Export CSV",
            rowsCount: "Rows count:",
            connectionSuccess: "Connected to API successfully!",
            connectionFailed: "Failed to connect to API. Verify backend server is running.",
            fileUploadedSuccess: "File uploaded and profiled successfully!",
            sampleLoadedSuccess: "Demo dataset loaded successfully!",
            tableSummary: "Table:",
            rowMeaning: "Row meaning:",
            noMatchingColumns: "No matching columns",
            chatCleared: "Chat cleared",
            csvExported: "CSV exported successfully",
            unsupportedFile: "Unsupported file format. Please upload CSV or Excel.",
            failedLoadSample: "Failed to load demo data. Ensure server is running."
        }
    };

    // ==========================================
    // 2. Application State
    // ==========================================
    let currentLang = localStorage.getItem("data_assistant_lang") || "ar";
    
    // Auto-detect base API URL
    function detectDefaultApiUrl() {
        const stored = localStorage.getItem("data_assistant_api_url");
        if (stored) return stored.replace(/\/+$/, "");

        const origin = window.location.origin;
        if (window.location.protocol.startsWith("http")) {
            // If served from FastAPI on port 8000 or similar
            return origin;
        }
        // Default fallback for file:// or external frontend runner
        return "http://localhost:8000";
    }

    const state = {
        apiBaseUrl: detectDefaultApiUrl(),
        apiHealthy: false,
        activeFile: null,        // { path, kind, name, size }
        schemaContext: "",       // Raw JSON string
        metadata: null,          // Parsed JSON metadata
        currentColumns: [],      // Extracted columns for filtering
        isThinking: false,
        chatHistory: []
    };

    // DOM Elements
    const dom = {
        html: document.documentElement,
        btnLangAr: document.getElementById("btnLangAr"),
        btnLangEn: document.getElementById("btnLangEn"),
        apiHealthBadge: document.getElementById("apiHealthBadge"),
        apiStatusText: document.getElementById("apiStatusText"),
        btnLoadSample: document.getElementById("btnLoadSample"),
        btnOpenSettings: document.getElementById("btnOpenSettings"),
        btnCloseSettings: document.getElementById("btnCloseSettings"),
        settingsModal: document.getElementById("settingsModal"),
        apiUrlInput: document.getElementById("apiUrlInput"),
        btnTestApi: document.getElementById("btnTestApi"),
        btnSaveSettings: document.getElementById("btnSaveSettings"),
        testResultBox: document.getElementById("testResultBox"),

        // Upload
        dropzone: document.getElementById("dropzone"),
        fileInput: document.getElementById("fileInput"),
        uploadLoader: document.getElementById("uploadLoader"),
        uploadStatusTitle: document.getElementById("uploadStatusTitle"),
        uploadStatusSub: document.getElementById("uploadStatusSub"),
        activeFileCard: document.getElementById("activeFileCard"),
        activeFileName: document.getElementById("activeFileName"),
        activeFileKind: document.getElementById("activeFileKind"),
        activeFileSize: document.getElementById("activeFileSize"),
        btnClearFile: document.getElementById("btnClearFile"),

        // Schema
        schemaEmptyState: document.getElementById("schemaEmptyState"),
        schemaContent: document.getElementById("schemaContent"),
        columnCountBadge: document.getElementById("columnCountBadge"),
        tableSummaryName: document.getElementById("tableSummaryName"),
        tableSummaryDesc: document.getElementById("tableSummaryDesc"),
        tableRowMeaningText: document.getElementById("tableRowMeaningText"),
        columnSearchInput: document.getElementById("columnSearchInput"),
        columnsList: document.getElementById("columnsList"),
        suggestionsContainer: document.getElementById("suggestionsContainer"),
        quickChipsBar: document.getElementById("quickChipsBar"),

        // Chat
        chatMessages: document.getElementById("chatMessages"),
        welcomeHero: document.getElementById("welcomeHero"),
        btnClearChat: document.getElementById("btnClearChat"),
        thinkingIndicator: document.getElementById("thinkingIndicator"),
        thinkingStepText: document.getElementById("thinkingStepText"),
        chatForm: document.getElementById("chatForm"),
        queryInput: document.getElementById("queryInput"),
        btnSend: document.getElementById("btnSend"),
        toastContainer: document.getElementById("toastContainer")
    };

    // ==========================================
    // 3. Internationalization Engine
    // ==========================================
    function setLanguage(lang) {
        currentLang = lang;
        localStorage.setItem("data_assistant_lang", lang);
        dom.html.setAttribute("lang", lang);
        dom.html.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");

        // Toggle active button in prominent switcher
        if (dom.btnLangAr && dom.btnLangEn) {
            dom.btnLangAr.classList.toggle("active", lang === "ar");
            dom.btnLangEn.classList.toggle("active", lang === "en");
        }

        // Update elements with data-i18n
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (i18n[lang] && i18n[lang][key] !== undefined) {
                el.innerHTML = i18n[lang][key];
            }
        });

        // Update placeholders
        document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
            const key = el.getAttribute("data-i18n-placeholder");
            if (i18n[lang] && i18n[lang][key] !== undefined) {
                el.setAttribute("placeholder", i18n[lang][key]);
            }
        });

        // Update title tooltips
        document.querySelectorAll("[data-i18n-title]").forEach(el => {
            const key = el.getAttribute("data-i18n-title");
            if (i18n[lang] && i18n[lang][key] !== undefined) {
                el.setAttribute("title", i18n[lang][key]);
            }
        });

        // Update column count badge
        if (state.currentColumns && state.currentColumns.length > 0) {
            const colCount = state.currentColumns.length;
            dom.columnCountBadge.textContent = `${colCount} ${i18n[lang].columnsCountUnit}`;
        } else {
            dom.columnCountBadge.textContent = `0 ${i18n[lang].columnsCountUnit}`;
        }

        // Update live API badge text according to health state
        updateHealthUI(state.apiHealthy);
    }

    // ==========================================
    // 4. Toast Notifications
    // ==========================================
    function showToast(message, type = "info") {
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;

        let iconSvg = "";
        if (type === "success") {
            iconSvg = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        } else if (type === "error") {
            iconSvg = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
        } else {
            iconSvg = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
        }

        toast.innerHTML = `${iconSvg}<span>${escapeHtml(message)}</span>`;
        dom.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(10px)";
            toast.style.transition = "all 0.25s ease";
            setTimeout(() => toast.remove(), 250);
        }, 3500);
    }

    // ==========================================
    // 5. Backend Health Check
    // ==========================================
    async function checkHealth() {
        const t = i18n[currentLang];
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 4000);

            const res = await fetch(`${state.apiBaseUrl}/api/health`, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (res.ok) {
                const data = await res.json();
                if (data.status === "healthy") {
                    state.apiHealthy = true;
                    updateHealthUI(true);
                    return true;
                }
            }
            state.apiHealthy = false;
            updateHealthUI(false);
            return false;
        } catch (e) {
            state.apiHealthy = false;
            updateHealthUI(false);
            return false;
        }
    }

    function updateHealthUI(isHealthy) {
        const t = i18n[currentLang];
        dom.apiHealthBadge.className = "health-badge " + (isHealthy ? "connected" : "disconnected");
        dom.apiStatusText.textContent = isHealthy ? t.apiConnected : t.apiDisconnected;
    }

    // ==========================================
    // 6. Dataset Ingestion & Upload Handling
    // ==========================================
    async function handleFileUpload(file) {
        if (!file) return;

        const validExts = [".csv", ".xlsx", ".xls"];
        const ext = "." + file.name.split(".").pop().toLowerCase();
        if (!validExts.includes(ext)) {
            showToast(i18n[currentLang].unsupportedFile, "error");
            return;
        }

        // Show uploading progress
        dom.dropzone.classList.add("hidden");
        dom.uploadLoader.classList.remove("hidden");
        dom.activeFileCard.classList.add("hidden");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(`${state.apiBaseUrl}/api/upload`, {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "Failed to upload file");
            }

            const data = await res.json();
            onDatasetLoaded({
                path: data.file_path,
                kind: data.file_kind,
                name: file.name,
                size: formatFileSize(file.size),
                schema_context: data.schema_context,
                metadata: data.metadata
            });

            showToast(i18n[currentLang].fileUploadedSuccess, "success");
        } catch (err) {
            console.error("Upload Error:", err);
            showToast(`${err.message}`, "error");
            dom.dropzone.classList.remove("hidden");
        } finally {
            dom.uploadLoader.classList.add("hidden");
        }
    }

    // Sample Dataset Loader
    async function loadSampleDataset() {
        dom.dropzone.classList.add("hidden");
        dom.uploadLoader.classList.remove("hidden");
        dom.activeFileCard.classList.add("hidden");

        try {
            // First attempt to call /api/sample
            const res = await fetch(`${state.apiBaseUrl}/api/sample`, {
                method: "POST"
            });

            if (res.ok) {
                const data = await res.json();
                onDatasetLoaded({
                    path: data.file_path,
                    kind: data.file_kind || "csv",
                    name: "sample_ecommerce.csv",
                    size: "1.4 KB",
                    schema_context: data.schema_context,
                    metadata: data.metadata
                });
                showToast(i18n[currentLang].sampleLoadedSuccess, "success");
            } else {
                // If /api/sample doesn't exist, we can fallback or alert
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "Sample endpoint failed");
            }
        } catch (err) {
            console.warn("Sample load error:", err);
            showToast(i18n[currentLang].failedLoadSample, "error");
            dom.dropzone.classList.remove("hidden");
        } finally {
            dom.uploadLoader.classList.add("hidden");
        }
    }

    function onDatasetLoaded(fileInfo) {
        state.activeFile = {
            path: fileInfo.path,
            kind: fileInfo.kind,
            name: fileInfo.name,
            size: fileInfo.size
        };
        state.schemaContext = fileInfo.schema_context;
        state.metadata = fileInfo.metadata;

        // Render Active File
        dom.dropzone.classList.add("hidden");
        dom.uploadLoader.classList.add("hidden");
        dom.activeFileCard.classList.remove("hidden");
        dom.activeFileName.textContent = fileInfo.name;
        dom.activeFileKind.textContent = (fileInfo.kind || "CSV").toUpperCase();
        dom.activeFileSize.textContent = fileInfo.size;

        // Render Schema Inspector
        renderSchema(fileInfo.metadata);

        // Render Suggested Questions
        renderSuggestions(fileInfo.metadata);
    }

    function clearActiveFile() {
        state.activeFile = null;
        state.schemaContext = "";
        state.metadata = null;
        state.currentColumns = [];

        dom.activeFileCard.classList.add("hidden");
        dom.dropzone.classList.remove("hidden");
        dom.schemaContent.classList.add("hidden");
        dom.schemaEmptyState.classList.remove("hidden");
        dom.columnCountBadge.textContent = `0 ${i18n[currentLang].columnsCountUnit}`;
        dom.suggestionsContainer.innerHTML = `<p class="empty-hint">${i18n[currentLang].loadDataForSuggestions}</p>`;
        dom.quickChipsBar.innerHTML = "";
        dom.quickChipsBar.classList.add("hidden");
    }

    // ==========================================
    // 7. Schema & Questions Rendering
    // ==========================================
    function renderSchema(metadata) {
        if (!metadata || !metadata.tables || metadata.tables.length === 0) {
            dom.schemaContent.classList.add("hidden");
            dom.schemaEmptyState.classList.remove("hidden");
            return;
        }

        dom.schemaEmptyState.classList.add("hidden");
        dom.schemaContent.classList.remove("hidden");

        const primaryTable = metadata.tables[0];
        dom.tableSummaryName.textContent = primaryTable.table_name || (currentLang === "ar" ? "الجدول الرئيسي" : "Main Table");
        dom.tableSummaryDesc.textContent = primaryTable.description || "--";
        dom.tableRowMeaningText.textContent = primaryTable.row_meaning || "--";

        state.currentColumns = primaryTable.columns || [];
        const colCount = state.currentColumns.length;
        dom.columnCountBadge.textContent = `${colCount} ${i18n[currentLang].columnsCountUnit}`;

        renderColumnsList(state.currentColumns);
    }

    function renderColumnsList(columns) {
        dom.columnsList.innerHTML = "";
        if (!columns || columns.length === 0) {
            dom.columnsList.innerHTML = `<p class="empty-hint">${i18n[currentLang].noMatchingColumns}</p>`;
            return;
        }

        columns.forEach(col => {
            const item = document.createElement("div");
            item.className = "column-item";

            const roleClass = `role-${(col.role || "ignore").toLowerCase()}`;
            const semanticType = col.semantic_type || "";

            item.innerHTML = `
                <div class="column-top">
                    <span class="column-name" title="${escapeHtml(col.name)}">${escapeHtml(col.name)}</span>
                    <div class="column-tags">
                        <span class="tag-dtype">${escapeHtml(col.dtype || "any")}</span>
                        <span class="tag-role ${roleClass}">${escapeHtml(col.role || "ignore")}</span>
                    </div>
                </div>
                ${col.description ? `<p class="column-desc">${escapeHtml(col.description)}</p>` : ""}
                ${col.value_notes ? `<p class="column-notes">${escapeHtml(col.value_notes)}</p>` : ""}
            `;
            dom.columnsList.appendChild(item);
        });
    }

    function renderSuggestions(metadata) {
        dom.suggestionsContainer.innerHTML = "";
        dom.quickChipsBar.innerHTML = "";

        if (!metadata || !metadata.tables) {
            dom.suggestionsContainer.innerHTML = `<p class="empty-hint">${i18n[currentLang].loadDataForSuggestions}</p>`;
            dom.quickChipsBar.classList.add("hidden");
            return;
        }

        let allQuestions = [];
        metadata.tables.forEach(tbl => {
            if (tbl.example_questions && Array.isArray(tbl.example_questions)) {
                allQuestions.push(...tbl.example_questions);
            }
        });

        if (allQuestions.length === 0) {
            dom.suggestionsContainer.innerHTML = `<p class="empty-hint">${i18n[currentLang].loadDataForSuggestions}</p>`;
            dom.quickChipsBar.classList.add("hidden");
            return;
        }

        dom.quickChipsBar.classList.remove("hidden");

        allQuestions.slice(0, 6).forEach(q => {
            // Sidebar chip
            const chip = document.createElement("button");
            chip.className = "prompt-chip";
            chip.textContent = q;
            chip.addEventListener("click", () => {
                dom.queryInput.value = q;
                dom.queryInput.focus();
                adjustTextareaHeight();
            });
            dom.suggestionsContainer.appendChild(chip);

            // Quick chip above input
            const quickChip = document.createElement("button");
            quickChip.type = "button";
            quickChip.className = "quick-chip";
            quickChip.textContent = q;
            quickChip.addEventListener("click", () => {
                dom.queryInput.value = q;
                sendUserQuery(q);
            });
            dom.quickChipsBar.appendChild(quickChip);
        });
    }

    // ==========================================
    // 8. Chat & Query Execution
    // ==========================================
    let stepInterval = null;

    function startThinkingAnimation() {
        dom.thinkingIndicator.classList.remove("hidden");
        const steps = i18n[currentLang].thinkingSteps;
        let stepIdx = 0;
        dom.thinkingStepText.textContent = steps[0];

        if (stepInterval) clearInterval(stepInterval);
        stepInterval = setInterval(() => {
            stepIdx = (stepIdx + 1) % steps.length;
            dom.thinkingStepText.textContent = steps[stepIdx];
        }, 1800);

        scrollChatToBottom();
    }

    function stopThinkingAnimation() {
        dom.thinkingIndicator.classList.add("hidden");
        if (stepInterval) {
            clearInterval(stepInterval);
            stepInterval = null;
        }
    }

    async function sendUserQuery(text) {
        const query = (text || dom.queryInput.value).trim();
        if (!query) {
            showToast(i18n[currentLang].queryEmpty, "error");
            return;
        }

        if (!state.activeFile) {
            showToast(i18n[currentLang].warnUploadFirst, "error");
            return;
        }

        // Hide welcome hero on first message
        if (dom.welcomeHero) {
            dom.welcomeHero.style.display = "none";
        }

        // Append User Message Bubble
        appendUserMessage(query);
        dom.queryInput.value = "";
        adjustTextareaHeight();

        // Lock send button and start thinking
        state.isThinking = true;
        dom.btnSend.disabled = true;
        startThinkingAnimation();

        try {
            const payload = {
                user_query: query,
                file_path: state.activeFile.path,
                file_kind: state.activeFile.kind,
                schema_context: state.schemaContext
            };

            const res = await fetch(`${state.apiBaseUrl}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || `Server returned error (${res.status})`);
            }

            const data = await res.json();
            stopThinkingAnimation();
            appendAssistantMessage(data);

        } catch (err) {
            console.error("Chat error:", err);
            stopThinkingAnimation();
            appendErrorMessage(err.message);
        } finally {
            state.isThinking = false;
            dom.btnSend.disabled = false;
            dom.queryInput.focus();
            scrollChatToBottom();
        }
    }

    function appendUserMessage(text) {
        const row = document.createElement("div");
        row.className = "message-row message-user";
        row.innerHTML = `
            <div class="message-bubble">
                <p class="user-text">${escapeHtml(text)}</p>
            </div>
        `;
        dom.chatMessages.appendChild(row);
        scrollChatToBottom();
    }

    function appendAssistantMessage(data) {
        const t = i18n[currentLang];
        const row = document.createElement("div");
        row.className = "message-row message-assistant";

        const guardAllowed = data.guardrail_allowed !== false;
        const guardCategory = data.guardrail_category || (guardAllowed ? "OK" : "BLOCKED");
        const guardClass = guardAllowed ? "guardrail-ok" : "guardrail-blocked";

        // Format executive response
        const formattedText = formatMarkdown(data.final_response || "No response generated.");

        // SQL section
        let sqlHtml = "";
        if (data.sql) {
            const escapedSql = escapeHtml(data.sql);
            sqlHtml = `
                <div class="collapsible-box open">
                    <div class="collapsible-header" onclick="this.parentElement.classList.toggle('open')">
                        <div class="collapsible-title">
                            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="16 18 22 12 16 6"></polyline>
                                <polyline points="8 6 2 12 8 18"></polyline>
                            </svg>
                            <span>${t.sqlQueryTitle}</span>
                        </div>
                        <div class="collapsible-actions">
                            <button type="button" class="btn btn-ghost btn-sm btn-copy-sql" onclick="event.stopPropagation(); window.copySqlToClipboard(this)">
                                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                </svg>
                                <span class="copy-label">${t.copySql}</span>
                            </button>
                            <svg class="chevron-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </div>
                    </div>
                    <div class="collapsible-content">
                        <pre class="sql-code-container"><code>${escapedSql}</code></pre>
                    </div>
                </div>
            `;
        }

        // Query Result Table section
        let tableHtml = "";
        if (data.query_result && Array.isArray(data.query_result) && data.query_result.length > 0) {
            const tableGenerated = generateResultTable(data.query_result);
            tableHtml = `
                <div class="collapsible-box open">
                    <div class="collapsible-header" onclick="this.parentElement.classList.toggle('open')">
                        <div class="collapsible-title">
                            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="3" y1="9" x2="21" y2="9"></line>
                                <line x1="9" y1="21" x2="9" y2="9"></line>
                            </svg>
                            <span>${t.queryResultTitle}</span>
                        </div>
                        <div class="collapsible-actions">
                            <button type="button" class="btn btn-ghost btn-sm" onclick="event.stopPropagation(); window.exportResultToCsv(this)">
                                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                    <polyline points="7 10 12 15 17 10"></polyline>
                                    <line x1="12" y1="15" x2="12" y2="3"></line>
                                </svg>
                                <span>${t.exportCsv}</span>
                            </button>
                            <svg class="chevron-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </div>
                    </div>
                    <div class="collapsible-content">
                        ${tableGenerated}
                    </div>
                </div>
            `;
        }

        row.innerHTML = `
            <div class="avatar-box">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"></path>
                    <rect x="3" y="8" width="18" height="12" rx="2"></rect>
                    <circle cx="9" cy="13" r="1"></circle>
                    <circle cx="15" cy="13" r="1"></circle>
                    <path d="M9 17h6"></path>
                </svg>
            </div>
            <div class="message-content-wrapper">
                <div class="message-bubble">
                    <div class="message-meta-header">
                        <span class="meta-agent-name">Data Assistant</span>
                        <div class="meta-badges">
                            <span class="badge-guardrail ${guardClass}">${escapeHtml(guardCategory)}</span>
                        </div>
                    </div>
                    <div class="response-text">
                        ${formattedText}
                    </div>
                    ${sqlHtml}
                    ${tableHtml}
                    <div class="message-footer-meta">
                        ${data.llm_calls ? `<span>LLM Calls: ${data.llm_calls}</span>` : ""}
                        <span>•</span>
                        <span>${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                </div>
            </div>
        `;

        dom.chatMessages.appendChild(row);
        scrollChatToBottom();
    }

    function appendErrorMessage(errorMsg) {
        const row = document.createElement("div");
        row.className = "message-row message-assistant";
        row.innerHTML = `
            <div class="avatar-box" style="background: linear-gradient(135deg, #f43f5e, #e11d48);">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
            </div>
            <div class="message-content-wrapper">
                <div class="message-bubble" style="border-color: rgba(244, 63, 94, 0.3);">
                    <div class="message-meta-header">
                        <span class="meta-agent-name" style="color: #fb7185;">Error</span>
                    </div>
                    <div class="response-text" style="color: #fca5a5;">
                        <p>${escapeHtml(errorMsg)}</p>
                    </div>
                </div>
            </div>
        `;
        dom.chatMessages.appendChild(row);
        scrollChatToBottom();
    }

    // ==========================================
    // 9. Table & Text Formatting Helpers
    // ==========================================
    function generateResultTable(records) {
        if (!records || records.length === 0) return "<p>No data</p>";

        const t = i18n[currentLang];
        const headers = Object.keys(records[0]);

        let ths = headers.map(h => `<th>${escapeHtml(h)}</th>`).join("");
        let trs = records.map(row => {
            let tds = headers.map(h => {
                let val = row[h];
                if (typeof val === "number") {
                    val = Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2);
                } else if (val === null || val === undefined) {
                    val = `<span style="color: var(--text-muted);">NULL</span>`;
                } else {
                    val = escapeHtml(String(val));
                }
                return `<td>${val}</td>`;
            }).join("");
            return `<tr>${tds}</tr>`;
        }).join("");

        return `
            <div class="table-scroll-wrapper">
                <table class="result-table">
                    <thead><tr>${ths}</tr></thead>
                    <tbody>${trs}</tbody>
                </table>
            </div>
            <div class="table-footer">
                <span>${t.rowsCount} <strong>${records.length}</strong></span>
            </div>
        `;
    }

    function formatMarkdown(text) {
        if (!text) return "";
        let html = escapeHtml(text);

        // Bold: **text** or __text__
        html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        html = html.replace(/__(.*?)__/g, "<strong>$1</strong>");

        // Code: `code`
        html = html.replace(/`([^`]+)`/g, "<code style=\"background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-family: monospace;\">$1</code>");

        // Line breaks & bullet points
        const lines = html.split("\n");
        let inList = false;
        let result = [];

        lines.forEach(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith("* ") || trimmed.startsWith("- ") || trimmed.startsWith("• ")) {
                if (!inList) {
                    inList = true;
                    result.push("<ul>");
                }
                result.push(`<li>${trimmed.substring(2)}</li>`);
            } else {
                if (inList) {
                    inList = false;
                    result.push("</ul>");
                }
                if (trimmed.length > 0) {
                    result.push(`<p>${trimmed}</p>`);
                }
            }
        });

        if (inList) result.push("</ul>");
        return result.join("");
    }

    function escapeHtml(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatFileSize(bytes) {
        if (!bytes || bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
    }

    function scrollChatToBottom() {
        requestAnimationFrame(() => {
            dom.chatMessages.scrollTop = dom.chatMessages.scrollHeight;
        });
    }

    function adjustTextareaHeight() {
        dom.queryInput.style.height = "auto";
        dom.queryInput.style.height = Math.min(dom.queryInput.scrollHeight, 120) + "px";
    }

    // ==========================================
    // 10. Global Window Handlers (Copy & Export)
    // ==========================================
    window.copySqlToClipboard = function (btn) {
        const pre = btn.closest(".collapsible-box").querySelector("code");
        if (!pre) return;
        const sqlText = pre.innerText || pre.textContent;

        navigator.clipboard.writeText(sqlText).then(() => {
            const label = btn.querySelector(".copy-label");
            const original = label.textContent;
            label.textContent = i18n[currentLang].copiedSql;
            setTimeout(() => {
                label.textContent = original;
            }, 2000);
            showToast(i18n[currentLang].copiedSql, "success");
        }).catch(err => {
            console.error("Clipboard failed:", err);
        });
    };

    window.exportResultToCsv = function (btn) {
        const box = btn.closest(".collapsible-box");
        const table = box.querySelector(".result-table");
        if (!table) return;

        let csv = [];
        const rows = table.querySelectorAll("tr");
        for (let i = 0; i < rows.length; i++) {
            let row = [];
            let cols = rows[i].querySelectorAll("td, th");
            for (let j = 0; j < cols.length; j++) {
                let cellData = cols[j].innerText.replace(/"/g, '""');
                row.push(`"${cellData}"`);
            }
            csv.push(row.join(","));
        }

        const csvContent = "\uFEFF" + csv.join("\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `data_assistant_export_${Date.now()}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast(i18n[currentLang].csvExported, "success");
    };

    // ==========================================
    // 11. Event Listeners Setup
    // ==========================================
    function setupEventListeners() {
        // Language Switcher Buttons
        if (dom.btnLangAr) {
            dom.btnLangAr.addEventListener("click", () => {
                if (currentLang !== "ar") setLanguage("ar");
            });
        }
        if (dom.btnLangEn) {
            dom.btnLangEn.addEventListener("click", () => {
                if (currentLang !== "en") setLanguage("en");
            });
        }

        // Load Sample Dataset Button
        dom.btnLoadSample.addEventListener("click", () => {
            loadSampleDataset();
        });

        // Dropzone & File Input
        dom.dropzone.addEventListener("click", () => dom.fileInput.click());
        dom.fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFileUpload(e.target.files[0]);
            }
        });

        // Drag & Drop
        dom.dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dom.dropzone.classList.add("drag-over");
        });
        dom.dropzone.addEventListener("dragleave", () => {
            dom.dropzone.classList.remove("drag-over");
        });
        dom.dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dom.dropzone.classList.remove("drag-over");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        // Clear active file
        dom.btnClearFile.addEventListener("click", () => {
            clearActiveFile();
        });

        // Filter schema columns
        dom.columnSearchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (!query) {
                renderColumnsList(state.currentColumns);
                return;
            }
            const filtered = state.currentColumns.filter(c =>
                (c.name && c.name.toLowerCase().includes(query)) ||
                (c.role && c.role.toLowerCase().includes(query)) ||
                (c.semantic_type && c.semantic_type.toLowerCase().includes(query)) ||
                (c.description && c.description.toLowerCase().includes(query))
            );
            renderColumnsList(filtered);
        });

        // Chat input resize & submit
        dom.queryInput.addEventListener("input", adjustTextareaHeight);
        dom.queryInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                dom.chatForm.requestSubmit();
            }
        });

        dom.chatForm.addEventListener("submit", (e) => {
            e.preventDefault();
            if (!state.isThinking) {
                sendUserQuery();
            }
        });

        // Clear Chat
        dom.btnClearChat.addEventListener("click", () => {
            dom.chatMessages.innerHTML = "";
            if (dom.welcomeHero) {
                dom.chatMessages.appendChild(dom.welcomeHero);
                dom.welcomeHero.style.display = "block";
            }
            showToast(i18n[currentLang].chatCleared, "info");
        });

        // Settings Modal
        dom.btnOpenSettings.addEventListener("click", () => {
            dom.apiUrlInput.value = state.apiBaseUrl;
            dom.testResultBox.className = "connection-test-result hidden";
            dom.testResultBox.textContent = "";
            dom.settingsModal.classList.remove("hidden");
        });

        dom.btnCloseSettings.addEventListener("click", () => {
            dom.settingsModal.classList.add("hidden");
        });

        dom.settingsModal.addEventListener("click", (e) => {
            if (e.target === dom.settingsModal) {
                dom.settingsModal.classList.add("hidden");
            }
        });

        // Test API Connection inside modal
        dom.btnTestApi.addEventListener("click", async () => {
            const testUrl = dom.apiUrlInput.value.trim().replace(/\/+$/, "");
            dom.testResultBox.className = "connection-test-result connecting";
            dom.testResultBox.classList.remove("hidden");
            dom.testResultBox.textContent = i18n[currentLang].apiConnecting;

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 4000);
                const res = await fetch(`${testUrl}/api/health`, { signal: controller.signal });
                clearTimeout(timeoutId);

                if (res.ok) {
                    dom.testResultBox.className = "connection-test-result test-success";
                    dom.testResultBox.textContent = i18n[currentLang].connectionSuccess;
                } else {
                    throw new Error("HTTP " + res.status);
                }
            } catch (err) {
                dom.testResultBox.className = "connection-test-result test-error";
                dom.testResultBox.textContent = i18n[currentLang].connectionFailed;
            }
        });

        // Save Settings
        dom.btnSaveSettings.addEventListener("click", () => {
            const newUrl = dom.apiUrlInput.value.trim().replace(/\/+$/, "");
            state.apiBaseUrl = newUrl;
            localStorage.setItem("data_assistant_api_url", newUrl);
            dom.settingsModal.classList.add("hidden");
            showToast(i18n[currentLang].saveSettings, "success");
            checkHealth();
        });
    }

    // ==========================================
    // 12. Initialization
    // ==========================================
    function init() {
        setLanguage(currentLang);
        setupEventListeners();
        checkHealth();

        // Health check polling every 15s
        setInterval(checkHealth, 15000);
    }

    // Start on DOM ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

})();
