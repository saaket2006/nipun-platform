# Graph Report - nipun-platform  (2026-11-10)

## Corpus Check
- 146 files · ~224,966 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1391 nodes · 3061 edges · 93 communities (83 shown, 10 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 315 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9a4c087e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PipelineStage
- test_custom_scoring.py
- xai/builder.py
- Skill
- login.js
- state.js
- routers/test_auth.py
- gsap.min.js
- AnalysisContext
- stages.py
- ScrollTrigger.min.js
- test_password_reset.py
- screen_resumes
- api.js
- UserRole
- navbar.js
- s
- recruiter.js
- Tween
- package.json
- test_password_visibility_duplication.py
- test_candidate_patch_rejects_forbidden_fields
- _d
- .__init__
- yc
- ja
- jc
- landing.js
- .__init__
- cb
- test_profile_editing.py
- Oa
- bf
- skill_expander.py
- User
- Landing Index HTML
- Nipun AI Resume Screener & Ranking System — High-Level Architecture
- loadingOverlay.js
- Q
- r
- auth.py
- validate_skill_name
- zd
- firebase-config.example.js
- Graphify Agent Rule
- Graphify Workflow Guide
- AI Resume Screener Overview
- test_live_schema_verification_job_descriptions
- Python Dependencies
- Session
- main.py
- test_firebase_auth.py
- test_get_recruiter_stats_omits_candidate_recommendations
- backend/tests/test_recruiter.py
- candidate.js
- test_frontend_assets.py
- Chapter: Semantic Matching Evaluation & Knowledge Base Verification
- test_auth_modal_regression.py
- generate_grounded_xai_insights
- extract_education
- router.js
- process_resumes
- test_remediation.py
- K
- update_job_description
- legacy_process_resumes
- get_screening_task_detail
- test_candidate_xai_dashboard.py
- app.js
- test_confirm_password.py
- list_job_descriptions

## God Nodes (most connected - your core abstractions)
1. `User` - 67 edges
2. `UserRole` - 47 edges
3. `CompanyType` - 38 edges
4. `AnalysisContext` - 33 edges
5. `PipelineStage` - 33 edges
6. `request()` - 31 edges
7. `PersistenceStage` - 28 edges
8. `ResumeStatus` - 27 edges
9. `AnalysisPipeline` - 26 edges
10. `ScoringProfileResolutionStage` - 26 edges

## Surprising Connections (you probably didn't know these)
- `CandidateProfile` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `PasswordResetToken` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `Resume` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `ScanResult` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `ScoringProfile` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py

## Import Cycles
- 3-file cycle: `frontend/assets/js/auth.js -> frontend/assets/js/router.js -> frontend/assets/js/pages/login.js -> frontend/assets/js/auth.js`

## Communities (93 total, 10 thin omitted)

### Community 0 - "PipelineStage"
Cohesion: 0.18
Nodes (41): ResumeStatus, Resume, ScanResult, ScoringProfile, ExplanationBuiltEvent, PersistenceEvent, PipelineEvent, ProfileResolvedEvent (+33 more)

### Community 1 - "test_custom_scoring.py"
Cohesion: 0.05
Nodes (58): Defines thresholds and priorities for AI Resume Improvement Engine…, RecommendationPolicy, Defines recruiter-specific configurations and security permissions., RecruiterPolicy, Defines policy configurations for ATS scoring and weights. Removes magic…, ScoringPolicy, Any, Validates, sanitizes, and normalizes optional recruiter custom scoring… (+50 more)

### Community 2 - "xai/builder.py"
Cohesion: 0.07
Nodes (48): build_score_components(), Any, Builds the structured ScoreComponent list using the candidate's scored…, _resolve_status(), Any, Helper to construct a dict representation of StructuredExplanations., Generates structured multi-level explanations (SUMMARY, DETAILED, TECHNICAL)…, effective_exp_title() (+40 more)

### Community 3 - "Skill"
Cohesion: 0.06
Nodes (38): get_weight(), Returns the matching weight for the given match type., MatchReason, MatchResult, BaseModel, Universal domain object representing a semantic match between a required skill…, Evaluates relationship type, confidence, and matches between two Skill objects.…, resolve_relationship() (+30 more)

### Community 4 - "login.js"
Cohesion: 0.17
Nodes (22): checkAuthStatus(), _doCheckAuthStatus(), hideEmailVerificationModal(), initAuthListener(), showEmailVerificationModal(), waitForAuthState(), app, auth (+14 more)

### Community 5 - "state.js"
Cohesion: 0.15
Nodes (16): getStepsForRole(), hideObError(), initializeOnboardingPage, initOnboarding(), showObError(), showOnboardingWizard(), submitOnboarding(), updateOnboardingUI() (+8 more)

### Community 6 - "routers/test_auth.py"
Cohesion: 0.24
Nodes (7): fetch_google_certs(), test_fetch_google_certs_error(), test_fetch_google_certs_success(), test_fetch_google_certs_timeout(), Verifies that after screening, stats and history return fresh authoritative…, test_candidate_dashboard_stats_and_history_lifecycle(), Exception

### Community 7 - "gsap.min.js"
Cohesion: 0.06
Nodes (16): ee(), Jd(), Kd(), Ld(), ma(), Md(), na(), Od() (+8 more)

### Community 8 - "AnalysisContext"
Cohesion: 0.11
Nodes (17): AnalysisContext, Any, Lightweight, shared context carrying tracing IDs, configurations, and stage…, AnalysisPipeline, Session, Orchestrator to run raw resume payloads through sequential pipeline stages., Runs stages 1 through 7 of the analysis pipeline., create_docx_bytes() (+9 more)

### Community 9 - "stages.py"
Cohesion: 0.08
Nodes (38): extract_email(), extract_experience(), extract_github(), extract_name(), extract_phone(), extract_projects(), extract_relevant_internships(), Very crude heuristic to determine the scale or presence of personal/academic… (+30 more)

### Community 10 - "ScrollTrigger.min.js"
Cohesion: 0.07
Nodes (4): dc(), Ha(), Ia(), ob()

### Community 11 - "test_password_reset.py"
Cohesion: 0.08
Nodes (27): Verifies a plain text password against the hashed version using bcrypt., verify_password(), disable_rate_limiting(), existing_user(), fixture, Test resetting password with a valid token., Temporarily disables SlowAPI rate limiting for unit tests., Test that a reset token cannot be reused a second time. (+19 more)

### Community 12 - "screen_resumes"
Cohesion: 0.15
Nodes (10): preprocess_text(), Cleans text by: - Lowercasing - Removing punctuation - Removing stopwords -…, Any, Session, Core business logic to screen and rank candidate resumes against a job…, screen_resumes(), extract_skills(), load_tech_skills() (+2 more)

### Community 13 - "api.js"
Cohesion: 0.12
Nodes (33): archiveJob(), createJob(), deleteCandidateResume(), deleteJob(), _executeRequest(), forgotPassword(), getCandidateResumeDetails(), getCandidateResumes() (+25 more)

### Community 14 - "UserRole"
Cohesion: 0.14
Nodes (38): CompanyType, UserRole, JobDescription, RecruiterProfile, ScreeningTask, BaseModel, UpdateRecommendationPayload, patch (+30 more)

### Community 15 - "navbar.js"
Cohesion: 0.16
Nodes (19): handleLogout(), initNavbar(), collapseSidebar(), expandSidebar(), handleKeyDown(), initSidebar(), isSidebarCollapsed(), setSidebarCollapsed() (+11 more)

### Community 16 - "s"
Cohesion: 0.15
Nodes (20): _a(), ac(), Bo(), db(), ea(), eb(), ga(), gb() (+12 more)

### Community 17 - "recruiter.js"
Cohesion: 0.13
Nodes (31): renderResults(), getCandidateDetailRowHTML(), getCandidateRowHTML(), getRecruiterCandidateCardHTML(), updateStatisticCard(), applyJdSelection(), autoBalanceActiveWeights(), getCustomScoringPayload() (+23 more)

### Community 18 - "Tween"
Cohesion: 0.15
Nodes (18): _assertThisInitialized(), Ec(), Fc(), gc(), ka(), qa(), t(), tb() (+10 more)

### Community 19 - "package.json"
Cohesion: 0.12
Nodes (15): autoprefixer, cors, firebase, dependencies, cors, firebase, devDependencies, autoprefixer (+7 more)

### Community 20 - "test_password_visibility_duplication.py"
Cohesion: 0.18
Nodes (10): Verify auth.css suppresses Microsoft Edge & IE native password reveal/clear…, Test Confirm Password field focus, typing, blur, refocus, and toggling in…, Verify that Password and Confirm Password visibility toggles and clear buttons…, Verify that every password-input-wrapper in index.html contains exactly ONE…, Test interactive focus, typing, blur, refocus, and toggling in Chromium/Edge., test_css_suppresses_native_ms_reveal_and_clear(), test_dom_has_exactly_one_toggle_per_password_wrapper(), test_independent_visibility_toggles_and_clear() (+2 more)

### Community 21 - "test_candidate_patch_rejects_forbidden_fields"
Cohesion: 0.40
Nodes (5): PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., test_candidate_patch_rejects_forbidden_fields(), test_recruiter_patch_rejects_forbidden_fields(), parametrize

### Community 22 - "_d"
Cohesion: 0.29
Nodes (10): be(), _d(), fa(), ia(), ie(), je(), ke(), le() (+2 more)

### Community 24 - "yc"
Cohesion: 0.22
Nodes (11): Fa(), Ga(), mb(), oc(), qc(), rc(), Ta(), ub() (+3 more)

### Community 25 - "ja"
Cohesion: 0.28
Nodes (9): Aa(), Animation(), ha(), ja(), Jc(), Lc(), Ra(), Sa() (+1 more)

### Community 26 - "jc"
Cohesion: 0.22
Nodes (9): Ab(), J(), jc(), kb(), lc(), Ra(), rb(), Sa() (+1 more)

### Community 27 - "landing.js"
Cohesion: 0.44
Nodes (9): initCounters(), initFeatureStack(), initHeroAnimation(), initNavbarEffects(), initStoryAnimation(), initWalkthrough(), initAllLandingAnimations(), initLandingMobileNav() (+1 more)

### Community 29 - "cb"
Cohesion: 0.29
Nodes (7): Ab(), Bb(), cb(), Context(), Ew(), fb(), zb()

### Community 30 - "test_profile_editing.py"
Cohesion: 0.05
Nodes (39): candidate_user(), disable_rate_limiting(), fixture, Temporarily disables SlowAPI rate limiting for unit tests., Candidate partial update changes only provided field, preserving others., Recruiter can update display_name., Recruiter can update company_name, company_type, and hiring_domain., Recruiter partial update changes only provided field, preserving others. (+31 more)

### Community 31 - "Oa"
Cohesion: 0.53
Nodes (6): Bb(), Ja(), Ka(), La(), Oa(), z()

### Community 32 - "bf"
Cohesion: 0.22
Nodes (10): bf(), cf(), df(), ef(), kf(), lf(), M(), mf() (+2 more)

### Community 33 - "skill_expander.py"
Cohesion: 0.40
Nodes (4): get_related_skills(), is_skill_in_text(), Checks if an explicit skill contains a broad conceptual keyword. For example,…, Checks if a skill or any of its known aliases exists in the given text. Handles…

### Community 34 - "User"
Cohesion: 0.08
Nodes (36): User, candidate_status(), delete_candidate_resume(), get_candidate_resume_details(), get_candidate_resumes(), get_candidate_stats(), process_candidate_resume(), delete (+28 more)

### Community 35 - "Landing Index HTML"
Cohesion: 0.40
Nodes (5): Nipun Main Branding Image, Candidate Portal HTML, Landing Index HTML, Onboarding Portal HTML, Recruiter Dashboard HTML

### Community 36 - "Nipun AI Resume Screener & Ranking System — High-Level Architecture"
Cohesion: 0.29
Nodes (6): Authentication & Authorization Boundaries, Deployment Boundaries, Major Components & Services, Nipun AI Resume Screener & Ranking System — High-Level Architecture, Primary Data Stores, System Overview

### Community 37 - "loadingOverlay.js"
Cohesion: 0.50
Nodes (3): loadingOverlay, STAGES, STATUS_MESSAGES

### Community 38 - "Q"
Cohesion: 0.50
Nodes (4): la(), Q(), Gb(), Hb()

### Community 39 - "r"
Cohesion: 0.50
Nodes (4): mc(), O(), P(), r()

### Community 48 - "auth.py"
Cohesion: 0.13
Nodes (29): Settings, create_access_token(), Generates a secure JSON Web Token., PasswordResetToken, forgot_password(), get_me(), google_login(), GoogleLoginRequest (+21 more)

### Community 49 - "validate_skill_name"
Cohesion: 0.33
Nodes (9): Validates that a skill name contains reasonable characters and isn't empty,…, validate_skill_name(), test_validate_skill_name_empty_or_whitespace_only(), test_validate_skill_name_invalid_chars(), test_validate_skill_name_non_string(), test_validate_skill_name_too_long(), test_validate_skill_name_valid_common(), test_validate_skill_name_valid_special_chars() (+1 more)

### Community 66 - "Session"
Cohesion: 0.29
Nodes (8): archive_job_description(), delete_job_description(), delete, Session, Soft-deletes (archives) a job description., Permanently deletes a job description and its scan results., test_archive_job_description_success(), test_archive_job_description_unauthorized()

### Community 68 - "main.py"
Cohesion: 0.09
Nodes (21): Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online(), api_route, check_db_connection(), get_db(), Tests connection to the configured database on demand (e.g. startup or health… (+13 more)

### Community 69 - "test_firebase_auth.py"
Cohesion: 0.06
Nodes (45): App, get_firebase_admin_app(), Any, Verifies a Firebase ID token using the Firebase Admin SDK. Extracts trusted…, Lazily initializes and returns the singleton Firebase Admin App. Supports: 1.…, verify_firebase_id_token(), get_current_user(), Session (+37 more)

### Community 74 - "backend/tests/test_recruiter.py"
Cohesion: 0.18
Nodes (15): create_job_description(), Adds a new job description to the recruiter's library or promotes an ad-hoc JD.…, Verify that JobDescription.name is an active synonym for JobDescription.title., Verify create_job_description correctly accepts 'name' instead of 'title'., Verify get_candidate_resume_details still returns recommendations for candidate…, test_candidate_resume_details_preserves_recommendations(), test_create_job_description_deduplication(), test_create_job_description_duplicate_names_distinct_records() (+7 more)

### Community 75 - "candidate.js"
Cohesion: 0.19
Nodes (12): getEmptyStateHTML(), toggleButtonLoading(), populateCandidateProfileUI(), closeCandidateAnalysisModal(), initCandidatePage(), renderCandidateAnalysisResults(), renderFileList(), renderRecommendations() (+4 more)

### Community 79 - "test_frontend_assets.py"
Cohesion: 0.05
Nodes (38): Verify frontend/firebase-config.js exists and is valid JavaScript exporting…, Verify recruiter.html contains the full quick view modal and candidate.html…, Verify candidate card renders quick view button with data attributes and…, Verify recruiter profile has horizontal side-by-side layout, pencil icon…, Verify recruiter screening history has a compact icon-only refresh button with…, Verify that frontend/firebase-config.js is not ignored by .gitignore., Verify recruiter pages hide candidate recommendations while candidate views…, Verify recruiter screening has explicit reset controls and state reset… (+30 more)

### Community 87 - "Chapter: Semantic Matching Evaluation & Knowledge Base Verification"
Cohesion: 0.07
Nodes (26): 1. Executive Summary & Evaluation Scope, 2.1 Canonical Knowledge Base & Taxonomy Structure, 2.2 Relationship Categories & Deterministic Policy Weights, 2.3 Rule Precedence Cascade, 2.4 Multi-Skill Scoring Formula, 2. Methodology & Mathematical Formulation, 3.1 Total Evaluation Case Construction (Total $N = 317$), 3.2 Match Type Distribution (Experiment A) (+18 more)

### Community 89 - "test_auth_modal_regression.py"
Cohesion: 0.12
Nodes (16): Verify app.js handles readyState interactive/complete so module execution never…, Verify router.js integrates with modal.js for auth routing., Verify index.html contains exactly one #auth-modal element., Verify #auth-modal has login and signup tabs and planes., Verify all key CTA buttons in index.html possess resilient data-auth-modal…, Verify modal.js exports explicit openAuthModal and closeAuthModal functions., Verify modal.js attaches event delegation on document to handle auth triggers…, Verify app.js actively calls initModals() during page initialization. (+8 more)

### Community 92 - "generate_grounded_xai_insights"
Cohesion: 0.20
Nodes (17): _build_deterministic_fallback(), _call_gemini_content(), generate_grounded_xai_insights(), Any, Makes HTTP request to Gemini API and parses JSON response., Safely extracts and parses JSON even if wrapped in markdown code fences or…, Constructs a deterministic, grounded rule-based summary when Gemini is…, Invokes the Google Gemini API to generate grounded, explainable AI insights for… (+9 more)

### Community 93 - "extract_education"
Cohesion: 0.21
Nodes (15): extract_education(), extract_linkedin(), Heuristically extract highest degree level. Returns standard labels for…, Extract a LinkedIn profile URL., test_extract_education_bachelor(), test_extract_education_boundaries(), test_extract_education_case_insensitivity(), test_extract_education_master() (+7 more)

### Community 100 - "router.js"
Cohesion: 0.23
Nodes (19): getProfile(), handleLogoNavigation(), populateRecruiterProfileUI(), updateSidebarActiveLink(), initializeCandidateDashboard(), initializeCandidateProfile(), initializeCandidateScreen(), initializeRecruiterDashboard() (+11 more)

### Community 101 - "process_resumes"
Cohesion: 0.20
Nodes (10): process_resumes(), limit, post, Request, UploadFile, Screens uploaded resume files against a job description. Enforces…, test_process_resumes_rejects_invalid_custom_scoring(), anyio (+2 more)

### Community 105 - "test_remediation.py"
Cohesion: 0.08
Nodes (30): extract_text(), extract_text_from_docx(), extract_text_from_pdf(), Extract text from a DOCX file, including paragraphs and tables., Route to appropriate extractor based on extension., Extract text from a PDF file., build_analysis_metadata(), Any (+22 more)

### Community 125 - "K"
Cohesion: 0.40
Nodes (5): A(), B(), F(), G(), K()

### Community 130 - "update_job_description"
Cohesion: 0.25
Nodes (8): put, Edits an existing job description in the recruiter's library. Accepts updated…, update_job_description(), Verify update_job_description correctly accepts 'name' instead of 'title'., test_update_job_description_success(), test_update_job_description_unauthorized(), test_update_job_description_validation(), test_update_job_description_with_name_parameter()

### Community 131 - "legacy_process_resumes"
Cohesion: 0.29
Nodes (7): legacy_process_resumes(), limit, post, Request, Session, UploadFile, Legacy endpoint delegating to recruiter process_resumes. Requires Recruiter…

### Community 132 - "get_screening_task_detail"
Cohesion: 0.33
Nodes (6): get_screening_task_detail(), Retrieves complete details for a specific screening task owned by the…, Verify get_screening_task_detail strips recommendations from candidate…, test_get_screening_task_detail_omits_candidate_recommendations(), test_get_screening_task_detail_owner_success(), test_get_screening_task_detail_unauthorized_or_missing()

### Community 134 - "test_candidate_xai_dashboard.py"
Cohesion: 0.08
Nodes (29): get_password_hash(), Hashes a plain text password using bcrypt., CandidateProfile, post, Session, Creates a user profile based on the role and marks onboarding as completed., submit_onboarding(), anyio_backend() (+21 more)

### Community 135 - "app.js"
Cohesion: 0.30
Nodes (9): clearCandidateState(), handleFiles(), renderFileList(), updateResumeCountDisplay(), uploadedFiles, closeAuthModal(), initModals(), openAuthModal() (+1 more)

### Community 137 - "test_confirm_password.py"
Cohesion: 0.13
Nodes (14): Verify index.html contains #signup-confirm-group and #signup-confirm-password…, Verify that when opened via file:// protocol (CORS-isolated, zero-module), the…, Confirm Password field must NOT appear in Login, Forgot Password, or unrelated…, Verify signup.js exports validatePasswordMatch and gates Firebase registration., Confirm password value must never be sent to API, state, or storage., Verify auth.css defines .confirm-password-group, .is-visible, and feedback…, Verify full interactive lifecycle: reveal, clear, match, mismatch, tab…, test_auth_css_defines_smooth_transitions_and_semantic_feedback() (+6 more)

### Community 139 - "list_job_descriptions"
Cohesion: 0.22
Nodes (9): get_screening_history(), list_job_descriptions(), get, Retrieves all job descriptions created by the recruiter. Deduplicates identical…, Retrieves the screening history runs for the authenticated recruiter, ordered…, Verify list_job_descriptions serializes both 'name' and 'title'., test_get_screening_history_ordered(), test_list_job_descriptions_deduplication() (+1 more)

## Knowledge Gaps
- **53 isolated node(s):** `Settings`, `inflightGetRequests`, `uploadedFiles`, `sidebarLinkIds`, `COMPANY_TYPES` (+48 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `PipelineStage`, `test_custom_scoring.py`, `Session`, `legacy_process_resumes`, `main.py`, `test_firebase_auth.py`, `test_candidate_xai_dashboard.py`, `get_screening_task_detail`, `process_resumes`, `update_job_description`, `backend/tests/test_recruiter.py`, `list_job_descriptions`, `routers/test_auth.py`, `test_password_reset.py`, `UserRole`, `auth.py`, `test_profile_editing.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `s()` connect `s` to `bf`, `gsap.min.js`, `recruiter.js`, `Tween`, `cb`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `CompanyType` and `ResumeStatus`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `UserRole` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`UserRole` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `CompanyType` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`CompanyType` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AnalysisContext` (e.g. with `AnalysisPipeline` and `ExplanationBuildingStage`) actually correct?**
  _`AnalysisContext` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `PipelineStage` (e.g. with `AnalysisPipeline` and `ResumeStatus`) actually correct?**
  _`PipelineStage` has 18 INFERRED edges - model-reasoned connections that need verification._