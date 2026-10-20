# Graph Report - nipun-platform  (2026-10-16)

## Corpus Check
- 150 files · ~161,834 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1484 nodes · 3119 edges · 94 communities (86 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 313 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ad5cbf08`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- stages.py
- test_custom_scoring.py
- xai/builder.py
- Skill
- app.js
- state.js
- UpdateRecommendationPayload
- gsap.min.js
- Core Principles
- extract_education
- ScrollTrigger.min.js
- test_password_reset.py
- router.js
- api.js
- UserRole
- candidate.js
- r
- recruiter.js
- Tween
- package.json
- Session
- update_job_description
- _d
- Documentation Architect
- yc
- ja
- jc
- landing.js
- get_screening_history
- cb
- test_profile_editing.py
- Oa
- s
- skill_expander.py
- User
- Landing Index HTML
- Nipun AI Resume Screener & Ranking System — High-Level Architecture
- loadingOverlay.js
- Q
- r
- google_login
- validate_skill_name
- zd
- firebase-config.example.js
- Graphify Agent Rule
- Graphify Workflow Guide
- AI Resume Screener Overview
- Capabilities
- Python Dependencies
- backend/tests/test_recruiter.py
- test_firebase_auth.py
- seed_default_profiles
- Core Principles
- Capabilities
- test_remediation.py
- process_resumes
- API Design Principles Implementation Playbook
- Core Principles
- API Design Principles
- test_frontend_assets.py
- xe
- routers/test_auth.py
- RecruiterProfileUpdate
- legacy_process_resumes
- firebaseConfig
- test_candidate_patch_rejects_forbidden_fields
- get_screening_task_detail
- navbar.js
- list_job_descriptions
- test_candidate_resume_details_preserves_recommendations
- generate_grounded_xai_insights
- test_candidate_xai_dashboard.py

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
- `JobDescription` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `PasswordResetToken` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `RecruiterProfile` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `Resume` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py

## Import Cycles
- 3-file cycle: `frontend/assets/js/auth.js -> frontend/assets/js/router.js -> frontend/assets/js/pages/login.js -> frontend/assets/js/auth.js`

## Communities (94 total, 8 thin omitted)

### Community 0 - "stages.py"
Cohesion: 0.07
Nodes (71): ResumeStatus, Resume, ScanResult, ScoringProfile, preprocess_text(), Cleans text by: - Lowercasing - Removing punctuation - Removing stopwords -…, AnalysisContext, Any (+63 more)

### Community 1 - "test_custom_scoring.py"
Cohesion: 0.05
Nodes (58): Defines thresholds and priorities for AI Resume Improvement Engine…, RecommendationPolicy, Defines recruiter-specific configurations and security permissions., RecruiterPolicy, Defines policy configurations for ATS scoring and weights. Removes magic…, ScoringPolicy, Any, Validates, sanitizes, and normalizes optional recruiter custom scoring… (+50 more)

### Community 2 - "xai/builder.py"
Cohesion: 0.07
Nodes (48): build_score_components(), Any, Builds the structured ScoreComponent list using the candidate's scored…, _resolve_status(), Any, Helper to construct a dict representation of StructuredExplanations., Generates structured multi-level explanations (SUMMARY, DETAILED, TECHNICAL)…, effective_exp_title() (+40 more)

### Community 3 - "Skill"
Cohesion: 0.07
Nodes (31): get_weight(), Returns the matching weight for the given match type., MatchReason, MatchResult, BaseModel, Universal domain object representing a semantic match between a required skill…, Evaluates relationship type, confidence, and matches between two Skill objects.…, resolve_relationship() (+23 more)

### Community 4 - "app.js"
Cohesion: 0.14
Nodes (25): clearCandidateState(), handleFiles(), renderFileList(), renderResults(), updateResumeCountDisplay(), uploadedFiles, getCandidateDetailRowHTML(), getCandidateRowHTML() (+17 more)

### Community 5 - "state.js"
Cohesion: 0.13
Nodes (23): checkAuthStatus(), _doCheckAuthStatus(), hideEmailVerificationModal(), initAuthListener(), showEmailVerificationModal(), waitForAuthState(), getStepsForRole(), hideObError() (+15 more)

### Community 6 - "UpdateRecommendationPayload"
Cohesion: 0.10
Nodes (23): candidate_status(), delete_candidate_resume(), get_candidate_resume_details(), process_candidate_resume(), BaseModel, delete, get, patch (+15 more)

### Community 7 - "gsap.min.js"
Cohesion: 0.07
Nodes (10): ee(), Jd(), Kd(), Ld(), ma(), Md(), na(), Od() (+2 more)

### Community 8 - "Core Principles"
Cohesion: 0.06
Nodes (33): 10. Content and microcopy, 11. Feedback and error recovery, 12. Data-heavy interfaces, 13. Animation and interaction, 1. Understand, 1. Understand the user and the task, 2. Prioritize usability, 2. Structure (+25 more)

### Community 9 - "extract_education"
Cohesion: 0.08
Nodes (40): extract_education(), extract_email(), extract_experience(), extract_github(), extract_linkedin(), extract_name(), extract_phone(), extract_projects() (+32 more)

### Community 10 - "ScrollTrigger.min.js"
Cohesion: 0.07
Nodes (4): dc(), Ha(), Ia(), ob()

### Community 11 - "test_password_reset.py"
Cohesion: 0.08
Nodes (28): Verifies a plain text password against the hashed version using bcrypt., verify_password(), PasswordResetToken, disable_rate_limiting(), existing_user(), fixture, Test resetting password with a valid token., Temporarily disables SlowAPI rate limiting for unit tests. (+20 more)

### Community 12 - "router.js"
Cohesion: 0.25
Nodes (18): getProfile(), populateRecruiterProfileUI(), updateSidebarActiveLink(), initializeCandidateDashboard(), initializeCandidateProfile(), initializeCandidateScreen(), initializeRecruiterDashboard(), initializeRecruiterHistoryDetail() (+10 more)

### Community 13 - "api.js"
Cohesion: 0.12
Nodes (33): archiveJob(), createJob(), deleteCandidateResume(), deleteJob(), _executeRequest(), forgotPassword(), getCandidateResumeDetails(), getCandidateResumes() (+25 more)

### Community 14 - "UserRole"
Cohesion: 0.24
Nodes (30): CompanyType, UserRole, GoogleLoginRequest, BaseModel, CandidateProfileResponse, CandidateProfileUpdate, Config, ForgotPasswordRequest (+22 more)

### Community 15 - "candidate.js"
Cohesion: 0.19
Nodes (12): getEmptyStateHTML(), populateCandidateProfileUI(), closeCandidateAnalysisModal(), initCandidatePage(), renderCandidateAnalysisResults(), renderFileList(), renderRecommendations(), renderTimelineList() (+4 more)

### Community 16 - "r"
Cohesion: 0.12
Nodes (20): _a(), ac(), Bo(), db(), eb(), ga(), gb(), hb() (+12 more)

### Community 17 - "recruiter.js"
Cohesion: 0.15
Nodes (26): toggleButtonLoading(), updateStatisticCard(), applyJdSelection(), autoBalanceActiveWeights(), getCustomScoringPayload(), getSelectedProfileWeights(), hasUnsavedJdChanges(), initAdvancedScoringControls() (+18 more)

### Community 18 - "Tween"
Cohesion: 0.15
Nodes (17): _assertThisInitialized(), Ec(), Fc(), gc(), ka(), qa(), t(), tb() (+9 more)

### Community 19 - "package.json"
Cohesion: 0.12
Nodes (15): autoprefixer, cors, firebase, dependencies, cors, firebase, devDependencies, autoprefixer (+7 more)

### Community 20 - "Session"
Cohesion: 0.29
Nodes (8): archive_job_description(), delete_job_description(), delete, Session, Soft-deletes (archives) a job description., Permanently deletes a job description and its scan results., test_archive_job_description_success(), test_archive_job_description_unauthorized()

### Community 21 - "update_job_description"
Cohesion: 0.25
Nodes (8): put, Edits an existing job description in the recruiter's library. Accepts updated…, update_job_description(), Verify update_job_description correctly accepts 'name' instead of 'title'., test_update_job_description_success(), test_update_job_description_unauthorized(), test_update_job_description_validation(), test_update_job_description_with_name_parameter()

### Community 22 - "_d"
Cohesion: 0.25
Nodes (11): be(), _d(), ea(), fa(), ia(), ie(), je(), ke() (+3 more)

### Community 23 - "Documentation Architect"
Cohesion: 0.06
Nodes (32): 1. Documentation must reflect reality, 2. Optimize for usefulness, not length, 3. Start with the audience and purpose, 4. Use progressive disclosure, 5. Explain important "why", Architecture, Architecture Documentation, Code References (+24 more)

### Community 24 - "yc"
Cohesion: 0.15
Nodes (16): A(), B(), F(), Fa(), G(), Ga(), K(), mb() (+8 more)

### Community 25 - "ja"
Cohesion: 0.28
Nodes (9): Aa(), Animation(), ha(), ja(), Jc(), Lc(), Ra(), Sa() (+1 more)

### Community 26 - "jc"
Cohesion: 0.22
Nodes (9): Ab(), J(), jc(), kb(), lc(), Ra(), rb(), Sa() (+1 more)

### Community 27 - "landing.js"
Cohesion: 0.53
Nodes (7): initCounters(), initFeatureStack(), initHeroAnimation(), initNavbarEffects(), initStoryAnimation(), initWalkthrough(), initAllLandingAnimations()

### Community 28 - "get_screening_history"
Cohesion: 0.33
Nodes (6): get_scoring_profiles(), get_screening_history(), get, Returns all configured and seeded scoring profiles., Retrieves the screening history runs for the authenticated recruiter, ordered…, test_get_screening_history_ordered()

### Community 29 - "cb"
Cohesion: 0.29
Nodes (7): Ab(), Bb(), cb(), Context(), Ew(), fb(), zb()

### Community 30 - "test_profile_editing.py"
Cohesion: 0.05
Nodes (40): RecruiterProfile, candidate_user(), disable_rate_limiting(), fixture, Temporarily disables SlowAPI rate limiting for unit tests., Candidate partial update changes only provided field, preserving others., Recruiter can update display_name., Recruiter can update company_name, company_type, and hiring_domain. (+32 more)

### Community 31 - "Oa"
Cohesion: 0.53
Nodes (6): Bb(), Ja(), Ka(), La(), Oa(), z()

### Community 32 - "s"
Cohesion: 0.24
Nodes (11): s(), bf(), cf(), df(), ef(), kf(), lf(), M() (+3 more)

### Community 33 - "skill_expander.py"
Cohesion: 0.40
Nodes (4): get_related_skills(), is_skill_in_text(), Checks if an explicit skill contains a broad conceptual keyword. For example,…, Checks if a skill or any of its known aliases exists in the given text. Handles…

### Community 34 - "User"
Cohesion: 0.08
Nodes (40): Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online(), api_route, check_db_connection(), get_db(), Tests connection to the configured database on demand (e.g. startup or health… (+32 more)

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
Cohesion: 0.40
Nodes (5): mc(), O(), P(), r(), wb()

### Community 48 - "google_login"
Cohesion: 0.13
Nodes (24): Settings, create_access_token(), Generates a secure JSON Web Token., forgot_password(), get_me(), google_login(), login(), get (+16 more)

### Community 49 - "validate_skill_name"
Cohesion: 0.33
Nodes (9): Validates that a skill name contains reasonable characters and isn't empty,…, validate_skill_name(), test_validate_skill_name_empty_or_whitespace_only(), test_validate_skill_name_invalid_chars(), test_validate_skill_name_non_string(), test_validate_skill_name_too_long(), test_validate_skill_name_valid_common(), test_validate_skill_name_valid_special_chars() (+1 more)

### Community 63 - "Capabilities"
Cohesion: 0.06
Nodes (31): API Contract & Documentation, API Design & Patterns, API Gateway & Load Balancing, Asynchronous Processing, Authentication & Authorization, Backend Architect, Behavioral Traits, Caching Strategies (+23 more)

### Community 66 - "backend/tests/test_recruiter.py"
Cohesion: 0.16
Nodes (17): create_job_description(), Adds a new job description to the recruiter's library or promotes an ad-hoc JD.…, Verify that JobDescription.name is an active synonym for JobDescription.title., Verify create_job_description correctly accepts 'name' instead of 'title'., Inspects live database schema to verify the table and name/title column…, Verify get_recruiter_stats returns empty top_recommended_improvements even if…, test_create_job_description_deduplication(), test_create_job_description_duplicate_names_distinct_records() (+9 more)

### Community 68 - "test_firebase_auth.py"
Cohesion: 0.06
Nodes (45): App, get_firebase_admin_app(), Any, Verifies a Firebase ID token using the Firebase Admin SDK. Extracts trusted…, Lazily initializes and returns the singleton Firebase Admin App. Supports: 1.…, verify_firebase_id_token(), get_current_user(), Session (+37 more)

### Community 69 - "seed_default_profiles"
Cohesion: 0.29
Nodes (6): Startup event handler: verify database connectivity and seed default profiles., startup_event(), Session, Checks if scoring profiles exist in the database; if not, seeds missing default…, seed_default_profiles(), on_event

### Community 71 - "Core Principles"
Cohesion: 0.08
Nodes (24): 1. Start with requirements, 2. Prefer simplicity, 3. Evaluate technology choices rationally, 4. Design for data integrity, 5. Design schemas around actual access patterns, 6. Treat migrations as production changes, 7. Scale only when justified, 8. Consider the whole system (+16 more)

### Community 72 - "Capabilities"
Cohesion: 0.09
Nodes (22): Application Security Testing, Behavioral Traits, Capabilities, Cloud Security, Compliance & Governance, DevSecOps & Security Automation, Do not use this skill when, Emerging Security Technologies (+14 more)

### Community 74 - "test_remediation.py"
Cohesion: 0.08
Nodes (30): extract_text(), extract_text_from_docx(), extract_text_from_pdf(), Extract text from a DOCX file, including paragraphs and tables., Route to appropriate extractor based on extension., Extract text from a PDF file., build_analysis_metadata(), Any (+22 more)

### Community 75 - "process_resumes"
Cohesion: 0.20
Nodes (10): process_resumes(), limit, post, Request, UploadFile, Screens uploaded resume files against a job description. Enforces…, test_process_resumes_rejects_invalid_custom_scoring(), anyio (+2 more)

### Community 76 - "API Design Principles Implementation Playbook"
Cohesion: 0.10
Nodes (19): 1. RESTful Design Principles, 2. GraphQL Design Principles, 3. API Versioning Strategies, API Design Principles Implementation Playbook, Best Practices, Common Pitfalls, Core Concepts, GraphQL APIs (+11 more)

### Community 77 - "Core Principles"
Cohesion: 0.10
Nodes (19): 10. Testing, 11. SEO, 1. Follow the existing project architecture, 2. Build for correctness first, 3. Component design, 4. State and data fetching, 5. Responsive design, 6. Accessibility (+11 more)

### Community 78 - "API Design Principles"
Cohesion: 0.25
Nodes (7): API Design Principles, Description:, Do not use this skill when, Instructions, Name: api-design-principles, Resources, Use this skill when

### Community 79 - "test_frontend_assets.py"
Cohesion: 0.05
Nodes (38): Verify frontend/firebase-config.js exists and is valid JavaScript exporting…, Verify recruiter.html contains the full quick view modal and candidate.html…, Verify candidate card renders quick view button with data attributes and…, Verify recruiter profile has horizontal side-by-side layout, pencil icon…, Verify recruiter screening history has a compact icon-only refresh button with…, Verify that frontend/firebase-config.js is not ignored by .gitignore., Verify recruiter pages hide candidate recommendations while candidate views…, Verify recruiter screening has explicit reset controls and state reset… (+30 more)

### Community 81 - "xe"
Cohesion: 0.50
Nodes (4): Ud(), vd(), we(), xe()

### Community 83 - "routers/test_auth.py"
Cohesion: 0.24
Nodes (7): fetch_google_certs(), test_fetch_google_certs_error(), test_fetch_google_certs_success(), test_fetch_google_certs_timeout(), Verifies that after screening, stats and history return fresh authoritative…, test_candidate_dashboard_stats_and_history_lifecycle(), Exception

### Community 84 - "RecruiterProfileUpdate"
Cohesion: 0.29
Nodes (5): patch, Update recruiter's profile information and display name. Strictly scoped to…, update_recruiter_profile(), RecruiterProfileUpdate, field_validator

### Community 85 - "legacy_process_resumes"
Cohesion: 0.29
Nodes (7): legacy_process_resumes(), limit, post, Request, Session, UploadFile, Legacy endpoint delegating to recruiter process_resumes. Requires Recruiter…

### Community 87 - "test_candidate_patch_rejects_forbidden_fields"
Cohesion: 0.40
Nodes (5): PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., test_candidate_patch_rejects_forbidden_fields(), test_recruiter_patch_rejects_forbidden_fields(), parametrize

### Community 88 - "get_screening_task_detail"
Cohesion: 0.33
Nodes (6): get_screening_task_detail(), Retrieves complete details for a specific screening task owned by the…, Verify get_screening_task_detail strips recommendations from candidate…, test_get_screening_task_detail_omits_candidate_recommendations(), test_get_screening_task_detail_owner_success(), test_get_screening_task_detail_unauthorized_or_missing()

### Community 89 - "navbar.js"
Cohesion: 0.17
Nodes (17): handleLogoNavigation(), handleLogout(), initNavbar(), initSidebar(), isSidebarCollapsed(), setSidebarCollapsed(), sidebarLinkIds, toggleSidebar() (+9 more)

### Community 90 - "list_job_descriptions"
Cohesion: 0.40
Nodes (5): list_job_descriptions(), Retrieves all job descriptions created by the recruiter. Deduplicates identical…, Verify list_job_descriptions serializes both 'name' and 'title'., test_list_job_descriptions_deduplication(), test_list_job_descriptions_includes_name_and_title()

### Community 92 - "generate_grounded_xai_insights"
Cohesion: 0.20
Nodes (17): _build_deterministic_fallback(), _call_gemini_content(), generate_grounded_xai_insights(), Any, Makes HTTP request to Gemini API and parses JSON response., Safely extracts and parses JSON even if wrapped in markdown code fences or…, Constructs a deterministic, grounded rule-based summary when Gemini is…, Invokes the Google Gemini API to generate grounded, explainable AI insights for… (+9 more)

### Community 93 - "test_candidate_xai_dashboard.py"
Cohesion: 0.11
Nodes (21): get_password_hash(), Hashes a plain text password using bcrypt., CandidateProfile, post, Session, Creates a user profile based on the role and marks onboarding as completed., submit_onboarding(), candidate_a() (+13 more)

## Knowledge Gaps
- **196 isolated node(s):** `Settings`, `inflightGetRequests`, `uploadedFiles`, `sidebarLinkIds`, `COMPANY_TYPES` (+191 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `stages.py`, `test_custom_scoring.py`, `UpdateRecommendationPayload`, `test_password_reset.py`, `UserRole`, `Session`, `update_job_description`, `get_screening_history`, `test_profile_editing.py`, `google_login`, `backend/tests/test_recruiter.py`, `test_firebase_auth.py`, `process_resumes`, `routers/test_auth.py`, `RecruiterProfileUpdate`, `legacy_process_resumes`, `get_screening_task_detail`, `list_job_descriptions`, `test_candidate_xai_dashboard.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `s()` connect `s` to `app.js`, `gsap.min.js`, `r`, `Tween`, `_d`, `cb`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `XaiEngine` connect `stages.py` to `xai/builder.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `CompanyType` and `ResumeStatus`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `UserRole` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`UserRole` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `CompanyType` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`CompanyType` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AnalysisContext` (e.g. with `AnalysisPipeline` and `ExplanationBuildingStage`) actually correct?**
  _`AnalysisContext` has 11 INFERRED edges - model-reasoned connections that need verification._