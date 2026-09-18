import { API_BASE, API_ENDPOINTS } from './constants.js';
import * as state from './state.js';
import { auth, signOut } from './firebase-init.js?v=5';

/**
 * Shared HTTP request helper with dynamic Firebase ID token resolution,
 * single-attempt non-recursive 401 token refresh retry, and global error handling.
 */
// In-flight GET request deduplication cache to prevent duplicate concurrent network calls
const inflightGetRequests = new Map();

async function request(endpoint, options = {}, isRetry = false) {
    const method = (options.method || "GET").toUpperCase();
    
    // Non-GET requests and retry attempts bypass in-flight cache
    if (method !== "GET" || isRetry) {
        return _executeRequest(endpoint, options, isRetry);
    }

    const currentToken = state.getToken() || (auth.currentUser ? auth.currentUser.uid : '');
    const cacheKey = `${endpoint}:${currentToken}`;
    if (inflightGetRequests.has(cacheKey)) {
        return inflightGetRequests.get(cacheKey);
    }

    const promise = (async () => {
        try {
            return await _executeRequest(endpoint, options, isRetry);
        } finally {
            inflightGetRequests.delete(cacheKey);
        }
    })();

    inflightGetRequests.set(cacheKey, promise);
    return promise;
}

async function _executeRequest(endpoint, options = {}, isRetry = false) {
    const headers = { ...options.headers };

    // Dynamically retrieve fresh Firebase ID token if user is signed in
    let token = null;
    if (auth.currentUser) {
        try {
            token = await auth.currentUser.getIdToken(isRetry);
        } catch (tokenErr) {
            console.warn("Failed to dynamically fetch Firebase ID token:", tokenErr);
        }
    }
    if (!token) {
        token = state.getToken();
    }

    // Auto-inject auth header
    if (token && !headers["Authorization"]) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    // Default Content-Type to application/json except for FormData
    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    const timeout = options.timeout || 15000; // 15 seconds default timeout
    const controller = new AbortController();
    const timerId = setTimeout(() => controller.abort(), timeout);

    const config = {
        ...options,
        headers,
        signal: controller.signal
    };

    const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`;

    try {
        const response = await fetch(url, config);
        clearTimeout(timerId);

        // Controlled 401 Token Refresh & Retry Handling (Single Controlled Attempt, No Recursion)
        if (response.status === 401) {
            if (!isRetry && auth.currentUser) {
                try {
                    // Force refresh token from Firebase server
                    const freshToken = await auth.currentUser.getIdToken(true);
                    state.setToken(freshToken);
                    return await request(endpoint, options, true);
                } catch (refreshErr) {
                    console.error("Firebase token force-refresh failed on 401:", refreshErr);
                }
            }

            // Persistent failure or no user session: clear local state and sign out
            state.clearState();
            try {
                await signOut(auth);
            } catch (signOutErr) {
                console.warn("Sign out on 401 failed:", signOutErr);
            }
            const currentPath = window.location.pathname.toLowerCase();
            if (!currentPath.endsWith('index.html') && currentPath !== '/' && currentPath !== '') {
                window.location.href = 'index.html#/login';
            } else {
                window.location.hash = "#/login";
            }
            throw new Error("Session expired. Please log in again.");
        }

        if (!response.ok) {
            // Handle HTTP errors (500, 502, 503, etc.)
            if (response.status >= 500) {
                showOfflineBanner("Database or Server is currently undergoing maintenance. Please try again later.");
            }
        } else {
            hideOfflineBanner();
        }

        const contentType = response.headers.get("content-type");
        let data;
        if (contentType && contentType.includes("application/json")) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            const message = (data && data.detail) || data || "Request failed";
            throw new Error(message);
        }

        return data;
    } catch (error) {
        clearTimeout(timerId);
        if (error.name === "AbortError") {
            throw new Error("Request timed out");
        }
        // Handle network/connection failure
        showOfflineBanner("Cannot connect to server. The backend may be starting up (cold start) or your connection is offline.");
        throw error;
    }
}

/**
 * Global functions to manage the offline warning banner
 */
function showOfflineBanner(message) {
    let banner = document.getElementById("offline-warning-banner");
    if (!banner) {
        banner = document.createElement("div");
        banner.id = "offline-warning-banner";
        banner.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(239, 68, 68, 0.95);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 9999;
            font-family: 'Outfit', sans-serif;
            font-size: 0.9rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.3s ease;
            opacity: 0;
            margin-top: -10px;
        `;
        
        const textSpan = document.createElement("span");
        textSpan.id = "offline-warning-text";
        banner.appendChild(textSpan);
        
        const closeBtn = document.createElement("button");
        closeBtn.innerHTML = "&times;";
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.25rem;
            cursor: pointer;
            padding: 0 4px;
            line-height: 1;
            transition: color 0.2s;
            margin-left: 8px;
        `;
        closeBtn.addEventListener("mouseover", () => closeBtn.style.color = "#fff");
        closeBtn.addEventListener("mouseout", () => closeBtn.style.color = "rgba(255, 255, 255, 0.8)");
        closeBtn.onclick = () => hideOfflineBanner();
        banner.appendChild(closeBtn);
        
        document.body.appendChild(banner);
        
        // Trigger reflow to animate
        banner.offsetHeight;
        banner.style.opacity = "1";
        banner.style.marginTop = "0px";
    }
    const textSpan = document.getElementById("offline-warning-text");
    if (textSpan) {
        textSpan.innerHTML = `&#x26A0;&#xFE0F; ${message}`;
    }
}

function hideOfflineBanner() {
    const banner = document.getElementById("offline-warning-banner");
    if (banner) {
        banner.style.opacity = "0";
        banner.style.marginTop = "-10px";
        setTimeout(() => banner.remove(), 300);
    }
}

/**
 * POST /api/auth/login
 */
export async function login(email, password) {
    return request(API_ENDPOINTS.LOGIN, {
        method: "POST",
        body: JSON.stringify({ email, password })
    });
}

/**
 * POST /api/auth/signup
 */
export async function signup(email, password) {
    return request(API_ENDPOINTS.SIGNUP, {
        method: "POST",
        body: JSON.stringify({ email, password })
    });
}

/**
 * POST /api/auth/google
 */
export async function googleLogin(idToken) {
    return request("/api/auth/google", {
        method: "POST",
        body: JSON.stringify({ id_token: idToken })
    });
}

/**
 * POST /api/auth/forgot-password
 */
export async function forgotPassword(email) {
    return request(API_ENDPOINTS.FORGOT_PASSWORD, {
        method: "POST",
        body: JSON.stringify({ email })
    });
}

/**
 * POST /api/auth/reset-password
 */
export async function resetPassword(token, newPassword) {
    return request(API_ENDPOINTS.RESET_PASSWORD, {
        method: "POST",
        body: JSON.stringify({ token, new_password: newPassword })
    });
}

/**
 * GET /api/auth/me
 */
export async function getMe() {
    return request(API_ENDPOINTS.ME, {
        method: "GET"
    });
}

/**
 * GET /api/profile
 */
export async function getProfile() {
    return request(API_ENDPOINTS.PROFILE, {
        method: "GET"
    });
}

/**
 * GET /api/recruiter/stats
 */
export async function getRecruiterStats() {
    return request(API_ENDPOINTS.STATS, {
        method: "GET"
    });
}





/**
 * POST /api/onboarding
 */
export async function submitOnboarding(payload) {
    return request(API_ENDPOINTS.ONBOARDING, {
        method: "POST",
        body: JSON.stringify(payload)
    });
}

/**
 * POST /api/process (legacy candidate-facing ATS)
 */
export async function screenResumes(formData) {
    return request(API_ENDPOINTS.PROCESS, {
        method: "POST",
        body: formData
    });
}

/**
 * POST /api/recruiter/process
 */
export async function screenResumesRecruiter(formData) {
    return request(API_ENDPOINTS.PROCESS_RECRUITER, {
        method: "POST",
        body: formData
    });
}

/**
 * GET /api/candidate/stats
 */
export async function getCandidateStats() {
    return request(API_ENDPOINTS.CANDIDATE_STATS, {
        method: "GET"
    });
}

/**
 * POST /api/candidate/process
 */
export async function screenResumeCandidate(formData) {
    return request(API_ENDPOINTS.CANDIDATE_PROCESS, {
        method: "POST",
        body: formData
    });
}

/**
 * GET /api/candidate/resumes
 */
export async function getCandidateResumes() {
    return request(API_ENDPOINTS.CANDIDATE_RESUMES, {
        method: "GET"
    });
}

/**
 * GET /api/candidate/resumes/{resume_id}
 */
export async function getCandidateResumeDetails(resumeId) {
    return request(`${API_ENDPOINTS.CANDIDATE_RESUMES}/${resumeId}`, {
        method: "GET"
    });
}

/**
 * DELETE /api/candidate/resumes/{resume_id}
 */
export async function deleteCandidateResume(resumeId) {
    return request(`${API_ENDPOINTS.CANDIDATE_RESUMES}/${resumeId}`, {
        method: "DELETE"
    });
}

/**
 * PUT /api/candidate/resumes/{resume_id}/label
 */
export async function updateCandidateResumeLabel(resumeId, label) {
    return request(`${API_ENDPOINTS.CANDIDATE_RESUMES}/${resumeId}/label`, {
        method: "PUT",
        body: JSON.stringify({ label })
    });
}

/**
 * PUT /api/candidate/resumes/{resume_id}/recommendations/{rec_id}
 */
export async function updateRecommendationStatus(resumeId, recId, status, acceptedByUser = null) {
    const payload = { status };
    if (acceptedByUser !== null) {
        payload.accepted_by_user = acceptedByUser;
    }
    return request(`${API_ENDPOINTS.CANDIDATE_RESUMES}/${resumeId}/recommendations/${recId}`, {
        method: "PUT",
        body: JSON.stringify(payload)
    });
}

/**
 * GET /api/recruiter/profiles
 */
export async function getScoringProfiles() {
    return request(API_ENDPOINTS.PROFILES, {
        method: "GET"
    });
}

/**
 * GET /api/recruiter/jobs
 */
export async function getJobs(includeArchived = false) {
    return request(`${API_ENDPOINTS.JOBS}?include_archived=${includeArchived}`, {
        method: "GET"
    });
}

/**
 * POST /api/recruiter/jobs
 */
export async function createJob(formData) {
    return request(API_ENDPOINTS.JOBS, {
        method: "POST",
        body: formData
    });
}

/**
 * PUT /api/recruiter/jobs/{jd_id}
 */
export async function updateJob(jdId, formData) {
    return request(`${API_ENDPOINTS.JOBS}/${jdId}`, {
        method: "PUT",
        body: formData
    });
}

/**
 * DELETE /api/recruiter/jobs/{jd_id}
 */
export async function archiveJob(jdId) {
    return request(`${API_ENDPOINTS.JOBS}/${jdId}`, {
        method: "DELETE"
    });
}

/**
 * DELETE /api/recruiter/jobs/{jd_id}/delete
 */
export async function deleteJob(jdId) {
    return request(`${API_ENDPOINTS.JOBS}/${jdId}/delete`, {
        method: "DELETE"
    });
}
