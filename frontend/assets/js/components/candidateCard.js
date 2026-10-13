import { escapeHTML } from '../utils.js';

/**
 * Unified candidate layout rendering component.
 * Outputs exact same HTML markup structure, attributes, and classes to keep UI identical.
 */

/**
 * Returns candidate row HTML string for the legacy table.
 */
export function getCandidateRowHTML(cand) {
    const rankClass = cand.rank <= 3 ? `rank-${cand.rank}` : '';

    let scoreClass = 'low-score';
    let fillClass = 'score-fill-low';
    if (cand.similarity_score >= 15) {
        scoreClass = 'high-score';
        fillClass = 'score-fill-high';
    } else if (cand.similarity_score >= 5) {
        scoreClass = 'med-score';
        fillClass = 'score-fill-med';
    }

    const email = cand.email !== 'Not Provided' ? escapeHTML(cand.email) : '<span style="opacity:0.6">Not Provided</span>';
    const phone = cand.phone !== 'Not Provided' ? escapeHTML(cand.phone) : '<span style="opacity:0.6">Not Provided</span>';
    
    // For URL sanitization, ensure the href is safe (escapeHTML handles basic attribute escaping, but ideally we'd also check scheme)
    let linkedinUrl = cand.linkedin;
    if (linkedinUrl !== 'Not Provided') {
        if (!linkedinUrl.startsWith('http://') && !linkedinUrl.startsWith('https://')) {
            linkedinUrl = 'https://' + linkedinUrl;
        }
    }
    const linkedin = cand.linkedin !== 'Not Provided' 
        ? `<a href="${escapeHTML(linkedinUrl)}" target="_blank" style="color: #6366f1; text-decoration: none;">${escapeHTML(cand.linkedin)}</a>`
        : '<span style="opacity:0.6">LinkedIn Not Provided</span>';

    let githubUrl = cand.github;
    if (githubUrl !== 'Not Provided') {
        if (!githubUrl.startsWith('http://') && !githubUrl.startsWith('https://')) {
            githubUrl = 'https://' + githubUrl;
        }
    }
    const github = cand.github !== 'Not Provided' 
        ? `<a href="${escapeHTML(githubUrl)}" target="_blank" style="color: #6366f1; text-decoration: none;">${escapeHTML(cand.github)}</a>`
        : '<span style="opacity:0.6">GitHub Not Provided</span>';

    return `
        <td><span class="rank-badge ${rankClass}">#${cand.rank}</span></td>
        <td>
            <strong>${escapeHTML(cand.name)}</strong><br>
            <small style="color:var(--text-secondary); display:block; margin-top:2px;">&#x1F4E7; ${email}</small>
            <small style="color:var(--text-secondary); display:block; margin-top:2px;">&#x1F4DE; ${phone}</small>
            <small style="color:var(--text-secondary); display:block; margin-top:2px;">&#x1F517; ${linkedin}</small>
            <small style="color:var(--text-secondary); display:block; margin-top:2px;">&#x1F4BB; ${github}</small>
            <div class="candidate-stats">
                <span class="stat-badge">&#x1F393; ${escapeHTML(cand.education) || 'None'}</span>
                <span class="stat-badge">&#x1F4BC; ${escapeHTML(cand.experience) || 0} Yrs</span>
                <span class="stat-badge">&#x1F680; Proj: ${escapeHTML(cand.projects) || 0}/5</span>
            </div>
        </td>
        <td style="min-width: 150px;">
            <span class="score-badge ${scoreClass}">${cand.similarity_score}%</span>
            <div class="score-container">
                <div class="score-bar-fill ${fillClass}" style="width: 0%" data-target="${Math.min(cand.similarity_score, 100)}%"></div>
            </div>
        </td>
        <td class="expand-hint-cell"><span class="expand-chevron">&#x25B6;</span></td>
    `;
}

/**
 * Returns candidate detail row HTML string for the legacy table.
 */
export function getCandidateDetailRowHTML(cand) {
    const matchedHtml = cand.matched_skills.map(s => `<span class="skill-tag matched">${escapeHTML(s)}</span>`).join('');
    const missingHtml = cand.missing_skills.map(s => `<span class="skill-tag missing">${escapeHTML(s)}</span>`).join('');

    const breakdownItems = [
        { label: 'Skill Match', value: cand.skill_score || 0, weight: '50%' },
        { label: 'Experience', value: cand.experience_score || 0, weight: '25%' },
        { label: 'Education', value: cand.education_score || 0, weight: '15%' },
        { label: 'Projects', value: cand.projects_score || 0, weight: '10%' },
    ];

    let breakdownHtml = breakdownItems.map(item => {
        const val = Math.round(item.value);
        let barClass = 'score-fill-low';
        if (val >= 60) barClass = 'score-fill-high';
        else if (val >= 30) barClass = 'score-fill-med';
        return `
            <div class="breakdown-item">
                <div class="breakdown-label">
                    <span>${escapeHTML(item.label)}</span>
                    <span class="breakdown-weight">(${escapeHTML(item.weight)})</span>
                    <span class="breakdown-value">${val}%</span>
                </div>
                <div class="score-container breakdown-bar">
                    <div class="score-bar-fill ${barClass}" style="width: 0%" data-target="${val}%"></div>
                </div>
            </div>`;
    }).join('');

    breakdownHtml += `
        <div class="breakdown-final">
            <span>Final Score</span>
            <span class="final-score-value">${cand.similarity_score}%</span>
        </div>`;

    return `
        <td colspan="4" class="detail-cell">
            <div class="detail-panel">
                <div class="detail-section">
                    <h4>&#x1F4CA; Score Breakdown</h4>
                    <div class="breakdown-grid">${breakdownHtml}</div>
                </div>
                <div class="detail-section">
                    <h4>&#x2705; Matched Skills</h4>
                    <div class="skills-list">${matchedHtml || '<span style="color:#666">None</span>'}</div>
                </div>
                <div class="detail-section">
                    <h4>&#x274C; Missing Skills</h4>
                    <div class="skills-list">${missingHtml || '<span style="color:#666">None</span>'}</div>
                </div>
            </div>
        </td>
    `;
}

/**
 * Returns candidate card HTML string for the Recruiter Workspace.
 */
export function getRecruiterCandidateCardHTML(cand, index = null) {
    if (!cand) return '';
    const isTopRank = (cand.rank && cand.rank <= 3) ? 'top-rank' : '';
    
    let scoreClass = 'low-score';
    const score = typeof cand.similarity_score === 'number' ? cand.similarity_score : 0;
    if (score >= 70) {
        scoreClass = 'high-score';
    } else if (score >= 40) {
        scoreClass = 'med-score';
    }

    const matchedList = Array.isArray(cand.matched_skills) ? cand.matched_skills : [];
    const missingList = Array.isArray(cand.missing_skills) ? cand.missing_skills : [];

    const matchedTags = matchedList.slice(0, 5).map(s => `<span class="skill-tag matched">${escapeHTML(s)}</span>`).join('');
    const missingTags = missingList.slice(0, 5).map(s => `<span class="skill-tag missing">${escapeHTML(s)}</span>`).join('');

    const indexAttr = (index !== null && index !== undefined) ? ` data-candidate-index="${index}"` : '';

    return `
        <div class="cand-left">
            <div class="cand-rank ${isTopRank}">#${cand.rank || ''}</div>
            <div class="cand-info">
                <h4 class="cand-name">${escapeHTML(cand.name || 'Unnamed Candidate')}</h4>
                <div class="cand-skills-summary">
                    <div class="skills-row">
                        <span class="skills-row-label matched">Matched:</span>
                        ${matchedTags || '<span style="color:#666; font-size:0.8rem;">None</span>'}
                    </div>
                    <div class="skills-row" style="margin-top: 0.25rem;">
                        <span class="skills-row-label missing">Missing:</span>
                        ${missingTags || '<span style="color:#666; font-size:0.8rem;">None</span>'}
                    </div>
                </div>
            </div>
        </div>
        <div class="cand-right">
            <div class="score-block">
                <span class="score-badge ${scoreClass}">${score}%</span>
            </div>
            <button type="button" class="quick-view-btn"${indexAttr}>Quick View</button>
        </div>
    `;
}
