import * as api from '../api.js';
import * as state from '../state.js';
import { getEmptyStateHTML } from '../components/emptyState.js';
import { toggleButtonLoading } from '../components/loadingSpinner.js';
import { MESSAGES } from '../constants.js';

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

    const closeBtn = document.getElementById('close-cand-analysis-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            document.getElementById('cand-analysis-view-modal').classList.add('hidden');
        });
    }

    initialized = true;
}

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

/**
 * Page view initializer for Candidate Dashboard.
 */
export async function initializeCandidateDashboard() {
    const dashCandName = document.getElementById('dash-cand-name');
    const dashCandStatus = document.getElementById('dash-cand-status');
    const dashCandField = document.getElementById('dash-cand-field');
    const dashCandDomain = document.getElementById('dash-cand-domain');
    const candTopUserName = document.getElementById('cand-top-user-name');
    const statsContainer = document.getElementById('cand-stats-container');

    if (!statsContainer) return;

    // 1. Loading state indicators to prevent permanent "..."
    if (dashCandName && dashCandName.textContent === "...") dashCandName.textContent = "Loading...";
    if (dashCandStatus && dashCandStatus.textContent === "...") dashCandStatus.textContent = "Loading...";
    if (dashCandField && dashCandField.textContent === "...") dashCandField.textContent = "Loading...";
    if (dashCandDomain && dashCandDomain.textContent === "...") dashCandDomain.textContent = "Loading...";
    if (statsContainer && (!statsContainer.innerHTML.trim() || statsContainer.querySelector('.loader'))) {
        statsContainer.innerHTML = `<div style="text-align: center; padding: 2.5rem; color: var(--text-secondary);"><div class="loader" style="margin: 0 auto 0.75rem;"></div>Loading your dashboard data...</div>`;
    }

    try {
        // 2. Fetch or retrieve cached candidate profile
        let profile = state.getProfile();
        if (!profile) {
            profile = await api.getProfile();
            state.setProfile(profile);
        }

        const candName = profile.email.split('@')[0];
        const statusVal = profile.candidate_profile?.current_status || "N/A";
        const fieldVal = profile.candidate_profile?.field_of_study || "N/A";
        const domainVal = profile.candidate_profile?.current_domain || "N/A";

        if (dashCandName) dashCandName.textContent = candName;
        if (dashCandStatus) dashCandStatus.textContent = statusVal;
        if (dashCandField) dashCandField.textContent = fieldVal;
        if (dashCandDomain) dashCandDomain.textContent = domainVal;
        if (candTopUserName) candTopUserName.textContent = candName;

        // 3. Fetch or retrieve cached stats & history in parallel
        let stats = state.getCandidateStats();
        let historyList = state.getCandidateResumes();

        if (!stats || !historyList) {
            const [fetchedStats, fetchedHistory] = await Promise.all([
                stats ? Promise.resolve(stats) : api.getCandidateStats(),
                historyList ? Promise.resolve(historyList) : api.getCandidateResumes()
            ]);
            stats = fetchedStats;
            historyList = fetchedHistory;
            state.setCandidateStats(stats);
            state.setCandidateResumes(historyList);
        }
        
        if (stats.latest_ats_score !== null && stats.latest_ats_score !== undefined) {
            let formattedDate = "N/A";
            if (stats.last_analysis_date) {
                const dateObj = new Date(stats.last_analysis_date);
                formattedDate = dateObj.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            }
            
            // Generate Career Progress Timeline
            const chronologicalList = [...historyList].reverse();
            let progressTimelineHTML = "";
            if (chronologicalList.length > 0) {
                const timelineSteps = chronologicalList.map(item => `
                    <div style="display: flex; flex-direction: column; align-items: center; min-width: 80px; position: relative;">
                        <span style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">V${item.version}</span>
                        <div style="width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #6366f1, #a855f7); color: #fff; font-size: 0.85rem; font-weight: bold; display: flex; align-items: center; justify-content: center; z-index: 2; border: 3px solid #1e1e2e; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                            ${item.ats_score}%
                        </div>
                        <span style="font-size: 0.7rem; color: #94a3b8; margin-top: 0.4rem; text-align: center; max-width: 100px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${item.label}">${item.label}</span>
                    </div>
                `).join(`
                    <div style="height: 4px; flex-grow: 1; min-width: 40px; background: rgba(255,255,255,0.08); margin-top: 24px; position: relative; z-index: 1;">
                        <div style="position: absolute; top: -8px; left: calc(50% - 6px); color: var(--text-secondary); font-size: 0.9rem;">&#x2192;</div>
                    </div>
                `);

                const oldest = chronologicalList[0];
                const newest = chronologicalList[chronologicalList.length - 1];
                const scoreDiff = newest.ats_score - oldest.ats_score;
                
                const timeDiffMs = new Date(newest.uploaded_at) - new Date(oldest.uploaded_at);
                const weeks = Math.round(timeDiffMs / (1000 * 60 * 60 * 24 * 7));
                const days = Math.round(timeDiffMs / (1000 * 60 * 60 * 24));
                let timeText = "";
                if (weeks > 0) {
                    timeText = `${weeks} week${weeks > 1 ? 's' : ''}`;
                } else {
                    timeText = `${days} day${days !== 1 ? 's' : ''}`;
                }

                let progressStatsHTML = "";
                if (chronologicalList.length > 1) {
                    const oldestJD = oldest.job_description_title || "Unknown JD";
                    const newestJD = newest.job_description_title || "Unknown JD";
                    const oldestProfile = oldest.analysis_metadata?.profile_name || "General Software Engineer";
                    const newestProfile = newest.analysis_metadata?.profile_name || "General Software Engineer";
                    const oldestEngine = oldest.analysis_metadata?.engine_version || "v1.0.0";
                    const newestEngine = newest.analysis_metadata?.engine_version || "v1.0.0";
                    
                    const sameJD = (oldestJD === newestJD);
                    const sameProfile = (oldestProfile === newestProfile);
                    const sameEngine = (oldestEngine === newestEngine);
                    const isReliable = sameJD && sameProfile && sameEngine;

                    let reliabilityDetailsHTML = `
                        <div style="font-size: 0.75rem; margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.2rem; opacity: 0.85;">
                            <div style="color: ${sameJD ? '#10b981' : '#ef4444'}; font-weight: 500;">
                                ${sameJD ? '&#x2713; Same Job Description' : '&#x2717; Different Job Description'}
                            </div>
                            <div style="color: ${sameProfile ? '#10b981' : '#ef4444'}; font-weight: 500;">
                                ${sameProfile ? '&#x2713; Same Profile' : '&#x2717; Different Profile'}
                            </div>
                            <div style="color: ${sameEngine ? '#10b981' : '#ef4444'}; font-weight: 500;">
                                ${sameEngine ? '&#x2713; Same Engine Version' : '&#x2717; Different Engine Version'}
                            </div>
                        </div>
                    `;

                    if (scoreDiff > 0) {
                        progressStatsHTML = `
                            <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1.25rem;">
                                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.15); padding: 0.6rem 0.9rem; border-radius: 8px; display: inline-flex; align-items: center; gap: 0.5rem; color: #34d399; font-weight: bold; font-size: 0.9rem; width: fit-content;">
                                    <span>&#x1F680; Resume Improved:</span>
                                    <span style="font-size: 1.05rem; color: #10b981;">+${scoreDiff.toFixed(1)} points</span>
                                    <span style="font-weight: normal; color: #a7f3d0; font-size: 0.8rem;">in ${timeText}</span>
                                </div>
                                <div style="font-size: 0.8rem; color: ${isReliable ? '#10b981' : '#f59e0b'}; font-weight: 600; margin-top: 0.25rem;">
                                    Comparison Reliability: ${isReliable ? 'HIGH &#x2B50;' : 'LOW &#x26A0;'}
                                </div>
                                ${reliabilityDetailsHTML}
                            </div>
                        `;
                    } else {
                        progressStatsHTML = `
                            <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1rem;">
                                <div style="font-size: 0.8rem; color: ${isReliable ? '#10b981' : '#f59e0b'}; font-weight: 600;">
                                    Comparison Reliability: ${isReliable ? 'HIGH &#x2B50;' : 'LOW &#x26A0;'}
                                </div>
                                ${reliabilityDetailsHTML}
                            </div>
                        `;
                    }
                }

                progressTimelineHTML = `
                    <div class="stat-card span-two" style="grid-column: span 2; background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 12px;">
                        <div class="stat-header" style="margin-bottom: 1rem;">
                            <span class="stat-title" style="font-weight: 600; color: #fff;">&#x1F4C8; Career Progress Timeline</span>
                            <span class="stat-icon">&#x1F525;</span>
                        </div>
                        <div style="display: flex; align-items: center; overflow-x: auto; padding: 0.5rem 0; width: 100%; gap: 0.25rem;">
                            ${timelineSteps}
                        </div>
                        ${progressStatsHTML}
                    </div>
                `;
            }
            
            statsContainer.innerHTML = `
                <div class="rec-grid">
                    <div class="stat-card">
                        <div class="stat-header">
                            <span class="stat-title">Latest Resume Match Score</span>
                            <span class="stat-icon">&#x1F4C8;</span>
                        </div>
                        <div class="stat-value" id="cand-stat-latest-score">${stats.latest_ats_score}%</div>
                        <p class="stat-description">Most recent semantic relevance match</p>
                    </div>
                    <div class="stat-card">
                        <div class="stat-header">
                            <span class="stat-title">Last Analysis Date</span>
                            <span class="stat-icon">&#x1F4C5;</span>
                        </div>
                        <div class="stat-value" style="font-size: 1.5rem; margin-top: 0.5rem;" id="cand-stat-last-date">${formattedDate}</div>
                        <p class="stat-description">Timestamp of the last run</p>
                    </div>
                    ${progressTimelineHTML}
                </div>
            `;
        } else {
            statsContainer.innerHTML = getEmptyStateHTML("You have not analyzed any resumes yet. Go to Resume Analysis to evaluate your resume!");
        }

        renderTimelineList(historyList);

    } catch (err) {
        console.error("Error loading candidate dashboard data:", err);
        const user = state.getUser();
        if (dashCandName && (dashCandName.textContent === "..." || dashCandName.textContent === "Loading...")) {
            dashCandName.textContent = user?.email?.split('@')[0] || "Candidate";
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
        if (statsContainer && (!statsContainer.innerHTML.trim() || statsContainer.querySelector('.loader'))) {
            statsContainer.innerHTML = getEmptyStateHTML("Could not load dashboard statistics. Please refresh the page.");
        }
    }
}

function renderTimelineList(historyList) {
    const container = document.getElementById('candidate-timeline-list');
    if (!container) return;

    if (!historyList || historyList.length === 0) {
        container.innerHTML = `<p style="color: var(--text-secondary); text-align: center; padding: 2rem; background: rgba(255,255,255,0.02); border-radius: 8px;">No analysis history yet.</p>`;
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

        return `
            <div class="glass-card timeline-card" style="margin-bottom: 1rem; padding: 1.5rem; position: relative; border-left: 4px solid ${isNewest ? '#6366f1' : 'transparent'}; background: rgba(255, 255, 255, 0.02); border-radius: 12px; transition: transform 0.2s, box-shadow 0.2s;">
                ${isNewest ? `<span class="newest-badge" style="position: absolute; top: 1rem; right: 1rem; background: linear-gradient(135deg, #6366f1, #a855f7); color: #fff; font-size: 0.75rem; font-weight: bold; padding: 0.25rem 0.6rem; border-radius: 12px;">Newest Version</span>` : ''}
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 250px;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <h3 style="margin: 0; font-size: 1.15rem; color: #fff; display: flex; align-items: center; gap: 0.5rem;">
                                <span>${item.label}</span>
                                <span style="font-size: 0.8rem; color: var(--text-secondary); font-weight: normal;">(V${item.version})</span>
                            </h3>                            <button onclick="renameCandidateAnalysis(${item.id}, '${item.label.replace(/'/g, "\\'")}')" class="footer-link-btn" style="background: none; border: none; font-size: 0.9rem; cursor: pointer; color: #94a3b8; padding: 0;" title="Rename Label">&#x2712;&#xFE0F;</button>
                        </div>
                        <p style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-secondary); display: flex; align-items: center; gap: 0.5rem;">
                            <span>&#x1F4C1; ${item.original_filename}</span>
                            <span>&bull;</span>
                            <span>&#x1F4C5; ${uploadDate}</span>
                        </p>
                        <p style="margin: 0; font-size: 0.85rem; color: #94a3b8; background: rgba(0,0,0,0.15); padding: 0.5rem; border-radius: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">
                            <strong>JD:</strong> ${item.job_description_title} &#x2014; ${item.job_description_summary}
                        </p>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.75rem; min-width: 150px;">
                        <span class="score-badge ${scoreClass}" style="font-size: 1.1rem; font-weight: bold; padding: 0.4rem 0.8rem;">${item.ats_score}% Match</span>
                        <div style="display: flex; gap: 0.5rem;">
                            <button onclick="viewCandidateAnalysis(${item.id})" class="glow-btn" style="font-size: 0.8rem; padding: 0.4rem 0.8rem;">
                                <span>View Analysis</span>
                            </button>
                            <button onclick="deleteCandidateAnalysis(${item.id})" class="glow-btn secondary" style="font-size: 0.8rem; padding: 0.4rem 0.8rem; border-color: #ef4444; color: #ef4444;">
                                <span>Delete</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
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
            cavCtxJd.textContent = details.job_description?.title || "N/A";
            const cleanEngine = engineVer.replace(/^v/, '');
            cavCtxEngine.textContent = `Nipun Engine v${cleanEngine}`;
        }

        document.getElementById('cav-jd-title').textContent = details.job_description?.title || "N/A";
        document.getElementById('cav-jd-description').textContent = details.job_description?.description || "N/A";
        
        // Candidate Contact Details
        const cand = details.candidate_details || {};
        document.getElementById('cav-cand-email').textContent = cand.email || "N/A";
        document.getElementById('cav-cand-phone').textContent = cand.phone || "N/A";
        document.getElementById('cav-cand-linkedin').textContent = cand.linkedin || "N/A";
        document.getElementById('cav-cand-github').textContent = cand.github || "N/A";
        
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
        
        document.getElementById('cand-analysis-view-modal').classList.remove('hidden');
    } catch (err) {
        alert("Failed to load version details: " + err.message);
    }
};

window.toggleRecCard = (headerEl) => {
    const item = headerEl.closest('.rec-card');
    const content = item.querySelector('.rec-content');
    const chevron = item.querySelector('.rec-chevron');
    
    if (content.style.display === 'none' || content.classList.contains('hidden')) {
        content.style.display = 'block';
        content.classList.remove('hidden');
        chevron.style.transform = 'rotate(90deg)';
        headerEl.style.background = 'rgba(255, 255, 255, 0.03)';
    } else {
        content.style.display = 'none';
        content.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
        headerEl.style.background = 'transparent';
    }
};

window.updateRecommendationStatus = async (resumeId, recId, status) => {
    try {
        await api.updateRecommendationStatus(resumeId, recId, status);
        await initializeCandidateDashboard();
        await window.viewCandidateAnalysis(resumeId);
    } catch (err) {
        alert("Failed to update recommendation status: " + err.message);
    }
};

export function renderRecommendations(recsData, resumeId = null) {
    if (!recsData || !recsData.list || recsData.list.length === 0) {
        return `
            <div style="background: rgba(255, 255, 255, 0.02); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 8px;">
                <p style="margin: 0; font-size: 0.95rem; color: #fca5a5;">This analysis was created before Resume Improvement Recommendations were available.</p>
            </div>
        `;
    }

    let html = `<div style="display: flex; flex-direction: column; gap: 0.75rem;">`;

    recsData.list.forEach((rec) => {
        let priColor = "#ef4444"; // red
        if (rec.priority === "HIGH") priColor = "#f59e0b"; // orange
        else if (rec.priority === "MEDIUM") priColor = "#eab308"; // yellow
        else if (rec.priority === "LOW") priColor = "#3b82f6"; // blue
        
        let statusColor = "#3b82f6"; // blue for active
        const statusUpper = (rec.status || "ACTIVE").toUpperCase();
        if (statusUpper === "COMPLETED") statusColor = "#10b981"; // green
        else if (statusUpper === "DISMISSED") statusColor = "#6b7280"; // gray
        else if (statusUpper === "EXPIRED") statusColor = "#ef4444"; // red

        const priBadge = `<span style="background: ${priColor}15; color: ${priColor}; font-size: 0.75rem; font-weight: bold; padding: 0.15rem 0.4rem; border-radius: 4px; text-transform: uppercase;">${rec.priority}</span>`;
        const statusBadge = `<span style="background: ${statusColor}15; color: ${statusColor}; font-size: 0.75rem; font-weight: bold; padding: 0.15rem 0.4rem; border-radius: 4px; text-transform: uppercase; margin-right: 0.5rem;">${statusUpper}</span>`;
        const gainBadge = `<span style="background: rgba(16, 185, 129, 0.1); color: #10b981; font-size: 0.75rem; font-weight: bold; padding: 0.15rem 0.4rem; border-radius: 4px;">+${rec.estimated_score_gain.toFixed(1)} ATS pts</span>`;

        html += `
            <div class="rec-card" style="border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden; background: rgba(255,255,255,0.01);">
                <div class="rec-header" onclick="toggleRecCard(this)" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; cursor: pointer; transition: background 0.2s;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; flex: 1;">
                        <span class="rec-chevron" style="font-size: 0.75rem; color: var(--text-secondary); transition: transform 0.2s; display: inline-block;">&#x25B6;</span>
                        <strong style="color: #fff; font-size: 0.95rem;">${rec.title}</strong>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        ${statusBadge}
                        ${priBadge}
                        ${gainBadge}
                    </div>
                </div>
                
                <div class="rec-content hidden" style="padding: 1rem; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.15); display: none;">
                    <div style="margin-bottom: 0.75rem;">
                        <h5 style="margin: 0 0 0.25rem 0; font-size: 0.8rem; color: #cbd5e1; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">&#x1F4A1; Actionable Advice</h5>
                        <p style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: #e2e8f0;">${rec.description}</p>
                    </div>
                    
                    <div style="margin-bottom: 0.75rem;">
                        <h5 style="margin: 0 0 0.25rem 0; font-size: 0.8rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">&#x2753; Why We Recommend This</h5>
                        <p style="margin: 0; font-size: 0.85rem; line-height: 1.4; color: var(--text-secondary);">${rec.reason}</p>
                    </div>
        `;

        if (rec.related_skills && rec.related_skills.length > 0) {
            const skillTags = rec.related_skills.map(s => `<span class="skill-tag" style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); color: #a5b4fc; font-size: 0.75rem; padding: 0.1rem 0.4rem; border-radius: 4px; display: inline-block; margin-right: 0.25rem; margin-top: 0.25rem;">${s}</span>`).join('');
            html += `
                    <div style="margin-top: 0.5rem;">
                        <h5 style="margin: 0 0 0.25rem 0; font-size: 0.8rem; color: #6366f1; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">&#x1F3F7;&#xFE0F; Related Skill(s)</h5>
                        <div style="display: flex; flex-wrap: wrap;">${skillTags}</div>
                    </div>
            `;
        }

        if (resumeId && statusUpper === "ACTIVE") {
            html += `
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 1rem;">
                    <button onclick="event.stopPropagation(); updateRecommendationStatus(${resumeId}, '${rec.id}', 'COMPLETED')" class="glow-btn" style="font-size: 0.8rem; padding: 0.35rem 0.75rem; background: linear-gradient(135deg, #10b981, #059669); border: none; color: #fff; cursor: pointer;">
                        <span>&#x2713; Mark Completed</span>
                    </button>
                    <button onclick="event.stopPropagation(); updateRecommendationStatus(${resumeId}, '${rec.id}', 'DISMISSED')" class="glow-btn secondary" style="font-size: 0.8rem; padding: 0.35rem 0.75rem; border-color: rgba(255,255,255,0.2); color: #ccc; cursor: pointer;">
                        <span>&#x2715; Dismiss</span>
                    </button>
                </div>
            `;
        } else if (statusUpper !== "ACTIVE") {
            const dateStr = rec.resolved_at ? new Date(rec.resolved_at).toLocaleDateString() : '';
            html += `
                <div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.75rem; display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem; color: var(--text-secondary);">
                    <span>Status: <strong>${statusUpper}</strong></span>
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
        headerEl.style.background = 'rgba(255, 255, 255, 0.03)';
    } else {
        content.style.display = 'none';
        content.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
        headerEl.style.background = 'transparent';
    }
};

window.toggleXaiLevel = (level) => {
    const summaryBtns = document.querySelectorAll('.xai-level-btn');
    summaryBtns.forEach(btn => {
        if (btn.getAttribute('onclick').includes(level)) {
            btn.classList.add('active');
            btn.style.background = '#6366f1';
            btn.style.color = '#fff';
        } else {
            btn.classList.remove('active');
            btn.style.background = 'rgba(255,255,255,0.05)';
            btn.style.color = '#ccc';
        }
    });

    const summaryAw = document.querySelectorAll('.xai-text-awarded-summary');
    const detailedAw = document.querySelectorAll('.xai-text-awarded-detailed');
    const summaryDe = document.querySelectorAll('.xai-text-deducted-summary');
    const detailedDe = document.querySelectorAll('.xai-text-deducted-detailed');

    if (level === 'summary') {
        summaryAw.forEach(el => el.style.display = 'block');
        detailedAw.forEach(el => el.style.display = 'none');
        summaryDe.forEach(el => el.style.display = 'block');
        detailedDe.forEach(el => el.style.display = 'none');
    } else {
        summaryAw.forEach(el => el.style.display = 'none');
        detailedAw.forEach(el => el.style.display = 'block');
        summaryDe.forEach(el => el.style.display = 'none');
        detailedDe.forEach(el => el.style.display = 'block');
    }
};

export function renderXaiContent(xaiData) {
    if (!xaiData || !xaiData.enabled) {
        return `
            <div style="background: rgba(255, 255, 255, 0.02); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 8px;">
                <p style="margin: 0; font-size: 0.95rem; color: #fca5a5;">This analysis was created before Explainable Scoring was available.</p>
            </div>
        `;
    }

    const components = xaiData.components || [];
    const explanations = xaiData.explanations || {};
    
    let html = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; background: rgba(255,255,255,0.02); padding: 0.5rem 1rem; border-radius: 8px;">
            <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600;">Explanation Level:</span>
            <div style="display: flex; gap: 0.5rem;">
                <button class="xai-level-btn active" onclick="toggleXaiLevel('summary')" style="font-size: 0.8rem; padding: 0.25rem 0.6rem; border-radius: 4px; background: #6366f1; border: none; color: #fff; cursor: pointer;">Summary</button>
                <button class="xai-level-btn" onclick="toggleXaiLevel('detailed')" style="font-size: 0.8rem; padding: 0.25rem 0.6rem; border-radius: 4px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #ccc; cursor: pointer;">Detailed</button>
            </div>
        </div>

        <div style="background: rgba(99, 102, 241, 0.05); border-left: 4px solid #6366f1; padding: 1.25rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.05rem; color: #fff;">&#x1F4A1; Overall Summary</h4>
            <p style="margin: 0; font-size: 0.95rem; line-height: 1.6; color: #cbd5e1;">${xaiData.overall_summary}</p>
        </div>

        <div class="xai-accordion-group" style="display: flex; flex-direction: column; gap: 0.75rem;">
    `;

    components.forEach((comp) => {
        let key = comp.name.toLowerCase().replace(" ", "_");
        if (key === "technical_skills") key = "skills";
        if (key === "work_experience") key = "experience";
        
        const compExpl = explanations[key] || {};
        const summaryExpl = compExpl.summary || { why_awarded: "No summary explanation.", why_deducted: "" };
        const detailedExpl = compExpl.detailed || { why_awarded: "No detailed explanation.", why_deducted: "" };
        
        let statusColor = "#ef4444";
        if (comp.status === "met") statusColor = "#10b981";
        else if (comp.status === "partially_met") statusColor = "#f59e0b";
        else if (comp.status === "exceeded") statusColor = "#3b82f6";

        const statusBadge = `<span style="background: ${statusColor}15; color: ${statusColor}; font-size: 0.75rem; font-weight: bold; padding: 0.15rem 0.4rem; border-radius: 4px; text-transform: uppercase;">${comp.status.replace("_", " ")}</span>`;

        html += `
            <div class="xai-accordion-item" style="border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden; background: rgba(255,255,255,0.01);">
                <div class="xai-accordion-header" onclick="toggleXaiAccordion(this)" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; cursor: pointer; transition: background 0.2s;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span class="xai-chevron" style="font-size: 0.75rem; color: var(--text-secondary); transition: transform 0.2s; display: inline-block;">&#x25B6;</span>
                        <strong style="color: #fff; font-size: 0.95rem;">${comp.name}</strong>
                        <span style="font-size: 0.85rem; color: var(--text-secondary);">(${comp.weight * 100}% weight)</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        ${statusBadge}
                        <strong style="color: #fff; font-size: 1rem;">${Math.round(comp.raw_score)}%</strong>
                    </div>
                </div>
                
                <div class="xai-accordion-content hidden" style="padding: 1rem; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.15); display: none;">
                    <div style="margin-bottom: 0.75rem;">
                        <h5 style="margin: 0 0 0.25rem 0; font-size: 0.8rem; color: #10b981; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">&#x2705; Points Awarded</h5>
                        <p class="xai-text-awarded-summary" style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: #e2e8f0;">${summaryExpl.why_awarded}</p>
                        <p class="xai-text-awarded-detailed" style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: #e2e8f0; display: none;">${detailedExpl.why_awarded}</p>
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <h5 style="margin: 0 0 0.25rem 0; font-size: 0.8rem; color: #ef4444; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">&#x274C; Deductions &amp; Gaps</h5>
                        <p class="xai-text-deducted-summary" style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: #cbd5e1;">${summaryExpl.why_deducted || 'No deductions applied.'}</p>
                        <p class="xai-text-deducted-detailed" style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: #cbd5e1; display: none;">${detailedExpl.why_deducted || 'No deductions applied.'}</p>
                    </div>

                    <div>
                        <h5 style="margin: 0 0 0.5rem 0; font-size: 0.8rem; color: #6366f1; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">&#x1F4C2; Supporting Evidence</h5>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                            ${comp.evidence.map(ev => {
                                let impColor = "#10b981";
                                if (ev.importance === "medium") impColor = "#f59e0b";
                                else if (ev.importance === "high") impColor = "#ef4444";
                                
                                return `
                                    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.03); padding: 0.75rem; border-radius: 6px; display: flex; flex-direction: column; gap: 0.25rem;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                                            <strong style="font-size: 0.85rem; color: #fff;">${ev.title}</strong>
                                            <span style="font-size: 0.7rem; color: ${impColor}; font-weight: bold; background: ${impColor}10; padding: 0.1rem 0.3rem; border-radius: 3px; text-transform: uppercase;">${ev.importance}</span>
                                        </div>
                                        <p style="margin: 0; font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">${ev.description}</p>
                                    </div>
                                `;
                            }).join('') || '<p style="margin:0; font-size:0.8rem; color:#666;">No evidence items identified.</p>'}
                        </div>
                    </div>
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

/**
 * Page view initializer for Candidate Profile view.
 * Reuses shared profile state from Dashboard if already fetched.
 */
export async function initializeCandidateProfile() {
    const profileCandName = document.getElementById('profile-cand-name');
    const profileCandEmail = document.getElementById('profile-cand-email');
    const profileCandStatus = document.getElementById('profile-cand-status');
    const profileCandField = document.getElementById('profile-cand-field');
    const profileCandDomain = document.getElementById('profile-cand-domain');
    const profileCandJoined = document.getElementById('profile-cand-joined');

    try {
        let profile = state.getProfile();
        if (!profile) {
            profile = await api.getProfile();
            state.setProfile(profile);
        }

        const candName = profile.email.split('@')[0];
        if (profileCandName) profileCandName.textContent = candName;
        if (profileCandEmail) profileCandEmail.textContent = profile.email;
        if (profileCandStatus) profileCandStatus.textContent = profile.candidate_profile?.current_status || "N/A";
        if (profileCandField) profileCandField.textContent = profile.candidate_profile?.field_of_study || "N/A";
        if (profileCandDomain) profileCandDomain.textContent = profile.candidate_profile?.current_domain || "N/A";

        if (profile.created_at) {
            const joinDate = new Date(profile.created_at);
            const formattedJoin = joinDate.toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            if (profileCandJoined) profileCandJoined.textContent = formattedJoin;
        } else {
            if (profileCandJoined) profileCandJoined.textContent = "N/A";
        }
    } catch (err) {
        console.error("Error loading candidate profile details:", err);
    }
}

function renderCandidateAnalysisResults(cand) {
    const resultsDetails = document.getElementById('cand-results-details');
    const resultsContainer = document.getElementById('cand-results-container');
    if (!resultsDetails || !resultsContainer) return;

    let scoreClass = 'low-score';
    if (cand.similarity_score >= 70) {
        scoreClass = 'high-score';
    } else if (cand.similarity_score >= 40) {
        scoreClass = 'med-score';
    }

    const matchedTags = cand.matched_skills.map(s => `<span class="skill-tag matched">${s}</span>`).join('') || '<span style="color:#666">None</span>';
    const missingTags = cand.missing_skills.map(s => `<span class="skill-tag missing">${s}</span>`).join('') || '<span style="color:#666">None</span>';
    const extractedTags = cand.matched_skills.concat(cand.missing_skills).map(s => `<span class="skill-tag">${s}</span>`).join('') || '<span style="color:#666">None</span>';

    resultsDetails.innerHTML = `
        <div class="qv-profile-summary" style="display: flex; align-items: center; gap: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 1.5rem;">
            <div class="qv-avatar" style="font-size: 3rem; background: rgba(255,255,255,0.02); width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">&#x1F4C4;</div>
            <div class="qv-meta">
                <h2 style="font-size: 1.6rem; font-weight: 800; color: #fff; margin: 0 0 0.25rem 0;">${cand.name}</h2>
                <p class="score-badge ${scoreClass}" style="font-size: 1.25rem; font-weight: bold; margin: 0;">${cand.similarity_score}% Match</p>
            </div>
        </div>

        <div style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem;">
            <div>
                <h4 style="font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 0.5rem; margin-bottom: 0.5rem;">Resume Information</h4>
                <div class="profile-info-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div class="info-field">
                        <span class="info-label" style="font-size: 0.75rem; color: #94a3b8;">Education</span>
                        <span class="info-value" style="color: #fff; font-weight: 500;">${cand.education || 'N/A'}</span>
                    </div>
                    <div class="info-field">
                        <span class="info-label" style="font-size: 0.75rem; color: #94a3b8;">Experience</span>
                        <span class="info-value" style="color: #fff; font-weight: 500;">${cand.experience ? `${cand.experience} Years` : '0 Years'}</span>
                    </div>
                    <div class="info-field">
                        <span class="info-label" style="font-size: 0.75rem; color: #94a3b8;">Projects Match</span>
                        <span class="info-value" style="color: #fff; font-weight: 500;">${cand.projects ? `${cand.projects} out of 5 projects` : '0 projects'}</span>
                    </div>
                </div>
            </div>

            <div>
                <h4 style="font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 0.5rem; margin-bottom: 0.5rem;">Skills Overview</h4>
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    <div>
                        <h5 style="margin: 0 0 0.5rem 0; font-size: 0.8rem; color: #cbd5e1; font-weight: 600;">Extracted Skills</h5>
                        <div class="skills-tags-container" style="display: flex; flex-wrap: wrap; gap: 0.5rem;">${extractedTags}</div>
                    </div>
                    <div>
                        <h5 style="margin: 0 0 0.5rem 0; font-size: 0.8rem; color: #cbd5e1; font-weight: 600;">&#x2705; Matched Skills</h5>
                        <div class="skills-tags-container" style="display: flex; flex-wrap: wrap; gap: 0.5rem;">${matchedTags}</div>
                    </div>
                    <div>
                        <h5 style="margin: 0 0 0.5rem 0; font-size: 0.8rem; color: #cbd5e1; font-weight: 600;">&#x274C; Missing Skills</h5>
                        <div class="skills-tags-container" style="display: flex; flex-wrap: wrap; gap: 0.5rem;">${missingTags}</div>
                    </div>
                </div>
            </div>
        </div>
    `;

    resultsContainer.classList.remove('hidden');
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}
