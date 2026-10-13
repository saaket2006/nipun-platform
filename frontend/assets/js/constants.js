export const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.hostname === "" 
    ? "http://127.0.0.1:8000" 
    : "https://ai-resume-screener-backend-t2e0.onrender.com";

export const ROLES = {
    RECRUITER: "RECRUITER",
    CANDIDATE: "CANDIDATE",
    UNASSIGNED: "UNASSIGNED"
};

export const ROUTES = {
    DASHBOARD: "#/recruiter/dashboard",
    SCREEN: "#/recruiter/screen",
    PROFILE: "#/recruiter/profile",
    HISTORY: "#/recruiter/history",
    CANDIDATE_DASHBOARD: "#/candidate/dashboard",
    CANDIDATE_SCREEN: "#/candidate/screen",
    CANDIDATE_PROFILE: "#/candidate/profile",
    LOGIN: "#/login",
    SIGNUP: "#/signup",
    FORGOT_PASSWORD: "#/forgot-password",
    RESET_PASSWORD: "#/reset-password"
};

export const API_ENDPOINTS = {
    LOGIN: "/api/auth/login",
    SIGNUP: "/api/auth/signup",
    ME: "/api/auth/me",
    PROFILE: "/api/profile",
    STATS: "/api/recruiter/stats",
    ONBOARDING: "/api/onboarding",
    PROCESS: "/api/process",
    PROCESS_RECRUITER: "/api/recruiter/process",
    CANDIDATE_STATS: "/api/candidate/stats",
    CANDIDATE_PROCESS: "/api/candidate/process",
    CANDIDATE_RESUMES: "/api/candidate/resumes",
    PROFILES: "/api/recruiter/profiles",
    JOBS: "/api/recruiter/jobs",
    FORGOT_PASSWORD: "/api/auth/forgot-password",
    RESET_PASSWORD: "/api/auth/reset-password",
    CANDIDATE_PROFILE: "/api/candidate/profile",
    RECRUITER_PROFILE: "/api/recruiter/profile",
    RECRUITER_HISTORY: "/api/recruiter/history"
};

export const COMPANY_TYPES = [
    "Startup",
    "SME",
    "Enterprise",
    "MNC",
    "Government",
    "Educational Institution",
    "Consultancy",
    "Non-Profit",
    "Other"
];

export const CANDIDATE_STATUS_VALUES = [
    "Student",
    "Working Professional",
    "Career Switcher",
    "Freelancer",
    "Job Seeker",
    "Other"
];

export const MESSAGES = {
    ENTER_JD: "Please enter a job description.",
    UPLOAD_RESUME: "Please upload at least one resume.",
    ROLE_REQUIRED: "Please select a role to continue.",
    COMPANY_NAME_REQUIRED: "Company name is required.",
    COMPANY_TYPE_REQUIRED: "Please select a company type.",
    HIRING_DOMAIN_REQUIRED: "Please select a hiring domain.",
    STATUS_REQUIRED: "Please select your current status.",
    FIELD_STUDY_REQUIRED: "Field of study is required.",
    CURRENT_DOMAIN_REQUIRED: "Current domain is required.",
    AUTH_LOST: "Authentication session lost. Please log in again.",
    PASSWORD_REQ: "Please meet all password requirements.",
    SESSION_EXPIRED: "Session expired or invalid. Please log in again.",
    PASSWORD_RESET_SENT: "If an account exists for this email, a password reset link has been sent.",
    PASSWORD_RESET_SUCCESS: "Your password has been successfully reset. Please log in with your new password.",
    PASSWORD_MISMATCH: "Passwords do not match."
};
