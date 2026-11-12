/* AI Processing Pipeline Overlay Module */

const STAGES = [
    "Resume Uploaded",
    "Resume Parsing",
    "Skill Extraction",
    "Semantic Matching",
    "Multi-Agent Analysis",
    "Candidate Ranking",
    "Explainability"
];

const STATUS_MESSAGES = [
    "Extracting textual blocks...",
    "Building semantic skill graphs...",
    "Running spatial vector match...",
    "Resolving adaptive profiles...",
    "Synthesizing recruitment insights...",
    "Calculating match explanations..."
];

let overlayTimer = null;
let currentStageIndex = 0;
let messageTimer = null;

export const loadingOverlay = {
    show(isDeterministic = false) {
        if (document.getElementById('ai-processing-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'ai-processing-overlay';
        overlay.className = 'fixed inset-0 bg-dark/95 backdrop-blur-md flex items-center justify-center z-[9999] opacity-0 transition-opacity duration-300';
        
        const stagesHTML = STAGES.map((stage, idx) => `
            <div class="flex items-center gap-4 py-1" id="overlay-stage-row-${idx}">
                <div id="overlay-stage-circle-${idx}" class="w-6 h-6 rounded-full flex items-center justify-center border border-slate-800 text-[10px] font-bold text-slate-500 bg-dark transition-colors duration-300">
                    ${idx + 1}
                </div>
                <span id="overlay-stage-label-${idx}" class="text-sm font-medium text-slate-500 transition-colors duration-300">${stage}</span>
            </div>
        `).join('');

        overlay.innerHTML = `
            <div class="speed-lines-bg"></div>
            <div class="relative w-full max-w-md p-8 mx-4 bg-slateDark/80 border border-emerald-500/10 rounded-2xl shadow-glow text-center">
                <div class="mb-4 flex justify-center">
                    <span class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400 animate-pulse">
                        <i data-lucide="cpu" style="width: 20px; height: 20px;"></i>
                    </span>
                </div>
                <h3 class="text-lg font-bold text-white mb-1">Processing Pipeline</h3>
                <p id="overlay-status-message" class="text-xs text-emerald-400/80 mb-6 font-mono">Initializing pipelines...</p>
                
                <!-- Progress Line -->
                <div class="w-full bg-slate-900 h-1 rounded-full mb-6 overflow-hidden relative">
                    <div id="overlay-progress-bar" class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 w-0 transition-all duration-500"></div>
                </div>
                
                <!-- Pipeline Stages -->
                <div class="flex flex-col gap-2 text-left pl-6">
                    ${stagesHTML}
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        
        // Render lucide icons inside loader
        if (window.lucide) {
            window.lucide.createIcons();
        }

        // Trigger opacity fade-in
        setTimeout(() => {
            overlay.classList.remove('opacity-0');
        }, 10);

        currentStageIndex = 0;
        this.updateStage(0);

        // Cycle status messages
        let msgIdx = 0;
        messageTimer = setInterval(() => {
            const msgEl = document.getElementById('overlay-status-message');
            if (msgEl) {
                msgEl.textContent = STATUS_MESSAGES[msgIdx % STATUS_MESSAGES.length];
                msgIdx++;
            }
        }, 2200);

        // If not deterministic, automatically advance stages simulating progression
        if (!isDeterministic) {
            overlayTimer = setInterval(() => {
                if (currentStageIndex < STAGES.length - 1) {
                    currentStageIndex++;
                    this.updateStage(currentStageIndex);
                } else {
                    clearInterval(overlayTimer);
                }
            }, 1600);
        }
    },

    updateStage(index) {
        currentStageIndex = index;
        const total = STAGES.length;
        const percent = Math.min(((index + 1) / total) * 100, 100);
        
        const progressBar = document.getElementById('overlay-progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }

        for (let i = 0; i < total; i++) {
            const circle = document.getElementById(`overlay-stage-circle-${i}`);
            const label = document.getElementById(`overlay-stage-label-${i}`);
            if (!circle || !label) continue;

            if (i < index) {
                // Completed
                circle.innerHTML = '\u2713';
                circle.className = 'w-6 h-6 rounded-full flex items-center justify-center border-none text-[10px] font-bold text-white bg-emerald-500 transition-all duration-300';
                label.className = 'text-sm font-semibold text-emerald-400 transition-colors duration-300';
            } else if (i === index) {
                // Active
                circle.innerHTML = '\u2B24';
                circle.className = 'w-6 h-6 rounded-full flex items-center justify-center border-emerald-500/40 text-[8px] font-bold text-emerald-400 bg-emerald-500/10 animate-pulse transition-colors duration-300';
                label.className = 'text-sm font-bold text-white transition-colors duration-300';
            } else {
                // Pending
                circle.innerHTML = `${i + 1}`;
                circle.className = 'w-6 h-6 rounded-full flex items-center justify-center border border-slate-800 text-[10px] font-bold text-slate-600 bg-dark transition-colors duration-300';
                label.className = 'text-sm font-medium text-slate-600 transition-colors duration-300';
            }
        }
    },

    hide() {
        const overlay = document.getElementById('ai-processing-overlay');
        if (!overlay) return;

        clearInterval(overlayTimer);
        clearInterval(messageTimer);

        overlay.classList.add('opacity-0');
        setTimeout(() => {
            overlay.remove();
        }, 300);
    }
};

// Bind to window for absolute convenience in legacy codes
window.loadingOverlay = loadingOverlay;
