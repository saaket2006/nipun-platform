# Graph Report - nipun-platform  (2026-11-11)

## Corpus Check
- 153 files · ~234,344 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1527 nodes · 3242 edges · 102 communities (94 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 319 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f4f81c17`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- stages.py
- test_custom_scoring.py
- engine.py
- Skill
- app.js
- login.js
- candidate.js
- gsap.min.js
- recruiter.py
- tests/test_info_extractor.py
- ScrollTrigger.min.js
- UserRole
- test_layout_consistency.py
- api.js
- test_password_reset.py
- test_preflight_options_allowed_origins
- r
- recruiter.js
- Tween
- package.json
- test_password_visibility_duplication.py
- test_screening_xai_refinement.py
- _d
- google_login
- yc
- ja
- jc
- landing.js
- _resolve_status
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
- sidebar.js
- validate_skill_name
- zd
- firebase-config.example.js
- Graphify Agent Rule
- Graphify Workflow Guide
- AI Resume Screener Overview
- test_profile_and_task_details_refinement.py
- Python Dependencies
- get_screening_history
- update_job_description
- test_firebase_auth.py
- get_screening_task_detail
- test_candidate_xai_dashboard.py
- backend/tests/test_recruiter.py
- xai/builder.py
- test_candidate_dashboard_refinement.py
- list_job_descriptions
- get_current_user
- test_frontend_assets.py
- test_xai_and_dropzone_refinement.py
- format_overall_explanation
- router.js
- generate_experience_evidence
- legacy_process_resumes
- Chapter: Semantic Matching Evaluation & Knowledge Base Verification
- test_candidate_patch_rejects_forbidden_fields
- test_auth_modal_regression.py
- firebaseConfig
- test_candidate_resume_details_preserves_recommendations
- generate_grounded_xai_insights
- v
- ka
- xe
- state.js
- process_resumes
- test_remediation.py
- K
- Session
- test_confirm_password.py

## God Nodes (most connected - your core abstractions)
1. `User` - 68 edges
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
- `test_actual_authenticated_request_cors_headers_on_localhost_3000()` --indirect_call--> `get_current_user()`  [INFERRED]
  tests/test_cors_configuration.py → backend/dependencies/auth_deps.py
- `test_backend_xai_engine_suppresses_skills_supporting_evidence()` --calls--> `XaiEngine`  [EXTRACTED]
  tests/test_xai_and_dropzone_refinement.py → backend/services/xai/engine.py
- `test_backend_xai_engine_suppresses_skills_supporting_evidence()` --calls--> `Evidence`  [EXTRACTED]
  tests/test_xai_and_dropzone_refinement.py → backend/services/xai/models.py
- `test_backend_xai_engine_suppresses_skills_supporting_evidence()` --calls--> `ScoreComponent`  [EXTRACTED]
  tests/test_xai_and_dropzone_refinement.py → backend/services/xai/models.py
- `test_explicit_env_override_allowed_origins()` --calls--> `Settings`  [EXTRACTED]
  tests/test_cors_configuration.py → backend/config.py

## Import Cycles
- 3-file cycle: `frontend/assets/js/auth.js -> frontend/assets/js/router.js -> frontend/assets/js/pages/login.js -> frontend/assets/js/auth.js`

## Communities (102 total, 8 thin omitted)

### Community 0 - "stages.py"
Cohesion: 0.08
Nodes (69): ResumeStatus, Resume, ScanResult, ScoringProfile, preprocess_text(), Cleans text by: - Lowercasing - Removing punctuation - Removing stopwords -…, AnalysisContext, Any (+61 more)

### Community 1 - "test_custom_scoring.py"
Cohesion: 0.05
Nodes (58): Defines thresholds and priorities for AI Resume Improvement Engine…, RecommendationPolicy, Defines recruiter-specific configurations and security permissions., RecruiterPolicy, Defines policy configurations for ATS scoring and weights. Removes magic…, ScoringPolicy, Any, Validates, sanitizes, and normalizes optional recruiter custom scoring… (+50 more)

### Community 2 - "engine.py"
Cohesion: 0.16
Nodes (16): Any, Helper to construct a dict representation of StructuredExplanations., Generates structured multi-level explanations (SUMMARY, DETAILED, TECHNICAL)…, format_document_similarity_explanation(), format_education_explanation(), format_experience_explanation(), format_skills_explanation(), Any (+8 more)

### Community 3 - "Skill"
Cohesion: 0.06
Nodes (40): get_weight(), Returns the matching weight for the given match type., MatchReason, MatchResult, BaseModel, Universal domain object representing a semantic match between a required skill…, Evaluates relationship type, confidence, and matches between two Skill objects.…, resolve_relationship() (+32 more)

### Community 4 - "app.js"
Cohesion: 0.25
Nodes (10): clearCandidateState(), handleFiles(), renderFileList(), updateResumeCountDisplay(), uploadedFiles, toggleButtonLoading(), closeAuthModal(), initModals() (+2 more)

### Community 5 - "login.js"
Cohesion: 0.19
Nodes (21): checkAuthStatus(), _doCheckAuthStatus(), hideEmailVerificationModal(), initAuthListener(), showEmailVerificationModal(), waitForAuthState(), app, auth (+13 more)

### Community 6 - "candidate.js"
Cohesion: 0.11
Nodes (24): getEmptyStateHTML(), handleLogoNavigation(), handleLogout(), initNavbar(), API_BASE, API_ENDPOINTS, CANDIDATE_STATUS_VALUES, COMPANY_TYPES (+16 more)

### Community 7 - "gsap.min.js"
Cohesion: 0.07
Nodes (10): ee(), Jd(), Kd(), Ld(), ma(), Md(), na(), Od() (+2 more)

### Community 8 - "recruiter.py"
Cohesion: 0.08
Nodes (38): Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online(), api_route, check_db_connection(), get_db(), Tests connection to the configured database on demand (e.g. startup or health… (+30 more)

### Community 9 - "tests/test_info_extractor.py"
Cohesion: 0.06
Nodes (52): extract_education(), extract_email(), extract_experience(), extract_github(), extract_linkedin(), extract_name(), extract_phone(), extract_projects() (+44 more)

### Community 10 - "ScrollTrigger.min.js"
Cohesion: 0.07
Nodes (4): dc(), Ha(), Ia(), ob()

### Community 11 - "UserRole"
Cohesion: 0.21
Nodes (30): CompanyType, UserRole, GoogleLoginRequest, BaseModel, CandidateProfileResponse, CandidateProfileUpdate, Config, ForgotPasswordRequest (+22 more)

### Community 12 - "test_layout_consistency.py"
Cohesion: 0.15
Nodes (15): Verify .rec-main-wrapper is centered with margin-inline: auto and has no…, Workspace intelligence summary in recruiter.html must not override padding with…, Candidate dashboard Card 2 must not override font-size inline, breaking…, Stat cards must be full height in grid cells and icons must have standard…, Verify recruiter dashboard KPI cards have equal heights and summary card gap…, Verify candidate dashboard KPI cards have equal heights and consistent metrics., Verify zero horizontal scroll/overflow on all 6 viewports for recruiter and…, setup_page_mock() (+7 more)

### Community 13 - "api.js"
Cohesion: 0.12
Nodes (33): archiveJob(), createJob(), deleteCandidateResume(), deleteJob(), _executeRequest(), forgotPassword(), getCandidateResumeDetails(), getCandidateResumes() (+25 more)

### Community 14 - "test_password_reset.py"
Cohesion: 0.08
Nodes (28): Verifies a plain text password against the hashed version using bcrypt., verify_password(), PasswordResetToken, disable_rate_limiting(), existing_user(), fixture, Test resetting password with a valid token., Temporarily disables SlowAPI rate limiting for unit tests. (+20 more)

### Community 15 - "test_preflight_options_allowed_origins"
Cohesion: 0.67
Nodes (3): parametrize, Verify that OPTIONS preflight requests from all supported local dev and prod…, test_preflight_options_allowed_origins()

### Community 16 - "r"
Cohesion: 0.13
Nodes (16): Bo(), ga(), gb(), hb(), Jc(), lb(), Lc(), oa() (+8 more)

### Community 17 - "recruiter.js"
Cohesion: 0.12
Nodes (36): renderResults(), getCandidateDetailRowHTML(), getCandidateRowHTML(), getRecruiterCandidateCardHTML(), updateStatisticCard(), renderXaiContent(), applyJdSelection(), autoBalanceActiveWeights() (+28 more)

### Community 18 - "Tween"
Cohesion: 0.20
Nodes (14): _assertThisInitialized(), Ec(), Fc(), gc(), qa(), t(), Timeline(), Tween() (+6 more)

### Community 19 - "package.json"
Cohesion: 0.12
Nodes (15): autoprefixer, cors, firebase, dependencies, cors, firebase, devDependencies, autoprefixer (+7 more)

### Community 20 - "test_password_visibility_duplication.py"
Cohesion: 0.18
Nodes (10): Verify auth.css suppresses Microsoft Edge & IE native password reveal/clear…, Test Confirm Password field focus, typing, blur, refocus, and toggling in…, Verify that Password and Confirm Password visibility toggles and clear buttons…, Verify that every password-input-wrapper in index.html contains exactly ONE…, Test interactive focus, typing, blur, refocus, and toggling in Chromium/Edge., test_css_suppresses_native_ms_reveal_and_clear(), test_dom_has_exactly_one_toggle_per_password_wrapper(), test_independent_visibility_toggles_and_clear() (+2 more)

### Community 21 - "test_screening_xai_refinement.py"
Cohesion: 0.10
Nodes (21): fixture, Verify #rec-drop-zone has centered content wrapper, icon badge, primary &…, Verify dropzone content group (icon, primary text, helper) is visually and…, Verify quick view modal displays consolidated overall score, skills overview,…, Verify dropzone CSS enforces centered group alignment, min-height, hover/drag…, Verify dropzone drag events, file input, and collapsed state transition., Verify recruiter.html quick view modal structure supports the refined…, renderXaiContent must NOT render summary/detailed toggle buttons (.xai-level-… (+13 more)

### Community 22 - "_d"
Cohesion: 0.25
Nodes (11): be(), _d(), ea(), fa(), ia(), ie(), je(), ke() (+3 more)

### Community 23 - "google_login"
Cohesion: 0.18
Nodes (21): create_access_token(), Generates a secure JSON Web Token., forgot_password(), get_me(), google_login(), login(), get, limit (+13 more)

### Community 24 - "yc"
Cohesion: 0.22
Nodes (11): Fa(), Ga(), mb(), oc(), qc(), rc(), Ta(), ub() (+3 more)

### Community 25 - "ja"
Cohesion: 0.38
Nodes (7): Aa(), Animation(), ha(), ja(), Ra(), Sa(), Sb()

### Community 26 - "jc"
Cohesion: 0.22
Nodes (9): Ab(), J(), jc(), kb(), lc(), Ra(), rb(), Sa() (+1 more)

### Community 27 - "landing.js"
Cohesion: 0.44
Nodes (9): initCounters(), initFeatureStack(), initHeroAnimation(), initNavbarEffects(), initStoryAnimation(), initWalkthrough(), initAllLandingAnimations(), initLandingMobileNav() (+1 more)

### Community 28 - "_resolve_status"
Cohesion: 0.17
Nodes (9): _resolve_status(), parametrize, Unit and boundary tests for candidate scoring status logic. Audits the existing…, Demonstrates the mathematical anomalies under current hardcoded thresholds: 1.…, Tests the status resolution function with exact boundaries., Reproduces the exact candidate scenario reported by the user: - Education: 60%…, TestCurrentThresholdDisparities, TestResolveStatusBoundaries (+1 more)

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
Nodes (34): get_profile(), get, Retrieves the full profile details of the authenticated user., read_root(), User, candidate_status(), delete_candidate_resume(), get_candidate_resume_details() (+26 more)

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

### Community 48 - "sidebar.js"
Cohesion: 0.47
Nodes (8): collapseSidebar(), expandSidebar(), handleKeyDown(), initSidebar(), isSidebarCollapsed(), setSidebarCollapsed(), sidebarLinkIds, toggleSidebar()

### Community 49 - "validate_skill_name"
Cohesion: 0.33
Nodes (9): Validates that a skill name contains reasonable characters and isn't empty,…, validate_skill_name(), test_validate_skill_name_empty_or_whitespace_only(), test_validate_skill_name_invalid_chars(), test_validate_skill_name_non_string(), test_validate_skill_name_too_long(), test_validate_skill_name_valid_common(), test_validate_skill_name_valid_special_chars() (+1 more)

### Community 63 - "test_profile_and_task_details_refinement.py"
Cohesion: 0.14
Nodes (17): Verify #btn-back-to-profile has compact secondary styling and does not stretch…, Verify Back to Profile button is compact, left-aligned, and does NOT stretch…, Verify screening task details loading state is centered horizontally and…, Verify profile layout has balanced proportions and history entries render…, Verify screening history empty state is clean, informative, and without…, Verify loading and error states use restrained editorial styling rather than…, Verify profile card padding and grid rules avoid excessive whitespace., Verify screening history section has content-driven layout and compact refresh… (+9 more)

### Community 66 - "get_screening_history"
Cohesion: 0.33
Nodes (6): get_scoring_profiles(), get_screening_history(), get, Returns all configured and seeded scoring profiles., Retrieves the screening history runs for the authenticated recruiter, ordered…, test_get_screening_history_ordered()

### Community 68 - "update_job_description"
Cohesion: 0.25
Nodes (8): put, Edits an existing job description in the recruiter's library. Accepts updated…, update_job_description(), Verify update_job_description correctly accepts 'name' instead of 'title'., test_update_job_description_success(), test_update_job_description_unauthorized(), test_update_job_description_validation(), test_update_job_description_with_name_parameter()

### Community 69 - "test_firebase_auth.py"
Cohesion: 0.07
Nodes (36): App, get_firebase_admin_app(), Any, Verifies a Firebase ID token using the Firebase Admin SDK. Extracts trusted…, Lazily initializes and returns the singleton Firebase Admin App. Supports: 1.…, verify_firebase_id_token(), Restricts route access to users registered with the CANDIDATE role in…, require_candidate() (+28 more)

### Community 71 - "get_screening_task_detail"
Cohesion: 0.33
Nodes (6): get_screening_task_detail(), Retrieves complete details for a specific screening task owned by the…, Verify get_screening_task_detail strips recommendations from candidate…, test_get_screening_task_detail_omits_candidate_recommendations(), test_get_screening_task_detail_owner_success(), test_get_screening_task_detail_unauthorized_or_missing()

### Community 72 - "test_candidate_xai_dashboard.py"
Cohesion: 0.07
Nodes (31): get_password_hash(), Hashes a plain text password using bcrypt., fetch_google_certs(), anyio_backend(), client(), db_session(), fixture, Create a new database session for a test. (+23 more)

### Community 74 - "backend/tests/test_recruiter.py"
Cohesion: 0.16
Nodes (17): create_job_description(), Adds a new job description to the recruiter's library or promotes an ad-hoc JD.…, Verify that JobDescription.name is an active synonym for JobDescription.title., Verify create_job_description correctly accepts 'name' instead of 'title'., Inspects live database schema to verify the table and name/title column…, Verify get_recruiter_stats returns empty top_recommended_improvements even if…, test_create_job_description_deduplication(), test_create_job_description_duplicate_names_distinct_records() (+9 more)

### Community 75 - "xai/builder.py"
Cohesion: 0.25
Nodes (13): build_score_components(), Any, Builds the structured ScoreComponent list using the candidate's scored…, generate_document_similarity_evidence(), generate_education_evidence(), generate_projects_evidence(), generate_skills_evidence(), Any (+5 more)

### Community 76 - "test_candidate_dashboard_refinement.py"
Cohesion: 0.07
Nodes (31): Verify that version progression is role-specific and does not conflate…, Verify expandable job description toggle button and collapsed/expanded state., Verify that latest version badge contains independent green dot and accessible…, Verify complete removal of artificial metrics like 'Comparison Reliability:…, Verify that Summary/Detailed toggle buttons and handler are completely removed., Verify removal of 'Grounded AI Insights (Gemini)' and 'Deterministic Matching…, Verify that both dashboard and timeline loading containers are compact and…, Verify smooth scrolling and absence of scroll locking in quick-view-body. (+23 more)

### Community 77 - "list_job_descriptions"
Cohesion: 0.40
Nodes (5): list_job_descriptions(), Retrieves all job descriptions created by the recruiter. Deduplicates identical…, Verify list_job_descriptions serializes both 'name' and 'title'., test_list_job_descriptions_deduplication(), test_list_job_descriptions_includes_name_and_title()

### Community 78 - "get_current_user"
Cohesion: 0.08
Nodes (24): Settings, get_current_user(), Session, Validates the incoming Firebase ID token using Firebase Admin SDK, extracts the…, Dispatches a secure password reset email to the specified recipient. Security…, send_password_reset_email(), Verifies that a user with an existing firebase_uid is resolved directly., Verifies that an existing dev user matching email is linked to the Firebase UID. (+16 more)

### Community 79 - "test_frontend_assets.py"
Cohesion: 0.05
Nodes (38): Verify frontend/firebase-config.js exists and is valid JavaScript exporting…, Verify recruiter.html contains the full quick view modal and candidate.html…, Verify candidate card renders quick view button with data attributes and…, Verify recruiter profile has horizontal side-by-side layout, pencil icon…, Verify recruiter screening history has a compact icon-only refresh button with…, Verify that frontend/firebase-config.js is not ignored by .gitignore., Verify recruiter pages hide candidate recommendations while candidate views…, Verify recruiter screening has explicit reset controls and state reset… (+30 more)

### Community 80 - "test_xai_and_dropzone_refinement.py"
Cohesion: 0.16
Nodes (13): Verify that backend XaiEngine suppresses per-skill supporting_evidence…, Verify Quick View modal displays consolidated Skills Overview and NO per-skill…, Verify dropzone and action button have matching widths and perfectly centered…, Verify that recruiter.js explicitly suppresses per-skill Supporting Evidence…, Verify that candidate.js also suppresses per-skill Supporting Evidence cards in…, Verify dropzones in recruiter and candidate have unified .drop-zone-content and…, setup_page_mock(), test_backend_xai_engine_suppresses_skills_supporting_evidence() (+5 more)

### Community 81 - "format_overall_explanation"
Cohesion: 0.31
Nodes (9): format_overall_explanation(), format_projects_explanation(), Returns (why_awarded, why_deducted) for Projects component., Returns (why_awarded, why_deducted) for Overall Score., test_format_overall_explanation_detailed(), test_format_overall_explanation_other(), test_format_overall_explanation_summary(), test_format_overall_explanation_technical() (+1 more)

### Community 83 - "router.js"
Cohesion: 0.25
Nodes (17): getProfile(), populateCandidateProfileUI(), populateRecruiterProfileUI(), updateSidebarActiveLink(), initializeCandidateDashboard(), initializeCandidateProfile(), initializeCandidateScreen(), initializeRecruiterDashboard() (+9 more)

### Community 84 - "generate_experience_evidence"
Cohesion: 0.31
Nodes (9): effective_exp_title(), generate_experience_evidence(), Generates Evidence for candidate professional experience., test_generate_experience_evidence_entry_level(), test_generate_experience_evidence_junior(), test_generate_experience_evidence_no_internships(), test_generate_experience_evidence_senior(), test_generate_experience_evidence_with_internships() (+1 more)

### Community 85 - "legacy_process_resumes"
Cohesion: 0.29
Nodes (7): legacy_process_resumes(), limit, post, Request, Session, UploadFile, Legacy endpoint delegating to recruiter process_resumes. Requires Recruiter…

### Community 87 - "Chapter: Semantic Matching Evaluation & Knowledge Base Verification"
Cohesion: 0.07
Nodes (26): 1. Executive Summary & Evaluation Scope, 2.1 Canonical Knowledge Base & Taxonomy Structure, 2.2 Relationship Categories & Deterministic Policy Weights, 2.3 Rule Precedence Cascade, 2.4 Multi-Skill Scoring Formula, 2. Methodology & Mathematical Formulation, 3.1 Total Evaluation Case Construction (Total $N = 317$), 3.2 Match Type Distribution (Experiment A) (+18 more)

### Community 88 - "test_candidate_patch_rejects_forbidden_fields"
Cohesion: 0.40
Nodes (5): parametrize, PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., test_candidate_patch_rejects_forbidden_fields(), test_recruiter_patch_rejects_forbidden_fields()

### Community 89 - "test_auth_modal_regression.py"
Cohesion: 0.12
Nodes (16): Verify app.js handles readyState interactive/complete so module execution never…, Verify router.js integrates with modal.js for auth routing., Verify index.html contains exactly one #auth-modal element., Verify #auth-modal has login and signup tabs and planes., Verify all key CTA buttons in index.html possess resilient data-auth-modal…, Verify modal.js exports explicit openAuthModal and closeAuthModal functions., Verify modal.js attaches event delegation on document to handle auth triggers…, Verify app.js actively calls initModals() during page initialization. (+8 more)

### Community 92 - "generate_grounded_xai_insights"
Cohesion: 0.20
Nodes (17): _build_deterministic_fallback(), _call_gemini_content(), generate_grounded_xai_insights(), Any, Makes HTTP request to Gemini API and parses JSON response., Safely extracts and parses JSON even if wrapped in markdown code fences or…, Constructs a deterministic, grounded rule-based summary when Gemini is…, Invokes the Google Gemini API to generate grounded, explainable AI insights for… (+9 more)

### Community 93 - "v"
Cohesion: 0.33
Nodes (6): _a(), ac(), db(), eb(), ta(), v()

### Community 94 - "ka"
Cohesion: 0.50
Nodes (4): ka(), tb(), xa(), za()

### Community 95 - "xe"
Cohesion: 0.50
Nodes (4): Ud(), vd(), we(), xe()

### Community 100 - "state.js"
Cohesion: 0.16
Nodes (14): getStepsForRole(), hideObError(), initializeOnboardingPage, initOnboarding(), showObError(), showOnboardingWizard(), submitOnboarding(), updateOnboardingUI() (+6 more)

### Community 101 - "process_resumes"
Cohesion: 0.20
Nodes (10): process_resumes(), limit, post, Request, UploadFile, Screens uploaded resume files against a job description. Enforces…, test_process_resumes_rejects_invalid_custom_scoring(), anyio (+2 more)

### Community 105 - "test_remediation.py"
Cohesion: 0.08
Nodes (30): extract_text(), extract_text_from_docx(), extract_text_from_pdf(), Extract text from a DOCX file, including paragraphs and tables., Route to appropriate extractor based on extension., Extract text from a PDF file., build_analysis_metadata(), Any (+22 more)

### Community 125 - "K"
Cohesion: 0.40
Nodes (5): A(), B(), F(), G(), K()

### Community 134 - "Session"
Cohesion: 0.29
Nodes (8): archive_job_description(), delete_job_description(), delete, Session, Soft-deletes (archives) a job description., Permanently deletes a job description and its scan results., test_archive_job_description_success(), test_archive_job_description_unauthorized()

### Community 137 - "test_confirm_password.py"
Cohesion: 0.13
Nodes (14): Verify index.html contains #signup-confirm-group and #signup-confirm-password…, Verify that when opened via file:// protocol (CORS-isolated, zero-module), the…, Confirm Password field must NOT appear in Login, Forgot Password, or unrelated…, Verify signup.js exports validatePasswordMatch and gates Firebase registration., Confirm password value must never be sent to API, state, or storage., Verify auth.css defines .confirm-password-group, .is-visible, and feedback…, Verify full interactive lifecycle: reveal, clear, match, mismatch, tab…, test_auth_css_defines_smooth_transitions_and_semantic_feedback() (+6 more)

## Knowledge Gaps
- **52 isolated node(s):** `inflightGetRequests`, `uploadedFiles`, `sidebarLinkIds`, `COMPANY_TYPES`, `CANDIDATE_STATUS_VALUES` (+47 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `stages.py`, `test_custom_scoring.py`, `get_screening_history`, `update_job_description`, `test_firebase_auth.py`, `Session`, `get_screening_task_detail`, `recruiter.py`, `process_resumes`, `backend/tests/test_recruiter.py`, `UserRole`, `test_candidate_xai_dashboard.py`, `list_job_descriptions`, `get_current_user`, `test_password_reset.py`, `legacy_process_resumes`, `google_login`, `test_profile_editing.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `build_score_components()` connect `xai/builder.py` to `stages.py`, `engine.py`, `_resolve_status`, `generate_experience_evidence`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `s()` connect `recruiter.js` to `bf`, `gsap.min.js`, `r`, `Tween`, `v`, `_d`, `cb`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `CompanyType` and `ResumeStatus`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `UserRole` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`UserRole` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `CompanyType` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`CompanyType` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AnalysisContext` (e.g. with `AnalysisPipeline` and `ExplanationBuildingStage`) actually correct?**
  _`AnalysisContext` has 11 INFERRED edges - model-reasoned connections that need verification._