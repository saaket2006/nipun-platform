import * as api from '../api.js';
import * as state from '../state.js';
import { getRecruiterCandidateCardHTML } from '../components/candidateCard.js';
import { updateStatisticCard } from '../components/statisticCard.js';
import { populateRecruiterProfileUI } from '../components/profileSection.js';
import { toggleButtonLoading } from '../components/loadingSpinner.js';
import { MESSAGES } from '../constants.js';
import { sanitizeUrl } from '../utils.js';

let recUploadedFiles = [];
let initialized = false;

/**
 * Binds event listeners for recruiter workspace (runs once on startup).
 */
export function initRecruiterPage() {
    if (initialized) return;

    const recDropZone = document.getElementById('rec-drop-zone');
    const recResumesInput = document.getElementById('rec-resumes');
    const recResumesHeader = document.getElementById('rec-resumes-header');
    const recProcessBtn = document.getElementById('rec-process-btn');
    const recResultsContainer = document.getElementById('rec-results-container');
    const recJobDescription = document.getElementById('rec-job-description');

    if (recDropZone && recResumesInput) {
        recDropZone.addEventListener('click', () => recResumesInput.click());

        recDropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            recDropZone.classList.add('drag-over');
        });

        recDropZone.addEventListener('dragleave', () => {
            recDropZone.classList.remove('drag-over');
        });

        recDropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            recDropZone.classList.remove('drag-over');
            handleRecFiles(e.dataTransfer.files);
        });

        recResumesInput.addEventListener('change', (e) => {
            handleRecFiles(e.target.files);
        });
    }

    function handleRecFiles(files) {
        for (let file of files) {
            if (file.name.match(/\.(pdf|docx)$/i)) {
                recUploadedFiles.push(file);
                renderRecFileList();
            } else {
                alert(`File ${file.name} is not a valid format. Only PDF and DOCX are supported.`);
            }
        }
        updateRecResumeCountDisplay();
    }

    window.removeRecFile = (index) => {
        recUploadedFiles.splice(index, 1);
        renderRecFileList();
        updateRecResumeCountDisplay();
        
        if (recUploadedFiles.length === 0) {
            recDropZone.classList.remove('collapsed', 'active');
            recResumesHeader.classList.add('hidden');
        }
    };

    if (recProcessBtn) {
        recProcessBtn.addEventListener('click', async () => {
            const jd = recJobDescription.value.trim();
            if (!jd) {
                alert(MESSAGES.ENTER_JD);
                return;
            }
            if (recUploadedFiles.length === 0) {
                alert(MESSAGES.UPLOAD_RESUME);
                return;
            }

            recResultsContainer.classList.add('hidden');

            recDropZone.classList.add('collapsed');
            recDropZone.classList.remove('active');
            recResumesHeader.classList.remove('hidden');
            updateRecResumeCountDisplay();

            const formData = new FormData();
            formData.append('job_description', jd);
            
            const profileSelect = document.getElementById('rec-profile-select');
            if (profileSelect && profileSelect.value) {
                formData.append('profile_id', profileSelect.value);
            }
            
            const jdSelect = document.getElementById('rec-jd-select');
            if (jdSelect && jdSelect.value) {
                formData.append('jd_id', jdSelect.value);
            }
            
            recUploadedFiles.forEach(file => {
                formData.append('resumes', file);
            });

            toggleButtonLoading(recProcessBtn, true, "Processing...", "Run Match Screening");
            if (window.loadingOverlay) window.loadingOverlay.show();

            try {
                const data = await api.screenResumesRecruiter(formData);
                state.setRecruiterStats(null);
                renderRecruiterResults(data.results);
            } catch (err) {
                alert(err.message);
            } finally {
                if (window.loadingOverlay) window.loadingOverlay.hide();
                toggleButtonLoading(recProcessBtn, false, "Processing...", "Run Match Screening");
            }
        });
    }

    const jdSelect = document.getElementById('rec-jd-select');
    const btnSaveJd = document.getElementById('btn-save-jd');
    const btnArchiveJd = document.getElementById('btn-archive-jd');

    if (jdSelect) {
        jdSelect.addEventListener('change', () => {
            const selectedId = jdSelect.value;
            if (selectedId && window.recruiterJobsList) {
                const job = window.recruiterJobsList.find(j => j.id == selectedId);
                if (job) {
                    recJobDescription.value = job.description;
                    if (btnSaveJd) btnSaveJd.textContent = "💾 Update Library Item";
                }
            } else {
                recJobDescription.value = '';
                if (btnSaveJd) btnSaveJd.textContent = "💾 Save to Library";
            }
        });
    }

    if (btnSaveJd) {
        btnSaveJd.addEventListener('click', async () => {
            const jdText = recJobDescription.value.trim();
            if (!jdText) {
                alert("Please enter a job description to save.");
                return;
            }
            const selectedId = jdSelect ? jdSelect.value : "";
            try {
                const title = jdText.substring(0, 50) + (jdText.length > 50 ? "..." : "");
                const formData = new FormData();
                formData.append('title', title);
                formData.append('description', jdText);
                
                if (selectedId) {
                    await api.updateJob(selectedId, formData);
                    alert("Job description updated successfully!");
                } else {
                    const res = await api.createJob(formData);
                    alert("Job description saved to library!");
                }
                await loadJobDescriptionsDropdown();
            } catch (err) {
                alert("Failed to save job description: " + err.message);
            }
        });
    }

    if (btnArchiveJd) {
        btnArchiveJd.addEventListener('click', async () => {
            const selectedId = jdSelect ? jdSelect.value : "";
            if (!selectedId) {
                alert("Please select a job description from the library to archive.");
                return;
            }
            if (confirm("Are you sure you want to archive this job description?")) {
                try {
                    await api.archiveJob(selectedId);
                    alert("Job description archived successfully.");
                    recJobDescription.value = "";
                    await loadJobDescriptionsDropdown();
                    if (btnSaveJd) btnSaveJd.textContent = "💾 Save to Library";
                } catch (err) {
                    alert("Failed to archive job description: " + err.message);
                }
            }
        });
    }

    const recQuickViewModal = document.getElementById('rec-quick-view-modal');
    const closeQuickViewBtn = document.getElementById('close-quick-view-btn');

    if (closeQuickViewBtn && recQuickViewModal) {
        closeQuickViewBtn.addEventListener('click', () => {
            recQuickViewModal.classList.add('hidden');
        });
        
        recQuickViewModal.addEventListener('click', (e) => {
            if (e.target === recQuickViewModal) {
                recQuickViewModal.classList.add('hidden');
            }
        });
    }

    initialized = true;
}

/**
 * Initializer for Recruiter Resume Screening view.
 */
export async function initializeRecruiterScreen() {
    await loadScoringProfilesDropdown();
    await loadJobDescriptionsDropdown();
}

async function loadScoringProfilesDropdown() {
    const profileSelect = document.getElementById('rec-profile-select');
    if (!profileSelect) return;
    try {
        const profiles = await api.getScoringProfiles();
        profileSelect.innerHTML = profiles.map(p => 
            `<option value="${p.id}" ${p.is_default ? "selected" : ""}>${p.name} (Skills: ${parseInt(p.weights.skills*100)}%, Exp: ${parseInt(p.weights.experience*100)}%)</option>`
        ).join("");
    } catch (err) {
        console.error("Failed to load scoring profiles:", err);
    }
}

async function loadJobDescriptionsDropdown() {
    const jdSelect = document.getElementById('rec-jd-select');
    if (!jdSelect) return;
    try {
        const jobs = await api.getJobs();
        let options = '<option value="">-- Create New (No Library Item Selected) --</option>';
        options += jobs.map(j => 
            `<option value="${j.id}">${j.title} ${j.company ? " | " + j.company : ""}</option>`
        ).join("");
        jdSelect.innerHTML = options;
        window.recruiterJobsList = jobs;
    } catch (err) {
        console.error("Failed to load job descriptions:", err);
    }
}

/**
 * Clears Recruiter workspace input state.
 */
export function clearRecruiterWorkspaceState() {
    const recJobDescription = document.getElementById('rec-job-description');
    const recDropZone = document.getElementById('rec-drop-zone');
    const recResumesHeader = document.getElementById('rec-resumes-header');
    const recResultsContainer = document.getElementById('rec-results-container');
    const recResultsList = document.getElementById('rec-results-list');

    if (recJobDescription) recJobDescription.value = '';
    recUploadedFiles = [];
    renderRecFileList();
    if (recDropZone) recDropZone.classList.remove('collapsed', 'active');
    if (recResumesHeader) recResumesHeader.classList.add('hidden');
    if (recResultsContainer) recResultsContainer.classList.add('hidden');
    if (recResultsList) recResultsList.innerHTML = '';
}

function updateRecResumeCountDisplay() {
    const recResumesCount = document.getElementById('rec-resumes-count');
    if (recResumesCount) {
        recResumesCount.textContent = `Resumes (${recUploadedFiles.length})`;
    }
}

function renderRecFileList() {
    const recFileList = document.getElementById('rec-file-list');
    if (!recFileList) return;
    recFileList.innerHTML = '';
    recUploadedFiles.forEach((file, index) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${file.name}</span>
            <span style="color: #ef4444; cursor:pointer;" onclick="removeRecFile(${index})">&times;</span>
        `;
        recFileList.appendChild(li);
    });
}

/**
 * Initializer for Recruiter Dashboard view.
 */
export async function initializeRecruiterDashboard() {
    const dashRecName = document.getElementById('dash-rec-name');
    const dashCompName = document.getElementById('dash-comp-name');
    const dashCompType = document.getElementById('dash-comp-type');
    const dashHiringDomain = document.getElementById('dash-hiring-domain');

    // Loading state indicators
    if (dashRecName && dashRecName.textContent === "...") dashRecName.textContent = "Loading...";
    if (dashCompName && dashCompName.textContent === "...") dashCompName.textContent = "Loading...";
    if (dashCompType && dashCompType.textContent === "...") dashCompType.textContent = "Loading...";
    if (dashHiringDomain && dashHiringDomain.textContent === "...") dashHiringDomain.textContent = "Loading...";

    try {
        let profile = state.getProfile();
        if (!profile) {
            profile = await api.getProfile();
            state.setProfile(profile);
        }
        populateRecruiterProfileUI(profile);
        
        let stats = state.getRecruiterStats();
        if (!stats) {
            stats = await api.getRecruiterStats();
            state.setRecruiterStats(stats);
        }

        updateStatisticCard("stat-total-screened", stats.total_candidates_screened);
        updateStatisticCard("stat-avg-score", `${stats.average_ats_score.toFixed(1)}%`);
        updateStatisticCard("stat-avg-experience", `${stats.average_experience_tenure.toFixed(1)} yrs`);
        updateStatisticCard("stat-common-education", stats.most_common_education_level);
        
        // Render common missing skills list
        const missingList = document.getElementById("stat-missing-skills-list");
        if (missingList) {
            missingList.innerHTML = stats.most_common_missing_skills.length > 0
                ? stats.most_common_missing_skills.map(s => `<li>${s.skill} (found ${s.count} times)</li>`).join("")
                : "<li style='list-style:none; color:gray;'>No missing skills recorded yet</li>";
        }
        
        // Render common matched skills list
        const matchedList = document.getElementById("stat-matched-skills-list");
        if (matchedList) {
            matchedList.innerHTML = stats.most_common_matched_skills.length > 0
                ? stats.most_common_matched_skills.map(s => `<li>${s.skill} (found ${s.count} times)</li>`).join("")
                : "<li style='list-style:none; color:gray;'>No matched skills recorded yet</li>";
        }
        
        // Render top improvements list
        const improvementsList = document.getElementById("stat-improvements-list");
        if (improvementsList) {
            improvementsList.innerHTML = stats.top_recommended_improvements.length > 0
                ? stats.top_recommended_improvements.map(r => `<li>${r.recommendation} (found ${r.count} times)</li>`).join("")
                : "<li style='list-style:none; color:gray;'>No improvements generated yet</li>";
        }
    } catch (err) {
        console.error("Error loading recruiter dashboard:", err);
        const user = state.getUser();
        if (dashRecName && (dashRecName.textContent === "..." || dashRecName.textContent === "Loading...")) {
            dashRecName.textContent = user?.email?.split('@')[0] || "Recruiter";
        }
        if (dashCompName && (dashCompName.textContent === "..." || dashCompName.textContent === "Loading...")) {
            dashCompName.textContent = "Unavailable";
        }
        if (dashCompType && (dashCompType.textContent === "..." || dashCompType.textContent === "Loading...")) {
            dashCompType.textContent = "Unavailable";
        }
        if (dashHiringDomain && (dashHiringDomain.textContent === "..." || dashHiringDomain.textContent === "Loading...")) {
            dashHiringDomain.textContent = "Unavailable";
        }
    }
}


/**
 * Initializer for Recruiter Profile view.
 * Reuses shared profile state from Dashboard if already fetched.
 */
export async function initializeRecruiterProfile() {
    try {
        let profile = state.getProfile();
        if (!profile) {
            profile = await api.getProfile();
            state.setProfile(profile);
        }
        populateRecruiterProfileUI(profile);
    } catch (err) {
        console.error("Error loading recruiter profile:", err);
    }
}

function renderRecruiterResults(results) {
    const recResultsList = document.getElementById('rec-results-list');
    const recResultsContainer = document.getElementById('rec-results-container');
    if (!recResultsList) return;
    recResultsList.innerHTML = '';

    results.forEach(cand => {
        const card = document.createElement('div');
        card.className = 'candidate-card';
        card.innerHTML = getRecruiterCandidateCardHTML(cand);
        recResultsList.appendChild(card);
    });

    recResultsContainer.classList.remove('hidden');
    recResultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Modal quick view details mapping, bound to window
window.showCandidateQuickView = (cand) => {
    const recQuickViewModal = document.getElementById('rec-quick-view-modal');
    const qvCandName = document.getElementById('qv-cand-name');
    const qvCandScoreBadge = document.getElementById('qv-cand-score-badge');
    const qvCandEmail = document.getElementById('qv-cand-email');
    const qvCandPhone = document.getElementById('qv-cand-phone');
    const qvCandLinkedin = document.getElementById('qv-cand-linkedin');
    const qvCandGithub = document.getElementById('qv-cand-github');
    const qvCandExtractedSkills = document.getElementById('qv-cand-extracted-skills');
    const qvCandMatchedSkills = document.getElementById('qv-cand-matched-skills');
    const qvCandMissingSkills = document.getElementById('qv-cand-missing-skills');

    if (!recQuickViewModal) return;
    
    qvCandName.textContent = cand.name;
    
    let scoreClass = 'low-score';
    if (cand.similarity_score >= 70) {
        scoreClass = 'high-score';
    } else if (cand.similarity_score >= 40) {
        scoreClass = 'med-score';
    }
    
    qvCandScoreBadge.className = `score-badge ${scoreClass}`;
    qvCandScoreBadge.textContent = `${cand.similarity_score}% Match`;
    
    const qvCtxProfile = document.getElementById('qv-ctx-profile');
    const qvCtxJd = document.getElementById('qv-ctx-jd');
    const qvCtxEngine = document.getElementById('qv-ctx-engine');
    if (qvCtxProfile && qvCtxJd && qvCtxEngine) {
        const profileName = cand.analysis_metadata?.profile_name || "General Software Engineer";
        const profileVer = cand.analysis_metadata?.profile_version || "1.0.0";
        const engineVer = cand.analysis_metadata?.engine_version || "v1.0.0";
        qvCtxProfile.textContent = `${profileName} (v${profileVer})`;
        qvCtxJd.textContent = cand.job_description_title || "Selected JD";
        const cleanEngine = engineVer.replace(/^v/, '');
        qvCtxEngine.textContent = `Nipun Engine v${cleanEngine}`;
    }
    
    qvCandEmail.textContent = cand.email !== 'Not Provided' ? cand.email : 'N/A';
    qvCandPhone.textContent = cand.phone !== 'Not Provided' ? cand.phone : 'N/A';
    
    if (cand.linkedin !== 'Not Provided') {
        const url = sanitizeUrl(cand.linkedin);
        if (url !== '#') {
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank';
            a.style.color = '#6366f1';
            a.style.textDecoration = 'none';
            a.textContent = cand.linkedin;
            qvCandLinkedin.innerHTML = '';
            qvCandLinkedin.appendChild(a);
        } else {
            qvCandLinkedin.textContent = cand.linkedin;
        }
    } else {
        qvCandLinkedin.textContent = 'N/A';
    }
    
    if (cand.github !== 'Not Provided') {
        const url = sanitizeUrl(cand.github);
        if (url !== '#') {
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank';
            a.style.color = '#6366f1';
            a.style.textDecoration = 'none';
            a.textContent = cand.github;
            qvCandGithub.innerHTML = '';
            qvCandGithub.appendChild(a);
        } else {
            qvCandGithub.textContent = cand.github;
        }
    } else {
        qvCandGithub.textContent = 'N/A';
    }
    
    // Render XAI details
    const xaiContainer = document.getElementById('qv-xai-container');
    if (xaiContainer) {
        xaiContainer.innerHTML = renderXaiContent(cand.analysis_metadata?.xai);
    }
    
    // Render Resume Improvement Recommendations
    const recsContainer = document.getElementById('qv-recommendations-container');
    if (recsContainer) {
        recsContainer.innerHTML = renderRecommendations(cand.analysis_metadata?.recommendations);
    }
    
    const allExtracted = cand.matched_skills.concat(cand.missing_skills);
    // Sanitize skills via textContent assignment by creating elements
    const createSkillTags = (skills, className) => {
        if (!skills || skills.length === 0) return '<span style="color:#666">None</span>';
        const container = document.createElement('div');
        skills.forEach(s => {
            const span = document.createElement('span');
            span.className = className;
            span.textContent = s;
            container.appendChild(span);
        });
        return container.innerHTML; // Safe because we just set textContent
    };

    qvCandExtractedSkills.innerHTML = createSkillTags(allExtracted, 'skill-tag');
    qvCandMatchedSkills.innerHTML = createSkillTags(cand.matched_skills, 'skill-tag matched');
    qvCandMissingSkills.innerHTML = createSkillTags(cand.missing_skills, 'skill-tag missing');
    
    recQuickViewModal.classList.remove('hidden');
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

export function renderRecommendations(recsData) {
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
        const gainBadge = `<span style="background: rgba(16, 185, 129, 0.1); color: #10b981; font-size: 0.75rem; font-weight: bold; padding: 0.15rem 0.4rem; border-radius: 4px;">+${rec.estimated_score_gain.toFixed(1)} Match pts</span>`;

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

        if (statusUpper !== "ACTIVE") {
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
