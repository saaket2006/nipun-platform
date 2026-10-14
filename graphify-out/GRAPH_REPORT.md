# Graph Report - nipun-platform  (2026-10-14)

## Corpus Check
- 147 files · ~155,523 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1431 nodes · 3014 edges · 91 communities (83 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 312 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `06bf40b9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- stages.py
- test_custom_scoring.py
- xai/builder.py
- Skill
- test_remediation.py
- state.js
- UpdateRecommendationPayload
- gsap.min.js
- Core Principles
- extract_education
- ScrollTrigger.min.js
- test_password_reset.py
- login.js
- api.js
- UserRole
- router.js
- s
- recruiter.js
- Tween
- package.json
- archive_job_description
- update_job_description
- _d
- Documentation Architect
- yc
- ja
- jc
- landing.js
- Session
- cb
- models/models.py
- Oa
- bf
- skill_expander.py
- app.js
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
- Capabilities
- Python Dependencies
- backend/tests/test_recruiter.py
- User
- seed_default_profiles
- Core Principles
- Capabilities
- get_recruiter_stats
- process_resumes
- API Design Principles Implementation Playbook
- Core Principles
- API Design Principles
- test_frontend_assets.py
- K
- firebaseConfig
- legacy_process_resumes
- get_password_hash
- test_candidate_patch_rejects_forbidden_fields
- get_screening_task_detail
- constants.js
- test_live_schema_verification_job_descriptions
- test_candidate_resume_details_preserves_recommendations

## God Nodes (most connected - your core abstractions)
1. `User` - 64 edges
2. `UserRole` - 46 edges
3. `CompanyType` - 38 edges
4. `AnalysisContext` - 33 edges
5. `PipelineStage` - 33 edges
6. `request()` - 31 edges
7. `PersistenceStage` - 28 edges
8. `ResumeStatus` - 26 edges
9. `AnalysisPipeline` - 26 edges
10. `ScoringProfileResolutionStage` - 26 edges

## Surprising Connections (you probably didn't know these)
- `test_get_recruiter_stats_empty_scans()` --calls--> `User`  [EXTRACTED]
  tests/test_recruiter.py → backend/models/models.py
- `CandidateProfile` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `JobDescription` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `PasswordResetToken` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `RecruiterProfile` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py

## Import Cycles
- 3-file cycle: `frontend/assets/js/auth.js -> frontend/assets/js/router.js -> frontend/assets/js/pages/login.js -> frontend/assets/js/auth.js`

## Communities (91 total, 8 thin omitted)

### Community 0 - "stages.py"
Cohesion: 0.09
Nodes (62): ResumeStatus, Resume, ScanResult, ScoringProfile, AnalysisContext, Any, Lightweight, shared context carrying tracing IDs, configurations, and stage…, ExplanationBuiltEvent (+54 more)

### Community 1 - "test_custom_scoring.py"
Cohesion: 0.05
Nodes (58): Defines thresholds and priorities for AI Resume Improvement Engine…, RecommendationPolicy, Defines recruiter-specific configurations and security permissions., RecruiterPolicy, Defines policy configurations for ATS scoring and weights. Removes magic…, ScoringPolicy, Any, Validates, sanitizes, and normalizes optional recruiter custom scoring… (+50 more)

### Community 2 - "xai/builder.py"
Cohesion: 0.07
Nodes (48): build_score_components(), Any, Builds the structured ScoreComponent list using the candidate's scored…, _resolve_status(), Any, Helper to construct a dict representation of StructuredExplanations., Generates structured multi-level explanations (SUMMARY, DETAILED, TECHNICAL)…, effective_exp_title() (+40 more)

### Community 3 - "Skill"
Cohesion: 0.08
Nodes (27): get_weight(), Returns the matching weight for the given match type., MatchReason, MatchResult, BaseModel, Universal domain object representing a semantic match between a required skill…, Evaluates relationship type, confidence, and matches between two Skill objects.…, resolve_relationship() (+19 more)

### Community 4 - "test_remediation.py"
Cohesion: 0.06
Nodes (43): extract_text(), extract_text_from_docx(), extract_text_from_pdf(), Extract text from a DOCX file, including paragraphs and tables., Route to appropriate extractor based on extension., Extract text from a PDF file., build_analysis_metadata(), Any (+35 more)

### Community 5 - "state.js"
Cohesion: 0.17
Nodes (16): getStepsForRole(), hideObError(), initializeOnboardingPage, initOnboarding(), showObError(), showOnboardingWizard(), submitOnboarding(), updateOnboardingUI() (+8 more)

### Community 6 - "UpdateRecommendationPayload"
Cohesion: 0.09
Nodes (27): candidate_status(), delete_candidate_resume(), get_candidate_resume_details(), get_candidate_resumes(), get_candidate_stats(), process_candidate_resume(), BaseModel, delete (+19 more)

### Community 7 - "gsap.min.js"
Cohesion: 0.06
Nodes (16): ee(), Jd(), Kd(), Ld(), ma(), Md(), na(), Od() (+8 more)

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

### Community 12 - "login.js"
Cohesion: 0.19
Nodes (21): checkAuthStatus(), _doCheckAuthStatus(), hideEmailVerificationModal(), initAuthListener(), showEmailVerificationModal(), waitForAuthState(), app, auth (+13 more)

### Community 13 - "api.js"
Cohesion: 0.11
Nodes (34): archiveJob(), createJob(), deleteCandidateResume(), deleteJob(), _executeRequest(), forgotPassword(), getCandidateResumeDetails(), getCandidateResumes() (+26 more)

### Community 14 - "UserRole"
Cohesion: 0.17
Nodes (34): CompanyType, UserRole, ScreeningTask, GoogleLoginRequest, BaseModel, patch, Update recruiter's profile information and display name. Strictly scoped to…, update_recruiter_profile() (+26 more)

### Community 15 - "router.js"
Cohesion: 0.12
Nodes (28): getEmptyStateHTML(), populateCandidateProfileUI(), populateRecruiterProfileUI(), sidebarLinkIds, updateSidebarActiveLink(), initCandidatePage(), initializeCandidateDashboard(), initializeCandidateProfile() (+20 more)

### Community 16 - "s"
Cohesion: 0.15
Nodes (20): _a(), ac(), Bo(), db(), ea(), eb(), ga(), gb() (+12 more)

### Community 17 - "recruiter.js"
Cohesion: 0.15
Nodes (26): toggleButtonLoading(), updateStatisticCard(), applyJdSelection(), autoBalanceActiveWeights(), getCustomScoringPayload(), getSelectedProfileWeights(), hasUnsavedJdChanges(), initAdvancedScoringControls() (+18 more)

### Community 18 - "Tween"
Cohesion: 0.15
Nodes (18): _assertThisInitialized(), Ec(), Fc(), gc(), ka(), qa(), t(), tb() (+10 more)

### Community 19 - "package.json"
Cohesion: 0.12
Nodes (15): autoprefixer, cors, firebase, dependencies, cors, firebase, devDependencies, autoprefixer (+7 more)

### Community 20 - "archive_job_description"
Cohesion: 0.29
Nodes (7): archive_job_description(), delete_job_description(), delete, Soft-deletes (archives) a job description., Permanently deletes a job description and its scan results., test_archive_job_description_success(), test_archive_job_description_unauthorized()

### Community 21 - "update_job_description"
Cohesion: 0.25
Nodes (8): put, Edits an existing job description in the recruiter's library. Accepts updated…, update_job_description(), Verify update_job_description correctly accepts 'name' instead of 'title'., test_update_job_description_success(), test_update_job_description_unauthorized(), test_update_job_description_validation(), test_update_job_description_with_name_parameter()

### Community 22 - "_d"
Cohesion: 0.29
Nodes (10): be(), _d(), fa(), ia(), ie(), je(), ke(), le() (+2 more)

### Community 23 - "Documentation Architect"
Cohesion: 0.06
Nodes (32): 1. Documentation must reflect reality, 2. Optimize for usefulness, not length, 3. Start with the audience and purpose, 4. Use progressive disclosure, 5. Explain important "why", Architecture, Architecture Documentation, Code References (+24 more)

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
Cohesion: 0.53
Nodes (7): initCounters(), initFeatureStack(), initHeroAnimation(), initNavbarEffects(), initStoryAnimation(), initWalkthrough(), initAllLandingAnimations()

### Community 28 - "Session"
Cohesion: 0.20
Nodes (12): get_scoring_profiles(), get_screening_history(), list_job_descriptions(), get, Session, Returns all configured and seeded scoring profiles., Retrieves all job descriptions created by the recruiter. Deduplicates identical…, Retrieves the screening history runs for the authenticated recruiter, ordered… (+4 more)

### Community 29 - "cb"
Cohesion: 0.29
Nodes (7): Ab(), Bb(), cb(), Context(), Ew(), fb(), zb()

### Community 30 - "models/models.py"
Cohesion: 0.04
Nodes (53): Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online(), CandidateProfile, RecruiterProfile, get_onboarding_status(), get (+45 more)

### Community 31 - "Oa"
Cohesion: 0.53
Nodes (6): Bb(), Ja(), Ka(), La(), Oa(), z()

### Community 32 - "bf"
Cohesion: 0.22
Nodes (10): bf(), cf(), df(), ef(), kf(), lf(), M(), mf() (+2 more)

### Community 33 - "skill_expander.py"
Cohesion: 0.40
Nodes (4): get_related_skills(), is_skill_in_text(), Checks if an explicit skill contains a broad conceptual keyword. For example,…, Checks if a skill or any of its known aliases exists in the given text. Handles…

### Community 34 - "app.js"
Cohesion: 0.25
Nodes (12): clearCandidateState(), handleFiles(), renderFileList(), renderResults(), updateResumeCountDisplay(), uploadedFiles, getCandidateDetailRowHTML(), getCandidateRowHTML() (+4 more)

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
Cohesion: 0.17
Nodes (23): create_access_token(), Generates a secure JSON Web Token., forgot_password(), get_me(), google_login(), login(), get, limit (+15 more)

### Community 49 - "validate_skill_name"
Cohesion: 0.33
Nodes (9): Validates that a skill name contains reasonable characters and isn't empty,…, validate_skill_name(), test_validate_skill_name_empty_or_whitespace_only(), test_validate_skill_name_invalid_chars(), test_validate_skill_name_non_string(), test_validate_skill_name_too_long(), test_validate_skill_name_valid_common(), test_validate_skill_name_valid_special_chars() (+1 more)

### Community 63 - "Capabilities"
Cohesion: 0.06
Nodes (31): API Contract & Documentation, API Design & Patterns, API Gateway & Load Balancing, Asynchronous Processing, Authentication & Authorization, Backend Architect, Behavioral Traits, Caching Strategies (+23 more)

### Community 66 - "backend/tests/test_recruiter.py"
Cohesion: 0.18
Nodes (17): JobDescription, create_job_description(), Adds a new job description to the recruiter's library or promotes an ad-hoc JD.…, Verify that JobDescription.name is an active synonym for JobDescription.title., Verify that JobDescriptionResponse correctly maps both title and name from an…, Verify create_job_description correctly accepts 'name' instead of 'title'., test_create_job_description_deduplication(), test_create_job_description_duplicate_names_distinct_records() (+9 more)

### Community 68 - "User"
Cohesion: 0.05
Nodes (60): api_route, App, Settings, get_firebase_admin_app(), Any, Verifies a Firebase ID token using the Firebase Admin SDK. Extracts trusted…, Lazily initializes and returns the singleton Firebase Admin App. Supports: 1.…, verify_firebase_id_token() (+52 more)

### Community 69 - "seed_default_profiles"
Cohesion: 0.29
Nodes (6): Startup event handler: verify database connectivity and seed default profiles., startup_event(), Session, Checks if scoring profiles exist in the database; if not, seeds missing default…, seed_default_profiles(), on_event

### Community 71 - "Core Principles"
Cohesion: 0.08
Nodes (24): 1. Start with requirements, 2. Prefer simplicity, 3. Evaluate technology choices rationally, 4. Design for data integrity, 5. Design schemas around actual access patterns, 6. Treat migrations as production changes, 7. Scale only when justified, 8. Consider the whole system (+16 more)

### Community 72 - "Capabilities"
Cohesion: 0.09
Nodes (22): Application Security Testing, Behavioral Traits, Capabilities, Cloud Security, Compliance & Governance, DevSecOps & Security Automation, Do not use this skill when, Emerging Security Technologies (+14 more)

### Community 74 - "get_recruiter_stats"
Cohesion: 0.67
Nodes (3): get_recruiter_stats(), Retrieves dashboard statistics and aggregates recruiter intelligence statistics., test_get_recruiter_stats_empty_scans()

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
Cohesion: 0.07
Nodes (26): Verify frontend/firebase-config.js exists and is valid JavaScript exporting…, Verify recruiter.html contains the full quick view modal and candidate.html…, Verify candidate card renders quick view button with data attributes and…, Verify recruiter profile has horizontal side-by-side layout, pencil icon…, Verify recruiter screening history has a compact icon-only refresh button with…, Verify that frontend/firebase-config.js is not ignored by .gitignore., Verify recruiter pages hide candidate recommendations while candidate views…, Verify recruiter screening has explicit reset controls and state reset… (+18 more)

### Community 81 - "K"
Cohesion: 0.40
Nodes (5): A(), B(), F(), G(), K()

### Community 85 - "legacy_process_resumes"
Cohesion: 0.29
Nodes (7): legacy_process_resumes(), limit, post, Request, Session, UploadFile, Legacy endpoint delegating to recruiter process_resumes. Requires Recruiter…

### Community 86 - "get_password_hash"
Cohesion: 0.12
Nodes (16): get_password_hash(), Hashes a plain text password using bcrypt., fetch_google_certs(), anyio_backend(), client(), db_session(), fixture, Create a new database session for a test. (+8 more)

### Community 87 - "test_candidate_patch_rejects_forbidden_fields"
Cohesion: 0.40
Nodes (5): PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., test_candidate_patch_rejects_forbidden_fields(), test_recruiter_patch_rejects_forbidden_fields(), parametrize

### Community 88 - "get_screening_task_detail"
Cohesion: 0.33
Nodes (6): get_screening_task_detail(), Retrieves complete details for a specific screening task owned by the…, Verify get_screening_task_detail strips recommendations from candidate…, test_get_screening_task_detail_omits_candidate_recommendations(), test_get_screening_task_detail_owner_success(), test_get_screening_task_detail_unauthorized_or_missing()

### Community 89 - "constants.js"
Cohesion: 0.21
Nodes (12): handleLogoNavigation(), handleLogout(), initNavbar(), API_BASE, API_ENDPOINTS, CANDIDATE_STATUS_VALUES, COMPANY_TYPES, MESSAGES (+4 more)

### Community 91 - "test_candidate_resume_details_preserves_recommendations"
Cohesion: 0.33
Nodes (4): Verify get_recruiter_stats returns empty top_recommended_improvements even if…, Verify get_candidate_resume_details still returns recommendations for candidate…, test_candidate_resume_details_preserves_recommendations(), test_get_recruiter_stats_omits_candidate_recommendations()

## Knowledge Gaps
- **196 isolated node(s):** `Settings`, `inflightGetRequests`, `uploadedFiles`, `sidebarLinkIds`, `COMPANY_TYPES` (+191 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `stages.py`, `test_custom_scoring.py`, `backend/tests/test_recruiter.py`, `UpdateRecommendationPayload`, `get_recruiter_stats`, `process_resumes`, `test_password_reset.py`, `UserRole`, `auth.py`, `archive_job_description`, `legacy_process_resumes`, `update_job_description`, `get_password_hash`, `get_screening_task_detail`, `Session`, `models/models.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `XaiEngine` connect `stages.py` to `xai/builder.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `s()` connect `s` to `bf`, `app.js`, `gsap.min.js`, `Tween`, `cb`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `CompanyType` and `ResumeStatus`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `UserRole` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`UserRole` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `CompanyType` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`CompanyType` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AnalysisContext` (e.g. with `AnalysisPipeline` and `ExplanationBuildingStage`) actually correct?**
  _`AnalysisContext` has 11 INFERRED edges - model-reasoned connections that need verification._