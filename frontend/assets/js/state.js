let state = {
    currentUser: null,
    currentProfile: null,
    candidateStats: null,
    candidateResumes: null,
    recruiterStats: null,
    authToken: localStorage.getItem("access_token") || null,
    currentRoute: window.location.hash || "",
    onboardingStatus: null
};

export function setUser(user) {
    // Invalidate cached user-specific data if switching users
    if (state.currentUser && user && (state.currentUser.id !== user.id || state.currentUser.firebase_uid !== user.firebase_uid)) {
        state.currentProfile = null;
        state.candidateStats = null;
        state.candidateResumes = null;
        state.recruiterStats = null;
    }
    state.currentUser = user;
}

export function getUser() {
    return state.currentUser;
}

export function setProfile(profile) {
    state.currentProfile = profile;
}

export function getProfile() {
    return state.currentProfile;
}

export function setCandidateStats(stats) {
    state.candidateStats = stats;
}

export function getCandidateStats() {
    return state.candidateStats;
}

export function setCandidateResumes(resumes) {
    state.candidateResumes = resumes;
}

export function getCandidateResumes() {
    return state.candidateResumes;
}

export function setRecruiterStats(stats) {
    state.recruiterStats = stats;
}

export function getRecruiterStats() {
    return state.recruiterStats;
}

export function setToken(token) {
    state.authToken = token;
    if (token) {
        localStorage.setItem("access_token", token);
    } else {
        localStorage.removeItem("access_token");
    }
}

export function getToken() {
    return state.authToken;
}

export function clearState() {
    state.currentUser = null;
    state.currentProfile = null;
    state.candidateStats = null;
    state.candidateResumes = null;
    state.recruiterStats = null;
    state.authToken = null;
    state.currentRoute = "";
    state.onboardingStatus = null;
    localStorage.removeItem("access_token");
}

export function setRoute(route) {
    state.currentRoute = route;
}

export function getRoute() {
    return state.currentRoute;
}

export function setOnboardingStatus(status) {
    state.onboardingStatus = status;
}

export function getOnboardingStatus() {
    return state.onboardingStatus;
}

