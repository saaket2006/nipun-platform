/**
 * Profile Section component. Maps profile properties to DOM text fields and edit inputs.
 */

/**
 * Populates Recruiter dashboard and profile view element fields.
 * @param {Object} profile - User profile containing recruiter details
 */
export function populateRecruiterProfileUI(profile) {
    if (!profile) return;
    const recName = profile.display_name || (profile.email ? profile.email.split('@')[0] : "Recruiter");
    const compName = profile.recruiter_profile?.company_name || "N/A";
    const compType = profile.recruiter_profile?.company_type || "N/A";
    const hiringDomain = profile.recruiter_profile?.hiring_domain || "N/A";

    const mappings = {
        "dash-rec-name": recName,
        "dash-comp-name": compName,
        "dash-comp-type": compType,
        "dash-hiring-domain": hiringDomain,
        "rec-top-user-name": recName,
        "profile-rec-name": recName,
        "profile-rec-email": profile.email || "N/A",
        "profile-comp-name": compName,
        "profile-comp-type": compType,
        "profile-hiring-domain": hiringDomain
    };

    Object.entries(mappings).forEach(([id, val]) => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = val;
        }
    });

    // Populate edit form inputs if present
    const inputMappings = {
        "rec-edit-display-name": profile.display_name || "",
        "rec-edit-comp-name": profile.recruiter_profile?.company_name || "",
        "rec-edit-comp-type": profile.recruiter_profile?.company_type || "",
        "rec-edit-hiring-domain": profile.recruiter_profile?.hiring_domain || ""
    };

    Object.entries(inputMappings).forEach(([id, val]) => {
        const inputEl = document.getElementById(id);
        if (inputEl) {
            inputEl.value = val;
        }
    });
}

/**
 * Populates Candidate dashboard and profile view element fields.
 * @param {Object} profile - User profile containing candidate details
 */
export function populateCandidateProfileUI(profile) {
    if (!profile) return;
    const candName = profile.display_name || (profile.email ? profile.email.split('@')[0] : "Candidate");
    const statusVal = profile.candidate_profile?.current_status || "N/A";
    const fieldVal = profile.candidate_profile?.field_of_study || "N/A";
    const domainVal = profile.candidate_profile?.current_domain || "N/A";

    let formattedJoin = "N/A";
    if (profile.created_at) {
        const joinDate = new Date(profile.created_at);
        formattedJoin = joinDate.toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    const mappings = {
        "dash-cand-name": candName,
        "dash-cand-status": statusVal,
        "dash-cand-field": fieldVal,
        "dash-cand-domain": domainVal,
        "cand-top-user-name": candName,
        "profile-cand-name": candName,
        "profile-cand-email": profile.email || "N/A",
        "profile-cand-status": statusVal,
        "profile-cand-field": fieldVal,
        "profile-cand-domain": domainVal,
        "profile-cand-joined": formattedJoin
    };

    Object.entries(mappings).forEach(([id, val]) => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = val;
        }
    });

    // Populate edit form inputs if present
    const inputMappings = {
        "cand-edit-display-name": profile.display_name || "",
        "cand-edit-status": profile.candidate_profile?.current_status || "",
        "cand-edit-field": profile.candidate_profile?.field_of_study || "",
        "cand-edit-domain": profile.candidate_profile?.current_domain || ""
    };

    Object.entries(inputMappings).forEach(([id, val]) => {
        const inputEl = document.getElementById(id);
        if (inputEl) {
            inputEl.value = val;
        }
    });
}
