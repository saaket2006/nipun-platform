import * as api from '../api.js';
import * as state from '../state.js';
import { getEmptyStateHTML } from '../components/emptyState.js';
import { toggleButtonLoading } from '../components/loadingSpinner.js';
import { populateCandidateProfileUI } from '../components/profileSection.js';
import { MESSAGES, ROUTES } from '../constants.js';
import { escapeHTML, sanitizeUrl } from '../utils.js';

let candUploadedFile = null;
let initialized = false;

/**
 * Binds event listeners for candidate workspace views (runs once on startup).
 */
export function initCandidatePage() {
    if (initialized) return;

    const candDropZone = document.getElementById('cand-drop-zone');
    const candResumesInput = document.getElementById('cand-resumes');
    const candResumesHeader = document.getElementById('cand-resumes-header');
    const candProcessBtn = document.getElementById('cand-process-btn');
    const candResultsContainer = document.getElementById('cand-results-container');
    const candJobDescription = document.getElementById('cand-job-description');

    if (candDropZone && candResumesInput) {
        candDropZone.addEventListener('click', () => candResumesInput.click());

        candDropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            candDropZone.classList.add('drag-over');
        });

        candDropZone.addEventListener('dragleave', () => {
            candDropZone.classList.remove('drag-over');
        });

        candDropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            candDropZone.classList.remove('drag-over');
            handleCandidateFile(e.dataTransfer.files[0]);
        });

        candResumesInput.addEventListener('change', (e) => {
            handleCandidateFile(e.target.files[0]);
        });
    }

    function handleCandidateFile(file) {
        if (!file) return;
        if (file.name.match(/\.(pdf|docx)$/i)) {
            candUploadedFile = file;
            renderFileList();
            updateResumeCountDisplay();
        } else {
            alert(`File ${file.name} is not a valid format. Only PDF and DOCX are supported.`);
        }
    }

    window.removeCandFile = () => {
        candUploadedFile = null;
        renderFileList();
        updateResumeCountDisplay();
        if (candDropZone) {
            candDropZone.classList.remove('collapsed', 'active');
        }
        if (candResumesHeader) {
            candResumesHeader.classList.add('hidden');
        }
    };

    if (candProcessBtn) {
        candProcessBtn.addEventListener('click', async () => {
            const jd = candJobDescription.value.trim();
            const labelInput = document.getElementById('cand-resume-label');
            const labelValue = labelInput ? labelInput.value.trim() : '';

            if (!jd) {
                alert(MESSAGES.ENTER_JD);
                return;
            }
            if (!candUploadedFile) {
                alert(MESSAGES.UPLOAD_RESUME);
                return;
            }

            candResultsContainer.classList.add('hidden');

            if (candDropZone) {
                candDropZone.classList.add('collapsed');
                candDropZone.classList.remove('active');
            }
            if (candResumesHeader) {
                candResumesHeader.classList.remove('hidden');
            }
            updateResumeCountDisplay();

            const formData = new FormData();
            formData.append('job_description', jd);
            formData.append('resume', candUploadedFile);
            if (labelValue) {
                formData.append('label', labelValue);
            }

            toggleButtonLoading(candProcessBtn, true, "Analyzing...", "Analyze Resume");
            if (window.loadingOverlay) window.loadingOverlay.show();

            try {
                const results = await api.screenResumeCandidate(formData);
                // Invalidate cached candidate stats and resumes so dashboard shows fresh data on navigation
                state.setCandidateStats(null);
                state.setCandidateResumes(null);
                renderCandidateAnalysisResults(results.results[0]);
                if (labelInput) {
                    labelInput.value = '';
                }
            } catch (err) {
                alert(err.message);
            } finally {
                if (window.loadingOverlay) window.loadingOverlay.hide();
                toggleButtonLoading(candProcessBtn, false, "Analyzing...", "Analyze Resume");
            }
        });
    }

    const modal = document.getElementById('cand-analysis-view-modal');
    const closeBtn = document.getElementById('close-cand-analysis-btn');

    if (modal) {
        let isMouseDownOnBackdrop = false;

        // Prevent accidental closing when clicking, dragging, selecting text, or interacting inside the report card
        const card = modal.querySelector('.quick-view-card');
        if (card) {
            card.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                isMouseDownOnBackdrop = false;
            });
            card.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        modal.addEventListener('mousedown', (e) => {
            isMouseDownOnBackdrop = (e.target === modal);
        });

        modal.addEventListener('mouseup', (e) => {
            if (isMouseDownOnBackdrop && e.target === modal) {
                closeCandidateAnalysisModal();
            }
            isMouseDownOnBackdrop = false;
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeCandidateAnalysisModal();
            });
        }

        // Close on Escape keypress when modal is visible
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                closeCandidateAnalysisModal();
            }
        });
    }

    initialized = true;
}

export function closeCandidateAnalysisModal() {
    const modal = document.getElementById('cand-analysis-view-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
    // Navigate back to the candidate dashboard via existing hash router
    if (window.location.hash !== ROUTES.CANDIDATE_DASHBOARD) {
        window.location.hash = ROUTES.CANDIDATE_DASHBOARD;
    }
}
window.closeCandidateAnalysisModal = closeCandidateAnalysisModal;

function updateResumeCountDisplay() {
    const countSpan = document.getElementById('cand-resumes-count');
    if (countSpan) {
        countSpan.textContent = candUploadedFile ? "Resume (1)" : "Resume (0)";
    }
}

function renderFileList() {
    const list = document.getElementById('cand-file-list');
    if (!list) return;
    list.innerHTML = '';
    if (candUploadedFile) {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${candUploadedFile.name}</span>
            <span style="color: #ef4444; cursor:pointer;" onclick="removeCandFile()">✕</span>
        `;
        list.appendChild(li);
    }
}

export function clearCandidateWorkspaceState() {
    const candJobDescription = document.getElementById('cand-job-description');
    const candResumeLabel = document.getElementById('cand-resume-label');
    const candDropZone = document.getElementById('cand-drop-zone');
    const candResumesHeader = document.getElementById('cand-resumes-header');
    const candResultsContainer = document.getElementById('cand-results-container');
    
    if (candJobDescription) candJobDescription.value = '';
    if (candResumeLabel) candResumeLabel.value = '';
    candUploadedFile = null;
    renderFileList();
    if (candDropZone) candDropZone.classList.remove('collapsed', 'active');
    if (candResumesHeader) candResumesHeader.classList.add('hidden');
    if (candResultsContainer) candResultsContainer.classList.add('hidden');
}

let currentDashboardReqId = 0;

/**
 * Page view initializer for Candidate Dashboard.
 * Always fetches fresh, authoritative statistics and analysis history,
 * guarding against race conditions and stale response overwrites.
 */
export async function initializeCandidateDashboard() {
    const dashCandName = document.getElementById('dash-cand-name');
    const dashCandStatus = document.getElementById('dash-cand-status');
    const dashCandField = document.getElementById('dash-cand-field');
    const dashCandDomain = document.getElementById('dash-cand-domain');
    const candTopUserName = document.getElementById('cand-top-user-name');
    const statsContainer = document.getElementById('cand-stats-container');
    const timelineContainer = document.getElementById('candidate-timeline-list');

    if (!statsContainer) return;

    // Track request sequence to prevent delayed responses from overwriting newer state
    const reqId = ++currentDashboardReqId;

    // 1. Loading state indicators to prevent permanent "..." and avoid false empty states
    if (dashCandName && (dashCandName.textContent === "..." || !dashCandName.textContent)) dashCandName.textContent = "Loading...";
    if (dashCandStatus && (dashCandStatus.textContent === "..." || !dashCandStatus.textContent)) dashCandStatus.textContent = "Loading...";
    if (dashCandField && (dashCandField.textContent === "..." || !dashCandField.textContent)) dashCandField.textContent = "Loading...";
    if (dashCandDomain && (dashCandDomain.textContent === "..." || !dashCandDomain.textContent)) dashCandDomain.textContent = "Loading...";

    statsContainer.innerHTML = `
        <div class="dashboard-loading" style="width: 100%; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 180px; padding: 1.5rem; text-align: center; color: var(--color-muted); background: var(--color-paper-2); border: 1px solid var(--color-rule); border-radius: 12px;">
            <div class="loader" style="margin: 0 auto 0.75rem;"></div>
            <span style="font-size: 0.875rem; font-family: var(--font-body); color: var(--color-ink-2);">Loading your dashboard data...</span>
        </div>
    `;

    if (timelineContainer) {
        timelineContainer.innerHTML = `
            <div class="timeline-loading" style="width: 100%; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 180px; padding: 1.5rem; text-align: center; color: var(--color-muted); background: var(--color-paper-2); border: 1px solid var(--color-rule); border-radius: 12px;">
                <div class="loader" style="margin: 0 auto 0.75rem;"></div>
                <span style="font-size: 0.875rem; font-family: var(--font-body); color: var(--color-ink-2);">Loading analysis history...</span>
            </div>
        `;
    }

    try {
        // 2. Fetch or retrieve candidate profile
        let profile = state.getProfile();
        if (!profile) {
            profile = await api.getProfile();
            state.setProfile(profile);
        }

        if (reqId !== currentDashboardReqId) return;

        const candName = profile.display_name || profile.email.split('@')[0];
        const statusVal = profile.candidate_profile?.current_status || "N/A";
        const fieldVal = profile.candidate_profile?.field_of_study || "N/A";
        const domainVal = profile.candidate_profile?.current_domain || "N/A";

        if (dashCandName) dashCandName.textContent = candName;
        if (dashCandStatus) dashCandStatus.textContent = statusVal;
        if (dashCandField) dashCandField.textContent = fieldVal;
        if (dashCandDomain) dashCandDomain.textContent = domainVal;
        if (candTopUserName) candTopUserName.textContent = candName;

        // 3. Always fetch fresh authoritative stats and history in parallel
        const [stats, historyList] = await Promise.all([
            api.getCandidateStats(),
            api.getCandidateResumes()
        ]);

        if (reqId !== currentDashboardReqId) return;

        // Synchronize in-memory shared client state
        state.setCandidateStats(stats);
        state.setCandidateResumes(historyList);
        
        if (stats && stats.latest_ats_score !== null && stats.latest_ats_score !== undefined) {
            let formattedDate = "N/A";
            if (stats.last_analysis_date) {
                const dateObj = new Date(stats.last_analysis_date);
                formattedDate = dateObj.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            }
            
            // Generate Career Progress Timeline strictly based on actual recorded history per target role
            const safeHistoryList = Array.isArray(historyList) ? historyList : [];
            
            // Group safeHistoryList by normalized target role:
            const roleGroups = {};
            safeHistoryList.forEach(item => {
                const rawRole = (item.job_description_title || "").trim();
                const roleKey = rawRole.toLowerCase() || "unspecified";
                if (!roleGroups[roleKey]) {
                    roleGroups[roleKey] = {
                        roleTitle: rawRole || "General Evaluation",
                        items: []
                    };
                }
                roleGroups[roleKey].items.push(item);
            });

            // Find eligible group with >= 2 versions:
            let activeGroup = null;
            const latestRoleKey = safeHistoryList.length > 0 ? (safeHistoryList[0].job_description_title || "").trim().toLowerCase() : "";
            if (latestRoleKey && roleGroups[latestRoleKey] && roleGroups[latestRoleKey].items.length >= 2) {
                activeGroup = roleGroups[latestRoleKey];
            } else {
                for (const key of Object.keys(roleGroups)) {
                    if (roleGroups[key].items.length >= 2) {
                        if (!activeGroup || roleGroups[key].items.length > activeGroup.items.length) {
                            activeGroup = roleGroups[key];
                        }
                    }
                }
            }

            let progressTimelineHTML = "";

            const renderNode = (item) => {
                const dateStr = new Date(item.uploaded_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                });
                const rawScore = Math.round(Number(item.ats_score) || 0);
                let circleClass = 'score-low';
                if (rawScore >= 70) circleClass = 'score-high';
                else if (rawScore >= 40) circleClass = 'score-med';

                return `
                    <div class="career-node">
                        <span class="career-node-version">V${item.version}</span>
                        <div class="career-node-circle ${circleClass}">
                            ${rawScore}%
                        </div>
                        <span class="career-node-date">${dateStr}</span>
                    </div>
                `;
            };

            const renderConnector = (delta) => {
                let deltaClass = 'delta-zero';
                let deltaText = '0 pts';
                if (delta > 0) {
                    deltaClass = 'delta-pos';
                    deltaText = `+${delta} pts`;
                } else if (delta < 0) {
                    deltaClass = 'delta-neg';
                    deltaText = `${delta} pts`;
                }

                return `
                    <div class="career-node-connector" aria-label="Score change: ${deltaText}">
                        <div class="career-connector-track"></div>
                        <div class="career-connector-badge ${deltaClass}">
                            <span>${deltaText}</span>
                            <span class="career-connector-arrow" aria-hidden="true">→</span>
                        </div>
                    </div>
                `;
            };

            if (activeGroup && activeGroup.items.length >= 2) {
                const chronologicalList = [...activeGroup.items].sort((a, b) => new Date(a.uploaded_at) - new Date(b.uploaded_at));
                const oldest = chronologicalList[0];
                const newest = chronologicalList[chronologicalList.length - 1];
                const scoreDiff = Number((newest.ats_score - oldest.ats_score).toFixed(1));

                let deltaBadge = "";
                if (scoreDiff > 0) {
                    deltaBadge = `<span style="font-family: var(--font-mono); font-size: 0.8125rem; color: var(--color-forest); font-weight: 700; background: var(--color-forest-light); border: 1px solid var(--color-forest-border); padding: 0.2rem 0.6rem; border-radius: 4px;">+${scoreDiff} pts</span>`;
                } else if (scoreDiff < 0) {
                    deltaBadge = `<span style="font-family: var(--font-mono); font-size: 0.8125rem; color: var(--color-clay); font-weight: 700; background: var(--color-clay-light); border: 1px solid var(--color-clay-border); padding: 0.2rem 0.6rem; border-radius: 4px;">${scoreDiff} pts</span>`;
                } else {
                    deltaBadge = `<span style="font-family: var(--font-mono); font-size: 0.8125rem; color: var(--color-muted); font-weight: 600; background: var(--color-paper-3); border: 1px solid var(--color-rule); padding: 0.2rem 0.6rem; border-radius: 4px;">0 pts change</span>`;
                }

                let timelineStepsHtml = '';
                for (let i = 0; i < chronologicalList.length; i++) {
                    timelineStepsHtml += renderNode(chronologicalList[i]);
                    if (i < chronologicalList.length - 1) {
                        const currScore = Number(chronologicalList[i].ats_score) || 0;
                        const nextScore = Number(chronologicalList[i + 1].ats_score) || 0;
                        const stepDelta = Number((nextScore - currScore).toFixed(1));
                        timelineStepsHtml += renderConnector(stepDelta);
                    }
                }

                progressTimelineHTML = `
                    <div class="stat-card span-two" style="grid-column: span 2;">
                        <div class="stat-header" style="margin-bottom: 0.85rem;">
                            <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
                                <span class="stat-title" style="font-weight: 600; color: var(--color-ink); font-size: 0.9375rem; display: inline-flex; align-items: center; gap: 0.5rem;">
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                                    <span>Career Progress Timeline</span>
                                </span>
                                ${deltaBadge}
                            </div>
                            <span class="stat-icon" style="color: var(--color-forest); display: inline-flex;">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                            </span>
                        </div>
                        <div class="career-ribbon-container">
                            ${timelineStepsHtml}
                        </div>
                    </div>
                `;
            } else if (safeHistoryList.length > 0) {
                // When only one version exists for a target role, show just one circular indicator with its version and match percentage.
                // Below it, display a short, clean message explaining that another version must be analysed to track progress.
                const singleItem = safeHistoryList[0];
                progressTimelineHTML = `
                    <div class="stat-card span-two" style="grid-column: span 2;">
                        <div class="stat-header" style="margin-bottom: 0.85rem;">
                            <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
                                <span class="stat-title" style="font-weight: 600; color: var(--color-ink); font-size: 0.9375rem; display: inline-flex; align-items: center; gap: 0.5rem;">
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                                    <span>Career Progress Timeline</span>
                                </span>
                            </div>
                            <span class="stat-icon" style="color: var(--color-forest); display: inline-flex;">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                            </span>
                        </div>
                        <div class="career-ribbon-container">
                            ${renderNode(singleItem)}
                        </div>
                        <p class="career-timeline-hint">Another version must be analysed to track progress.</p>
                    </div>
                `;
            }
            
            statsContainer.innerHTML = `
                <div class="rec-grid">
                    <div class="stat-card">
                        <div class="stat-header">
                            <span class="stat-title">Latest Account Benchmark</span>
                            <span class="stat-icon" style="color: var(--color-forest); display: inline-flex;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
                            </span>
                        </div>
                        <div class="stat-value" id="cand-stat-latest-score">${stats.latest_ats_score}%</div>
                        <p class="stat-description">Most recent evaluation match across target roles</p>
                    </div>
                    <div class="stat-card">
                        <div class="stat-header">
                            <span class="stat-title">Last Analysis Date</span>
                            <span class="stat-icon" style="color: var(--color-forest); display: inline-flex;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                            </span>
                        </div>
                        <div class="stat-value" id="cand-stat-last-date">${formattedDate}</div>
                        <p class="stat-description">Timestamp of the last run</p>
                    </div>
                    ${progressTimelineHTML}
                </div>
            `;
        } else {
            statsContainer.innerHTML = `
                <div class="empty-state-card" style="width: 100%; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 180px; padding: 2.5rem 1.5rem; text-align: center; background: var(--color-paper-2); border: 1px solid var(--color-rule); border-radius: 12px;">
                    <div style="width: 48px; height: 48px; border-radius: 50%; background: var(--color-paper-3); border: 1px solid var(--color-rule-2); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; color: var(--color-muted);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                    </div>
                    <p style="margin: 0 0 0.35rem 0; font-family: var(--font-display); font-size: 1.15rem; font-weight: 600; color: var(--color-ink);">No Resumes Analyzed Yet</p>
                    <p style="margin: 0 0 1.25rem 0; font-size: 0.875rem; color: var(--color-muted); max-width: 420px; line-height: 1.5;">Upload a resume and evaluate it against target job descriptions to unlock match scoring, skill gap detection, and personalized recommendations.</p>
                    <a href="#/candidate/screen" class="glow-btn" style="text-decoration: none; font-size: 0.8125rem; padding: 0.55rem 1.2rem; background: var(--color-forest); color: #fff; border-radius: 6px; font-weight: 600; display: inline-flex; align-items: center; gap: 0.4rem;">
                        <span>+ Analyze Your First Resume</span>
                    </a>
                </div>
            `;
        }

        renderTimelineList(historyList);

    } catch (err) {
        if (reqId !== currentDashboardReqId) return;
        console.error("Error loading candidate dashboard data:", err);
        const user = state.getUser();
        if (dashCandName && (dashCandName.textContent === "..." || dashCandName.textContent === "Loading...")) {
            dashCandName.textContent = user?.display_name || user?.email?.split('@')[0] || "Candidate";
        }
        if (dashCandStatus && (dashCandStatus.textContent === "..." || dashCandStatus.textContent === "Loading...")) {
            dashCandStatus.textContent = "Unavailable";
        }
        if (dashCandField && (dashCandField.textContent === "..." || dashCandField.textContent === "Loading...")) {
            dashCandField.textContent = "Unavailable";
        }
        if (dashCandDomain && (dashCandDomain.textContent === "..." || dashCandDomain.textContent === "Loading...")) {
            dashCandDomain.textContent = "Unavailable";
        }
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--color-clay); background: var(--color-paper-2); border: 1px solid var(--color-rule); border-radius: 8px;">
                    <p style="margin: 0 0 0.5rem 0; font-weight: 600;">Could not load dashboard statistics.</p>
                    <p style="margin: 0 0 1rem 0; font-size: 0.85rem; color: var(--color-muted);">${err.message || "An unexpected error occurred."}</p>
                    <button onclick="initializeCandidateDashboard()" class="glow-btn secondary" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">Retry</button>
                </div>
            `;
        }
        if (timelineContainer) {
            timelineContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--color-clay); background: var(--color-paper-2); border: 1px solid var(--color-rule); border-radius: 8px;">
                    <p style="margin: 0 0 0.5rem 0; font-weight: 600;">Could not load analysis history.</p>
                    <button onclick="initializeCandidateDashboard()" class="glow-btn secondary" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">Retry</button>
                </div>
            `;
        }
    }
}
window.initializeCandidateDashboard = initializeCandidateDashboard;

function renderTimelineList(historyList) {
    const container = document.getElementById('candidate-timeline-list');
    if (!container) return;

    if (!historyList || historyList.length === 0) {
        container.innerHTML = `
            <div class="empty-state-card" style="width: 100%; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 180px; padding: 2.25rem 1.5rem; text-align: center; background: var(--color-paper-2); border: 1px solid var(--color-rule); border-radius: 12px;">
                <div style="width: 44px; height: 44px; border-radius: 50%; background: var(--color-paper-3); border: 1px solid var(--color-rule-2); display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem auto; color: var(--color-muted);">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                </div>
                <p style="margin: 0 0 0.25rem 0; font-family: var(--font-display); font-size: 1.05rem; font-weight: 600; color: var(--color-ink);">No Analysis History</p>
                <p style="margin: 0; font-size: 0.8125rem; color: var(--color-muted); max-width: 380px; line-height: 1.45;">Past resume versions evaluated against job descriptions will appear here with version tracking and match score history.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = historyList.map((item, idx) => {
        const isNewest = idx === 0;
        const uploadDate = new Date(item.uploaded_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        let scoreClass = 'low-score';
        if (item.ats_score >= 70) {
            scoreClass = 'high-score';
        } else if (item.ats_score >= 40) {
            scoreClass = 'med-score';
        }

        const jdTitle = item.job_description_title || "General Evaluation";
        const jdSummary = item.job_description_summary || "";

        return `
            <div class="glass-card timeline-card ${isNewest ? 'is-newest' : ''}">
                ${isNewest ? `
                    <div class="latest-version-badge" title="Latest version" aria-label="Latest version">
                        <span class="latest-version-dot" aria-hidden="true"></span>
                        <span>Latest version</span>
                    </div>
                ` : ''}
                <div class="timeline-content-grid">
                    <div class="timeline-main-info">
                        <div class="timeline-title-row">
                            <h3 class="timeline-title">
                                <span>${escapeHTML(item.label)}</span>
                                <span class="timeline-version-tag">V${item.version}</span>
                            </h3>
                            <button onclick="renameCandidateAnalysis(${item.id}, '${item.label.replace(/'/g, "\\'")}')" class="timeline-rename-btn" title="Rename Label" aria-label="Rename Label">✎</button>
                        </div>
                        <p class="timeline-meta-text">
                            <span style="display: inline-flex; align-items: center; gap: 0.35rem;">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                                ${escapeHTML(item.original_filename)}
                            </span>
                            <span>•</span>
                            <span style="display: inline-flex; align-items: center; gap: 0.35rem;">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                                ${uploadDate}
                            </span>
                        </p>
                        
                        <div class="timeline-jd-box">
                            <div class="timeline-jd-header">
                                <span class="timeline-jd-role-label">Target Role:</span>
                                <span class="timeline-jd-role-title">${escapeHTML(jdTitle)}</span>
                                ${jdSummary ? `
                                    <button type="button" class="timeline-jd-toggle-btn" onclick="toggleJdSummary(${item.id})" aria-expanded="false" id="jd-toggle-${item.id}">
                                        <span class="toggle-text">Show full description</span>
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="toggle-icon"><path d="m6 9 6 6 6-6"/></svg>
                                    </button>
                                ` : ''}
                            </div>
                            ${jdSummary ? `
                                <div class="timeline-jd-body collapsed" id="jd-body-${item.id}">
                                    ${escapeHTML(jdSummary)}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="timeline-actions-group">
                        <div class="timeline-score-block">
                            <span class="timeline-score-label">Version Match:</span>
                            <span class="score-badge ${scoreClass}" style="font-size: 0.9375rem; font-family: var(--font-mono); font-weight: 700; padding: 0.3rem 0.65rem; border-radius: 6px;">${item.ats_score}%</span>
                        </div>
                        <div class="timeline-btn-group" style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                            <button onclick="viewCandidateAnalysis(${item.id})" class="glow-btn timeline-btn-view" style="font-size: 0.8125rem; height: 34px; padding: 0 0.85rem; background: var(--color-forest); border: 1px solid var(--color-forest); color: #FFFFFF; font-weight: 600; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; white-space: nowrap;">
                                <span>View Analysis</span>
                            </button>
                            <button onclick="deleteCandidateAnalysis(${item.id})" class="glow-btn secondary timeline-btn-delete" style="font-size: 0.8125rem; height: 34px; padding: 0 0.85rem; background: var(--color-paper-2); border: 1px solid var(--color-rule-2); color: var(--color-clay); font-weight: 500; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; white-space: nowrap;">
                                <span>Delete</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

window.toggleJdSummary = function(id) {
    const body = document.getElementById(`jd-body-${id}`);
    const btn = document.getElementById(`jd-toggle-${id}`);
    if (!body || !btn) return;
    const isCollapsed = body.classList.contains('collapsed');
    if (isCollapsed) {
        body.classList.remove('collapsed');
        body.classList.add('expanded');
        btn.classList.add('expanded');
        btn.setAttribute('aria-expanded', 'true');
        const textSpan = btn.querySelector('.toggle-text');
        if (textSpan) textSpan.textContent = 'Show less';
    } else {
        body.classList.remove('expanded');
        body.classList.add('collapsed');
        btn.classList.remove('expanded');
        btn.setAttribute('aria-expanded', 'false');
        const textSpan = btn.querySelector('.toggle-text');
        if (textSpan) textSpan.textContent = 'Show full description';
    }
};

export function formatContactLink(containerId, type, rawValue) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = '';

    if (!rawValue || typeof rawValue !== 'string') {
        el.textContent = 'N/A';
        return;
    }

    const value = rawValue.trim();
    if (!value || value === 'N/A' || value === 'Not Provided' || value === 'None') {
        el.textContent = 'N/A';
        return;
    }

    if (type === 'email') {
        if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            const a = document.createElement('a');
            a.href = `mailto:${value}`;
            a.className = 'contact-link';
            a.textContent = value;
            el.appendChild(a);
            return;
        }
    } else if (type === 'phone') {
        const telDigits = value.replace(/[^\d+]/g, '');
        if (telDigits.length >= 7) {
            const a = document.createElement('a');
            a.href = `tel:${telDigits}`;
            a.className = 'contact-link';
            a.textContent = value;
            el.appendChild(a);
            return;
        }
    } else if (type === 'linkedin' || type === 'github') {
        if (!/^(javascript|data|vbscript):/i.test(value)) {
            let url = value;
            if (!/^https?:\/\//i.test(url)) {
                if (/^(www\.)?(linkedin\.com|github\.com)/i.test(url)) {
                    url = 'https://' + url;
                } else if (/^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/.test(url)) {
                    url = 'https://' + url;
                }
            }

            try {
                const parsed = new URL(url);
                if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                    a.className = 'contact-link';
                    a.textContent = value;
                    el.appendChild(a);
                    return;
                }
            } catch (err) {
                // Not a valid URL destination
            }
        }
    }

    // Default fallback to text if not linkable
    el.textContent = value;
}

window.viewCandidateAnalysis = async (resumeId) => {
    try {
        const details = await api.getCandidateResumeDetails(resumeId);
        
        document.getElementById('cav-label').textContent = `${details.label} (V${details.version})`;
        document.getElementById('cav-filename').textContent = details.original_filename;
        
        const uploadDate = new Date(details.uploaded_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        document.getElementById('cav-date').textContent = `Uploaded on: ${uploadDate}`;
        
        const badge = document.getElementById('cav-score-badge');
        badge.textContent = `${details.ats_score}% Match`;
        badge.className = 'score-badge';
        if (details.ats_score >= 70) {
            badge.classList.add('high-score');
        } else if (details.ats_score >= 40) {
            badge.classList.add('med-score');
        } else {
            badge.classList.add('low-score');
        }

        const cavCtxProfile = document.getElementById('cav-ctx-profile');
        const cavCtxJd = document.getElementById('cav-ctx-jd');
        const cavCtxEngine = document.getElementById('cav-ctx-engine');
        if (cavCtxProfile && cavCtxJd && cavCtxEngine) {
            const profileName = details.analysis_metadata?.profile_name || "General Software Engineer";
            const profileVer = details.analysis_metadata?.profile_version || "1.0.0";
            const engineVer = details.analysis_metadata?.engine_version || "v1.0.0";
            cavCtxProfile.textContent = `${profileName} (v${profileVer})`;

            // Concise JD title/name for the summary card
            let conciseJd = (details.job_description?.title || "Target Job Description").trim();
            if (conciseJd.length > 40) {
                conciseJd = conciseJd.slice(0, 37).trim() + "...";
            }
            cavCtxJd.textContent = conciseJd;
            if (details.job_description?.title) {
                cavCtxJd.title = details.job_description.title;
            }

            const cleanEngine = String(engineVer).replace(/^v/, '');
            cavCtxEngine.textContent = `Nipun Engine v${cleanEngine}`;
        }

        // Single target job description box with full content
        const cavJdDescEl = document.getElementById('cav-jd-description');
        if (cavJdDescEl) {
            cavJdDescEl.textContent = details.job_description?.description || "N/A";
        }
        const cavJdTitleEl = document.getElementById('cav-jd-title');
        if (cavJdTitleEl) {
            cavJdTitleEl.remove();
        }
        
        // Candidate Contact Details with functional hyperlinks
        const cand = details.candidate_details || {};
        formatContactLink('cav-cand-email', 'email', cand.email);
        formatContactLink('cav-cand-phone', 'phone', cand.phone);
        formatContactLink('cav-cand-linkedin', 'linkedin', cand.linkedin);
        formatContactLink('cav-cand-github', 'github', cand.github);
        
        // Render Explainable AI Breakdown
        document.getElementById('cav-xai-container').innerHTML = renderXaiContent(details.xai);
        
        // Render Resume Improvement Recommendations
        const recsContainer = document.getElementById('cav-recommendations-container');
        if (recsContainer) {
            recsContainer.innerHTML = renderRecommendations(details.recommendations, details.id);
        }
        
        // Skills lists
        const ext = details.extracted_skills || [];
        const mat = details.matched_skills || [];
        const mis = details.missing_skills || [];
        
        document.getElementById('cav-cand-extracted-skills').innerHTML = ext.map(s => `<span class="skill-tag">${s}</span>`).join('') || '<span style="color:#666">None</span>';
        document.getElementById('cav-cand-matched-skills').innerHTML = mat.map(s => `<span class="skill-tag matched">${s}</span>`).join('') || '<span style="color:#666">None</span>';
        document.getElementById('cav-cand-missing-skills').innerHTML = mis.map(s => `<span class="skill-tag missing">${s}</span>`).join('') || '<span style="color:#666">None</span>';
        
        const modal = document.getElementById('cand-analysis-view-modal');
        if (modal) {
            modal.dataset.currentReportId = String(resumeId);
            modal.classList.remove('hidden');
        }

        const targetHash = `#/candidate/dashboard?report=${resumeId}`;
        if (window.location.hash !== targetHash) {
            window.location.hash = targetHash;
        }
    } catch (err) {
        alert("Failed to load version details: " + err.message);
    }
};

window.toggleRecCard = (headerEl) => {
    const item = headerEl.closest('.rec-card');
    const content = item.querySelector('.rec-content, .rec-card-content');
    const chevron = item.querySelector('.rec-chevron');
    
    if (content.style.display === 'none' || content.classList.contains('hidden')) {
        content.style.display = 'block';
        content.classList.remove('hidden');
        chevron.style.transform = 'rotate(90deg)';
        headerEl.style.background = 'var(--color-paper-3)';
    } else {
        content.style.display = 'none';
        content.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
        headerEl.style.background = 'var(--color-paper-2)';
    }
};

window.updateRecommendationStatus = async (resumeId, recId, status) => {
    try {
        await api.updateRecommendationStatus(resumeId, recId, status);
        state.setCandidateStats(null);
        state.setCandidateResumes(null);
        await initializeCandidateDashboard();
        const modal = document.getElementById('cand-analysis-view-modal');
        if (modal && !modal.classList.contains('hidden')) {
            await window.viewCandidateAnalysis(resumeId);
        }
    } catch (err) {
        alert("Failed to update recommendation status: " + err.message);
    }
};

export function renderRecommendations(recsData, resumeId = null) {
    if (!recsData || !recsData.list || recsData.list.length === 0) {
        return `
            <div style="background: var(--color-paper-2); border: 1px solid var(--color-rule); border-left: 4px solid var(--color-clay); padding: 1rem 1.25rem; border-radius: 8px;">
                <p style="margin: 0; font-size: 0.95rem; color: var(--color-clay); font-weight: 500;">This analysis was created before Resume Improvement Recommendations were available.</p>
            </div>
        `;
    }

    let html = `<div style="display: flex; flex-direction: column; gap: 0.75rem;">`;

    recsData.list.forEach((rec) => {
        let priBg = "var(--color-clay)";
        let priColor = "#FFFFFF";
        if (rec.priority === "HIGH") {
            priBg = "var(--color-clay)";
            priColor = "#FFFFFF";
        } else if (rec.priority === "MEDIUM") {
            priBg = "var(--color-ochre)";
            priColor = "#FFFFFF";
        } else if (rec.priority === "LOW") {
            priBg = "var(--color-paper-3)";
            priColor = "var(--color-ink-2)";
        }
        
        let statusBg = "var(--color-paper-3)";
        let statusColor = "var(--color-ink-2)";
        const statusUpper = (rec.status || "ACTIVE").toUpperCase();
        if (statusUpper === "COMPLETED") {
            statusBg = "rgba(30, 58, 47, 0.12)";
            statusColor = "var(--color-forest)";
        } else if (statusUpper === "DISMISSED") {
            statusBg = "var(--color-paper-3)";
            statusColor = "var(--color-muted)";
        } else if (statusUpper === "EXPIRED") {
            statusBg = "rgba(156, 75, 51, 0.12)";
            statusColor = "var(--color-clay)";
        }

        const priBadge = `<span style="background: ${priBg}; color: ${priColor}; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px; text-transform: uppercase; font-family: var(--font-mono);">${rec.priority}</span>`;
        const statusBadge = `<span style="background: ${statusBg}; color: ${statusColor}; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px; text-transform: uppercase; margin-right: 0.5rem; font-family: var(--font-mono); border: 1px solid var(--color-rule);">${statusUpper}</span>`;
        const gainBadge = `<span style="background: rgba(30, 58, 47, 0.1); color: var(--color-forest); font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px; font-family: var(--font-mono); border: 1px solid rgba(30, 58, 47, 0.2);">+${rec.estimated_score_gain.toFixed(1)} ATS pts</span>`;

        html += `
            <div class="rec-card">
                <div class="rec-card-header rec-header" onclick="toggleRecCard(this)">
                    <div style="display: flex; align-items: center; gap: 0.75rem; flex: 1;">
                        <span class="rec-chevron" style="font-size: 0.75rem; color: var(--color-muted); transition: transform 0.2s; display: inline-block;">▶</span>
                        <strong style="color: var(--color-ink); font-size: 0.95rem; font-weight: 600;">${rec.title}</strong>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        ${statusBadge}
                        ${priBadge}
                        ${gainBadge}
                    </div>
                </div>
                
                <div class="rec-card-content rec-content hidden" style="display: none;">
                    <div style="margin-bottom: 0.85rem;">
                        <h5 style="margin: 0 0 0.35rem 0; font-size: 0.75rem; color: var(--color-forest); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-family: var(--font-mono); display: flex; align-items: center; gap: 0.4rem;">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
                            Actionable Advice
                        </h5>
                        <p style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: var(--color-ink);">${rec.description}</p>
                    </div>
                    
                    <div style="margin-bottom: 0.85rem;">
                        <h5 style="margin: 0 0 0.35rem 0; font-size: 0.75rem; color: var(--color-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-family: var(--font-mono); display: flex; align-items: center; gap: 0.4rem;">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                            Why We Recommend This
                        </h5>
                        <p style="margin: 0; font-size: 0.85rem; line-height: 1.45; color: var(--color-ink-2);">${rec.reason}</p>
                    </div>
        `;

        if (rec.related_skills && rec.related_skills.length > 0) {
            const skillTags = rec.related_skills.map(s => `<span class="skill-tag" style="background: var(--color-paper-3); border: 1px solid var(--color-rule-2); color: var(--color-ink); font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 4px; display: inline-block; margin-right: 0.3rem; margin-top: 0.3rem;">${s}</span>`).join('');
            html += `
                    <div style="margin-top: 0.75rem;">
                        <h5 style="margin: 0 0 0.35rem 0; font-size: 0.75rem; color: var(--color-forest); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-family: var(--font-mono); display: flex; align-items: center; gap: 0.4rem;">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>
                            Related Skill(s)
                        </h5>
                        <div style="display: flex; flex-wrap: wrap;">${skillTags}</div>
                    </div>
            `;
        }

        if (resumeId && statusUpper === "ACTIVE") {
            html += `
                <div style="display: flex; gap: 0.6rem; margin-top: 1rem; border-top: 1px solid var(--color-rule); padding-top: 1rem;">
                    <button onclick="event.stopPropagation(); updateRecommendationStatus(${resumeId}, '${rec.id}', 'COMPLETED')" class="glow-btn" style="font-size: 0.8rem; padding: 0.4rem 0.85rem; background: var(--color-forest); border: none; color: #FFFFFF; cursor: pointer; border-radius: 6px; font-weight: 600;">
                        <span>✓ Mark Completed</span>
                    </button>
                    <button onclick="event.stopPropagation(); updateRecommendationStatus(${resumeId}, '${rec.id}', 'DISMISSED')" class="glow-btn secondary" style="font-size: 0.8rem; padding: 0.4rem 0.85rem; border-color: var(--color-rule-2); color: var(--color-muted); cursor: pointer; border-radius: 6px;">
                        <span>✕ Dismiss</span>
                    </button>
                </div>
            `;
        } else if (statusUpper !== "ACTIVE") {
            const dateStr = rec.resolved_at ? new Date(rec.resolved_at).toLocaleDateString() : '';
            html += `
                <div style="margin-top: 1rem; border-top: 1px solid var(--color-rule); padding-top: 0.75rem; display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem; color: var(--color-muted);">
                    <span>Status: <strong style="color: var(--color-ink);">${statusUpper}</strong></span>
                    ${dateStr ? `<span>Resolved on: ${dateStr}</span>` : ''}
                </div>
            `;
        }

        html += `
                </div>
            </div>
        `;
    });

    html += `</div>`;
    return html;
}

window.toggleXaiAccordion = (headerEl) => {
    const item = headerEl.closest('.xai-accordion-item');
    const content = item.querySelector('.xai-accordion-content');
    const chevron = item.querySelector('.xai-chevron');
    
    if (content.style.display === 'none' || content.classList.contains('hidden')) {
        content.style.display = 'block';
        content.classList.remove('hidden');
        chevron.style.transform = 'rotate(90deg)';
        headerEl.style.background = 'var(--color-paper-3)';
    } else {
        content.style.display = 'none';
        content.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
        headerEl.style.background = 'var(--color-paper-2)';
    }
};

export function renderXaiContent(xaiData) {
    if (!xaiData || !xaiData.enabled) {
        return `
            <div style="background: var(--color-paper-2); border: 1px solid var(--color-rule); border-left: 4px solid var(--color-clay); padding: 1rem 1.25rem; border-radius: 8px;">
                <p style="margin: 0; font-size: 0.95rem; color: var(--color-clay); font-weight: 500;">This analysis was created before Explainable Scoring was available.</p>
            </div>
        `;
    }

    const components = xaiData.components || [];
    const explanations = xaiData.explanations || {};
    const strengths = xaiData.strengths || [];
    const skillGaps = xaiData.skill_gaps || [];

    // Strengths and Gaps section
    let strengthsGapsHTML = "";
    if (strengths.length > 0 || skillGaps.length > 0) {
        const strengthsList = strengths.map(s => `
            <li style="margin-bottom: 0.4rem; display: flex; align-items: flex-start; gap: 0.5rem;">
                <span style="color: var(--color-forest); font-weight: bold;">✓</span>
                <span style="color: var(--color-ink); font-size: 0.85rem; line-height: 1.4;">${escapeHTML(s)}</span>
            </li>
        `).join('') || '<li style="color: var(--color-muted); font-size: 0.85rem;">None identified.</li>';

        const gapsList = skillGaps.map(g => `
            <li style="margin-bottom: 0.4rem; display: flex; align-items: flex-start; gap: 0.5rem;">
                <span style="color: var(--color-clay); font-weight: bold;">✗</span>
                <span style="color: var(--color-ink); font-size: 0.85rem; line-height: 1.4;">${escapeHTML(g)}</span>
            </li>
        `).join('') || '<li style="color: var(--color-muted); font-size: 0.85rem;">None identified.</li>';

        strengthsGapsHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                <div style="background: var(--color-paper-2); border: 1px solid var(--color-rule); border-top: 3px solid var(--color-forest); border-radius: 8px; padding: 1.15rem;">
                    <h5 style="margin: 0 0 0.6rem 0; font-size: 0.8125rem; color: var(--color-forest); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 0.4rem; font-family: var(--font-mono);">
                        <span style="font-weight: 700;">✓</span> Key Strengths
                    </h5>
                    <ul style="margin: 0; padding-left: 0.25rem; list-style: none;">${strengthsList}</ul>
                </div>
                <div style="background: var(--color-paper-2); border: 1px solid var(--color-rule); border-top: 3px solid var(--color-clay); border-radius: 8px; padding: 1.15rem;">
                    <h5 style="margin: 0 0 0.6rem 0; font-size: 0.8125rem; color: var(--color-clay); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 0.4rem; font-family: var(--font-mono);">
                        <span style="font-weight: 700;">✗</span> Skill Gaps &amp; Missing Qualifications
                    </h5>
                    <ul style="margin: 0; padding-left: 0.25rem; list-style: none;">${gapsList}</ul>
                </div>
            </div>
        `;
    }

    let html = `
        <div style="background: var(--color-paper-2); border: 1px solid var(--color-rule); border-left: 4px solid var(--color-forest); padding: 1.25rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.05rem; font-family: var(--font-display); color: var(--color-ink); font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-forest)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                Overall Alignment Summary
            </h4>
            <p style="margin: 0; font-size: 0.9375rem; line-height: 1.6; color: var(--color-ink-2);">${escapeHTML(xaiData.overall_summary || 'Evaluation summary generated based on target criteria.')}</p>
        </div>

        ${strengthsGapsHTML}

        <div class="xai-accordion-group" style="display: flex; flex-direction: column; gap: 0.75rem;">
    `;

    components.forEach((comp) => {
        let key = comp.name.toLowerCase().replace(" ", "_");
        if (key === "technical_skills") key = "skills";
        if (key === "work_experience") key = "experience";
        
        const compExpl = explanations[key] || {};
        const summaryExpl = compExpl.summary || {};
        const detailedExpl = compExpl.detailed || {};
        const whyAwarded = summaryExpl.why_awarded || detailedExpl.why_awarded || 'Full criteria alignment evaluated.';
        const whyDeducted = summaryExpl.why_deducted || detailedExpl.why_deducted || 'No deductions applied.';
        
        let statusBg = "var(--color-paper-3)";
        let statusColor = "var(--color-clay)";
        if (comp.status === "met") {
            statusBg = "rgba(30, 58, 47, 0.1)";
            statusColor = "var(--color-forest)";
        } else if (comp.status === "partially_met") {
            statusBg = "rgba(217, 119, 6, 0.1)";
            statusColor = "var(--color-ochre)";
        } else if (comp.status === "exceeded") {
            statusBg = "rgba(30, 58, 47, 0.15)";
            statusColor = "var(--color-forest)";
        }

        const statusBadge = `<span style="background: ${statusBg}; color: ${statusColor}; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; text-transform: uppercase; font-family: var(--font-mono);">${comp.status.replace("_", " ")}</span>`;

        html += `
            <div class="xai-accordion-item" style="border: 1px solid var(--color-rule); border-radius: 8px; overflow: hidden; background: var(--color-paper-2); margin-bottom: 0.75rem;">
                <div class="xai-accordion-header" onclick="toggleXaiAccordion(this)" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.25rem; cursor: pointer; transition: background 0.15s ease; user-select: none;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span class="xai-chevron" style="font-size: 0.75rem; color: var(--color-muted); transition: transform 0.2s; display: inline-block;">▶</span>
                        <strong style="color: var(--color-ink); font-size: 0.95rem; font-weight: 600;">${escapeHTML(comp.name)}</strong>
                        <span style="font-size: 0.8125rem; color: var(--color-muted); font-family: var(--font-mono);">(${Math.round(comp.weight * 100)}% weight)</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        ${statusBadge}
                        <strong style="color: var(--color-ink); font-size: 1rem; font-family: var(--font-mono);">${Math.round(comp.raw_score)}%</strong>
                    </div>
                </div>
                
                <div class="xai-accordion-content hidden" style="padding: 1.25rem; border-top: 1px solid var(--color-rule); background: var(--color-paper); display: none;">
                    <div style="margin-bottom: 0.85rem;">
                        <h5 style="margin: 0 0 0.35rem 0; font-size: 0.75rem; color: var(--color-forest); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-family: var(--font-mono); display: flex; align-items: center; gap: 0.35rem;">
                            <span>✓</span> Points Awarded
                        </h5>
                        <p class="xai-text-awarded" style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: var(--color-ink);">${escapeHTML(whyAwarded)}</p>
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <h5 style="margin: 0 0 0.35rem 0; font-size: 0.75rem; color: var(--color-clay); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-family: var(--font-mono); display: flex; align-items: center; gap: 0.35rem;">
                            <span>✗</span> Deductions &amp; Gaps
                        </h5>
                        <p class="xai-text-deducted" style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: var(--color-ink-2);">${escapeHTML(whyDeducted)}</p>
                    </div>

                    ${(() => {
                        const rawEvidence = Array.isArray(comp.evidence) ? comp.evidence : [];
                        const isSkillComp = comp.name && comp.name.toLowerCase().includes("skill");
                        if (isSkillComp) return '';
                        
                        const evidenceItems = rawEvidence.filter(ev => {
                            if (!ev) return false;
                            const cat = String(ev.category || '').toLowerCase();
                            if (cat.includes("skill")) return false;
                            const title = typeof ev === 'string' ? ev : (ev?.title || ev?.feature || '');
                            const t = title.toLowerCase();
                            return !t.startsWith("exact match:") && 
                                   !t.startsWith("missing skill:") && 
                                   !t.startsWith("alias match:") && 
                                   !t.startsWith("abbreviation match:") && 
                                   !t.startsWith("technology family:") && 
                                   !t.startsWith("hierarchical subtitle:") && 
                                   !t.startsWith("partial match:");
                        });
                        
                        if (evidenceItems.length === 0) return '';
                        
                        return `
                            <div>
                                <h5 style="margin: 0 0 0.5rem 0; font-size: 0.75rem; color: var(--color-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-family: var(--font-mono); display: flex; align-items: center; gap: 0.4rem;">
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                                    Supporting Evidence
                                </h5>
                                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                                    ${evidenceItems.map(ev => {
                                        let impColor = "var(--color-forest)";
                                        if (ev.importance === "medium") impColor = "var(--color-ochre)";
                                        else if (ev.importance === "high") impColor = "var(--color-clay)";
                                        
                                        return `
                                            <div style="background: var(--color-paper-2); border: 1px solid var(--color-rule); padding: 0.75rem 1rem; border-radius: 6px; display: flex; flex-direction: column; gap: 0.25rem;">
                                                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                                                    <strong style="font-size: 0.85rem; color: var(--color-ink); font-weight: 600;">${ev.title}</strong>
                                                    <span style="font-size: 0.7rem; color: ${impColor}; font-weight: bold; background: var(--color-paper-3); padding: 0.15rem 0.4rem; border-radius: 4px; text-transform: uppercase; font-family: var(--font-mono);">${ev.importance}</span>
                                                </div>
                                                <p style="margin: 0; font-size: 0.8125rem; color: var(--color-ink-2); line-height: 1.4;">${ev.description}</p>
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        `;
                    })()}
                </div>
            </div>
        `;
    });

    html += `</div>`;
    return html;
}

window.deleteCandidateAnalysis = async (resumeId) => {
    if (!confirm("Are you sure you want to delete this resume version? This action is permanent and cannot be undone.")) {
        return;
    }
    try {
        await api.deleteCandidateResume(resumeId);
        state.setCandidateStats(null);
        state.setCandidateResumes(null);
        await initializeCandidateDashboard();
    } catch (err) {
        alert("Failed to delete resume version: " + err.message);
    }
};

window.renameCandidateAnalysis = async (resumeId, currentLabel) => {
    const newLabel = prompt("Enter new label for this version:", currentLabel);
    if (newLabel === null) return;
    const trimmed = newLabel.trim();
    if (!trimmed) {
        alert("Label cannot be empty.");
        return;
    }
    try {
        await api.updateCandidateResumeLabel(resumeId, trimmed);
        state.setCandidateResumes(null);
        await initializeCandidateDashboard();
    } catch (err) {
        alert("Failed to update label: " + err.message);
    }
};

/**
 * Page view initializer for Candidate Resume Analysis view.
 */
export function initializeCandidateScreen() {
    // Screening workspace awaits input
}

let candProfileEventsBound = false;

/**
 * Page view initializer for Candidate Profile view.
 * Reuses shared profile state from Dashboard if already fetched.
 */
export async function initializeCandidateProfile() {
    const feedbackEl = document.getElementById('cand-profile-feedback');
    const displayContainer = document.getElementById('cand-profile-display');
    const editForm = document.getElementById('cand-profile-edit-form');
    const editBtn = document.getElementById('cand-edit-profile-btn');
    const cancelBtn = document.getElementById('cand-cancel-edit-btn');
    const saveBtn = document.getElementById('cand-save-profile-btn');

    try {
        let profile = state.getProfile();
        if (!profile) {
            profile = await api.getProfile();
            state.setProfile(profile);
        }

        populateCandidateProfileUI(profile);
    } catch (err) {
        console.error("Error loading candidate profile details:", err);
    }

    if (!candProfileEventsBound) {
        if (editBtn && displayContainer && editForm) {
            editBtn.addEventListener('click', () => {
                const currentProfile = state.getProfile();
                populateCandidateProfileUI(currentProfile);
                if (feedbackEl) {
                    feedbackEl.className = 'hidden';
                    feedbackEl.textContent = '';
                }
                displayContainer.classList.add('hidden');
                editForm.classList.remove('hidden');
                editBtn.classList.add('hidden');
                const nameInput = document.getElementById('cand-edit-display-name');
                if (nameInput) nameInput.focus();
            });
        }

        if (cancelBtn && displayContainer && editForm) {
            cancelBtn.addEventListener('click', () => {
                const currentProfile = state.getProfile();
                populateCandidateProfileUI(currentProfile);
                if (feedbackEl) {
                    feedbackEl.className = 'hidden';
                    feedbackEl.textContent = '';
                }
                editForm.classList.add('hidden');
                displayContainer.classList.remove('hidden');
                if (editBtn) editBtn.classList.remove('hidden');
            });
        }

        if (editForm) {
            editForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                const displayName = document.getElementById('cand-edit-display-name')?.value?.trim();
                const currentStatus = document.getElementById('cand-edit-status')?.value?.trim();
                const fieldOfStudy = document.getElementById('cand-edit-field')?.value?.trim();
                const currentDomain = document.getElementById('cand-edit-domain')?.value?.trim();

                if (!displayName) {
                    showCandidateProfileFeedback("Display name cannot be empty.", false);
                    return;
                }
                if (!fieldOfStudy) {
                    showCandidateProfileFeedback("Field of study cannot be empty.", false);
                    return;
                }
                if (!currentDomain) {
                    showCandidateProfileFeedback("Current domain cannot be empty.", false);
                    return;
                }

                if (saveBtn) {
                    saveBtn.disabled = true;
                    saveBtn.textContent = "Saving...";
                }

                try {
                    const patchResponse = await api.updateCandidateProfile({
                        display_name: displayName,
                        current_status: currentStatus,
                        field_of_study: fieldOfStudy,
                        current_domain: currentDomain
                    });

                    // Merge safely with existing profile state
                    const existingProfile = state.getProfile() || {};
                    const updatedProfile = {
                        ...existingProfile,
                        ...patchResponse,
                        candidate_profile: {
                            ...(existingProfile.candidate_profile || {}),
                            ...(patchResponse.candidate_profile || {})
                        }
                    };

                    state.setProfile(updatedProfile);
                    populateCandidateProfileUI(updatedProfile);

                    showCandidateProfileFeedback("Profile updated successfully!", true);

                    // Revert to display mode
                    editForm.classList.add('hidden');
                    displayContainer?.classList.remove('hidden');
                    if (editBtn) editBtn.classList.remove('hidden');
                } catch (err) {
                    console.error("Error updating candidate profile:", err);
                    showCandidateProfileFeedback(err.message || "Failed to update profile. Please try again.", false);
                } finally {
                    if (saveBtn) {
                        saveBtn.disabled = false;
                        saveBtn.textContent = "Save Changes";
                    }
                }
            });
        }

        candProfileEventsBound = true;
    }
}

function showCandidateProfileFeedback(message, isSuccess) {
    const feedbackEl = document.getElementById('cand-profile-feedback');
    if (!feedbackEl) return;

    feedbackEl.className = '';
    if (isSuccess) {
        feedbackEl.style.cssText = "margin-bottom: 1.5rem; padding: 0.85rem 1.2rem; border-radius: 8px; font-size: 0.9rem; font-weight: 500; background: rgba(30, 58, 47, 0.08); border: 1px solid rgba(30, 58, 47, 0.2); color: var(--color-forest);";
    } else {
        feedbackEl.style.cssText = "margin-bottom: 1.5rem; padding: 0.85rem 1.2rem; border-radius: 8px; font-size: 0.9rem; font-weight: 500; background: rgba(156, 75, 51, 0.08); border: 1px solid rgba(156, 75, 51, 0.2); color: var(--color-clay);";
    }
    feedbackEl.textContent = message;
}

function renderCandidateAnalysisResults(cand) {
    const resultsDetails = document.getElementById('cand-results-details');
    const resultsContainer = document.getElementById('cand-results-container');
    if (!resultsDetails || !resultsContainer) return;

    let scoreClass = 'low-score';
    let scoreInterpretation = "Relevance is low. Review missing skills and recommended improvements below to align with target role requirements.";
    if (cand.similarity_score >= 70) {
        scoreClass = 'high-score';
        scoreInterpretation = "Strong semantic relevance. Your qualifications strongly match core job requirements.";
    } else if (cand.similarity_score >= 40) {
        scoreClass = 'med-score';
        scoreInterpretation = "Moderate alignment. Core requirements partially met; targeted resume refinements can boost overall suitability.";
    }

    const matchedTags = (cand.matched_skills || []).map(s => `<span class="skill-tag matched">${s}</span>`).join('') || '<span style="color:var(--color-muted)">None</span>';
    const missingTags = (cand.missing_skills || []).map(s => `<span class="skill-tag missing">${s}</span>`).join('') || '<span style="color:var(--color-muted)">None</span>';
    const extractedTags = (cand.matched_skills || []).concat(cand.missing_skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('') || '<span style="color:var(--color-muted)">None</span>';

    const xaiData = cand.xai || cand.analysis_metadata?.xai;
    const recsData = cand.recommendations || cand.analysis_metadata?.recommendations;
    const resumeId = cand.resume_id || cand.id;

    resultsDetails.innerHTML = `
        <div class="qv-profile-summary" style="display: flex; align-items: center; gap: 1.5rem; border-bottom: 1px solid var(--color-rule); padding-bottom: 1.5rem; flex-wrap: wrap;">
            <div class="qv-avatar" style="background: var(--color-paper-3); border: 1px solid var(--color-rule); width: 68px; height: 68px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: var(--color-forest);">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            </div>
            <div class="qv-meta" style="flex: 1; min-width: 220px;">
                <h2 style="font-size: 1.6rem; font-family: var(--font-display); font-weight: 700; color: var(--color-ink); margin: 0 0 0.35rem 0;">${cand.name || 'Candidate Resume'}</h2>
                <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                    <span class="score-badge ${scoreClass}" style="font-size: 1.15rem; font-family: var(--font-mono); font-weight: 700; padding: 0.35rem 0.85rem;">${cand.similarity_score}% Match</span>
                    <span style="font-size: 0.8125rem; color: var(--color-muted);">Evaluated via Semantic Analysis Engine</span>
                </div>
            </div>
        </div>

        <div class="cand-score-callout">
            <strong style="color: var(--color-ink);">Analysis Insight:</strong> ${scoreInterpretation}
        </div>

        <div style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem;">
            <div>
                <h4 style="font-size: 0.8125rem; font-family: var(--font-mono); font-weight: 700; color: var(--color-muted); text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--color-rule); padding-bottom: 0.5rem; margin-bottom: 0.75rem;">Resume Information</h4>
                <div class="profile-info-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div class="info-field" style="background: var(--color-paper-2); border: 1px solid var(--color-rule); padding: 0.85rem 1rem; border-radius: 8px;">
                        <span class="info-label" style="font-size: 0.75rem; color: var(--color-muted); font-family: var(--font-mono); display: block; margin-bottom: 0.25rem;">Education</span>
                        <span class="info-value" style="color: var(--color-ink); font-weight: 600; font-size: 0.95rem;">${cand.education || 'N/A'}</span>
                    </div>
                    <div class="info-field" style="background: var(--color-paper-2); border: 1px solid var(--color-rule); padding: 0.85rem 1rem; border-radius: 8px;">
                        <span class="info-label" style="font-size: 0.75rem; color: var(--color-muted); font-family: var(--font-mono); display: block; margin-bottom: 0.25rem;">Experience</span>
                        <span class="info-value" style="color: var(--color-ink); font-weight: 600; font-size: 0.95rem;">${cand.experience ? `${cand.experience} Years` : '0 Years'}</span>
                    </div>
                    <div class="info-field" style="background: var(--color-paper-2); border: 1px solid var(--color-rule); padding: 0.85rem 1rem; border-radius: 8px;">
                        <span class="info-label" style="font-size: 0.75rem; color: var(--color-muted); font-family: var(--font-mono); display: block; margin-bottom: 0.25rem;">Projects Match</span>
                        <span class="info-value" style="color: var(--color-ink); font-weight: 600; font-size: 0.95rem;">${cand.projects ? `${cand.projects} out of 3 projects` : '0 projects'}</span>
                    </div>
                </div>
            </div>

            <div>
                <h4 style="font-size: 0.8125rem; font-family: var(--font-mono); font-weight: 700; color: var(--color-muted); text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--color-rule); padding-bottom: 0.5rem; margin-bottom: 0.75rem;">Skills Overview</h4>
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    <div>
                        <h5 style="margin: 0 0 0.4rem 0; font-size: 0.8rem; color: var(--color-ink); font-weight: 600;">Extracted Skills</h5>
                        <div class="skills-tags-container" style="display: flex; flex-wrap: wrap; gap: 0.4rem;">${extractedTags}</div>
                    </div>
                    <div>
                        <h5 style="margin: 0 0 0.4rem 0; font-size: 0.8rem; color: var(--color-forest); font-weight: 600; display: flex; align-items: center; gap: 0.35rem;"><span style="font-weight: 700;">✓</span> Matched Skills</h5>
                        <div class="skills-tags-container" style="display: flex; flex-wrap: wrap; gap: 0.4rem;">${matchedTags}</div>
                    </div>
                    <div>
                        <h5 style="margin: 0 0 0.4rem 0; font-size: 0.8rem; color: var(--color-clay); font-weight: 600; display: flex; align-items: center; gap: 0.35rem;"><span style="font-weight: 700;">✗</span> Missing Skills</h5>
                        <div class="skills-tags-container" style="display: flex; flex-wrap: wrap; gap: 0.4rem;">${missingTags}</div>
                    </div>
                </div>
            </div>

            <div id="cand-results-xai-section">
                <h4 style="font-size: 0.8125rem; font-family: var(--font-mono); font-weight: 700; color: var(--color-muted); text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--color-rule); padding-bottom: 0.5rem; margin-bottom: 0.75rem;">
                    Explainable AI (XAI) Breakdown
                </h4>
                <div id="cand-inline-xai-container">
                    ${renderXaiContent(xaiData)}
                </div>
            </div>

            <div id="cand-results-recs-section">
                <h4 style="font-size: 0.8125rem; font-family: var(--font-mono); font-weight: 700; color: var(--color-muted); text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--color-rule); padding-bottom: 0.5rem; margin-bottom: 0.75rem;">
                    Resume Improvement Recommendations
                </h4>
                <div id="cand-inline-recs-container">
                    ${renderRecommendations(recsData, resumeId)}
                </div>
            </div>

            <div style="display: flex; justify-content: flex-end; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--color-rule);">
                <a href="#/candidate/dashboard" class="glow-btn" style="text-decoration: none; font-size: 0.85rem; padding: 0.5rem 1.25rem;">
                    <span>View in Dashboard History →</span>
                </a>
            </div>
        </div>
    `;

    resultsContainer.classList.remove('hidden');
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}
