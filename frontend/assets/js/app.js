import { checkAuthStatus, initAuthListener } from './auth.js';
import { initLoginPage, initializeLoginPage } from './pages/login.js';
import { initSignupPage, initializeSignupPage } from './pages/signup.js';
import { initOnboarding, showOnboardingWizard } from './pages/onboarding.js';
import { initRecruiterPage } from './pages/recruiter.js';
import { initCandidatePage } from './pages/candidate.js';
import { initRouter, handleRouting } from './router.js';
import { initModals } from './components/modal.js';
import { initNavbar } from './components/navbar.js';
import * as api from './api.js';
import { getCandidateRowHTML, getCandidateDetailRowHTML } from './components/candidateCard.js';
import { toggleButtonLoading } from './components/loadingSpinner.js';
import { MESSAGES } from './constants.js';

let uploadedFiles = [];

document.addEventListener('DOMContentLoaded', () => {
    const pathname = window.location.pathname.toLowerCase();

    const isLandingPage = pathname === '/' || pathname.endsWith('index.html') || pathname === '';
    const isOnboardingPage = pathname.includes('onboarding');
    const isRecruiterPage = pathname.includes('recruiter');
    const isCandidatePage = pathname.includes('candidate');

    // Initialize modules conditionally based on page
    if (isLandingPage) {
        initLoginPage();
        initSignupPage();
        initializeLoginPage();
        initializeSignupPage();
        initRouter();
        handleRouting();

        // Bind navbar and landing buttons to navigate to auth hashes
        const loginBtns = document.querySelectorAll('.nav-login-btn');
        loginBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                window.location.hash = '#/login';
            });
        });

        const signupBtns = document.querySelectorAll('.nav-signup-btn');
        signupBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                window.location.hash = '#/signup';
            });
        });
    } else if (isOnboardingPage) {
        initOnboarding();
        showOnboardingWizard();
    } else if (isRecruiterPage) {
        initRecruiterPage();
        initRouter();
        initNavbar(clearCandidateState);
        handleRouting();
    } else if (isCandidatePage) {
        initCandidatePage();
        initRouter();
        initNavbar(clearCandidateState);
        handleRouting();
    }

    initModals();

    // 2. Candidate ATS Functionality
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('resumes');
    const fileList = document.getElementById('file-list');
    const processBtn = document.getElementById('process-btn');
    const resultsContainer = document.getElementById('results-container');
    const resultsBody = document.getElementById('results-body');
    const jdInput = document.getElementById('job-description');
    const resumesDropdownHeader = document.getElementById('resumes-dropdown-header');

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
    }

    function handleFiles(files) {
        for (let file of files) {
            if (file.name.match(/\.(pdf|doc|docx)$/i)) {
                uploadedFiles.push(file);
                renderFileList();
            } else {
                alert(`File ${file.name} is not a valid format. Only PDF and DOCX are supported.`);
            }
        }
        updateResumeCountDisplay();
    }

    function updateResumeCountDisplay() {
        const resumesCountSpan = document.getElementById('resumes-count');
        if (resumesCountSpan) {
            resumesCountSpan.textContent = `Resumes (${uploadedFiles.length})`;
        }
    }

    if (resumesDropdownHeader) {
        resumesDropdownHeader.addEventListener('click', (e) => {
            e.stopPropagation();
            if (dropZone.classList.contains('collapsed')) {
                dropZone.classList.toggle('active');
            }
        });
    }

    function renderFileList() {
        if (!fileList) return;
        fileList.innerHTML = '';
        uploadedFiles.forEach((file, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span>${file.name}</span>
                <span style="color: #ef4444; cursor:pointer;" onclick="removeFile(${index})">&times;</span>
            `;
            fileList.appendChild(li);
        });
    }

    window.removeFile = (index) => {
        uploadedFiles.splice(index, 1);
        renderFileList();
        updateResumeCountDisplay();
        
        if (uploadedFiles.length === 0) {
            dropZone.classList.remove('collapsed', 'active');
            resumesDropdownHeader.classList.add('hidden');
        }
    };

    if (processBtn) {
        processBtn.addEventListener('click', async () => {
            const jd = jdInput.value.trim();
            if (!jd) {
                alert(MESSAGES.ENTER_JD);
                return;
            }
            if (uploadedFiles.length === 0) {
                alert(MESSAGES.UPLOAD_RESUME);
                return;
            }

            resultsContainer.classList.add('hidden');

            dropZone.classList.add('collapsed');
            dropZone.classList.remove('active');
            resumesDropdownHeader.classList.remove('hidden');
            updateResumeCountDisplay();

            const formData = new FormData();
            formData.append('job_description', jd);
            uploadedFiles.forEach(file => {
                formData.append('resumes', file);
            });

            toggleButtonLoading(processBtn, true, "Processing...", "Rank Candidates");

            try {
                const data = await api.screenResumes(formData);
                renderResults(data.results);
            } catch (error) {
                alert(error.message);
            } finally {
                toggleButtonLoading(processBtn, false, "Processing...", "Rank Candidates");
            }
        });
    }

    function renderResults(results) {
        if (!resultsBody) return;
        resultsBody.innerHTML = '';

        results.forEach(cand => {
            // Main Row
            const tr = document.createElement('tr');
            tr.classList.add('candidate-row');
            tr.innerHTML = getCandidateRowHTML(cand);
            resultsBody.appendChild(tr);

            // Expandable Detail Row
            const detailTr = document.createElement('tr');
            detailTr.classList.add('detail-row');
            detailTr.innerHTML = getCandidateDetailRowHTML(cand);
            resultsBody.appendChild(detailTr);

            // Toggle detail row on main row click
            tr.addEventListener('click', (e) => {
                if (e.target.tagName === 'A') return;
                const isOpen = detailTr.classList.toggle('open');
                tr.querySelector('.expand-chevron').textContent = isOpen ? '▼' : '▶';

                // Animate breakdown bars when opening
                if (isOpen) {
                    setTimeout(() => {
                        detailTr.querySelectorAll('.score-bar-fill').forEach(bar => {
                            bar.style.width = bar.getAttribute('data-target');
                        });
                    }, 50);
                } else {
                    detailTr.querySelectorAll('.score-bar-fill').forEach(bar => {
                        bar.style.width = '0%';
                    });
                }
            });
        });

        resultsContainer.classList.remove('hidden');
        resultsContainer.scrollIntoView({ behavior: 'smooth' });

        // Trigger main score bar animations
        setTimeout(() => {
            const bars = resultsBody.querySelectorAll('.candidate-row .score-bar-fill');
            bars.forEach(bar => {
                bar.style.width = bar.getAttribute('data-target');
            });
        }, 100);
    }

    function clearCandidateState() {
        if (resultsContainer) resultsContainer.classList.add('hidden');
        if (resultsBody) resultsBody.innerHTML = '';
        if (jdInput) jdInput.value = '';
        uploadedFiles = [];
        renderFileList();
        if (dropZone) dropZone.classList.remove('collapsed', 'active');
        if (resumesDropdownHeader) resumesDropdownHeader.classList.add('hidden');
    }

    // 3. Kick off auth state listening (onAuthStateChanged triggers checkAuthStatus when ready)
    initAuthListener();
});
