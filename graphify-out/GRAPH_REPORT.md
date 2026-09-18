# Graph Report - nipun-platform  (2026-09-18)

## Corpus Check
- 131 files · ~140,214 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1042 nodes · 2420 edges · 71 communities (64 shown, 7 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 292 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dcb12081`
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
- get_current_user
- main.py
- ScrollTrigger.min.js
- test_password_reset.py
- onboarding.js
- api.js
- UserRole
- candidate.js
- s
- recruiter.js
- Tween
- package.json
- router.js
- app.js
- _d
- state.js
- yc
- ja
- jc
- landing.js
- process_candidate_resume
- cb
- auth
- Oa
- bf
- skill_expander.py
- K
- Landing Index HTML
- process_resumes
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
- Resume Screener Report
- Python Dependencies
- routers/test_auth.py
- verify_firebase_id_token
- seed_default_profiles

## God Nodes (most connected - your core abstractions)
1. `User` - 56 edges
2. `UserRole` - 37 edges
3. `PipelineStage` - 33 edges
4. `CompanyType` - 28 edges
5. `AnalysisContext` - 28 edges
6. `PersistenceStage` - 28 edges
7. `request()` - 27 edges
8. `ScoringProfileResolutionStage` - 26 edges
9. `ResumeStatus` - 25 edges
10. `ResumeTextExtractionStage` - 25 edges

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

## Communities (71 total, 7 thin omitted)

### Community 0 - "stages.py"
Cohesion: 0.10
Nodes (52): ResumeStatus, Resume, ScanResult, ScoringProfile, AnalysisContext, Any, Lightweight, shared context carrying tracing IDs, configurations, and stage…, ExplanationBuiltEvent (+44 more)

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
Nodes (43): anyio, extract_text(), extract_text_from_docx(), extract_text_from_pdf(), Extract text from a DOCX file, including paragraphs and tables., Route to appropriate extractor based on extension., Extract text from a PDF file., build_analysis_metadata() (+35 more)

### Community 6 - "User"
Cohesion: 0.06
Nodes (61): Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online(), get_db(), FastAPI Dependency to yield a database session., Restricts route access to users registered with the RECRUITER role in…, Restricts route access to users registered with the CANDIDATE role in… (+53 more)

### Community 7 - "gsap.min.js"
Cohesion: 0.06
Nodes (16): ee(), Jd(), Kd(), Ld(), ma(), Md(), na(), Od() (+8 more)

### Community 8 - "get_current_user"
Cohesion: 0.15
Nodes (13): get_current_user(), Session, Validates the incoming Firebase ID token using Firebase Admin SDK, extracts the…, Verifies that a user with an existing firebase_uid is resolved directly., Verifies that an existing dev user matching email is linked to the Firebase UID., Verifies that if the token lacks an email claim, it does not link to existing…, Verifies that a new Firebase user is automatically JIT-provisioned in…, Verifies that a token without a uid claim is rejected with HTTP 401. (+5 more)

### Community 9 - "main.py"
Cohesion: 0.11
Nodes (15): api_route, App, Settings, get_firebase_admin_app(), Lazily initializes and returns the singleton Firebase Admin App. Supports: 1.…, check_db_connection(), Tests connection to the configured database on demand (e.g. startup or health…, setup_logging() (+7 more)

### Community 10 - "ScrollTrigger.min.js"
Cohesion: 0.07
Nodes (4): dc(), Ha(), Ia(), ob()

### Community 11 - "test_password_reset.py"
Cohesion: 0.08
Nodes (28): Verifies a plain text password against the hashed version using bcrypt., verify_password(), PasswordResetToken, disable_rate_limiting(), existing_user(), fixture, Test resetting password with a valid token., Temporarily disables SlowAPI rate limiting for unit tests. (+20 more)

### Community 12 - "onboarding.js"
Cohesion: 0.20
Nodes (15): API_BASE, API_ENDPOINTS, CANDIDATE_STATUS_VALUES, COMPANY_TYPES, MESSAGES, ROLES, ROUTES, getStepsForRole() (+7 more)

### Community 13 - "api.js"
Cohesion: 0.13
Nodes (29): archiveJob(), createJob(), deleteCandidateResume(), deleteJob(), _executeRequest(), forgotPassword(), getCandidateResumeDetails(), getCandidateResumes() (+21 more)

### Community 14 - "UserRole"
Cohesion: 0.31
Nodes (22): CompanyType, UserRole, GoogleLoginRequest, BaseModel, CandidateProfileResponse, Config, ForgotPasswordRequest, ForgotPasswordResponse (+14 more)

### Community 15 - "candidate.js"
Cohesion: 0.22
Nodes (10): getEmptyStateHTML(), toggleButtonLoading(), handleLogout(), initNavbar(), clearCandidateWorkspaceState(), initCandidatePage(), renderCandidateAnalysisResults(), renderFileList() (+2 more)

### Community 16 - "s"
Cohesion: 0.15
Nodes (20): _a(), ac(), Bo(), db(), ea(), eb(), ga(), gb() (+12 more)

### Community 17 - "recruiter.js"
Cohesion: 0.17
Nodes (15): renderResults(), getCandidateDetailRowHTML(), getCandidateRowHTML(), getRecruiterCandidateCardHTML(), updateStatisticCard(), initializeRecruiterScreen(), initRecruiterPage(), loadJobDescriptionsDropdown() (+7 more)

### Community 18 - "Tween"
Cohesion: 0.15
Nodes (18): _assertThisInitialized(), Ec(), Fc(), gc(), ka(), qa(), t(), tb() (+10 more)

### Community 19 - "package.json"
Cohesion: 0.12
Nodes (15): autoprefixer, cors, firebase, dependencies, cors, firebase, devDependencies, autoprefixer (+7 more)

### Community 20 - "router.js"
Cohesion: 0.22
Nodes (17): sidebarLinkIds, updateSidebarActiveLink(), initializeCandidateScreen(), initializeLoginPage(), initLoginPage(), resetAuthModalToTabs(), showForgotPasswordView(), showResetPasswordView() (+9 more)

### Community 21 - "app.js"
Cohesion: 0.22
Nodes (16): clearCandidateState(), handleFiles(), renderFileList(), updateResumeCountDisplay(), uploadedFiles, checkAuthStatus(), _doCheckAuthStatus(), hideEmailVerificationModal() (+8 more)

### Community 22 - "_d"
Cohesion: 0.29
Nodes (10): be(), _d(), fa(), ia(), ie(), je(), ke(), le() (+2 more)

### Community 23 - "state.js"
Cohesion: 0.15
Nodes (19): getProfile(), populateRecruiterProfileUI(), initializeCandidateDashboard(), initializeCandidateProfile(), renderTimelineList(), submitOnboarding(), initializeRecruiterDashboard(), initializeRecruiterProfile() (+11 more)

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
Cohesion: 0.13
Nodes (18): candidate_status(), delete_candidate_resume(), get_candidate_resume_details(), get_candidate_resumes(), process_candidate_resume(), delete, get, post (+10 more)

### Community 29 - "cb"
Cohesion: 0.29
Nodes (7): Ab(), Bb(), cb(), Context(), Ew(), fb(), zb()

### Community 30 - "auth"
Cohesion: 0.50
Nodes (3): app, auth, googleProvider

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

### Community 36 - "process_resumes"
Cohesion: 0.17
Nodes (12): legacy_process_resumes(), limit, post, Request, Session, UploadFile, Legacy endpoint delegating to recruiter process_resumes. Requires Recruiter…, process_resumes() (+4 more)

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
Cohesion: 0.18
Nodes (21): create_access_token(), Generates a secure JSON Web Token., forgot_password(), get_me(), google_login(), login(), get, limit (+13 more)

### Community 49 - "validate_skill_name"
Cohesion: 0.33
Nodes (9): Validates that a skill name contains reasonable characters and isn't empty,…, validate_skill_name(), test_validate_skill_name_empty_or_whitespace_only(), test_validate_skill_name_invalid_chars(), test_validate_skill_name_non_string(), test_validate_skill_name_too_long(), test_validate_skill_name_valid_common(), test_validate_skill_name_valid_special_chars() (+1 more)

### Community 66 - "routers/test_auth.py"
Cohesion: 0.12
Nodes (16): get_password_hash(), Hashes a plain text password using bcrypt., fetch_google_certs(), anyio_backend(), client(), db_session(), fixture, Create a new database session for a test. (+8 more)

### Community 68 - "verify_firebase_id_token"
Cohesion: 0.12
Nodes (17): Any, Verifies a Firebase ID token using the Firebase Admin SDK. Extracts trusted…, verify_firebase_id_token(), Verifies that an empty or non-string token raises HTTP 401., Verifies that if Firebase Admin fails to initialize, verify_id_token raises…, Verifies that verify_firebase_id_token forwards clock_skew_seconds=5 to…, Verifies that verify_firebase_id_token allows custom clock_skew_seconds…, Verifies that auth.InvalidIdTokenError for future timestamp outside tolerance… (+9 more)

### Community 69 - "seed_default_profiles"
Cohesion: 0.29
Nodes (6): Startup event handler: verify database connectivity and seed default profiles., startup_event(), Session, Checks if scoring profiles exist in the database; if not, seeds missing default…, seed_default_profiles(), on_event

## Knowledge Gaps
- **29 isolated node(s):** `Settings`, `inflightGetRequests`, `uploadedFiles`, `sidebarLinkIds`, `COMPANY_TYPES` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `stages.py`, `routers/test_auth.py`, `process_resumes`, `get_current_user`, `main.py`, `test_password_reset.py`, `UserRole`, `google_login`, `process_candidate_resume`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `s()` connect `s` to `bf`, `gsap.min.js`, `recruiter.js`, `Tween`, `cb`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `XaiEngine` connect `stages.py` to `build_score_components`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `CompanyType` and `ResumeStatus`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `UserRole` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`UserRole` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `PipelineStage` (e.g. with `AnalysisPipeline` and `ResumeStatus`) actually correct?**
  _`PipelineStage` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `CompanyType` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`CompanyType` has 23 INFERRED edges - model-reasoned connections that need verification._