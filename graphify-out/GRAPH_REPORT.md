# Graph Report - nipun-platform  (2026-10-22)

## Corpus Check
- 193 files · ~277,534 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2156 nodes · 3759 edges · 131 communities (125 shown, 6 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 314 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4104eaae`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- stages.py
- test_custom_scoring.py
- xai/builder.py
- Skill
- router.js
- app.js
- UpdateRecommendationPayload
- gsap.min.js
- Core Principles
- info_extractor.py
- ScrollTrigger.min.js
- test_password_reset.py
- Expo Animation Recipes
- api.js
- UserRole
- candidate.js
- s
- recruiter.js
- Tween
- package.json
- Animation Recipes
- Worst-Case Catalog
- _d
- Documentation Architect
- yc
- ja
- jc
- landing.js
- Animation Standards Reference
- cb
- User
- Oa
- bf
- skill_expander.py
- fixture
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
- recruiter.py
- get_profile
- Core Principles
- Capabilities
- test_remediation.py
- navbar.js
- API Design Principles Implementation Playbook
- Core Principles
- API Design Principles
- test_frontend_assets.py
- Animation Audit Playbook
- Write Swift
- onboard.md
- Apple Design
- The Fixes
- Chapter: Semantic Matching Evaluation & Knowledge Base Verification
- Prototyping Variants
- Delight Techniques
- Implement Animations
- generate_grounded_xai_insights
- test_candidate_patch_rejects_forbidden_fields
- Glossary
- Introduce Color Strategically
- Design Critique
- Animation Performance
- Finding Animation Opportunities
- Polish Systematically
- onboarding.js
- extract_education
- Implement Adaptations
- Improve Copy Systematically
- Simplify the Design
- extract_text
- Generate Comprehensive Report
- Amplify the Design
- Optimization Strategy
- Working With Sonner
- Frontend Aesthetics Guidelines
- Refine the Design
- Hardening Dimensions
- The list
- Design Engineering
- Component Building Principles
- Step 2: Ask UX-Focused Questions
- The Animation Decision Framework
- clip-path for Animation
- Performance Rules
- Gesture and Drag Interactions
- extract.md
- CSS Transform Mastery
- The Sonner Principles (Building Loved Components)
- Spring Animations
- K
- Core Philosophy
- Debugging Animations
- normalize.md
- .execute
- seed_default_profiles
- legacy_process_resumes

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

## Communities (131 total, 6 thin omitted)

### Community 0 - "stages.py"
Cohesion: 0.08
Nodes (64): ResumeStatus, Resume, ScanResult, ScoringProfile, preprocess_text(), Cleans text by: - Lowercasing - Removing punctuation - Removing stopwords -…, AnalysisContext, Any (+56 more)

### Community 1 - "test_custom_scoring.py"
Cohesion: 0.05
Nodes (59): Defines thresholds and priorities for AI Resume Improvement Engine…, RecommendationPolicy, Defines recruiter-specific configurations and security permissions., RecruiterPolicy, Defines policy configurations for ATS scoring and weights. Removes magic…, ScoringPolicy, Any, Validates, sanitizes, and normalizes optional recruiter custom scoring… (+51 more)

### Community 2 - "xai/builder.py"
Cohesion: 0.07
Nodes (48): build_score_components(), Any, Builds the structured ScoreComponent list using the candidate's scored…, _resolve_status(), Any, Helper to construct a dict representation of StructuredExplanations., Generates structured multi-level explanations (SUMMARY, DETAILED, TECHNICAL)…, effective_exp_title() (+40 more)

### Community 3 - "Skill"
Cohesion: 0.07
Nodes (33): get_weight(), Returns the matching weight for the given match type., MatchReason, MatchResult, BaseModel, Universal domain object representing a semantic match between a required skill…, Evaluates relationship type, confidence, and matches between two Skill objects.…, resolve_relationship() (+25 more)

### Community 4 - "router.js"
Cohesion: 0.16
Nodes (20): updateSidebarActiveLink(), app, auth, googleProvider, initializeCandidateScreen(), initializeLoginPage(), initLoginPage(), resetAuthModalToTabs() (+12 more)

### Community 5 - "app.js"
Cohesion: 0.22
Nodes (16): clearCandidateState(), handleFiles(), renderFileList(), updateResumeCountDisplay(), uploadedFiles, checkAuthStatus(), _doCheckAuthStatus(), hideEmailVerificationModal() (+8 more)

### Community 6 - "UpdateRecommendationPayload"
Cohesion: 0.08
Nodes (29): candidate_status(), delete_candidate_resume(), get_candidate_resume_details(), get_candidate_resumes(), get_candidate_stats(), process_candidate_resume(), BaseModel, delete (+21 more)

### Community 7 - "gsap.min.js"
Cohesion: 0.06
Nodes (16): ee(), Jd(), Kd(), Ld(), ma(), Md(), na(), Od() (+8 more)

### Community 8 - "Core Principles"
Cohesion: 0.06
Nodes (33): 10. Content and microcopy, 11. Feedback and error recovery, 12. Data-heavy interfaces, 13. Animation and interaction, 1. Understand, 1. Understand the user and the task, 2. Prioritize usability, 2. Structure (+25 more)

### Community 9 - "info_extractor.py"
Cohesion: 0.16
Nodes (16): extract_experience(), extract_name(), Attempt to extract a candidate's name. As a heuristic for unstructured resumes,…, Heuristically extract total years of experience. Looks for phrases like "5…, Test extracting the maximum experience when mentioned multiple times., Test when no experience is mentioned., Test edge cases with formatting and spacing., Test case insensitivity. (+8 more)

### Community 10 - "ScrollTrigger.min.js"
Cohesion: 0.07
Nodes (4): dc(), Ha(), Ia(), ob()

### Community 11 - "test_password_reset.py"
Cohesion: 0.09
Nodes (26): PasswordResetToken, disable_rate_limiting(), existing_user(), fixture, Test resetting password with a valid token., Temporarily disables SlowAPI rate limiting for unit tests., Test that a reset token cannot be reused a second time., Test that an expired token is rejected. (+18 more)

### Community 12 - "Expo Animation Recipes"
Cohesion: 0.06
Nodes (33): Bottom sheet you can drag to dismiss, Collapsing header on scroll, Expo Animation Recipes, Firing something once at a threshold, Keyboard-synced UI, List entrances, Press feedback, Screen transitions (Expo Router) (+25 more)

### Community 13 - "api.js"
Cohesion: 0.11
Nodes (34): archiveJob(), createJob(), deleteCandidateResume(), deleteJob(), _executeRequest(), forgotPassword(), getCandidateResumeDetails(), getCandidateResumes() (+26 more)

### Community 14 - "UserRole"
Cohesion: 0.20
Nodes (30): CompanyType, UserRole, GoogleLoginRequest, BaseModel, CandidateProfileResponse, CandidateProfileUpdate, Config, ForgotPasswordRequest (+22 more)

### Community 15 - "candidate.js"
Cohesion: 0.09
Nodes (29): getEmptyStateHTML(), toggleButtonLoading(), populateCandidateProfileUI(), populateRecruiterProfileUI(), closeCandidateAnalysisModal(), initCandidatePage(), initializeCandidateDashboard(), initializeCandidateProfile() (+21 more)

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

### Community 20 - "Animation Recipes"
Cohesion: 0.06
Nodes (31): Accordion / collapse, Animation Recipes, Button press, Drag to dismiss, Drawer / sheet, Dropdown, popover, menu, select, Hold to confirm, Masking a crossfade that won't settle (+23 more)

### Community 21 - "Worst-Case Catalog"
Cohesion: 0.06
Nodes (29): Collections, Emails, URLs, identifiers, Environment, Images and media, Labels, titles, and copy from data, Numbers and money, People and names, States (+21 more)

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
Cohesion: 0.47
Nodes (8): initCounters(), initFeatureStack(), initHeroAnimation(), initNavbarEffects(), initStoryAnimation(), initWalkthrough(), initAllLandingAnimations(), initLandingPage()

### Community 28 - "Animation Standards Reference"
Cohesion: 0.07
Nodes (26): Aggressive Escalation Triggers, Guidelines, Initial Response, Operating Posture, Part 1 — Findings table (REQUIRED), Part 2 — Verdict (REQUIRED), Remedial Preference Hierarchy, Required Output Format (+18 more)

### Community 29 - "cb"
Cohesion: 0.29
Nodes (7): Ab(), Bb(), cb(), Context(), Ew(), fb(), zb()

### Community 30 - "User"
Cohesion: 0.03
Nodes (72): Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online(), CandidateProfile, RecruiterProfile, User, get_onboarding_status() (+64 more)

### Community 31 - "Oa"
Cohesion: 0.53
Nodes (6): Bb(), Ja(), Ka(), La(), Oa(), z()

### Community 32 - "bf"
Cohesion: 0.22
Nodes (10): bf(), cf(), df(), ef(), kf(), lf(), M(), mf() (+2 more)

### Community 33 - "skill_expander.py"
Cohesion: 0.40
Nodes (4): get_related_skills(), is_skill_in_text(), Checks if an explicit skill contains a broad conceptual keyword. For example,…, Checks if a skill or any of its known aliases exists in the given text. Handles…

### Community 34 - "fixture"
Cohesion: 0.33
Nodes (6): anyio_backend(), client(), db_session(), fixture, Create a new database session for a test., Create a test client using the test database.

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
Cohesion: 0.08
Nodes (38): Settings, create_access_token(), get_password_hash(), Verifies a plain text password against the hashed version using bcrypt., Hashes a plain text password using bcrypt., Generates a secure JSON Web Token., verify_password(), fetch_google_certs() (+30 more)

### Community 49 - "validate_skill_name"
Cohesion: 0.33
Nodes (9): Validates that a skill name contains reasonable characters and isn't empty,…, validate_skill_name(), test_validate_skill_name_empty_or_whitespace_only(), test_validate_skill_name_invalid_chars(), test_validate_skill_name_non_string(), test_validate_skill_name_too_long(), test_validate_skill_name_valid_common(), test_validate_skill_name_valid_special_chars() (+1 more)

### Community 63 - "Capabilities"
Cohesion: 0.06
Nodes (31): API Contract & Documentation, API Design & Patterns, API Gateway & Load Balancing, Asynchronous Processing, Authentication & Authorization, Backend Architect, Behavioral Traits, Caching Strategies (+23 more)

### Community 66 - "backend/tests/test_recruiter.py"
Cohesion: 0.05
Nodes (67): JobDescription, ScreeningTask, archive_job_description(), create_job_description(), delete_job_description(), get_recruiter_stats(), get_scoring_profiles(), get_screening_history() (+59 more)

### Community 68 - "recruiter.py"
Cohesion: 0.05
Nodes (57): api_route, App, get_firebase_admin_app(), Any, Verifies a Firebase ID token using the Firebase Admin SDK. Extracts trusted…, Lazily initializes and returns the singleton Firebase Admin App. Supports: 1.…, verify_firebase_id_token(), check_db_connection() (+49 more)

### Community 69 - "get_profile"
Cohesion: 0.50
Nodes (4): get_profile(), get, Retrieves the full profile details of the authenticated user., read_root()

### Community 71 - "Core Principles"
Cohesion: 0.08
Nodes (24): 1. Start with requirements, 2. Prefer simplicity, 3. Evaluate technology choices rationally, 4. Design for data integrity, 5. Design schemas around actual access patterns, 6. Treat migrations as production changes, 7. Scale only when justified, 8. Consider the whole system (+16 more)

### Community 72 - "Capabilities"
Cohesion: 0.09
Nodes (22): Application Security Testing, Behavioral Traits, Capabilities, Cloud Security, Compliance & Governance, DevSecOps & Security Automation, Do not use this skill when, Emerging Security Technologies (+14 more)

### Community 74 - "test_remediation.py"
Cohesion: 0.15
Nodes (14): build_analysis_metadata(), Any, Builds a standardized analysis_metadata dictionary according to the Phase 5…, _get_tfidf_model(), rank_candidates(), Caches the TF-IDF vectorizer and JD matrix for a given set of JD skills.…, Ranks resumes against a job description using TF-IDF and Cosine Similarity. To…, anyio (+6 more)

### Community 75 - "navbar.js"
Cohesion: 0.33
Nodes (10): handleLogoNavigation(), handleLogout(), initNavbar(), initSidebar(), isSidebarCollapsed(), setSidebarCollapsed(), sidebarLinkIds, toggleSidebar() (+2 more)

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

### Community 81 - "Animation Audit Playbook"
Cohesion: 0.08
Nodes (22): 1. Purpose & frequency, 2. Easing & duration, 3. Physicality & origin, 4. Interruptibility, 5. Performance, 6. Accessibility, 7. Cohesion & tokens, 8. Missed opportunities (+14 more)

### Community 83 - "Write Swift"
Cohesion: 0.09
Nodes (22): 10. ARC and object lifetime, 11. Testing — Swift Testing by default, 12. Macros, 13. Logging and debugging, 14. Unsafe code and interop, 15. Modern syntax you should be using, 16. Migrating an existing codebase to Swift 6, 1. Model data with value types (+14 more)

### Community 84 - "onboard.md"
Cohesion: 0.09
Nodes (22): Assess Onboarding Needs, Context Over Ceremony, Contextual Help, Design Onboarding Experiences, Documentation & Help, Empty State Design, Feature Discovery & Adoption, Guided Tours & Walkthroughs (+14 more)

### Community 85 - "Apple Design"
Cohesion: 0.09
Nodes (21): 10. Gesture design details (the "feel" checklist), 11. Frame-level smoothness, 12. Materials & depth — translucency conveys hierarchy, 13. Multimodal feedback — motion + sound + haptics, 14. Reduced motion & accessibility, 15. Typography — optical sizing, tracking, leading, 16. Design foundations — the eight principles, 17. Process (+13 more)

### Community 86 - "The Fixes"
Cohesion: 0.09
Nodes (21): 10. Status bar color doesn't match, 11. Right in Chrome, wrong on phone, 1. Hover state stuck after tap, 2. Gray/blue flash on tap, 3. Layout has the wrong height, 4. Page zooms into the input, 5. Tap feels laggy, 6. Pull-to-refresh hijacks scroll (+13 more)

### Community 87 - "Chapter: Semantic Matching Evaluation & Knowledge Base Verification"
Cohesion: 0.07
Nodes (26): 1. Executive Summary & Evaluation Scope, 2.1 Canonical Knowledge Base & Taxonomy Structure, 2.2 Relationship Categories & Deterministic Policy Weights, 2.3 Rule Precedence Cascade, 2.4 Multi-Skill Scoring Formula, 2. Methodology & Mathematical Formulation, 3.1 Total Evaluation Case Construction (Total $N = 317$), 3.2 Match Type Distribution (Experiment A) (+18 more)

### Community 88 - "Prototyping Variants"
Cohesion: 0.10
Nodes (19): Behavior contract, Markup, Reference wiring, Rules, Styles, The Picker, Hard Rules, Initial Response (+11 more)

### Community 90 - "Delight Techniques"
Cohesion: 0.10
Nodes (20): Appropriate to Context, Assess Delight Opportunities, Celebration Moments, Compound Over Time, Context Gathering (Do This First), Delight Amplifies, Never Blocks, Delight Principles, Delight Techniques (+12 more)

### Community 91 - "Implement Animations"
Cohesion: 0.10
Nodes (19): Accessibility, Assess Animation Opportunities, Context Gathering (Do This First), CSS Animations, Delight Moments, Entrance Animations, Feedback & Guidance, Implement Animations (+11 more)

### Community 92 - "generate_grounded_xai_insights"
Cohesion: 0.20
Nodes (17): _build_deterministic_fallback(), _call_gemini_content(), generate_grounded_xai_insights(), Any, Makes HTTP request to Gemini API and parses JSON response., Safely extracts and parses JSON even if wrapped in markdown code fences or…, Constructs a deterministic, grounded rule-based summary when Gemini is…, Invokes the Google Gemini API to generate grounded, explainable AI insights for… (+9 more)

### Community 93 - "test_candidate_patch_rejects_forbidden_fields"
Cohesion: 0.40
Nodes (5): PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity., test_candidate_patch_rejects_forbidden_fields(), test_recruiter_patch_rejects_forbidden_fields(), parametrize

### Community 94 - "Glossary"
Cohesion: 0.11
Nodes (18): Animation Vocabulary, Easing — how speed changes over an animation, Entrances & Exits — how elements appear and disappear, Examples, Feedback & Interaction — responding to the user's actions, Glossary, Initial Response, Instructions (+10 more)

### Community 95 - "Introduce Color Strategically"
Cohesion: 0.11
Nodes (18): Accent Color Application, Accessibility, Assess Color Opportunity, Background & Surfaces, Balance & Refinement, Borders & Accents, Cohesion, Context Gathering (Do This First) (+10 more)

### Community 96 - "Design Critique"
Cohesion: 0.11
Nodes (18): 10. Microcopy & Voice, 1. AI Slop Detection (CRITICAL), 2. Visual Hierarchy, 3. Information Architecture, 4. Emotional Resonance, 5. Discoverability & Affordance, 6. Composition & Balance, 7. Typography as Communication (+10 more)

### Community 97 - "Animation Performance"
Cohesion: 0.11
Nodes (17): Animation Performance, Hard Rules, Initial Response, Operating Posture, Phase 1: Find what animates, Phase 2: Diagnose, Phase 3: Report, React: Don't Animate Through State (+9 more)

### Community 98 - "Finding Animation Opportunities"
Cohesion: 0.12
Nodes (16): 1. Frequency — how often will a user see this?, 2. Purpose — why does this animate?, 3. Speed — can it stay inside budget?, 4. Function — does motion help or hinder here?, Finding Animation Opportunities, Hard Rules, Initial Response, Operating Posture (+8 more)

### Community 99 - "Polish Systematically"
Cohesion: 0.12
Nodes (16): Code Quality, Color & Contrast, Content & Copy, Edge Cases & Error States, Final Verification, Forms & Inputs, Icons & Images, Interaction States (+8 more)

### Community 100 - "onboarding.js"
Cohesion: 0.20
Nodes (15): API_BASE, API_ENDPOINTS, CANDIDATE_STATUS_VALUES, COMPANY_TYPES, MESSAGES, ROLES, ROUTES, getStepsForRole() (+7 more)

### Community 101 - "extract_education"
Cohesion: 0.23
Nodes (14): extract_education(), extract_linkedin(), Heuristically extract highest degree level. Returns standard labels for…, Extract a LinkedIn profile URL., test_extract_education_bachelor(), test_extract_education_boundaries(), test_extract_education_case_insensitivity(), test_extract_education_master() (+6 more)

### Community 102 - "Implement Adaptations"
Cohesion: 0.13
Nodes (14): Assess Adaptation Challenge, Content Adaptation, Desktop Adaptation (Mobile → Desktop), Email Adaptation (Web → Email), Implement Adaptations, Layout Adaptation Techniques, Mobile Adaptation (Desktop → Mobile), Navigation Adaptation (+6 more)

### Community 103 - "Improve Copy Systematically"
Cohesion: 0.13
Nodes (14): Apply Clarity Principles, Assess Current Copy, Button & CTA Text, Confirmation Dialogs, Empty States, Error Messages, Form Labels & Instructions, Help Text & Tooltips (+6 more)

### Community 104 - "Simplify the Design"
Cohesion: 0.13
Nodes (14): Assess Current State, Code Simplification, Content Simplification, Context Gathering (Do This First), Document Removed Complexity, Information Architecture, Interaction Simplification, Layout Simplification (+6 more)

### Community 105 - "extract_text"
Cohesion: 0.15
Nodes (16): extract_text(), extract_text_from_docx(), extract_text_from_pdf(), Extract text from a DOCX file, including paragraphs and tables., Route to appropriate extractor based on extension., Extract text from a PDF file., Test fallback extraction with invalid UTF-8 bytes raises ValueError., Test legacy .doc files raise ValueError. (+8 more)

### Community 106 - "Generate Comprehensive Report"
Cohesion: 0.14
Nodes (13): Anti-Patterns Verdict, Critical Issues, Detailed Findings by Severity, Diagnostic Scan, Executive Summary, Generate Comprehensive Report, High-Severity Issues, Low-Severity Issues (+5 more)

### Community 107 - "Amplify the Design"
Cohesion: 0.14
Nodes (13): Amplify the Design, Assess Current State, Color Intensification, Composition Boldness, Context Gathering (Do This First), MANDATORY PREPARATION, Motion & Animation, Plan Amplification (+5 more)

### Community 108 - "Optimization Strategy"
Cohesion: 0.14
Nodes (13): Animation Performance, Assess Performance Issues, Core Web Vitals Optimization, Cumulative Layout Shift (CLS < 0.1), First Input Delay (FID < 100ms) / INP (< 200ms), Largest Contentful Paint (LCP < 2.5s), Loading Performance, Network Optimization (+5 more)

### Community 109 - "Working With Sonner"
Cohesion: 0.15
Nodes (11): Functions, Sonner API Reference, `toast()` options, `<Toaster />`, Initial Response, Picking the right call, Recipes, Setup (+3 more)

### Community 110 - "Frontend Aesthetics Guidelines"
Cohesion: 0.15
Nodes (12): Color & Theme, Design Direction, Frontend Aesthetics Guidelines, Implementation Principles, Interaction, Layout & Space, Motion, Responsive (+4 more)

### Community 111 - "Refine the Design"
Cohesion: 0.15
Nodes (12): Assess Current State, Color Refinement, Composition Refinement, Context Gathering (Do This First), MANDATORY PREPARATION, Motion Reduction, Plan Refinement, Refine the Design (+4 more)

### Community 112 - "Hardening Dimensions"
Cohesion: 0.17
Nodes (11): Accessibility Resilience, Assess Hardening Needs, Edge Cases & Boundary Conditions, Error Handling, Hardening Dimensions, Input Validation & Sanitization, Internationalization (i18n), Performance Resilience (+3 more)

### Community 113 - "The list"
Cohesion: 0.18
Nodes (10): Charts, Common mismatches to catch, How to use this, Initial Response, Interaction & performance, Motion & visuals, Picking The Right Library, State & styling (+2 more)

### Community 114 - "Design Engineering"
Cohesion: 0.22
Nodes (8): Accessibility, Design Engineering, Initial Response, prefers-reduced-motion, Review Checklist, Review Format (Required), Stagger Animations, Touch device hover states

### Community 115 - "Component Building Principles"
Cohesion: 0.25
Nodes (8): Animate enter states with @starting-style, Buttons must feel responsive, Component Building Principles, Make popovers origin-aware, Never animate from scale(0), Tooltips: skip delay on subsequent hovers, Use blur to mask imperfect transitions, Use CSS transitions over keyframes for interruptible UI

### Community 116 - "Step 2: Ask UX-Focused Questions"
Cohesion: 0.25
Nodes (7): Accessibility & Inclusion, Aesthetic Preferences, Brand & Personality, Step 1: Explore the Codebase, Step 2: Ask UX-Focused Questions, Step 3: Write Design Context, Users & Purpose

### Community 117 - "The Animation Decision Framework"
Cohesion: 0.33
Nodes (6): 1. Should this animate at all?, 2. What is the purpose?, 3. What easing should it use?, 4. How fast should it be?, Perceived performance, The Animation Decision Framework

### Community 118 - "clip-path for Animation"
Cohesion: 0.33
Nodes (6): clip-path for Animation, Comparison sliders, Hold-to-delete pattern, Image reveals on scroll, Tabs with perfect color transitions, The inset shape

### Community 119 - "Performance Rules"
Cohesion: 0.33
Nodes (6): CSS animations beat JS under load, CSS variables are inheritable, Framer Motion hardware acceleration caveat, Only animate transform and opacity, Performance Rules, Use WAAPI for programmatic CSS animations

### Community 120 - "Gesture and Drag Interactions"
Cohesion: 0.33
Nodes (6): Damping at boundaries, Friction instead of hard stops, Gesture and Drag Interactions, Momentum-based dismissal, Multi-touch protection, Pointer capture for drag

### Community 121 - "extract.md"
Cohesion: 0.33
Nodes (5): Discover, Document, Extract & Enrich, Migrate, Plan Extraction

### Community 122 - "CSS Transform Mastery"
Cohesion: 0.40
Nodes (5): 3D transforms for depth, CSS Transform Mastery, scale() scales children too, transform-origin, translateY with percentages

### Community 123 - "The Sonner Principles (Building Loved Components)"
Cohesion: 0.40
Nodes (5): Asymmetric enter/exit timing, Cohesion matters, Review your work the next day, The opacity + height combination, The Sonner Principles (Building Loved Components)

### Community 124 - "Spring Animations"
Cohesion: 0.40
Nodes (5): Interruptibility advantage, Spring Animations, Spring-based mouse interactions, Spring configuration, When to use springs

### Community 125 - "K"
Cohesion: 0.40
Nodes (5): A(), B(), F(), G(), K()

### Community 126 - "Core Philosophy"
Cohesion: 0.50
Nodes (4): Beauty is leverage, Core Philosophy, Taste is trained, not innate, Unseen details compound

### Community 127 - "Debugging Animations"
Cohesion: 0.50
Nodes (4): Debugging Animations, Frame-by-frame inspection, Slow motion testing, Test on real devices

### Community 128 - "normalize.md"
Cohesion: 0.50
Nodes (3): Clean Up, Execute, Plan

### Community 129 - ".execute"
Cohesion: 0.18
Nodes (10): extract_email(), extract_github(), extract_phone(), extract_projects(), extract_relevant_internships(), Very crude heuristic to determine the scale or presence of personal/academic…, Extract a GitHub profile URL., Extract a phone number found in the text. (+2 more)

### Community 130 - "seed_default_profiles"
Cohesion: 0.29
Nodes (6): Startup event handler: verify database connectivity and seed default profiles., startup_event(), Session, Checks if scoring profiles exist in the database; if not, seeds missing default…, seed_default_profiles(), on_event

### Community 133 - "legacy_process_resumes"
Cohesion: 0.29
Nodes (7): legacy_process_resumes(), limit, post, Request, Session, UploadFile, Legacy endpoint delegating to recruiter process_resumes. Requires Recruiter…

## Knowledge Gaps
- **737 isolated node(s):** `Settings`, `inflightGetRequests`, `uploadedFiles`, `sidebarLinkIds`, `COMPANY_TYPES` (+732 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `s` to `bf`, `gsap.min.js`, `recruiter.js`, `Tween`, `cb`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `stages.py`, `test_custom_scoring.py`, `backend/tests/test_recruiter.py`, `recruiter.py`, `get_profile`, `legacy_process_resumes`, `UpdateRecommendationPayload`, `test_password_reset.py`, `UserRole`, `auth.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `getCandidateDetailRowHTML()` connect `recruiter.js` to `s`, `app.js`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `CompanyType` and `ResumeStatus`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `UserRole` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`UserRole` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `CompanyType` (e.g. with `CandidateProfile` and `JobDescription`) actually correct?**
  _`CompanyType` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AnalysisContext` (e.g. with `AnalysisPipeline` and `ExplanationBuildingStage`) actually correct?**
  _`AnalysisContext` has 11 INFERRED edges - model-reasoned connections that need verification._