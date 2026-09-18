import * as api from '../api.js';
import * as state from '../state.js';
import { checkAuthStatus } from '../auth.js';
import { ROLES, MESSAGES } from '../constants.js';

// Onboarding State
let currentStep = 1;
let selectedRole = null; // "RECRUITER" or "CANDIDATE"
let initialized = false;

function getStepsForRole() {
    if (selectedRole === ROLES.CANDIDATE) {
        return ["ob-step-1", "ob-cand-step-2", "ob-cand-step-3", "ob-cand-step-4"];
    }
    return ["ob-step-1", "ob-rec-step-2", "ob-rec-step-3", "ob-rec-step-4"];
}

function hideObError() {
    const obErrorMsg = document.getElementById('ob-error');
    if (obErrorMsg) {
        obErrorMsg.classList.add('hidden');
        obErrorMsg.textContent = "";
    }
}

function showObError(msg) {
    const obErrorMsg = document.getElementById('ob-error');
    if (obErrorMsg) {
        obErrorMsg.textContent = msg;
        obErrorMsg.classList.remove('hidden');
    }
}

function updateOnboardingUI() {
    const obStepIndicator = document.getElementById('onboarding-step-indicator');
    const obProgressBar = document.getElementById('onboarding-progress-bar');
    const obBackBtn = document.getElementById('ob-back-btn');
    const obNextBtn = document.getElementById('ob-next-btn');

    const steps = getStepsForRole();
    const totalSteps = steps.length;
    
    obStepIndicator.textContent = `Step ${currentStep} of ${totalSteps}`;
    
    const progressPercentage = (currentStep / totalSteps) * 100;
    obProgressBar.style.width = `${progressPercentage}%`;
    
    const allStepElems = document.querySelectorAll('.ob-step');
    allStepElems.forEach(el => {
        el.classList.add('hidden');
        el.classList.remove('active-plane');
    });
    
    const currentStepId = steps[currentStep - 1];
    const currentElem = document.getElementById(currentStepId);
    if (currentElem) {
        currentElem.classList.remove('hidden');
        currentElem.classList.add('active-plane');
    }
    
    if (currentStep === 1) {
        obBackBtn.classList.add('hidden');
    } else {
        obBackBtn.classList.remove('hidden');
    }
    
    obNextBtn.style.display = 'block';
    if (currentStep === totalSteps) {
        obNextBtn.querySelector('span').textContent = "Complete Profile";
    } else {
        obNextBtn.querySelector('span').textContent = "Next";
    }
    
    if (currentStep === 1 && !selectedRole) {
        obNextBtn.disabled = true;
    } else {
        obNextBtn.disabled = false;
    }
}

function validateCurrentStep() {
    const obCompanyName = document.getElementById('ob-company-name');
    const obCompanyType = document.getElementById('ob-company-type');
    const obHiringDomain = document.getElementById('ob-hiring-domain');
    const obCurrentStatus = document.getElementById('ob-current-status');
    const obFieldStudy = document.getElementById('ob-field-study');
    const obCurrentDomain = document.getElementById('ob-current-domain');

    if (currentStep === 1) {
        if (!selectedRole) {
            showObError(MESSAGES.ROLE_REQUIRED);
            return false;
        }
    } else if (selectedRole === ROLES.RECRUITER) {
        if (currentStep === 2) {
            const name = obCompanyName.value.trim();
            if (!name) {
                showObError(MESSAGES.COMPANY_NAME_REQUIRED);
                return false;
            }
        } else if (currentStep === 3) {
            const type = obCompanyType.value;
            if (!type) {
                showObError(MESSAGES.COMPANY_TYPE_REQUIRED);
                return false;
            }
        } else if (currentStep === 4) {
            const domain = obHiringDomain.value;
            if (!domain) {
                showObError(MESSAGES.HIRING_DOMAIN_REQUIRED);
                return false;
            }
        }
    } else if (selectedRole === ROLES.CANDIDATE) {
        if (currentStep === 2) {
            const statusVal = obCurrentStatus.value;
            if (!statusVal) {
                showObError(MESSAGES.STATUS_REQUIRED);
                return false;
            }
        } else if (currentStep === 3) {
            const study = obFieldStudy.value.trim();
            if (!study) {
                showObError(MESSAGES.FIELD_STUDY_REQUIRED);
                return false;
            }
        } else if (currentStep === 4) {
            const curDomain = obCurrentDomain.value.trim();
            if (!curDomain) {
                showObError(MESSAGES.CURRENT_DOMAIN_REQUIRED);
                return false;
            }
        }
    }
    hideObError();
    return true;
}

async function submitOnboarding() {
    const obNextBtn = document.getElementById('ob-next-btn');
    const obBackBtn = document.getElementById('ob-back-btn');
    const onboardingModal = document.getElementById('onboarding-modal');
    const obCompanyName = document.getElementById('ob-company-name');
    const obCompanyType = document.getElementById('ob-company-type');
    const obHiringDomain = document.getElementById('ob-hiring-domain');
    const obCurrentStatus = document.getElementById('ob-current-status');
    const obFieldStudy = document.getElementById('ob-field-study');
    const obCurrentDomain = document.getElementById('ob-current-domain');

    const token = state.getToken();
    if (!token) {
        showObError(MESSAGES.AUTH_LOST);
        return;
    }
    
    const nextSpan = obNextBtn.querySelector('span');
    const originalText = nextSpan.textContent;
    nextSpan.textContent = "Saving Profile...";
    obNextBtn.disabled = true;
    obBackBtn.disabled = true;
    
    let payload = {};
    
    try {
        if (selectedRole === ROLES.RECRUITER) {
            payload = {
                role: selectedRole,
                question_1: obCompanyName.value.trim(),
                question_2: obCompanyType.value,
                question_3: obHiringDomain.value
            };
        } else {
            payload = {
                role: selectedRole,
                question_1: obCurrentStatus.value,
                question_2: obFieldStudy.value.trim(),
                question_3: obCurrentDomain.value.trim()
            };
        }
        await api.submitOnboarding(payload);
        
        // Invalidate stale frontend state and mark onboarding completed
        state.setOnboardingStatus(true);
        state.setProfile(null);
        state.setCandidateStats(null);
        state.setCandidateResumes(null);
        state.setRecruiterStats(null);

        onboardingModal.classList.add('hidden');
        window.location.replace(selectedRole === ROLES.RECRUITER ? 'recruiter.html' : 'candidate.html');
    } catch (error) {
        showObError(error.message);
        nextSpan.textContent = originalText;
        obNextBtn.disabled = false;
        obBackBtn.disabled = false;
    }
}

/**
 * Shows the onboarding wizard modal and resets its state. Called on routing/auth check.
 */
export function showOnboardingWizard() {
    const onboardingModal = document.getElementById('onboarding-modal');
    const authModal = document.getElementById('auth-modal');
    const appContainer = document.getElementById('app-container');
    const obRoleRecruiter = document.getElementById('ob-role-recruiter');
    const obRoleCandidate = document.getElementById('ob-role-candidate');
    const obCompanyName = document.getElementById('ob-company-name');
    const obCompanyType = document.getElementById('ob-company-type');
    const obHiringDomain = document.getElementById('ob-hiring-domain');
    const obCurrentStatus = document.getElementById('ob-current-status');
    const obFieldStudy = document.getElementById('ob-field-study');
    const obCurrentDomain = document.getElementById('ob-current-domain');

    if (onboardingModal) onboardingModal.classList.remove('hidden');
    if (authModal) authModal.classList.add('hidden');
    if (appContainer) appContainer.classList.add('hidden');
    
    currentStep = 1;
    selectedRole = null;
    
    // Reset selected cards
    obRoleRecruiter.classList.remove('selected');
    obRoleCandidate.classList.remove('selected');
    
    // Reset inputs
    obCompanyName.value = "";
    obCompanyType.value = "";
    obHiringDomain.value = "";
    obCurrentStatus.value = "";
    obFieldStudy.value = "";
    obCurrentDomain.value = "";
    
    hideObError();
    updateOnboardingUI();
}

// Map alias for router consistency
export const initializeOnboardingPage = showOnboardingWizard;

/**
 * Initializes onboarding event listeners (runs once on startup).
 */
export function initOnboarding() {
    if (initialized) return;

    const obRoleRecruiter = document.getElementById('ob-role-recruiter');
    const obRoleCandidate = document.getElementById('ob-role-candidate');
    const obBackBtn = document.getElementById('ob-back-btn');
    const obNextBtn = document.getElementById('ob-next-btn');

    obRoleRecruiter.addEventListener('click', () => {
        selectedRole = ROLES.RECRUITER;
        obRoleRecruiter.classList.add('selected');
        obRoleCandidate.classList.remove('selected');
        hideObError();
        obNextBtn.disabled = false;
    });

    obRoleCandidate.addEventListener('click', () => {
        selectedRole = ROLES.CANDIDATE;
        obRoleCandidate.classList.add('selected');
        obRoleRecruiter.classList.remove('selected');
        hideObError();
        obNextBtn.disabled = false;
    });

    obBackBtn.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            hideObError();
            updateOnboardingUI();
        }
    });

    obNextBtn.addEventListener('click', async () => {
        if (!validateCurrentStep()) {
            return;
        }
        
        const steps = getStepsForRole();
        if (currentStep === steps.length) {
            await submitOnboarding();
        } else {
            currentStep++;
            hideObError();
            updateOnboardingUI();
        }
    });

    initialized = true;
}
