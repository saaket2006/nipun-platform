import * as api from '../api.js';
import * as state from '../state.js';
import { getRecruiterCandidateCardHTML } from '../components/candidateCard.js';
import { updateStatisticCard } from '../components/statisticCard.js';
import { populateRecruiterProfileUI } from '../components/profileSection.js';
import { toggleButtonLoading } from '../components/loadingSpinner.js';
import { MESSAGES, ROUTES } from '../constants.js';
import { sanitizeUrl, escapeHTML } from '../utils.js';

let recUploadedFiles = [];
let initialized = false;
let activeScreeningRunId = 0;
let isScreeningActive = false;
let currentScreeningAbortController = null;

// JD Library State
let currentSelectedJdId = null;
let currentSelectedJdText = "";
let pendingNavigationTargetId = null;

function hasUnsavedJdChanges() {
    const recJobDescription = document.getElementById('rec-job-description');
    if (!recJobDescription) return false;
    const currentVal = recJobDescription.value.trim();
    if (currentSelectedJdId) {
        return currentVal !== (currentSelectedJdText || "").trim();
    } else {
        return currentVal.length > 0;
    }
}

function updateJdActionButtons() {
    const btnSaveJd = document.getElementById('btn-save-jd');
    const btnUpdateJd = document.getElementById('btn-update-jd');
    const btnArchiveJd = document.getElementById('btn-archive-jd');

    if (currentSelectedJdId) {
        if (btnSaveJd) {
            btnSaveJd.textContent = "💾 Save as New";
            btnSaveJd.title = "Save current text as a new named job description";
        }
        if (btnUpdateJd) btnUpdateJd.classList.remove('hidden');
        if (btnArchiveJd) btnArchiveJd.classList.remove('hidden');
    } else {
        if (btnSaveJd) {
            btnSaveJd.textContent = "💾 Save to Library";
            btnSaveJd.title = "Save this job description to library with a name";
        }
        if (btnUpdateJd) btnUpdateJd.classList.add('hidden');
        if (btnArchiveJd) btnArchiveJd.classList.add('hidden');
    }
}

function applyJdSelection(targetId) {
    const jdSelect = document.getElementById('rec-jd-select');
    const recJobDescription = document.getElementById('rec-job-description');

    if (targetId && window.recruiterJobsList) {
        const job = window.recruiterJobsList.find(j => String(j.id) === String(targetId));
        if (job) {
            currentSelectedJdId = String(job.id);
            currentSelectedJdText = job.description || "";
            if (recJobDescription) recJobDescription.value = job.description || "";
            if (jdSelect) jdSelect.value = String(job.id);
        }
    } else {
        currentSelectedJdId = null;
        currentSelectedJdText = "";
        if (recJobDescription) recJobDescription.value = "";
        if (jdSelect) jdSelect.value = "";
    }
    updateJdActionButtons();
}

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
        recDropZone.addEventListener('click', (e) => {
            if (e.target.closest('#rec-resumes-header') || e.target.closest('.rec-file-item')) {
                return;
            }
            recResumesInput.click();
        });

        recDropZone.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                if (e.target.closest('#rec-resumes-header') || e.target.closest('.rec-file-item')) {
                    return;
                }
                e.preventDefault();
                recResumesInput.click();
            }
        });

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
            if (isScreeningActive) return; // Prevent duplicate concurrent submissions

            const jd = recJobDescription.value.trim();
            if (!jd) {
                alert(MESSAGES.ENTER_JD);
                return;
            }
            if (recUploadedFiles.length === 0) {
                alert(MESSAGES.UPLOAD_RESUME);
                return;
            }

            // Immediately clear any previous run's results while new screening processes
            if (recResultsContainer) recResultsContainer.classList.add('hidden');
            const recResultsList = document.getElementById('rec-results-list');
            if (recResultsList) recResultsList.innerHTML = '';
            window.currentRecruiterResults = [];

            const recQuickViewModal = document.getElementById('rec-quick-view-modal');
            if (recQuickViewModal) recQuickViewModal.classList.add('hidden');

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

            // Check for optional custom scoring configuration
            try {
                const customConfig = getCustomScoringPayload();
                if (customConfig) {
                    formData.append('custom_scoring_config', JSON.stringify(customConfig));
                }
            } catch (configErr) {
                alert(configErr.message);
                return;
            }
            
            const jdSelect = document.getElementById('rec-jd-select');
            if (jdSelect && jdSelect.value) {
                formData.append('jd_id', jdSelect.value);
                if (window.recruiterJobsList) {
                    const job = window.recruiterJobsList.find(j => j.id == jdSelect.value);
                    if (job && job.title) {
                        formData.append('role', job.title);
                    }
                }
            }
            
            recUploadedFiles.forEach(file => {
                formData.append('resumes', file);
            });

            isScreeningActive = true;
            const thisRunId = ++activeScreeningRunId;
            currentScreeningAbortController = new AbortController();

            toggleButtonLoading(recProcessBtn, true, "Processing...", "Run Match Screening");
            if (window.loadingOverlay) window.loadingOverlay.show();

            try {
                const data = await api.screenResumesRecruiter(formData, { signal: currentScreeningAbortController.signal });
                // Check if run was superseded or reset while in flight
                if (thisRunId !== activeScreeningRunId) {
                    return;
                }
                state.setRecruiterStats(null);
                renderRecruiterResults(data.results, data.scoring_config);
            } catch (err) {
                if (thisRunId !== activeScreeningRunId || err.name === 'AbortError') {
                    return;
                }
                alert(err.message);
            } finally {
                if (thisRunId === activeScreeningRunId) {
                    isScreeningActive = false;
                    currentScreeningAbortController = null;
                    if (window.loadingOverlay) window.loadingOverlay.hide();
                    toggleButtonLoading(recProcessBtn, false, "Processing...", "Run Match Screening");
                }
            }
        });
    }

    // Bind Start New Screening and Clear / Start Fresh buttons
    const btnNewScreening = document.getElementById('btn-new-screening');
    if (btnNewScreening) {
        btnNewScreening.addEventListener('click', () => {
            resetScreeningWorkflowState({ resetJd: false });
            const screenWorkspace = document.querySelector('.screening-workspace');
            if (screenWorkspace) screenWorkspace.scrollIntoView({ behavior: 'smooth' });
        });
    }

    const btnResetScreening = document.getElementById('btn-reset-screening');
    if (btnResetScreening) {
        btnResetScreening.addEventListener('click', () => {
            resetScreeningWorkflowState({ resetJd: true });
        });
    }

    // ==========================================
    // JD Library Controls & Modals
    // ==========================================
    const jdSelect = document.getElementById('rec-jd-select');
    const btnSaveJd = document.getElementById('btn-save-jd');
    const btnUpdateJd = document.getElementById('btn-update-jd');
    const btnArchiveJd = document.getElementById('btn-archive-jd');

    // Modals
    const saveJdModal = document.getElementById('save-jd-modal');
    const closeSaveJdBtn = document.getElementById('close-save-jd-btn');
    const btnCancelSaveJd = document.getElementById('btn-cancel-save-jd');
    const btnConfirmSaveJd = document.getElementById('btn-confirm-save-jd');
    const saveJdNameInput = document.getElementById('save-jd-name-input');
    const saveJdNameWarning = document.getElementById('save-jd-name-warning');
    const saveJdNameError = document.getElementById('save-jd-name-error');
    const saveJdPreview = document.getElementById('save-jd-preview');

    const updateJdModal = document.getElementById('update-jd-modal');
    const closeUpdateJdBtn = document.getElementById('close-update-jd-btn');
    const btnCancelUpdateJd = document.getElementById('btn-cancel-update-jd');
    const btnConfirmUpdateJd = document.getElementById('btn-confirm-update-jd');
    const updateJdNameInput = document.getElementById('update-jd-name-input');
    const updateJdError = document.getElementById('update-jd-error');

    const unsavedModal = document.getElementById('unsaved-changes-modal');
    const btnKeepEditing = document.getElementById('btn-keep-editing');
    const btnDiscardChanges = document.getElementById('btn-discard-changes');
    const closeUnsavedBtn = document.getElementById('close-unsaved-changes-btn');

    // 1. Dropdown Selection with Unsaved Changes Guard
    if (jdSelect) {
        jdSelect.addEventListener('change', () => {
            const targetId = jdSelect.value;
            if (hasUnsavedJdChanges()) {
                pendingNavigationTargetId = targetId;
                // Revert visual selection until user decides
                jdSelect.value = currentSelectedJdId || "";
                if (unsavedModal) unsavedModal.classList.remove('hidden');
            } else {
                applyJdSelection(targetId);
            }
        });
    }

    // Unsaved Changes Modal Actions
    const closeUnsavedModal = () => {
        if (unsavedModal) unsavedModal.classList.add('hidden');
        pendingNavigationTargetId = null;
    };

    if (btnKeepEditing) {
        btnKeepEditing.addEventListener('click', closeUnsavedModal);
    }
    if (closeUnsavedBtn) {
        closeUnsavedBtn.addEventListener('click', closeUnsavedModal);
    }
    if (unsavedModal) {
        unsavedModal.addEventListener('click', (e) => {
            if (e.target === unsavedModal) closeUnsavedModal();
        });
    }
    if (btnDiscardChanges) {
        btnDiscardChanges.addEventListener('click', () => {
            const target = pendingNavigationTargetId;
            closeUnsavedModal();
            applyJdSelection(target);
        });
    }

    // 2. Save JD Modal Actions
    const openSaveJdModal = () => {
        const jdText = (recJobDescription?.value || "").trim();
        if (!jdText) {
            alert("Please enter a job description to save.");
            return;
        }
        if (saveJdPreview) {
            saveJdPreview.textContent = jdText.substring(0, 160) + (jdText.length > 160 ? "..." : "");
        }
        if (saveJdNameInput) {
            saveJdNameInput.value = "";
        }
        if (saveJdNameWarning) saveJdNameWarning.classList.add('hidden');
        if (saveJdNameError) {
            saveJdNameError.textContent = "";
            saveJdNameError.classList.add('hidden');
        }
        if (saveJdModal) {
            saveJdModal.classList.remove('hidden');
            setTimeout(() => saveJdNameInput?.focus(), 60);
        }
    };

    const closeSaveJdModal = () => {
        if (saveJdModal) saveJdModal.classList.add('hidden');
    };

    if (btnSaveJd) {
        btnSaveJd.addEventListener('click', openSaveJdModal);
    }
    if (closeSaveJdBtn) {
        closeSaveJdBtn.addEventListener('click', closeSaveJdModal);
    }
    if (btnCancelSaveJd) {
        btnCancelSaveJd.addEventListener('click', closeSaveJdModal);
    }
    if (saveJdModal) {
        saveJdModal.addEventListener('click', (e) => {
            if (e.target === saveJdModal) closeSaveJdModal();
        });
    }

    if (saveJdNameInput) {
        saveJdNameInput.addEventListener('input', () => {
            const val = saveJdNameInput.value.trim().toLowerCase();
            if (saveJdNameError) saveJdNameError.classList.add('hidden');
            if (val && window.recruiterJobsList) {
                const isDup = window.recruiterJobsList.some(j => (j.name || j.title || "").trim().toLowerCase() === val);
                if (isDup) {
                    if (saveJdNameWarning) saveJdNameWarning.classList.remove('hidden');
                } else {
                    if (saveJdNameWarning) saveJdNameWarning.classList.add('hidden');
                }
            } else {
                if (saveJdNameWarning) saveJdNameWarning.classList.add('hidden');
            }
        });

        saveJdNameInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                btnConfirmSaveJd?.click();
            }
        });
    }

    if (btnConfirmSaveJd) {
        btnConfirmSaveJd.addEventListener('click', async () => {
            const name = (saveJdNameInput?.value || "").trim();
            const jdText = (recJobDescription?.value || "").trim();

            if (!name) {
                if (saveJdNameError) {
                    saveJdNameError.textContent = "Please enter a recognizable name for this job description.";
                    saveJdNameError.classList.remove('hidden');
                }
                saveJdNameInput?.focus();
                return;
            }

            if (!jdText) {
                closeSaveJdModal();
                alert("Please enter a job description to save.");
                return;
            }

            toggleButtonLoading(btnConfirmSaveJd, true, "Saving...", "Save JD");
            btnConfirmSaveJd.disabled = true;

            try {
                const formData = new FormData();
                formData.append('title', name);
                formData.append('name', name);
                formData.append('description', jdText);

                const res = await api.createJob(formData);
                closeSaveJdModal();
                alert("Job description saved to library successfully!");

                const savedId = res?.id;
                await loadJobDescriptionsDropdown(savedId);
                applyJdSelection(savedId);
            } catch (err) {
                if (saveJdNameError) {
                    saveJdNameError.textContent = err.message || "Failed to save job description.";
                    saveJdNameError.classList.remove('hidden');
                } else {
                    alert("Failed to save job description: " + err.message);
                }
            } finally {
                toggleButtonLoading(btnConfirmSaveJd, false, "Saving...", "Save JD");
                btnConfirmSaveJd.disabled = false;
            }
        });
    }

    // 3. Update Saved JD Modal Actions
    const openUpdateJdModal = () => {
        if (!currentSelectedJdId) return;
        const jdText = (recJobDescription?.value || "").trim();
        if (!jdText) {
            alert("Please enter a job description.");
            return;
        }
        const job = window.recruiterJobsList?.find(j => String(j.id) === String(currentSelectedJdId));
        if (updateJdNameInput) {
            updateJdNameInput.value = job ? (job.name || job.title) : "";
        }
        if (updateJdError) {
            updateJdError.textContent = "";
            updateJdError.classList.add('hidden');
        }
        if (updateJdModal) {
            updateJdModal.classList.remove('hidden');
            setTimeout(() => updateJdNameInput?.focus(), 60);
        }
    };

    const closeUpdateJdModal = () => {
        if (updateJdModal) updateJdModal.classList.add('hidden');
    };

    if (btnUpdateJd) {
        btnUpdateJd.addEventListener('click', openUpdateJdModal);
    }
    if (closeUpdateJdBtn) {
        closeUpdateJdBtn.addEventListener('click', closeUpdateJdModal);
    }
    if (btnCancelUpdateJd) {
        btnCancelUpdateJd.addEventListener('click', closeUpdateJdModal);
    }
    if (updateJdModal) {
        updateJdModal.addEventListener('click', (e) => {
            if (e.target === updateJdModal) closeUpdateJdModal();
        });
    }

    if (updateJdNameInput) {
        updateJdNameInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                btnConfirmUpdateJd?.click();
            }
        });
    }

    if (btnConfirmUpdateJd) {
        btnConfirmUpdateJd.addEventListener('click', async () => {
            if (!currentSelectedJdId) return;
            const name = (updateJdNameInput?.value || "").trim();
            const jdText = (recJobDescription?.value || "").trim();

            if (!name) {
                if (updateJdError) {
                    updateJdError.textContent = "Job description name cannot be empty.";
                    updateJdError.classList.remove('hidden');
                }
                updateJdNameInput?.focus();
                return;
            }

            if (!jdText) {
                closeUpdateJdModal();
                alert("Job description text cannot be empty.");
                return;
            }

            toggleButtonLoading(btnConfirmUpdateJd, true, "Updating...", "Update JD");
            btnConfirmUpdateJd.disabled = true;

            try {
                const formData = new FormData();
                formData.append('title', name);
                formData.append('name', name);
                formData.append('description', jdText);

                await api.updateJob(currentSelectedJdId, formData);
                closeUpdateJdModal();
                alert("Job description updated successfully!");

                currentSelectedJdText = jdText;
                await loadJobDescriptionsDropdown(currentSelectedJdId);
                applyJdSelection(currentSelectedJdId);
            } catch (err) {
                if (updateJdError) {
                    updateJdError.textContent = err.message || "Failed to update job description.";
                    updateJdError.classList.remove('hidden');
                } else {
                    alert("Failed to update job description: " + err.message);
                }
            } finally {
                toggleButtonLoading(btnConfirmUpdateJd, false, "Updating...", "Update JD");
                btnConfirmUpdateJd.disabled = false;
            }
        });
    }

    // 4. Archive Selected Action
    if (btnArchiveJd) {
        btnArchiveJd.addEventListener('click', async () => {
            if (!currentSelectedJdId) {
                alert("Please select a job description from the library to archive.");
                return;
            }
            const job = window.recruiterJobsList?.find(j => String(j.id) === String(currentSelectedJdId));
            const jdName = job ? (job.name || job.title) : null;
            const name = jdName ? `"${jdName}"` : "this job description";

            if (confirm(`Are you sure you want to archive ${name}? It will be removed from your active library.`)) {
                try {
                    await api.archiveJob(currentSelectedJdId);
                    alert("Job description archived successfully.");
                    applyJdSelection(null);
                    await loadJobDescriptionsDropdown(null);
                } catch (err) {
                    alert("Failed to archive job description: " + err.message);
                }
            }
        });
    }

    // 5. Global Esc key & backdrop click for JD Modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (unsavedModal && !unsavedModal.classList.contains('hidden')) {
                closeUnsavedModal();
            } else if (saveJdModal && !saveJdModal.classList.contains('hidden')) {
                closeSaveJdModal();
            } else if (updateJdModal && !updateJdModal.classList.contains('hidden')) {
                closeUpdateJdModal();
            }
        }
    });

    [saveJdModal, updateJdModal, unsavedModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    if (modal === unsavedModal) pendingNavigationTargetId = null;
                }
            });
        }
    });

    const recResultsList = document.getElementById('rec-results-list');
    if (recResultsList) {
        recResultsList.addEventListener('click', (e) => {
            const qvBtn = e.target.closest('.quick-view-btn');
            if (qvBtn) {
                const idxStr = qvBtn.dataset.candidateIndex;
                if (idxStr !== undefined && idxStr !== '') {
                    const idx = parseInt(idxStr, 10);
                    if (window.currentRecruiterResults && window.currentRecruiterResults[idx]) {
                        showCandidateQuickView(window.currentRecruiterResults[idx]);
                    }
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

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (unsavedModal && !unsavedModal.classList.contains('hidden')) {
                    closeUnsavedModal();
                    return;
                }
                if (updateJdModal && !updateJdModal.classList.contains('hidden')) {
                    closeUpdateJdModal();
                    return;
                }
                if (saveJdModal && !saveJdModal.classList.contains('hidden')) {
                    closeSaveJdModal();
                    return;
                }
                if (recQuickViewModal && !recQuickViewModal.classList.contains('hidden')) {
                    recQuickViewModal.classList.add('hidden');
                    return;
                }
            }
        });
    }

    initialized = true;
}

/**
 * Initializer for Recruiter Resume Screening view.
 */
export async function initializeRecruiterScreen() {
    // Reset transient screening results and state when navigating to screen view fresh
    if (!isScreeningActive) {
        resetScreeningWorkflowState({ resetJd: false });
    }
    await loadScoringProfilesDropdown();
    await loadJobDescriptionsDropdown();
    initAdvancedScoringControls();
}

async function loadScoringProfilesDropdown() {
    const profileSelect = document.getElementById('rec-profile-select');
    if (!profileSelect) return;
    try {
        const profiles = await api.getScoringProfiles();
        window.recruiterScoringProfiles = profiles || [];
        profileSelect.innerHTML = profiles.map(p => 
            `<option value="${p.id}" ${p.is_default ? "selected" : ""}>${p.name} (Skills: ${parseInt(p.weights.skills*100)}%, Exp: ${parseInt(p.weights.experience*100)}%)</option>`
        ).join("");

        if (!profileSelect.dataset.listenerBound) {
            profileSelect.dataset.listenerBound = "true";
            profileSelect.addEventListener('change', () => {
                syncScoringControlsWithSelectedProfile();
            });
        }
        syncScoringControlsWithSelectedProfile(true);
    } catch (err) {
        console.error("Failed to load scoring profiles:", err);
    }
}

async function loadJobDescriptionsDropdown(selectedId = null) {
    const jdSelect = document.getElementById('rec-jd-select');
    if (!jdSelect) return;
    try {
        jdSelect.innerHTML = '<option value="">Loading saved job descriptions...</option>';
        const jobs = await api.getJobs();
        window.recruiterJobsList = jobs || [];

        let options = '';
        if (!jobs || jobs.length === 0) {
            options = '<option value="">-- Create New (No saved JDs in library) --</option>';
        } else {
            options = '<option value="">-- Create New (No Library Item Selected) --</option>';
            options += jobs.map(j => {
                const label = j.name || j.title || "Untitled JD";
                return `<option value="${j.id}">${escapeHTML(label)}${j.company ? " | " + escapeHTML(j.company) : ""}</option>`;
            }).join("");
        }
        jdSelect.innerHTML = options;

        if (selectedId) {
            const exists = (jobs || []).some(j => String(j.id) === String(selectedId));
            if (exists) {
                applyJdSelection(selectedId);
            } else {
                applyJdSelection(null);
            }
        } else {
            applyJdSelection(null);
        }
    } catch (err) {
        console.error("Failed to load job descriptions:", err);
        jdSelect.innerHTML = '<option value="">-- Create New (Failed to load library) --</option>';
        applyJdSelection(null);
    }
}

/**
 * Unified reset mechanism for transient recruiter screening state.
 * Resets uploaded resumes, file inputs, previous results, quick view modal,
 * and aborts/supersedes any in-flight screening requests.
 */
export function resetScreeningWorkflowState(options = { resetJd: false }) {
    // 1. Invalidate and abort any in-flight asynchronous screening run
    activeScreeningRunId++;
    if (currentScreeningAbortController) {
        try {
            currentScreeningAbortController.abort();
        } catch (_) {}
        currentScreeningAbortController = null;
    }
    isScreeningActive = false;

    // 2. Clear in-memory resume files and reset file input element value
    recUploadedFiles = [];
    const recResumesInput = document.getElementById('rec-resumes');
    if (recResumesInput) {
        recResumesInput.value = ''; // Clears input so selecting the same files fires change event
    }
    renderRecFileList();
    updateRecResumeCountDisplay();

    // 3. Reset Dropzone visual state
    const recDropZone = document.getElementById('rec-drop-zone');
    const recResumesHeader = document.getElementById('rec-resumes-header');
    if (recDropZone) recDropZone.classList.remove('collapsed', 'active', 'drag-over');
    if (recResumesHeader) recResumesHeader.classList.add('hidden');

    // 4. Reset Results, Candidate Cards, and cached results
    const recResultsContainer = document.getElementById('rec-results-container');
    const recResultsList = document.getElementById('rec-results-list');
    if (recResultsContainer) recResultsContainer.classList.add('hidden');
    if (recResultsList) recResultsList.innerHTML = '';
    window.currentRecruiterResults = [];

    // 5. Reset Quick View modal if open
    const recQuickViewModal = document.getElementById('rec-quick-view-modal');
    if (recQuickViewModal) recQuickViewModal.classList.add('hidden');

    // 6. Reset loading spinners and overlays
    const recProcessBtn = document.getElementById('rec-process-btn');
    if (recProcessBtn) {
        toggleButtonLoading(recProcessBtn, false, "Processing...", "Run Match Screening");
    }
    if (window.loadingOverlay) window.loadingOverlay.hide();

    // 7. Reset per-run advanced scoring settings and results transparency banner
    resetAdvancedScoringState();

    // 8. Optional JD reset
    if (options && options.resetJd) {
        const recJobDescription = document.getElementById('rec-job-description');
        if (recJobDescription) recJobDescription.value = '';
        applyJdSelection(null);
    }
}

/**
 * Clears Recruiter workspace input state (called on logout or full clear).
 */
export function clearRecruiterWorkspaceState() {
    resetScreeningWorkflowState({ resetJd: true });
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
        li.className = 'rec-file-item';
        li.innerHTML = `
            <span class="rec-file-name" style="color: var(--color-ink); font-weight: 500; font-size: 0.85rem;">📄 ${escapeHTML(file.name)}</span>
            <button type="button" class="rec-file-remove-btn" onclick="removeRecFile(${index})" aria-label="Remove file" style="background: transparent; border: none; color: var(--color-clay); font-size: 1.25rem; line-height: 1; cursor: pointer; padding: 0 4px;">&times;</button>
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
            missingList.innerHTML = stats.most_common_missing_skills && stats.most_common_missing_skills.length > 0
                ? stats.most_common_missing_skills.map(s => `<li>${escapeHTML(s.skill)} (found ${s.count} times)</li>`).join("")
                : "<li style='list-style:none; color: var(--color-muted); font-size: 0.8125rem; font-family: var(--font-body);'>No missing skills recorded yet</li>";
        }
        
        // Render common matched skills list
        const matchedList = document.getElementById("stat-matched-skills-list");
        if (matchedList) {
            matchedList.innerHTML = stats.most_common_matched_skills && stats.most_common_matched_skills.length > 0
                ? stats.most_common_matched_skills.map(s => `<li>${escapeHTML(s.skill)} (found ${s.count} times)</li>`).join("")
                : "<li style='list-style:none; color: var(--color-muted); font-size: 0.8125rem; font-family: var(--font-body);'>No matched skills recorded yet</li>";
        }
        
        // Improvements list is candidate-only; clear and do not render on recruiter dashboard
        const improvementsList = document.getElementById("stat-improvements-list");
        if (improvementsList) {
            improvementsList.innerHTML = '';
        }
    } catch (err) {
        console.error("Error loading recruiter dashboard:", err);
        const user = state.getUser();
        if (dashRecName && (dashRecName.textContent === "..." || dashRecName.textContent === "Loading...")) {
            dashRecName.textContent = user?.display_name || user?.email?.split('@')[0] || "Recruiter";
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


let recProfileEventsBound = false;

/**
 * Initializer for Recruiter Profile view.
 * Reuses shared profile state from Dashboard if already fetched.
 */
export async function initializeRecruiterProfile() {
    const feedbackEl = document.getElementById('rec-profile-feedback');
    const displayContainer = document.getElementById('rec-profile-display');
    const editForm = document.getElementById('rec-profile-edit-form');
    const editBtn = document.getElementById('rec-edit-profile-btn');
    const cancelBtn = document.getElementById('rec-cancel-edit-btn');
    const saveBtn = document.getElementById('rec-save-profile-btn');

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

    loadRecruiterScreeningHistory();

    const refreshHistoryBtn = document.getElementById('rec-refresh-history-btn');
    if (refreshHistoryBtn && !refreshHistoryBtn.dataset.bound) {
        refreshHistoryBtn.dataset.bound = "true";
        refreshHistoryBtn.addEventListener('click', () => loadRecruiterScreeningHistory(true));
    }

    const retryHistoryBtn = document.getElementById('rec-history-retry-btn');
    if (retryHistoryBtn && !retryHistoryBtn.dataset.bound) {
        retryHistoryBtn.dataset.bound = "true";
        retryHistoryBtn.addEventListener('click', () => loadRecruiterScreeningHistory(true));
    }

    if (!recProfileEventsBound) {
        if (editBtn && displayContainer && editForm) {
            editBtn.addEventListener('click', () => {
                const currentProfile = state.getProfile();
                populateRecruiterProfileUI(currentProfile);
                if (feedbackEl) {
                    feedbackEl.className = 'hidden';
                    feedbackEl.textContent = '';
                }
                displayContainer.classList.add('hidden');
                editForm.classList.remove('hidden');
                editBtn.classList.add('hidden');
                const nameInput = document.getElementById('rec-edit-display-name');
                if (nameInput) nameInput.focus();
            });
        }

        if (cancelBtn && displayContainer && editForm) {
            cancelBtn.addEventListener('click', () => {
                const currentProfile = state.getProfile();
                populateRecruiterProfileUI(currentProfile);
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

                const displayName = document.getElementById('rec-edit-display-name')?.value?.trim();
                const compName = document.getElementById('rec-edit-comp-name')?.value?.trim();
                const compType = document.getElementById('rec-edit-comp-type')?.value?.trim();
                const hiringDomain = document.getElementById('rec-edit-hiring-domain')?.value?.trim();

                if (!displayName) {
                    showRecruiterProfileFeedback("Display name cannot be empty.", false);
                    return;
                }
                if (!compName) {
                    showRecruiterProfileFeedback("Company name cannot be empty.", false);
                    return;
                }
                if (!compType) {
                    showRecruiterProfileFeedback("Company type is required.", false);
                    return;
                }
                if (!hiringDomain) {
                    showRecruiterProfileFeedback("Hiring domain focus cannot be empty.", false);
                    return;
                }

                if (saveBtn) {
                    saveBtn.disabled = true;
                    saveBtn.textContent = "Saving...";
                }

                try {
                    const patchResponse = await api.updateRecruiterProfile({
                        display_name: displayName,
                        company_name: compName,
                        company_type: compType,
                        hiring_domain: hiringDomain
                    });

                    // Merge safely with existing profile state
                    const existingProfile = state.getProfile() || {};
                    const updatedProfile = {
                        ...existingProfile,
                        ...patchResponse,
                        recruiter_profile: {
                            ...(existingProfile.recruiter_profile || {}),
                            ...(patchResponse.recruiter_profile || {})
                        }
                    };

                    state.setProfile(updatedProfile);
                    populateRecruiterProfileUI(updatedProfile);

                    showRecruiterProfileFeedback("Profile updated successfully!", true);

                    // Revert to display mode
                    editForm.classList.add('hidden');
                    displayContainer?.classList.remove('hidden');
                    if (editBtn) editBtn.classList.remove('hidden');
                } catch (err) {
                    console.error("Error updating recruiter profile:", err);
                    showRecruiterProfileFeedback(err.message || "Failed to update profile. Please try again.", false);
                } finally {
                    if (saveBtn) {
                        saveBtn.disabled = false;
                        saveBtn.textContent = "Save Changes";
                    }
                }
            });
        }

        recProfileEventsBound = true;
    }
}

function showRecruiterProfileFeedback(message, isSuccess) {
    const feedbackEl = document.getElementById('rec-profile-feedback');
    if (!feedbackEl) return;

    feedbackEl.className = '';
    if (isSuccess) {
        feedbackEl.style.cssText = "margin-bottom: 1.5rem; padding: 0.85rem 1.2rem; border-radius: 8px; font-size: 0.9rem; font-weight: 500; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); color: #4ade80;";
    } else {
        feedbackEl.style.cssText = "margin-bottom: 1.5rem; padding: 0.85rem 1.2rem; border-radius: 8px; font-size: 0.9rem; font-weight: 500; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171;";
    }
    feedbackEl.textContent = message;
}

let isRefreshingHistory = false;

/**
 * Loads and displays the recruiter's past screening history tasks.
 */
export async function loadRecruiterScreeningHistory(force = false) {
    if (isRefreshingHistory) return;

    const loadingEl = document.getElementById('rec-history-loading');
    const errorEl = document.getElementById('rec-history-error');
    const errorMsgEl = document.getElementById('rec-history-error-msg');
    const emptyEl = document.getElementById('rec-history-empty');
    const listEl = document.getElementById('rec-history-list');
    const refreshBtn = document.getElementById('rec-refresh-history-btn');

    if (!listEl) return;

    isRefreshingHistory = true;
    if (refreshBtn) {
        refreshBtn.classList.add('is-refreshing');
        refreshBtn.disabled = true;
        refreshBtn.setAttribute('aria-busy', 'true');
    }

    const hasExistingItems = listEl.children.length > 0;

    if (!hasExistingItems) {
        if (loadingEl) loadingEl.classList.remove('hidden');
        listEl.classList.add('hidden');
    }
    if (errorEl) errorEl.classList.add('hidden');
    if (emptyEl) emptyEl.classList.add('hidden');

    try {
        const historyTasks = await api.getRecruiterHistory();
        if (loadingEl) loadingEl.classList.add('hidden');

        if (!Array.isArray(historyTasks) || historyTasks.length === 0) {
            listEl.innerHTML = '';
            listEl.classList.add('hidden');
            if (emptyEl) emptyEl.classList.remove('hidden');
            return;
        }

        renderRecruiterHistoryList(historyTasks);
        listEl.classList.remove('hidden');
    } catch (err) {
        console.error("Error loading screening history:", err);
        if (loadingEl) loadingEl.classList.add('hidden');
        if (errorEl) {
            if (errorMsgEl) errorMsgEl.textContent = err.message || "Failed to load screening history.";
            errorEl.classList.remove('hidden');
        }
        if (!hasExistingItems) {
            listEl.classList.add('hidden');
        }
    } finally {
        isRefreshingHistory = false;
        if (refreshBtn) {
            refreshBtn.classList.remove('is-refreshing');
            refreshBtn.disabled = false;
            refreshBtn.removeAttribute('aria-busy');
        }
    }
}

/**
 * Renders screening history items.
 * Each entry shows Date, Role, Resumes Scanned, and More Info button.
 */
function renderRecruiterHistoryList(tasks) {
    const listEl = document.getElementById('rec-history-list');
    if (!listEl) return;
    listEl.innerHTML = '';

    tasks.forEach(task => {
        const item = document.createElement('div');
        item.className = 'history-item-card';
        
        const dateStr = task.created_at ? new Date(task.created_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }) : 'N/A';

        item.innerHTML = `
            <div class="history-item-main" style="display: flex; flex-direction: column; gap: 0.35rem;">
                <h4 class="history-item-role" style="font-size: 1rem; font-weight: 600; color: var(--color-ink); margin: 0;">${escapeHTML(task.role || 'Screening Run')}</h4>
                <div class="history-item-meta" style="display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; font-size: 0.8125rem;">
                    <span class="history-meta-date" style="color: var(--color-muted); font-family: var(--font-mono); display: inline-flex; align-items: center; gap: 0.35rem;">📅 ${dateStr}</span>
                    <span class="history-meta-divider" style="color: var(--color-rule);">•</span>
                    <span class="history-meta-badge" style="background: var(--color-forest-light); color: var(--color-forest); border: 1px solid var(--color-forest-border); font-family: var(--font-mono); font-size: 0.75rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 4px; display: inline-flex; align-items: center; gap: 0.35rem;">${task.resume_count} Resumes Scanned</span>
                </div>
            </div>
            <div class="history-item-actions">
                <button type="button" class="glow-btn secondary history-more-info-btn" data-task-id="${task.id}" style="padding: 0.45rem 1rem; font-size: 0.8125rem; font-weight: 600; cursor: pointer;">
                    More Info →
                </button>
            </div>
        `;

        const moreBtn = item.querySelector('.history-more-info-btn');
        if (moreBtn) {
            moreBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                window.location.hash = `#/recruiter/history?id=${task.id}`;
            });
        }

        listEl.appendChild(item);
    });

    listEl.classList.remove('hidden');
}

/**
 * Initializes and displays the detailed view of a specific screening task.
 */
export async function initializeRecruiterHistoryDetail(taskId) {
    const loadingEl = document.getElementById('rec-task-detail-loading');
    const errorEl = document.getElementById('rec-task-detail-error');
    const errorMsgEl = document.getElementById('rec-task-detail-error-msg');
    const contentEl = document.getElementById('rec-task-detail-content');
    const backBtn = document.getElementById('btn-back-to-profile');
    const retryBtn = document.getElementById('rec-task-detail-retry-btn');

    if (backBtn && !backBtn.dataset.bound) {
        backBtn.dataset.bound = "true";
        backBtn.addEventListener('click', () => {
            window.location.hash = ROUTES.PROFILE;
        });
    }

    if (retryBtn && !retryBtn.dataset.bound) {
        retryBtn.dataset.bound = "true";
        retryBtn.addEventListener('click', () => {
            initializeRecruiterHistoryDetail(taskId);
        });
    }

    if (!taskId) {
        if (loadingEl) loadingEl.classList.add('hidden');
        if (contentEl) contentEl.classList.add('hidden');
        if (errorEl) {
            if (errorMsgEl) errorMsgEl.textContent = "No screening task ID specified.";
            errorEl.classList.remove('hidden');
        }
        return;
    }

    if (loadingEl) loadingEl.classList.remove('hidden');
    if (errorEl) errorEl.classList.add('hidden');
    if (contentEl) contentEl.classList.add('hidden');

    try {
        const task = await api.getRecruiterHistoryTask(taskId);
        if (loadingEl) loadingEl.classList.add('hidden');

        // Populate Task Header and Overview
        const roleEl = document.getElementById('task-detail-role');
        const dateEl = document.getElementById('task-detail-date');
        const resumesEl = document.getElementById('task-detail-resumes');
        const jdEl = document.getElementById('task-detail-jd');
        const candCountEl = document.getElementById('task-detail-candidate-count');
        const candListEl = document.getElementById('task-detail-candidates-list');

        if (roleEl) roleEl.textContent = task.role || "Screening Task";
        
        const dateStr = task.created_at ? new Date(task.created_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }) : 'N/A';
        if (dateEl) dateEl.textContent = dateStr;
        if (resumesEl) resumesEl.textContent = `${task.resume_count} Resumes Scanned`;
        if (jdEl) jdEl.textContent = task.job_description || "No job description text recorded.";

        const candidates = Array.isArray(task.ranked_results) ? task.ranked_results : [];
        if (candCountEl) candCountEl.textContent = `${candidates.length} candidate${candidates.length === 1 ? '' : 's'}`;

        window.currentRecruiterResults = candidates;

        if (candListEl) {
            candListEl.innerHTML = '';
            if (candidates.length === 0) {
                candListEl.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--text-secondary); font-size: 0.9rem;">
                        No ranked candidates available for this run.
                    </div>
                `;
            } else {
                candidates.forEach((cand, index) => {
                    const card = document.createElement('div');
                    card.className = 'candidate-card';
                    card.innerHTML = getRecruiterCandidateCardHTML(cand, index);

                    const qvBtn = card.querySelector('.quick-view-btn');
                    if (qvBtn) {
                        qvBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            showCandidateQuickView(cand);
                        });
                    }

                    candListEl.appendChild(card);
                });
            }
        }

        if (contentEl) contentEl.classList.remove('hidden');
    } catch (err) {
        console.error("Error loading task details:", err);
        if (loadingEl) loadingEl.classList.add('hidden');
        if (contentEl) contentEl.classList.add('hidden');
        if (errorEl) {
            if (errorMsgEl) errorMsgEl.textContent = err.message || "Screening task not found or unauthorized.";
            errorEl.classList.remove('hidden');
        }
    }
}

export function renderRecruiterResults(results, scoringConfig = null) {
    window.currentRecruiterResults = results;
    const recResultsList = document.getElementById('rec-results-list');
    const recResultsContainer = document.getElementById('rec-results-container');
    const banner = document.getElementById('scoring-applied-banner');

    if (!recResultsList) return;
    recResultsList.innerHTML = '';

    // Render Scoring Configuration Transparency Banner
    if (banner) {
        if (scoringConfig) {
            const isCustom = scoringConfig.is_custom;
            const profileName = scoringConfig.profile_name || "General Software Engineer";
            const w = scoringConfig.component_weights || {};
            const skillsPct = Math.round((w.skills || 0) * 100);
            const expPct = Math.round((w.experience || 0) * 100);
            const eduPct = Math.round((w.education || 0) * 100);
            const projPct = Math.round((w.projects || 0) * 100);
            const thresh = scoringConfig.scoring_thresholds || {};

            banner.className = 'scoring-applied-banner';
            banner.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;">
                    <span style="font-size: 0.75rem; font-weight: 700; font-family: var(--font-mono); padding: 3px 8px; border-radius: 4px; text-transform: uppercase; ${isCustom ? 'background: var(--color-clay-light); color: var(--color-clay); border: 1px solid var(--color-clay-border);' : 'background: var(--color-forest-light); color: var(--color-forest); border: 1px solid var(--color-forest-border);'}">
                        ${isCustom ? '⚙️ Custom Scoring Applied' : '✓ Profile Defaults Applied'}
                    </span>
                    <span style="font-weight: 600; color: var(--color-ink); font-family: var(--font-body);">${escapeHTML(profileName)}</span>
                </div>
                <div style="font-size: 0.8125rem; color: var(--color-muted); display: flex; gap: 0.85rem; flex-wrap: wrap; align-items: center;">
                    <span>Skills: <strong style="color: var(--color-ink); font-family: var(--font-mono);">${skillsPct}%</strong></span>
                    <span>Exp: <strong style="color: var(--color-ink); font-family: var(--font-mono);">${expPct}%</strong></span>
                    <span>Edu: <strong style="color: var(--color-ink); font-family: var(--font-mono);">${eduPct}%</strong></span>
                    <span>Projects: <strong style="color: var(--color-ink); font-family: var(--font-mono);">${projPct}%</strong></span>
                    ${isCustom && thresh.max_experience_years ? `<span style="border-left: 1px solid var(--color-rule); padding-left: 0.6rem;">Exp Target: <strong style="color: var(--color-ink); font-family: var(--font-mono);">${thresh.max_experience_years}y</strong></span>` : ''}
                    ${isCustom && thresh.project_target_count ? `<span>Proj Target: <strong style="color: var(--color-ink); font-family: var(--font-mono);">${thresh.project_target_count}</strong></span>` : ''}
                </div>
            `;
            banner.classList.remove('hidden');
        } else {
            banner.innerHTML = '';
            banner.classList.add('hidden');
        }
    }

    const candidateList = Array.isArray(results) ? results : [];

    candidateList.forEach((cand, index) => {
        const card = document.createElement('div');
        card.className = 'candidate-card';
        card.innerHTML = getRecruiterCandidateCardHTML(cand, index);

        const qvBtn = card.querySelector('.quick-view-btn');
        if (qvBtn) {
            qvBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                showCandidateQuickView(cand);
            });
        }

        recResultsList.appendChild(card);
    });

    if (recResultsContainer) {
        recResultsContainer.classList.remove('hidden');
        recResultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
}

// Modal quick view details mapping, exported and bound to window
export function showCandidateQuickView(cand) {
    if (!cand) return;
    const recQuickViewModal = document.getElementById('rec-quick-view-modal');
    if (!recQuickViewModal) return;

    const qvCandName = document.getElementById('qv-cand-name');
    const qvCandScoreBadge = document.getElementById('qv-cand-score-badge');
    const qvCandEmail = document.getElementById('qv-cand-email');
    const qvCandPhone = document.getElementById('qv-cand-phone');
    const qvCandLinkedin = document.getElementById('qv-cand-linkedin');
    const qvCandGithub = document.getElementById('qv-cand-github');
    const qvCandExtractedSkills = document.getElementById('qv-cand-extracted-skills');
    const qvCandMatchedSkills = document.getElementById('qv-cand-matched-skills');
    const qvCandMissingSkills = document.getElementById('qv-cand-missing-skills');
    
    if (qvCandName) {
        qvCandName.textContent = cand.name || 'Unnamed Candidate';
    }
    
    const score = typeof cand.similarity_score === 'number' ? cand.similarity_score : 0;
    let scoreClass = 'low-score';
    if (score >= 70) {
        scoreClass = 'high-score';
    } else if (score >= 40) {
        scoreClass = 'med-score';
    }
    
    if (qvCandScoreBadge) {
        qvCandScoreBadge.className = `score-badge ${scoreClass}`;
        qvCandScoreBadge.textContent = `${score}% Match`;
    }
    
    const qvCtxProfile = document.getElementById('qv-ctx-profile');
    const qvCtxJd = document.getElementById('qv-ctx-jd');
    const qvCtxEngine = document.getElementById('qv-ctx-engine');
    if (qvCtxProfile && qvCtxJd && qvCtxEngine) {
        const profileName = cand.analysis_metadata?.profile_name || "General Software Engineer";
        const profileVer = cand.analysis_metadata?.profile_version || "1.0.0";
        const engineVer = cand.analysis_metadata?.engine_version || "v1.0.0";
        qvCtxProfile.textContent = `${profileName} (v${profileVer})`;
        qvCtxJd.textContent = cand.job_description_title || "Selected JD";
        const cleanEngine = String(engineVer).replace(/^v/, '');
        qvCtxEngine.textContent = `Nipun Engine v${cleanEngine}`;
    }
    
    if (qvCandEmail) {
        qvCandEmail.textContent = (cand.email && cand.email !== 'Not Provided') ? cand.email : 'N/A';
    }
    if (qvCandPhone) {
        qvCandPhone.textContent = (cand.phone && cand.phone !== 'Not Provided') ? cand.phone : 'N/A';
    }
    
    if (qvCandLinkedin) {
        if (cand.linkedin && cand.linkedin !== 'Not Provided') {
            const url = sanitizeUrl(cand.linkedin);
            if (url !== '#') {
                const a = document.createElement('a');
                a.href = url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                a.style.color = 'var(--color-forest)';
                a.style.fontWeight = '500';
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
    }
    
    if (qvCandGithub) {
        if (cand.github && cand.github !== 'Not Provided') {
            const url = sanitizeUrl(cand.github);
            if (url !== '#') {
                const a = document.createElement('a');
                a.href = url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                a.style.color = 'var(--color-forest)';
                a.style.fontWeight = '500';
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
    }
    
    // Render Overall Match & Dimension Breakdown Overview
    const scoreOverviewContainer = document.getElementById('qv-score-overview-container');
    if (scoreOverviewContainer) {
        scoreOverviewContainer.innerHTML = renderScoreOverview(cand);
    }

    // Render XAI details
    const xaiContainer = document.getElementById('qv-xai-container');
    if (xaiContainer) {
        xaiContainer.innerHTML = renderXaiContent(cand.analysis_metadata?.xai);
    }
    
    // Resume Improvement Recommendations are strictly for candidates; completely hidden and cleared for recruiters
    const recsSection = document.getElementById('qv-recommendations-section');
    if (recsSection) {
        recsSection.style.display = 'none';
        recsSection.classList.add('hidden');
    }
    const recsContainer = document.getElementById('qv-recommendations-container');
    if (recsContainer) {
        recsContainer.innerHTML = '';
    }
    
    const matchedSkills = Array.isArray(cand.matched_skills) ? cand.matched_skills : [];
    const missingSkills = Array.isArray(cand.missing_skills) ? cand.missing_skills : [];
    const extractedSkills = Array.isArray(cand.extracted_skills) ? cand.extracted_skills : matchedSkills.concat(missingSkills);

    const matchedCountEl = document.getElementById('qv-matched-skills-count');
    if (matchedCountEl) matchedCountEl.textContent = matchedSkills.length;
    const missingCountEl = document.getElementById('qv-missing-skills-count');
    if (missingCountEl) missingCountEl.textContent = missingSkills.length;

    // Render structured skill chips with clear status indicators for Matched Skills and Missing Skills
    const { matchedHtml, missingHtml } = renderTechnicalSkillsOverview(matchedSkills, missingSkills);

    if (qvCandExtractedSkills) qvCandExtractedSkills.innerHTML = extractedSkills.map(s => `<span class="skill-tag">${escapeHTML(s)}</span>`).join('');
    if (qvCandMatchedSkills) qvCandMatchedSkills.innerHTML = matchedHtml;
    if (qvCandMissingSkills) qvCandMissingSkills.innerHTML = missingHtml;
    
    recQuickViewModal.classList.remove('hidden');
}

window.showCandidateQuickView = showCandidateQuickView;

/**
 * Renders the consolidated Technical Skills Overview with distinct Matched Skills and Missing Skills groups.
 */
export function renderTechnicalSkillsOverview(matchedSkills, missingSkills) {
    const renderChips = (skills, type) => {
        if (!skills || skills.length === 0) {
            return `<span style="color: var(--color-muted); font-size: 0.8125rem; font-family: var(--font-body); font-style: italic;">None recorded</span>`;
        }
        return skills.map(s => {
            const prefix = type === 'matched' ? '✓ ' : '✕ ';
            return `<span class="skill-chip ${type} skill-tag ${type}">${prefix}${escapeHTML(s)}</span>`;
        }).join('');
    };

    return {
        matchedHtml: renderChips(matchedSkills, 'matched'),
        missingHtml: renderChips(missingSkills, 'missing')
    };
}

/**
 * Builds the consolidated Overall Score & ATS Overview with dimension breakdown.
 */
export function renderScoreOverview(cand) {
    if (!cand) return '';
    const score = typeof cand.similarity_score === 'number' ? Math.round(cand.similarity_score) : 0;
    let scoreClass = 'low-score';
    if (score >= 70) {
        scoreClass = 'high-score';
    } else if (score >= 40) {
        scoreClass = 'med-score';
    }

    // Distinct ATS Resume Score (only when valid, positive, and genuinely distinct from similarity score)
    const hasValidAts = typeof cand.ats_score === 'number' && cand.ats_score > 0 && Math.round(cand.ats_score) !== score;
    let atsBadgeHtml = '';
    if (hasValidAts) {
        atsBadgeHtml = `
            <div class="ats-score-pill" title="ATS formatting and keyword compliance score">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span>ATS Score: <strong style="color: var(--color-ink);">${Math.round(cand.ats_score)}%</strong></span>
            </div>
        `;
    }

    // Extract dimension breakdown from XAI components or direct candidate scores
    const xaiComponents = Array.isArray(cand.analysis_metadata?.xai?.components) ? cand.analysis_metadata.xai.components : [];
    
    const getCompInfo = (matchKey, fallbackScore, fallbackWeight) => {
        const found = xaiComponents.find(c => {
            const n = String(c?.name || '').toLowerCase();
            return n.includes(matchKey);
        });
        const rawScore = found && typeof found.raw_score === 'number' ? Math.round(found.raw_score) : 
                        (typeof fallbackScore === 'number' ? Math.round(fallbackScore) : 0);
        const weight = found && typeof found.weight === 'number' ? Math.round(found.weight * 100) : fallbackWeight;
        const status = found?.status ? String(found.status).replace(/_/g, ' ') : (rawScore >= 70 ? 'met' : (rawScore >= 40 ? 'partial' : 'unmet'));
        return { score: rawScore, weight, status };
    };

    const dimensions = [
        { name: "Technical Skills", ...getCompInfo("skill", cand.skill_score, 50) },
        { name: "Work Experience", ...getCompInfo("experience", cand.experience_score, 25) },
        { name: "Education", ...getCompInfo("education", cand.education_score, 15) },
        { name: "Projects", ...getCompInfo("project", cand.projects_score, 10) }
    ];

    return `
        <div class="score-overview-panel">
            <div class="score-overview-top">
                <div class="score-overview-metric-group">
                    <span class="score-overview-main-val ${scoreClass}">${score}%</span>
                    <span class="score-overview-main-label">Overall Match Score</span>
                </div>
                ${atsBadgeHtml}
            </div>

            <div class="scoring-breakdown-wrapper">
                <div style="font-family: var(--font-body); font-size: 0.8125rem; font-weight: 600; color: var(--color-ink); margin-bottom: 0.5rem;">
                    Scoring Breakdown by Dimension
                </div>
                <table class="scoring-breakdown-table" aria-label="Scoring Breakdown">
                    <thead>
                        <tr>
                            <th>Dimension</th>
                            <th style="text-align: center;">Score</th>
                            <th style="text-align: center;">Weight</th>
                            <th style="text-align: right;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${dimensions.map(d => {
                            let statusBg = "var(--color-clay-light)";
                            let statusColor = "var(--color-clay)";
                            let statusBorder = "var(--color-clay-border)";
                            if (d.status === "met" || d.status === "exceeded") {
                                statusBg = "var(--color-forest-light)";
                                statusColor = "var(--color-forest)";
                                statusBorder = "var(--color-forest-border)";
                            } else if (d.status === "partially met" || d.status === "partial") {
                                statusBg = "#FEF6EB";
                                statusColor = "#8C5B14";
                                statusBorder = "#F2DEC0";
                            }
                            return `
                                <tr>
                                    <td style="font-weight: 500; color: var(--color-ink);">${escapeHTML(d.name)}</td>
                                    <td style="text-align: center; font-family: var(--font-mono); font-weight: 600; font-variant-numeric: tabular-nums;">${d.score}%</td>
                                    <td style="text-align: center; font-family: var(--font-mono); color: var(--color-muted); font-variant-numeric: tabular-nums;">${d.weight}%</td>
                                    <td style="text-align: right;">
                                        <span style="display: inline-block; background: ${statusBg}; color: ${statusColor}; border: 1px solid ${statusBorder}; font-family: var(--font-mono); font-size: 0.6875rem; font-weight: 600; padding: 0.1rem 0.45rem; border-radius: 4px; text-transform: uppercase;">
                                            ${escapeHTML(d.status)}
                                        </span>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

export function renderXaiContent(xaiData) {
    if (!xaiData || !xaiData.enabled) {
        return `
            <div style="background: var(--color-paper-3); border-left: 3px solid var(--color-clay); padding: 1rem 1.25rem; border-radius: 8px;">
                <p style="margin: 0; font-size: 0.875rem; color: var(--color-clay); font-family: var(--font-body);">This analysis was created before Explainable Scoring was available.</p>
            </div>
        `;
    }

    const components = Array.isArray(xaiData.components) ? xaiData.components : [];
    const explanations = xaiData.explanations || {};
    const overallSummary = xaiData.overall_summary || 'Overall alignment evaluated across candidate profile and job requirements.';
    
    let html = `
        <div style="background: var(--color-forest-light); border: 1px solid var(--color-forest-border); border-left: 3px solid var(--color-forest); padding: 1.1rem 1.25rem; border-radius: 8px; margin-bottom: 1.25rem;">
            <h4 style="margin-top: 0; margin-bottom: 0.35rem; font-size: 0.9375rem; color: var(--color-forest); font-family: var(--font-body); font-weight: 700;">Overall Alignment Summary</h4>
            <p style="margin: 0; font-size: 0.875rem; line-height: 1.6; color: var(--color-ink-2); font-family: var(--font-body);">${escapeHTML(overallSummary)}</p>
        </div>

        <div class="xai-accordion-group" style="display: flex; flex-direction: column; gap: 0.75rem;">
    `;

    components.forEach((comp) => {
        if (!comp) return;
        const compName = comp.name || "Evaluation Component";
        const lowerCompName = compName.toLowerCase();

        // Skip "Overall Score" component accordion: the top-level Overview already prominently presents it
        if (lowerCompName.includes("overall score") || lowerCompName === "overall") {
            return;
        }

        let key = lowerCompName.replace(/\s+/g, "_");
        if (key === "technical_skills") key = "skills";
        if (key === "work_experience") key = "experience";
        
        const compExpl = explanations[key] || {};
        const summaryExpl = compExpl.summary || {};
        const detailedExpl = compExpl.detailed || {};
        
        // Single concise, useful explanation: Points Awarded & Deductions/Gaps
        const whyAwarded = summaryExpl.why_awarded || detailedExpl.why_awarded || 'Full criteria alignment evaluated.';
        const whyDeducted = summaryExpl.why_deducted || detailedExpl.why_deducted || 'No deductions applied.';

        const statusVal = String(comp.status || "evaluated").toLowerCase();
        let statusBg = "var(--color-clay-light)";
        let statusColor = "var(--color-clay)";
        let statusBorder = "var(--color-clay-border)";
        if (statusVal === "met" || statusVal === "exceeded") {
            statusBg = "var(--color-forest-light)";
            statusColor = "var(--color-forest)";
            statusBorder = "var(--color-forest-border)";
        } else if (statusVal === "partially_met" || statusVal === "partial") {
            statusBg = "#FEF6EB";
            statusColor = "#8C5B14";
            statusBorder = "#F2DEC0";
        }

        const displayStatus = statusVal.replace(/_/g, " ");
        const statusBadge = `<span style="background: ${statusBg}; color: ${statusColor}; border: 1px solid ${statusBorder}; font-family: var(--font-mono); font-size: 0.75rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 4px; text-transform: uppercase;">${escapeHTML(displayStatus)}</span>`;
        const rawScore = Math.round(typeof comp.raw_score === 'number' ? comp.raw_score : (typeof comp.score === 'number' ? comp.score : 0));
        const weightPct = Math.round((typeof comp.weight === 'number' ? comp.weight : 0) * 100);

        const rawEvidence = Array.isArray(comp.evidence) ? comp.evidence : [];

        // For Technical Skills: Suppress the Supporting Evidence section entirely.
        // The consolidated Technical Skills Overview card directly above displays Matched Skills and Missing Skills cleanly.
        // XAI remains strictly focused on scoring: Points Awarded, Deductions, and genuine skill gaps.
        let evidenceItems = [];
        const isSkillRelated = lowerCompName.includes("skill") || lowerCompName.includes("competenc");
        if (!isSkillRelated) {
            evidenceItems = rawEvidence.filter(ev => {
                if (!ev) return false;
                const cat = String(ev.category || '').toLowerCase();
                if (cat.includes("skill") || cat.includes("competenc")) return false;
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
        }

        html += `
            <div class="xai-accordion-item" style="border: 1px solid var(--color-rule); border-radius: 8px; overflow: hidden; background: var(--color-paper-2);">
                <div class="xai-accordion-header" onclick="toggleXaiAccordion(this)" style="display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 1.15rem; cursor: pointer; transition: background 0.15s ease; background: var(--color-paper-2);">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span class="xai-chevron" style="font-size: 0.75rem; color: var(--color-muted); transition: transform 0.2s; display: inline-block;">&#x25B6;</span>
                        <strong style="color: var(--color-ink); font-family: var(--font-body); font-size: 0.9375rem;">${escapeHTML(compName)}</strong>
                        <span style="font-size: 0.8125rem; color: var(--color-muted); font-family: var(--font-mono);">(${weightPct}% weight)</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        ${statusBadge}
                        <strong style="color: var(--color-ink); font-family: var(--font-mono); font-size: 0.9375rem; font-variant-numeric: tabular-nums;">${rawScore}%</strong>
                    </div>
                </div>
                
                <div class="xai-accordion-content hidden" style="padding: 1.15rem; border-top: 1px solid var(--color-rule); background: var(--color-paper); display: none;">
                    <div style="margin-bottom: 0.85rem;">
                        <h5 style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: var(--color-forest); font-family: var(--font-mono); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Points Awarded</h5>
                        <p class="xai-text-awarded" style="margin: 0; font-size: 0.875rem; line-height: 1.55; color: var(--color-ink-2); font-family: var(--font-body);">${escapeHTML(whyAwarded)}</p>
                    </div>
                    
                    <div style="margin-bottom: ${evidenceItems.length > 0 ? '1rem' : '0.25rem'};">
                        <h5 style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: var(--color-clay); font-family: var(--font-mono); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Deductions &amp; Gaps</h5>
                        <p class="xai-text-deducted" style="margin: 0; font-size: 0.875rem; line-height: 1.55; color: var(--color-ink-2); font-family: var(--font-body);">${escapeHTML(whyDeducted)}</p>
                    </div>

                    ${evidenceItems.length > 0 ? `
                        <div>
                            <h5 style="margin: 0 0 0.5rem 0; font-size: 0.75rem; color: var(--color-forest); font-family: var(--font-mono); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Supporting Evidence</h5>
                            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                                ${evidenceItems.map(ev => {
                                    if (!ev) return '';
                                    const evTitle = typeof ev === 'string' ? ev : (ev.title || ev.feature || 'Supporting Signal');
                                    const evDesc = typeof ev === 'string' ? '' : (ev.description || ev.comment || '');
                                    const evImp = (typeof ev === 'object' && ev.importance) ? String(ev.importance).toLowerCase() : 'info';
                                    
                                    let impBg = "var(--color-forest-light)";
                                    let impColor = "var(--color-forest)";
                                    let impBorder = "var(--color-forest-border)";
                                    if (evImp === "medium") {
                                        impBg = "#FEF6EB";
                                        impColor = "#8C5B14";
                                        impBorder = "#F2DEC0";
                                    } else if (evImp === "high") {
                                        impBg = "var(--color-clay-light)";
                                        impColor = "var(--color-clay)";
                                        impBorder = "var(--color-clay-border)";
                                    }
                                    
                                    return `
                                        <div style="background: var(--color-paper-2); border: 1px solid var(--color-rule); padding: 0.75rem 1rem; border-radius: 6px; display: flex; flex-direction: column; gap: 0.25rem;">
                                            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                                                <strong style="font-size: 0.85rem; color: var(--color-ink); font-family: var(--font-body);">${escapeHTML(evTitle)}</strong>
                                                <span style="font-size: 0.6875rem; color: ${impColor}; background: ${impBg}; border: 1px solid ${impBorder}; font-family: var(--font-mono); font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 3px; text-transform: uppercase;">${escapeHTML(evImp)}</span>
                                            </div>
                                            ${evDesc ? `<p style="margin: 0; font-size: 0.8125rem; color: var(--color-ink-2); line-height: 1.45; font-family: var(--font-body);">${escapeHTML(evDesc)}</p>` : ''}
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });

    html += `</div>`;
    return html;
}

window.toggleXaiAccordion = (headerEl) => {
    if (!headerEl) return;
    const item = headerEl.closest('.xai-accordion-item');
    if (!item) return;
    const content = item.querySelector('.xai-accordion-content');
    const chevron = item.querySelector('.xai-chevron');
    if (!content) return;
    
    if (content.style.display === 'none' || content.classList.contains('hidden')) {
        content.style.display = 'block';
        content.classList.remove('hidden');
        if (chevron) chevron.style.transform = 'rotate(90deg)';
        headerEl.style.background = 'var(--color-paper-3)';
    } else {
        content.style.display = 'none';
        content.classList.add('hidden');
        if (chevron) chevron.style.transform = 'rotate(0deg)';
        headerEl.style.background = 'var(--color-paper-2)';
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

export function renderRecommendations(recsData) {
    // Resume Improvement Recommendations are strictly for candidates and must never be rendered in recruiter context
    return '';
}

// ==========================================
// Advanced Scoring Settings Controls (Optional Per-Run Customization)
// ==========================================

let advancedScoringInitialized = false;

export function initAdvancedScoringControls() {
    const toggleBtn = document.getElementById('btn-toggle-advanced-scoring');
    const body = document.getElementById('advanced-scoring-body');
    const icon = document.getElementById('advanced-scoring-icon');
    const modeDefault = document.getElementById('scoring-mode-default');
    const modeCustom = document.getElementById('scoring-mode-custom');
    const controlsPanel = document.getElementById('custom-scoring-controls');
    const statusBadge = document.getElementById('custom-scoring-status-badge');
    const btnResetDefaults = document.getElementById('btn-reset-scoring-defaults');
    const btnAutobalance = document.getElementById('btn-autobalance-weights');

    if (!toggleBtn || !body) return;

    if (!advancedScoringInitialized) {
        advancedScoringInitialized = true;

        // 1. Collapsible Section Toggle
        toggleBtn.addEventListener('click', () => {
            const isCollapsed = body.style.display === 'none' || !body.style.display;
            body.style.display = isCollapsed ? 'block' : 'none';
            toggleBtn.setAttribute('aria-expanded', isCollapsed ? 'true' : 'false');
            if (icon) {
                icon.style.transform = isCollapsed ? 'rotate(180deg)' : 'rotate(0deg)';
            }
        });

        // 2. Mode Radio Switch
        const handleModeChange = () => {
            const isCustom = modeCustom && modeCustom.checked;
            if (controlsPanel) {
                controlsPanel.style.opacity = isCustom ? '1' : '0.5';
                controlsPanel.style.pointerEvents = isCustom ? 'auto' : 'none';
            }
            if (statusBadge) {
                if (isCustom) {
                    statusBadge.textContent = 'Custom Scoring Active';
                    statusBadge.style.color = 'var(--color-clay)';
                    statusBadge.style.background = 'var(--color-clay-light)';
                    statusBadge.style.borderColor = 'var(--color-clay-border)';
                } else {
                    statusBadge.textContent = 'Default Scoring Active';
                    statusBadge.style.color = 'var(--color-forest)';
                    statusBadge.style.background = 'var(--color-forest-light)';
                    statusBadge.style.borderColor = 'var(--color-forest-border)';
                    // Re-sync with profile defaults when returning to default mode
                    syncScoringControlsWithSelectedProfile(true);
                }
            }
            updateTotalWeightsDisplay();
        };

        if (modeDefault) modeDefault.addEventListener('change', handleModeChange);
        if (modeCustom) modeCustom.addEventListener('change', handleModeChange);

        // 3. Slider and Checkbox Events
        const criteria = ['skills', 'exp', 'edu', 'proj'];
        criteria.forEach(crit => {
            const slider = document.getElementById(`crit-${crit}-weight`);
            const enable = document.getElementById(`crit-${crit}-enable`);
            const pct = document.getElementById(`crit-${crit}-pct`);

            if (slider) {
                slider.addEventListener('input', () => {
                    if (pct) pct.textContent = `${slider.value}%`;
                    updateTotalWeightsDisplay();
                });
            }

            if (enable) {
                enable.addEventListener('change', () => {
                    if (!enable.checked) {
                        if (slider) {
                            slider.disabled = true;
                            slider.dataset.prevVal = slider.value;
                            slider.value = 0;
                        }
                        if (pct) pct.textContent = '0% (Disabled)';
                        autoBalanceActiveWeights();
                    } else {
                        if (slider) {
                            slider.disabled = false;
                            slider.value = slider.dataset.prevVal && Number(slider.dataset.prevVal) > 0 ? slider.dataset.prevVal : 25;
                        }
                        if (pct) pct.textContent = `${slider.value}%`;
                        autoBalanceActiveWeights();
                    }
                    updateTotalWeightsDisplay();
                });
            }
        });

        // 4. Threshold inputs validation display
        const threshExp = document.getElementById('thresh-exp-years');
        const threshProj = document.getElementById('thresh-proj-count');
        [threshExp, threshProj].forEach(input => {
            if (input) {
                input.addEventListener('input', updateTotalWeightsDisplay);
            }
        });

        // 5. Reset & Auto-Balance Buttons
        if (btnResetDefaults) {
            btnResetDefaults.addEventListener('click', () => {
                resetToSelectedProfileDefaults();
            });
        }

        if (btnAutobalance) {
            btnAutobalance.addEventListener('click', () => {
                autoBalanceActiveWeights();
                updateTotalWeightsDisplay();
            });
        }
    }
}

export function getSelectedProfileWeights() {
    const profileSelect = document.getElementById('rec-profile-select');
    const selectedId = profileSelect ? profileSelect.value : null;
    const profiles = window.recruiterScoringProfiles || [];
    const profile = profiles.find(p => String(p.id) === String(selectedId)) || profiles.find(p => p.is_default) || profiles[0];
    if (profile && profile.weights) {
        let w = profile.weights;
        if (typeof w === 'string') {
            try { w = JSON.parse(w); } catch (_) {}
        }
        return {
            skills: Number(w.skills) || 0.50,
            experience: Number(w.experience) || 0.25,
            education: Number(w.education) || 0.15,
            projects: Number(w.projects) || 0.10
        };
    }
    return { skills: 0.50, experience: 0.25, education: 0.15, projects: 0.10 };
}

export function syncScoringControlsWithSelectedProfile(force = false) {
    const modeCustom = document.getElementById('scoring-mode-custom');
    // If custom mode is active and not forcing reset, leave user's custom edits untouched
    if (modeCustom && modeCustom.checked && !force) {
        return;
    }
    resetToSelectedProfileDefaults();
}

export function resetToSelectedProfileDefaults() {
    const w = getSelectedProfileWeights();
    const map = {
        skills: Math.round(w.skills * 100),
        exp: Math.round(w.experience * 100),
        edu: Math.round(w.education * 100),
        proj: Math.round(w.projects * 100)
    };

    ['skills', 'exp', 'edu', 'proj'].forEach(crit => {
        const slider = document.getElementById(`crit-${crit}-weight`);
        const enable = document.getElementById(`crit-${crit}-enable`);
        const pct = document.getElementById(`crit-${crit}-pct`);

        if (enable) enable.checked = true;
        if (slider) {
            slider.disabled = false;
            slider.value = map[crit] ?? 25;
        }
        if (pct) pct.textContent = `${map[crit] ?? 25}%`;
    });

    const threshExp = document.getElementById('thresh-exp-years');
    const threshProj = document.getElementById('thresh-proj-count');
    if (threshExp) threshExp.value = 10;
    if (threshProj) threshProj.value = 3;

    updateTotalWeightsDisplay();
}

function autoBalanceActiveWeights() {
    const criteria = ['skills', 'exp', 'edu', 'proj'];
    const active = [];

    criteria.forEach(crit => {
        const enable = document.getElementById(`crit-${crit}-enable`);
        const slider = document.getElementById(`crit-${crit}-weight`);
        if (enable && enable.checked && slider) {
            active.push({ crit, slider, val: Number(slider.value) || 0 });
        }
    });

    if (active.length === 0) return;

    const currentSum = active.reduce((acc, item) => acc + item.val, 0);
    let distributed = 0;

    active.forEach((item, idx) => {
        let newShare;
        if (idx === active.length - 1) {
            newShare = Math.max(0, 100 - distributed);
        } else {
            newShare = currentSum > 0 ? Math.round((item.val / currentSum) * 100) : Math.round(100 / active.length);
            distributed += newShare;
        }
        item.slider.value = Math.max(0, newShare);
        const pct = document.getElementById(`crit-${item.crit}-pct`);
        if (pct) pct.textContent = `${item.slider.value}%`;
    });
}

function updateTotalWeightsDisplay() {
    const criteria = ['skills', 'exp', 'edu', 'proj'];
    let total = 0;
    let anyEnabled = false;

    criteria.forEach(crit => {
        const enable = document.getElementById(`crit-${crit}-enable`);
        const slider = document.getElementById(`crit-${crit}-weight`);
        if (enable && enable.checked && slider) {
            total += Number(slider.value) || 0;
            anyEnabled = true;
        }
    });

    const badge = document.getElementById('scoring-total-weight');
    const msg = document.getElementById('scoring-validation-msg');
    const modeCustom = document.getElementById('scoring-mode-custom');
    const isCustom = modeCustom && modeCustom.checked;

    if (badge) {
        badge.textContent = `${total}%`;
        if (total === 100 && anyEnabled) {
            badge.style.color = 'var(--color-forest)';
            badge.style.background = 'var(--color-forest-light)';
        } else {
            badge.style.color = 'var(--color-warning)';
            badge.style.background = 'var(--color-warning-dim)';
        }
    }

    if (msg) {
        if (!isCustom) {
            msg.style.display = 'none';
        } else if (!anyEnabled) {
            msg.style.display = 'block';
            msg.style.background = 'var(--color-clay-light)';
            msg.style.border = '1px solid var(--color-clay-border)';
            msg.style.color = 'var(--color-clay)';
            msg.textContent = '❌ At least one scoring criterion must be enabled.';
        } else if (total !== 100) {
            msg.style.display = 'block';
            msg.style.background = 'var(--color-warning-dim)';
            msg.style.border = '1px solid #F2DEC0';
            msg.style.color = 'var(--color-warning)';
            msg.innerHTML = `⚠️ Active weights sum to <strong>${total}%</strong>. Adjust sliders or click Auto-Balance to sum to exactly 100%.`;
        } else {
            msg.style.display = 'none';
        }
    }
}

export function getCustomScoringPayload() {
    const modeCustom = document.getElementById('scoring-mode-custom');
    if (!modeCustom || !modeCustom.checked) {
        return null; // Use profile defaults
    }

    const disabledList = [];
    const weights = {};
    const criteriaMap = {
        skills: 'skills',
        exp: 'experience',
        edu: 'education',
        proj: 'projects'
    };

    let anyEnabled = false;
    let totalPct = 0;
    for (const [key, prop] of Object.entries(criteriaMap)) {
        const enable = document.getElementById(`crit-${key}-enable`);
        const slider = document.getElementById(`crit-${key}-weight`);
        if (enable && !enable.checked) {
            disabledList.push(prop);
            weights[prop] = 0.0;
        } else {
            anyEnabled = true;
            const val = slider ? Number(slider.value) : 0;
            totalPct += val;
            weights[prop] = val / 100.0;
        }
    }

    if (!anyEnabled) {
        throw new Error('At least one scoring criterion must be enabled with a positive weight.');
    }

    // If total differs from 100%, auto-balance before dispatching
    if (totalPct !== 100) {
        autoBalanceActiveWeights();
        for (const [key, prop] of Object.entries(criteriaMap)) {
            const enable = document.getElementById(`crit-${key}-enable`);
            const slider = document.getElementById(`crit-${key}-weight`);
            if (enable && enable.checked && slider) {
                weights[prop] = Number(slider.value) / 100.0;
            }
        }
    }

    const threshExp = document.getElementById('thresh-exp-years');
    const threshProj = document.getElementById('thresh-proj-count');
    const targetExp = threshExp ? Number(threshExp.value) : 10;
    const targetProj = threshProj ? Number(threshProj.value) : 3;

    if (isNaN(targetExp) || targetExp < 1 || targetExp > 30) {
        throw new Error('Target experience years must be between 1 and 30.');
    }
    if (isNaN(targetProj) || targetProj < 1 || targetProj > 10) {
        throw new Error('Target project count must be between 1 and 10.');
    }

    return {
        enabled: true,
        weights: weights,
        thresholds: {
            target_experience_years: targetExp,
            target_project_count: targetProj,
            max_experience_years: targetExp,
            project_target_count: targetProj
        },
        disabled_criteria: disabledList
    };
}

export function resetAdvancedScoringState() {
    const modeDefault = document.getElementById('scoring-mode-default');
    if (modeDefault) modeDefault.checked = true;

    const statusBadge = document.getElementById('custom-scoring-status-badge');
    if (statusBadge) {
        statusBadge.textContent = 'Default Scoring Active';
        statusBadge.style.color = 'var(--color-forest)';
        statusBadge.style.background = 'var(--color-forest-light)';
        statusBadge.style.borderColor = 'var(--color-forest-border)';
    }

    const controlsPanel = document.getElementById('custom-scoring-controls');
    if (controlsPanel) {
        controlsPanel.style.opacity = '0.5';
        controlsPanel.style.pointerEvents = 'none';
    }

    const body = document.getElementById('advanced-scoring-body');
    const icon = document.getElementById('advanced-scoring-icon');
    const toggleBtn = document.getElementById('btn-toggle-advanced-scoring');
    if (body) body.style.display = 'none';
    if (icon) icon.style.transform = 'rotate(0deg)';
    if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');

    const banner = document.getElementById('scoring-applied-banner');
    if (banner) {
        banner.innerHTML = '';
        banner.classList.add('hidden');
    }

    resetToSelectedProfileDefaults();
}
