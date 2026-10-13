# Graph Report - nipun-platform  (2026-10-13)

## Corpus Check
- 144 files · ~142,856 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1324 nodes · 2760 edges · 83 communities (77 shown, 6 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 299 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9f3466d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- stages.py
- test_estimator.py
- build_score_components
- Skill
- extract_education
- test_remediation.py
- User
- gsap.min.js
- Core Principles
- router.js
- ScrollTrigger.min.js
- test_password_reset.py
- app.js
- api.js
- UserRole
- candidate.js
- s
- recruiter.js
- Tween
- package.json
- state.js
- login.js
- _d
- Documentation Architect
- yc
- ja
- jc
- landing.js
- process_candidate_resume
- cb
- test_profile_editing.py
- Oa
- bf
- skill_expander.py
- K
- Landing Index HTML
- legacy_process_resumes
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
- RecruiterProfileUpdate
- test_firebase_auth.py
- seed_default_profiles
- Core Principles
- Capabilities
- routers/test_auth.py
- API Design Principles Implementation Playbook
- Core Principles
- API Design Principles
- test_frontend_assets.py
- get_profile
- test_candidate_patch_rejects_forbidden_fields
- firebase-init.js

## God Nodes (most connected - your core abstractions)
1. `User` - 61 edges
2. `UserRole` - 40 edges
3. `PipelineStage` - 33 edges
4. `CompanyType` - 32 edges
5. `request()` - 29 edges
6. `AnalysisContext` - 28 edges
7. `PersistenceStage` - 28 edges
8. `ScoringProfileResolutionStage` - 26 edges
9. `ResumeStatus` - 25 edges
10. `ResumeTextExtractionStage` - 25 edges

## Surprising Connections (you probably didn't know these)
- `CandidateProfile` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `JobDescription` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `RecruiterProfile` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `Resume` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py
- `ScanResult` --uses--> `UserRole`  [INFERRED]
  backend/models/models.py → backend/models/enums.py

## Import Cycles
- 3-file cycle: `frontend/assets/js/auth.js -> frontend/assets/js/router.js -> frontend/assets/js/pages/login.js -> frontend/assets/js/auth.js`

## Communities (83 total, 6 thin omitted)

### Community 0 - "stages.py"
Cohesion: 0.10
Nodes (54): ResumeStatus, Resume, ScanResult, ScoringProfile, AnalysisContext, Any, Lightweight, shared context carrying tracing IDs, configurations, and stage…, ExplanationBuiltEvent (+46 more)

### Community 1 - "test_estimator.py"
Cohesion: 0.06
Nodes (47): Defines thresholds and priorities for AI Resume Improvement Engine…, RecommendationPolicy, Defines recruiter-specific configurations and security permissions., RecruiterPolicy, Defines policy configurations for ATS scoring and weights. Removes magic…, ScoringPolicy, Defines policy configurations and fallback weights for adaptive scoring…, ScoringProfilePolicy (+39 more)

### Community 2 - "build_score_components"
Cohesion: 0.07
Nodes (46): build_score_components(), Any, Builds the structured ScoreComponent list using the candidate's scored…, _resolve_status(), Any, Helper to construct a dict representation of StructuredExplanations., Generates structured multi-level explanations (SUMMARY, DETAILED, TECHNICAL)…, effective_exp_title() (+38 more)

### Community 3 - "Skill"
Cohesion: 0.08
Nodes (27): get_weight(), Returns the matching weight for the given match type., MatchReason, MatchResult, BaseModel, Universal domain object representing a semantic match between a required skill…, Evaluates relationship type, confidence, and matches between two Skill objects.…, resolve_relationship() (+19 more)

### Community 4 - "extract_education"
Cohesion: 0.08
Nodes (40): extract_education(), extract_email(), extract_experience(), extract_github(), extract_linkedin(), extract_name(), extract_phone(), extract_projects() (+32 more)

### Community 5 - "test_remediation.py"
Cohesion: 0.06
Nodes (41): anyio, extract_text(), extract_text_from_docx(), extract_text_from_pdf(), Extract text from a DOCX file, including paragraphs and tables., Route to appropriate extractor based on extension., Extract text from a PDF file., build_analysis_metadata() (+33 more)

### Community 6 - "User"
Cohesion: 0.07
Nodes (57): Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online(), api_route, check_db_connection(), get_db(), Tests connection to the configured database on demand (e.g. startup or health… (+49 more)

### Community 7 - "gsap.min.js"
Cohesion: 0.06
Nodes (16): ee(), Jd(), Kd(), Ld(), ma(), Md(), na(), Od() (+8 more)

### Community 8 - "Core Principles"
Cohesion: 0.06
Nodes (33): 10. Content and microcopy, 11. Feedback and error recovery, 12. Data-heavy interfaces, 13. Animation and interaction, 1. Understand, 1. Understand the user and the task, 2. Prioritize usability, 2. Structure (+25 more)

### Community 9 - "router.js"
Cohesion: 0.20
Nodes (16): handleLogoNavigation(), handleLogout(), initNavbar(), sidebarLinkIds, updateSidebarActiveLink(), ROLES, ROUTES, initializeCandidateScreen() (+8 more)

### Community 10 - "ScrollTrigger.min.js"
Cohesion: 0.07
Nodes (4): dc(), Ha(), Ia(), ob()

### Community 11 - "test_password_reset.py"
Cohesion: 0.07
Nodes (27): Verifies a plain text password against the hashed version using bcrypt., verify_password(), disable_rate_limiting(), existing_user(), fixture, Test resetting password with a valid token., Temporarily disables SlowAPI rate limiting for unit tests., Test that a reset token cannot be reused a second time. (+19 more)

### Community 12 - "app.js"
Cohesion: 0.15
Nodes (20): clearCandidateState(), handleFiles(), renderFileList(), updateResumeCountDisplay(), uploadedFiles, initModals(), API_BASE, API_ENDPOINTS (+12 more)

### Community 13 - "api.js"
Cohesion: 0.12
Nodes (32): archiveJob(), createJob(), deleteCandidateResume(), deleteJob(), _executeRequest(), forgotPassword(), getCandidateResumeDetails(), getCandidateResumes() (+24 more)

### Community 14 - "UserRole"
Cohesion: 0.29
Nodes (24): CompanyType, UserRole, PasswordResetToken, GoogleLoginRequest, BaseModel, CandidateProfileResponse, CandidateProfileUpdate, Config (+16 more)

### Community 15 - "candidate.js"
Cohesion: 0.21
Nodes (9): getEmptyStateHTML(), toggleButtonLoading(), populateCandidateProfileUI(), populateRecruiterProfileUI(), clearCandidateWorkspaceState(), initCandidatePage(), renderCandidateAnalysisResults(), renderFileList() (+1 more)

### Community 16 - "s"
Cohesion: 0.15
Nodes (20): _a(), ac(), Bo(), db(), ea(), eb(), ga(), gb() (+12 more)

### Community 17 - "recruiter.js"
Cohesion: 0.17
Nodes (19): renderResults(), getCandidateDetailRowHTML(), getCandidateRowHTML(), getRecruiterCandidateCardHTML(), updateStatisticCard(), clearRecruiterWorkspaceState(), initializeRecruiterScreen(), initRecruiterPage() (+11 more)

### Community 18 - "Tween"
Cohesion: 0.15
Nodes (18): _assertThisInitialized(), Ec(), Fc(), gc(), ka(), qa(), t(), tb() (+10 more)

### Community 19 - "package.json"
Cohesion: 0.12
Nodes (15): autoprefixer, cors, firebase, dependencies, cors, firebase, devDependencies, autoprefixer (+7 more)

### Community 20 - "state.js"
Cohesion: 0.16
Nodes (17): initializeCandidateDashboard(), initializeCandidateProfile(), renderTimelineList(), showCandidateProfileFeedback(), submitOnboarding(), initializeRecruiterDashboard(), getCandidateResumes(), getCandidateStats() (+9 more)

### Community 21 - "login.js"
Cohesion: 0.24
Nodes (18): checkAuthStatus(), _doCheckAuthStatus(), hideEmailVerificationModal(), initAuthListener(), showEmailVerificationModal(), waitForAuthState(), auth, initializeLoginPage() (+10 more)

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

### Community 28 - "process_candidate_resume"
Cohesion: 0.10
Nodes (23): candidate_status(), delete_candidate_resume(), get_candidate_resume_details(), get_candidate_resumes(), get_candidate_stats(), process_candidate_resume(), delete, get (+15 more)

### Community 29 - "cb"
Cohesion: 0.29
Nodes (7): Ab(), Bb(), cb(), Context(), Ew(), fb(), zb()

### Community 30 - "test_profile_editing.py"
Cohesion: 0.04
Nodes (50): get_password_hash(), Hashes a plain text password using bcrypt., anyio_backend(), client(), db_session(), fixture, Create a new database session for a test., Create a test client using the test database. (+42 more)

### Community 31 - "Oa"
Cohesion: 0.53
Nodes (6): Bb(), Ja(), Ka(), La(), Oa(), z()

### Community 32 - "bf"
Cohesion: 0.22
Nodes (10): bf(), cf(), df(), ef(), kf(), lf(), M(), mf() (+2 more)

### Community 33 - "skill_expander.py"
Cohesion: 0.40
Nodes (4): get_related_skills(), is_skill_in_text(), Checks if an explicit skill contains a broad conceptual keyword. For example,…, Checks if a skill or any of its known aliases exists in the given text. Handles…

### Community 34 - "K"
Cohesion: 0.40
Nodes (5): A(), B(), F(), G(), K()

### Community 35 - "Landing Index HTML"
Cohesion: 0.40
Nodes (5): Nipun Main Branding Image, Candidate Portal HTML, Landing Index HTML, Onboarding Portal HTML, Recruiter Dashboard HTML

### Community 36 - "legacy_process_resumes"
Cohesion: 0.29
Nodes (7): legacy_process_resumes(), limit, post, Request, Session, UploadFile, Legacy endpoint delegating to recruiter process_resumes. Requires Recruiter…

### Community 37 - "loadingOverlay.js"
Cohesion: 0.50
Nodes (3): loadingOverlay, STAGES, STATUS_MESSAGES

### Community 38 - "Q"
Cohesion: 0.50
Nodes (4): la(), Q(), Gb(), Hb()

### Community 39 - "r"
Cohesion: 0.50
Nodes (4): mc(), O(), P(), r()

### Community 48 - "google_login"
Cohesion: 0.13
Nodes (24): Settings, create_access_token(), Generates a secure JSON Web Token., forgot_password(), get_me(), google_login(), login(), get (+16 more)

### Community 49 - "validate_skill_name"
Cohesion: 0.33
Nodes (9): Validates that a skill name contains reasonable characters and isn't empty,…, validate_skill_name(), test_validate_skill_name_empty_or_whitespace_only(), test_validate_skill_name_invalid_chars(), test_validate_skill_name_non_string(), test_validate_skill_name_too_long(), test_validate_skill_name_valid_common(), test_validate_skill_name_valid_special_chars() (+1 more)

### Community 63 - "Capabilities"
Cohesion: 0.06
Nodes (31): API Contract & Documentation, API Design & Patterns, API Gateway & Load Balancing, Asynchronous Processing, Authentication & Authorization, Backend Architect, Behavioral Traits, Caching Strategies (+23 more)

### Community 66 - "RecruiterProfileUpdate"
Cohesion: 0.29
Nodes (5): patch, Update recruiter's profile information and display name. Strictly scoped to…, update_recruiter_profile(), RecruiterProfileUpdate, field_validator

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

### Community 74 - "routers/test_auth.py"
Cohesion: 0.31
Nodes (5): fetch_google_certs(), test_fetch_google_certs_error(), test_fetch_google_certs_success(), test_fetch_google_certs_timeout(), Exception

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
Cohesion: 0.12
Nodes (16): Verify frontend/firebase-config.js exists and is valid JavaScript exporting…, Verify recruiter.html contains the full quick view modal and candidate.html…, Verify candidate card renders quick view button with data attributes and…, Verify that frontend/firebase-config.js is not ignored by .gitignore., Verify firebase.json hosting settings, headers, and rewrite safety., Verify that all script tags in HTML files reference files that exist on disk., Verify that static relative imports in local frontend JS files resolve to…, Verify logo elements exist in recruiter.html, candidate.html, index.html and… (+8 more)

### Community 81 - "get_profile"
Cohesion: 0.50
Nodes (4): get_profile(), get, Retrieves the full profile details of the authenticated user., read_root()

### Community 83 - "test_candidate_patch_rejects_forbidden_fields"
Cohesion: 0.40
Nodes (5): PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., test_candidate_patch_rejects_forbidden_fields(), test_recruiter_patch_rejects_forbidden_fields(), parametrize

### Community 84 - "firebase-init.js"
Cohesion: 0.40
Nodes (3): app, googleProvider, firebaseConfig

## Knowledge Gaps
- **191 isolated node(s):** `Settings`, `inflightGetRequests`, `uploadedFiles`, `sidebarLinkIds`, `COMPANY_TYPES` (+186 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `stages.py`, `RecruiterProfileUpdate`, `test_firebase_auth.py`, `legacy_process_resumes`, `routers/test_auth.py`, `test_password_reset.py`, `UserRole`, `google_login`, `get_profile`, `process_candidate_resume`, `test_profile_editing.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `XaiEngine` connect `stages.py` to `build_score_components`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `s()` connect `s` to `bf`, `gsap.min.js`, `recruiter.js`, `Tween`, `cb`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `CompanyType` and `ResumeStatus`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `UserRole` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`UserRole` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `PipelineStage` (e.g. with `AnalysisPipeline` and `ResumeStatus`) actually correct?**
  _`PipelineStage` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `CompanyType` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`CompanyType` has 25 INFERRED edges - model-reasoned connections that need verification._