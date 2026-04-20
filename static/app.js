const API_BASE = window.location.origin;

let sessionId = crypto.randomUUID();
let uploadedFiles = [];
let lastZipBlob = null;

// DOM refs
const form = document.getElementById("campaign-form");
const companyInput = document.getElementById("company_name");
const ejesInput = document.getElementById("ejes");
const quantitySlider = document.getElementById("quantity");
const qtyDisplay = document.getElementById("qty-display");
const styleSelect = document.getElementById("style");
const brandFilesInput = document.getElementById("brand-files");
const fileBrowse = document.getElementById("file-browse");
const fileDropZone = document.getElementById("file-drop-zone");
const fileList = document.getElementById("file-list");
const btnGenerate = document.getElementById("btn-generate");

const formSection = document.getElementById("form-section");
const progressSection = document.getElementById("progress-section");
const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");
const resultsSection = document.getElementById("results-section");
const gallery = document.getElementById("gallery");
const btnDownload = document.getElementById("btn-download");
const btnNew = document.getElementById("btn-new");

// Init: load styles
async function loadStyles() {
    try {
        const res = await fetch(`${API_BASE}/api/styles`);
        const data = await res.json();
        data.styles.forEach((s) => {
            const opt = document.createElement("option");
            opt.value = s;
            opt.textContent = s.charAt(0).toUpperCase() + s.slice(1);
            styleSelect.appendChild(opt);
        });
    } catch (e) {
        console.error("Error loading styles:", e);
    }
}

// Slider
quantitySlider.addEventListener("input", () => {
    qtyDisplay.textContent = quantitySlider.value;
});

// File upload
fileBrowse.addEventListener("click", (e) => {
    e.preventDefault();
    brandFilesInput.click();
});

fileDropZone.addEventListener("click", (e) => {
    if (e.target === fileDropZone || e.target.closest("p")) {
        brandFilesInput.click();
    }
});

fileDropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    fileDropZone.classList.add("drag-over");
});

fileDropZone.addEventListener("dragleave", () => {
    fileDropZone.classList.remove("drag-over");
});

fileDropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    fileDropZone.classList.remove("drag-over");
    handleFiles(e.dataTransfer.files);
});

brandFilesInput.addEventListener("change", () => {
    handleFiles(brandFilesInput.files);
});

function handleFiles(files) {
    for (const f of files) {
        if (f.name.endsWith(".md") || f.name.endsWith(".txt")) {
            if (!uploadedFiles.find((u) => u.name === f.name)) {
                uploadedFiles.push(f);
            }
        }
    }
    renderFileList();
}

function renderFileList() {
    fileList.innerHTML = "";
    uploadedFiles.forEach((f, i) => {
        const li = document.createElement("li");
        li.innerHTML = `<span>📄 ${f.name} (${(f.size / 1024).toFixed(1)} KB)</span>
            <button class="remove-file" data-idx="${i}">✕</button>`;
        fileList.appendChild(li);
    });
    document.querySelectorAll(".remove-file").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            const idx = parseInt(e.target.dataset.idx);
            uploadedFiles.splice(idx, 1);
            renderFileList();
        });
    });
}

// Upload knowledge files
async function uploadKnowledgeFiles() {
    if (uploadedFiles.length === 0) return;

    const formData = new FormData();
    uploadedFiles.forEach((f) => formData.append("files", f));
    formData.append("session_id", sessionId);

    const res = await fetch(`${API_BASE}/api/upload-knowledge`, {
        method: "POST",
        body: formData,
    });
    return res.json();
}

// Progress simulation
function simulateProgress(steps) {
    let current = 0;
    const messages = [
        "Buscando información de la empresa...",
        "Analizando y resumiendo datos...",
        "Generando frases publicitarias con IA...",
        "Creando imágenes con Freepik AI...",
        "Empaquetando resultados...",
    ];

    return setInterval(() => {
        if (current < steps) {
            const pct = Math.min(((current + 1) / steps) * 80, 90);
            progressFill.style.width = pct + "%";
            progressText.textContent =
                messages[Math.min(current, messages.length - 1)];
            current++;
        }
    }, 3000);
}

// Generate campaign
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const companyName = companyInput.value.trim();
    const ejes = ejesInput.value.trim();
    const quantity = parseInt(quantitySlider.value);
    const style = styleSelect.value || undefined;

    if (!companyName || !ejes) return;

    // Show progress
    formSection.classList.add("hidden");
    resultsSection.classList.add("hidden");
    progressSection.classList.remove("hidden");
    progressFill.style.width = "5%";

    const interval = simulateProgress(5);

    try {
        // Upload knowledge docs first if any
        await uploadKnowledgeFiles();

        // Generate campaign
        const body = {
            company_name: companyName,
            ejes: ejes,
            quantity: quantity,
            session_id: sessionId,
        };
        if (style) body.style = style;

        const res = await fetch(`${API_BASE}/api/generate-campaign`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            throw new Error(`Error ${res.status}: ${await res.text()}`);
        }

        lastZipBlob = await res.blob();

        // Extract and preview results from ZIP
        clearInterval(interval);
        progressFill.style.width = "100%";
        progressText.textContent = "¡Campaña generada!";

        await displayResults(lastZipBlob);

        setTimeout(() => {
            progressSection.classList.add("hidden");
            resultsSection.classList.remove("hidden");
        }, 600);
    } catch (err) {
        clearInterval(interval);
        progressSection.classList.add("hidden");
        formSection.classList.remove("hidden");
        alert("Error generando la campaña: " + err.message);
    }
});

// Display results from ZIP
async function displayResults(blob) {
    gallery.innerHTML = "";

    const JSZip = await loadJSZip();
    const zip = await JSZip.loadAsync(blob);

    // Read CSV
    const csvFile = zip.file("campaña.csv") || zip.file("campa\u00f1a.csv");
    let rows = [];
    if (csvFile) {
        const csvText = await csvFile.async("string");
        rows = parseCSV(csvText);
    }

    // Display each item
    for (const row of rows) {
        const num = row["Número"] || row["Numero"];
        const frase = row["Frase Publicitaria"];
        const prompt = row["Prompt de Imagen"];
        const estilo = row["Estilo"];
        const archivo = row["Archivo"];

        const imgFile = zip.file(archivo);
        let imgSrc = "";
        if (imgFile) {
            const imgData = await imgFile.async("base64");
            imgSrc = `data:image/png;base64,${imgData}`;
        }

        const item = document.createElement("div");
        item.className = "gallery-item";
        item.innerHTML = `
            ${imgSrc ? `<img src="${imgSrc}" alt="Imagen ${num}" loading="lazy">` : `<div style="aspect-ratio:1;background:var(--bg-primary);display:flex;align-items:center;justify-content:center;color:var(--gray-dark)">Sin imagen</div>`}
            <div class="item-info">
                <div class="frase">${escapeHtml(frase)}</div>
                <div class="meta">
                    <span class="estilo-badge">${escapeHtml(estilo)}</span>
                </div>
                <div class="prompt-text">${escapeHtml(prompt)}</div>
            </div>
        `;
        gallery.appendChild(item);
    }
}

// Simple CSV parser
function parseCSV(text) {
    const lines = text.split("\n").filter((l) => l.trim());
    if (lines.length < 2) return [];
    const headers = parseCSVLine(lines[0]);
    const rows = [];
    for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        const obj = {};
        headers.forEach((h, idx) => {
            obj[h] = values[idx] || "";
        });
        rows.push(obj);
    }
    return rows;
}

function parseCSVLine(line) {
    const result = [];
    let current = "";
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (ch === '"') {
            if (inQuotes && line[i + 1] === '"') {
                current += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (ch === "," && !inQuotes) {
            result.push(current.trim());
            current = "";
        } else {
            current += ch;
        }
    }
    result.push(current.trim());
    return result;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML;
}

// Download ZIP
btnDownload.addEventListener("click", () => {
    if (!lastZipBlob) return;
    const url = URL.createObjectURL(lastZipBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `campana_${companyInput.value.trim().replace(/\s+/g, "_").substring(0, 30)}.zip`;
    a.click();
    URL.revokeObjectURL(url);
});

// New campaign
btnNew.addEventListener("click", () => {
    resultsSection.classList.add("hidden");
    formSection.classList.remove("hidden");
    sessionId = crypto.randomUUID();
    gallery.innerHTML = "";
    lastZipBlob = null;
});

// Load JSZip from CDN
function loadJSZip() {
    return new Promise((resolve, reject) => {
        if (window.JSZip) return resolve(window.JSZip);
        const script = document.createElement("script");
        script.src =
            "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js";
        script.onload = () => resolve(window.JSZip);
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// Init
loadStyles();
