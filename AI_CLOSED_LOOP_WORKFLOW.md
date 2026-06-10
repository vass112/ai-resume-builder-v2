# AI Closed-Loop Development Workflow

A reusable, GitHub-native workflow where AI agents autonomously write, validate, and fix code using real toolchain feedback — with humans in the loop for decisions, reviews, and hard problems.

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Project Structure](#project-structure)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Agent Configuration](#agent-configuration)
5. [Issue-Driven Development](#issue-driven-development)
6. [Small Feature Workflow](#small-feature-workflow)
7. [Large Project Workflow](#large-project-workflow)
   - [Phase 1: Architecture](#phase-1-architecture)
   - [Phase 2: Scaffolding](#phase-2-scaffolding)
   - [Phase 3: Module-by-Module](#phase-3-module-by-module)
   - [Phase 4: Integration](#phase-4-integration)
   - [Phase 5: Sprint Contracts](#phase-5-sprint-contracts)
8. [Multi-Agent Collaboration](#multi-agent-collaboration)
9. [Handoff Protocol](#handoff-protocol)
10. [Dynamic Workflows](#dynamic-workflows)
11. [Human-AI Collaboration Patterns](#human-ai-collaboration-patterns)
12. [Validation Pipeline Reference](#validation-pipeline-reference)
13. [Checkpoints & State Recovery](#checkpoints--state-recovery)
14. [Documentation as Code](#documentation-as-code)
15. [Knowledge & Memory System](#knowledge--memory-system)
16. [Quick-Start Checklist](#quick-start-checklist)
17. [Example: Full Project Lifecycle](#example-full-project-lifecycle)
18. [Troubleshooting & Escalation](#troubleshooting--escalation)
19. [Comparative Analysis](#comparative-analysis)

---

## Philosophy

Every task — from a one-line bugfix to a 20-module architecture — follows the same loop:

```
Issue → Plan → Code → Validate → Fix → Pass → Merge → Close
```

**Rules:**
- No code merges without passing all validation layers
- Every artifact (code, tests, docs, migrations) is validated in the loop
- Humans approve architecture and review PRs; agents do the grunt work
- The workflow is the same at every scale — only the validation depth changes

---

## Project Structure

```
project/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Main CI pipeline
│   │   ├── pr-review.yml          # Auto-review agent on PRs
│   │   └── release.yml            # Tag & deploy
│   ├── CODEOWNERS                 # Agent/human ownership per module
│   └── ISSUE_TEMPLATE/
│       ├── feature.md             # Structured feature request
│       ├── bug.md                 # Structured bug report
│       └── epic.md                # Large project template
├── docs/
│   ├── ARCHITECTURE.md            # System design, updated per module
│   ├── CONTRIBUTING.md            # Workflow guide for humans + agents
│   └── adr/                       # Architecture Decision Records
│       └── ADR-0001-project-name.md
├── scripts/
│   ├── validate.sh                # Local validation (same as CI)
│   └── generate-docs.sh           # Doc generation pipeline
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .opencode/
│   ├── opencode.json              # Project-level agent config
│   └── agents.json                # Custom agent definitions
├── docker-compose.yml             # Full stack for integration tests
├── Dockerfile
├── Makefile                       # Dev convenience commands
├── README.md
└── codemeta.json                  # Project metadata (language, deps, etc.)
```

---

## CI/CD Pipeline

### `.github/workflows/ci.yml`

Every push triggers validation. The pipeline is layered — each stage blocks the next:

```yaml
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make lint        # ruff, eslint, prettier --check
      - run: make typecheck   # mypy, tsc, pyright

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test-unit   # pytest, vitest — fast (<30s)
      - run: make test-int    # testcontainers, drizzle — medium (<3m)

  coverage:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make coverage
      - run: make coverage-check  # fail if new code < 90%

  docs:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make docs-lint       # redocly, markdownlint
      - run: make docs-build      # verify docs generate without errors

  build:
    needs: [coverage, docs]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build           # docker build, npm build, etc.
```

### Makefile targets (reusable locally & in CI)

```makefile
lint:
	ruff check . && eslint src/ && prettier --check .

typecheck:
	mypy src/ && tsc --noEmit

test-unit:
	pytest tests/unit/ -x --timeout=30

test-int:
	pytest tests/integration/ -x --timeout=180

coverage:
	pytest --cov=src/ --cov-report=term --cov-report=xml

coverage-check:
	diff-cover coverage.xml --compare-branch=origin/main --fail-under=90

docs-lint:
	markdownlint docs/ && redocly lint docs/openapi.yaml

docs-build:
	mdbook build docs/  # or mkdocs, sphinx, etc.

build:
	docker compose build

validate: lint typecheck test-unit test-int coverage-check docs-lint docs-build build
```

---

## Agent Configuration

### `.opencode/opencode.json`

```jsonc
{
  "customCommands": [
    {
      "name": "validate",
      "command": "make validate",
      "description": "Run full validation pipeline"
    },
    {
      "name": "test",
      "command": "make test-unit",
      "description": "Run unit tests"
    },
    {
      "name": "coverage",
      "command": "make coverage && make coverage-check",
      "description": "Check test coverage"
    }
  ],
  "allowOnlyEnabledPlugins": false,
  "disabledPlugins": [],
  "enabledPlugins": [],
  "hooks": {
    "preCommit": ["validate"],
    "postCommit": []
  }
}
```

### `.opencode/agents.json`

```jsonc
{
  "agents": [
    {
      "name": "dev-agent",
      "description": "Writes implementation code per issue specs",
      "instructions": "Read the issue body and codebase conventions. Write code, tests, and docs. Validate with `make validate` before committing."
    },
    {
      "name": "review-agent",
      "description": "Reviews PRs for quality, security, and conventions",
      "instructions": "Check for: security issues, missing edge cases, deviation from ADRs, insufficient test coverage, documentation gaps."
    },
    {
      "name": "test-agent",
      "description": "Generates and improves test coverage",
      "instructions": "Read the module and existing tests. Generate missing tests. Run mutation testing to verify test quality."
    },
    {
      "name": "architect-agent",
      "description": "Designs system architecture and generates ADRs",
      "instructions": "Read project requirements. Generate ADRs with: context, decision, consequences. Include Mermaid diagrams."
    }
  ]
}
```

---

### Structured Progress Output

For long-running tasks, the agent updates a JSON schema in real time so humans (or CI) can track progress without reading the full conversation.

### Schema Template

```json
{
  "status": "in_progress",
  "current_task": "Implementing JWT refresh token rotation",
  "completed_tasks": [
    "Set up auth app structure",
    "Added User model with email/password",
    "Implemented JWT access token generation",
    "Added login endpoint with tests"
  ],
  "next_task": "Implement refresh token rotation",
  "blockers": [],
  "coverage": 87,
  "ci_status": "passing"
}
```

### How It Works

1. Agent receives a task
2. Agent creates `progress.json` at project root with the schema
3. Agent updates it after every meaningful step
4. Humans poll via `cat progress.json` or CI reads it
5. When task completes, status flips to `completed`

### Best Practices

- Include the full schema definition in the agent's instructions
- Define expected update frequency ("update after every file change")
- Use clear, descriptive field names
- Keep completed_tasks as an append-only list (never remove entries)
- The agent should write the progress file **before** making changes, **after** making changes, and **after** validation

---

## Issue-Driven Development

### Issue Templates

**Feature (`feature.md`)**
```markdown
## Description
*What should this feature do?*

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Notes
*Any constraints, existing patterns, or libraries to use*

## Validation
- [ ] Unit tests pass
- [ ] Integration tests pass  
- [ ] Docs updated
```

**Bug (`bug.md`)**
```markdown
## Steps to Reproduce
1. Go to ...
2. Do ...

## Expected Behavior
*What should happen*

## Actual Behavior
*What happens instead*

## Error Output
```
```

## Environment
- OS:
- Browser/Version:
```

## Acceptance Criteria
- [ ] Bug is fixed
- [ ] Regression test added
```

**Epic (`epic.md`)**
```markdown
## Vision
*What does this deliver when complete?*

## Modules
- [ ] Module A — *short description*
- [ ] Module B — *short description*

## Architecture Decisions Needed
- [ ] Decision 1

## Success Criteria
- [ ] All modules deliverable independently
- [ ] Integration test passes
- [ ] Docs generated
```

### Standard Issue Workflow

```
1. Issue filed with template → labeled `feature` / `bug` / `epic`
2. Agent assigned → reads issue body + codebase
3. Agent asks clarifying questions if acceptance criteria are vague
4. Agent works in `feat/<issue-number>-<short-name>` branch
5. Every push triggers CI
6. Agent fixes CI failures until green
7. Agent opens PR with: summary of changes, test coverage delta, docs updated
8. Review agent or human reviews
9. Squash-merge → issue closed with ref to PR
```

---

## Small Feature Workflow

For issues that touch 1-2 files and take < 30 min.

### Steps

1. **File issue** with acceptance criteria
2. **Dev Agent** reads issue, reads relevant files
3. **Writes code** following existing patterns
4. **Runs validation** (`make validate`)
5. **Fixes errors** — iterates until green
6. **Opens PR** with one-line summary
7. **Auto-merge** if all CI passes + review agent approves
8. **Issue closed**

### Example: Add Input Validation

```
Issue #14: "Validate email format on /signup"
  → Agent reads serializers.py
  → Adds EmailValidator with 3 test cases
  → make validate → fails (formats error message differently than existing validators)
  → Agent matches existing convention → re-runs → passes
  → Opens PR → auto-merged → #14 closed
  → Time: ~3 minutes
```

### Configuration

```yaml
# In CI: auto-merge for small changes
auto_merge_small:
  if: contains(github.event.pull_request.labels.*.name, 'small')
  runs-on: ubuntu-latest
  steps:
    - uses: actions/auto-merge@v1
```

---

## Large Project Workflow

For epics spanning multiple modules over weeks.

### Phase 1: Architecture

```
┌─────────────────────────────────────────────┐
│  Architect Agent                             │
│                                             │
│  Input:  Epic issue with vision             │
│  Output: ADR-0001 through ADR-000N          │
│          System diagram (Mermaid)           │
│          Module breakdown with boundaries   │
│          Tech stack decisions               │
│                                             │
│  Human:  Reviews ADRs → approves / revises  │
└─────────────────────────────────────────────┘
```

**ADR template:**

```markdown
# ADR-0001: Use PostgreSQL over MongoDB

## Context
We need persistent storage. Team is familiar with SQL. 
Data has relational structure.

## Decision
Use PostgreSQL 16 with pgvector for embedding search.

## Consequences
(+) Native JSON support, strong consistency, mature ORM
(-) Requires schema migrations, less flexible than NoSQL

## Status
Accepted
```

### Phase 2: Scaffolding

```
┌─────────────────────────────────────────────┐
│  DevOps Agent                                │
│                                             │
│  Creates:                                    │
│  - Repo structure                            │
│  - CI/CD workflows                           │
│  - Dockerfile + docker-compose.yml           │
│  - Makefile with all targets                 │
│  - README.md with setup instructions         │
│  - CONTRIBUTING.md with workflow guide       │
│  - Issue templates                           │
│  - codeowners                                │
│                                             │
│  Validates: docker compose up --build passes │
│             CI passes on first push          │
└─────────────────────────────────────────────┘
```

### Phase 3: Module-by-Module

Each module is a tracked GitHub Project item.

**Per module:**

```
1. Architect assigns module to Dev Agent via GitHub Project
2. Dev Agent reads module spec + ADRs + existing modules
3. Writes:
   - Implementation code
   - Unit tests (≥90% coverage for new code)
   - Integration tests
   - Module README (purpose, schema, examples, env vars)
   - OpenAPI spec (if API module)
   - Migration SQL (with rollback)
4. Validates independently: make validate
5. Opens PR → human reviews boundary decisions → merged
6. Module marked done in GitHub Project
```

### Phase 4: Integration

```
┌─────────────────────────────────────────────┐
│  Integration Agent                           │
│                                             │
│  Runs:                                       │
│  - Cross-module integration tests            │
│  - Contract tests between APIs               │
│  - E2E tests (full docker compose stack)     │
│  - Load test (if applicable)                 │
│                                             │
│  Generates:                                  │
│  - ARCHITECTURE.md (final)                   │
│  - Deployment guide                          │
│  - Troubleshooting guide                     │
│  - Changelog                                 │
│                                             │
│  Validates:                                  │
│  - docker compose up --build works end-to-end│
│  - All CI jobs green                         │
└─────────────────────────────────────────────┘
```

---

### Phase 5: Sprint Contracts

Before a module agent writes any code, it negotiates a **sprint contract** with the review agent — agreeing on what "done" looks like for that chunk of work. This prevents the agent from building the wrong thing.

```
┌─────────────────────────────────────────────┐
│  Sprint Contract (negotiated per module)    │
│                                             │
│  Generator Agent proposes:                  │
│  - What I will build (scope)                │
│  - How I will verify success (tests)        │
│  - What I will NOT build (exclusions)       │
│                                             │
│  Review Agent evaluates:                    │
│  - Does the scope match the ADR?            │
│  - Are acceptance criteria testable?        │
│  - Are there missing edge cases?            │
│                                             │
│  Iterate until both agree → contract saved  │
│  as `docs/contracts/module-auth.md`         │
└─────────────────────────────────────────────┘
```

**Contract format:**

```markdown
# Sprint Contract: Authentication Module

## Scope
- JWT-based login/signup with refresh tokens
- Password hashing with bcrypt
- Session management (Redis-backed)

## Out of Scope
- OAuth providers (Google, GitHub) — Phase 2
- MFA/2FA — not required

## Verification
- 15 unit tests, 5 integration tests
- Coverage ≥ 92%
- Security audit: no plaintext passwords, no hardcoded secrets
- API contract: response format matches openapi.yaml

## Dependencies
- auth service depends on: Redis (session store)
- auth service is depended on by: payments, documents
```

The contract is committed to `docs/contracts/` before any implementation starts. The review agent holds the generator to this contract during PR review — if the implementation deviates, the PR is rejected.

---

## Multi-Agent Collaboration

### Roles & Responsibilities

```
┌──────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                     │
│  - Reads epic, creates module issues                     │
│  - Assigns agents                                        │
│  - Tracks blockers, escalates to humans                  │
│  - Validates cross-cutting concerns                      │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
     ┌─────────▼─────────┐   ┌───────▼─────────┐
     │   MODULE A AGENT  │   │  MODULE B AGENT  │
     │                   │   │                  │
     │  - Code           │   │  - Code          │
     │  - Tests          │   │  - Tests         │
     │  - Module README  │   │  - Module README │
     │  - CI green       │   │  - CI green      │
     └─────────┬─────────┘   └───────┬──────────┘
               │                      │
               └──────────┬───────────┘
                          │
              ┌───────────▼────────────┐
              │    REVIEW AGENT        │
              │                        │
              │  - Code quality        │
              │  - Security scan       │
              │  - Convention check    │
              │  - Coverage check      │
              └────────────────────────┘
```

### Communication Between Agents

Agents communicate through git commits and issue comments:

```
Agent A commits: "feat(auth): add JWT token generation"
Agent A issues:  "Schema change in auth/models.py — needs migration"
Agent B reads:   "I see auth added JWT. My payments module will consume it.
                  Adding integration test for auth→payments flow."
```

### Avoiding Conflicts

- Each agent works in its own branch (`feat/auth`, `feat/payments`)
- Shared interfaces are documented in ADRs before any agent starts
- Integration agent catches contract violations before merge
- Git merge conflicts are handled by the agent that owns the later branch

---

## Handoff Protocol

Structured transitions between specialized agents with review gates at each step.

### Handoff Types

| Type | When | Behavior |
|---|---|---|
| **Sequential** | Task depends on another (architect → dev → review) | Agent finishes, triggers next agent, blocks until done |
| **Parallel** | Independent subtasks (module A + module B) | Orchestrator fans out, collects results, resolves conflicts |
| **Escalation** | Agent hits blocker it can't resolve | Summarizes attempts, assigns to human, blocks |
| **Review Gate** | Output needs validation before next step | Dev agent → Review agent → (pass/fail) → Next agent |
| **Handback** | Human provides guidance, returns to agent | Human comments on PR → Agent reads, fixes, re-runs CI |

### Sequential Handoff Flow

```
┌──────────┐    ADRs    ┌──────────┐    code + tests    ┌──────────┐    approved?    ┌──────────┐
│ Architect │ ────────→ │   Dev    │ ──────────────────→ │  Review  │ ──────────────→ │    CI    │
│   Agent   │           │  Agent   │                     │  Agent   │                 │          │
└──────────┘           └──────────┘                     └──────────┘                 └──────────┘
     │                      │                                │                            │
     │ done                 │ PR ready                        │ approve?                   │ green
     ▼                      ▼                                ▼                            ▼
  blocked              Review Gate                      if fail: back to Dev         Merge
```

### Handoff Manifest

When an agent completes its work, it writes a **handoff manifest** so the receiving agent can pick up without reading the full conversation:

```markdown
# Handoff: Dev Agent → Review Agent

## Completed
- feat(auth): JWT token generation (abc1234)
- feat(auth): login/signup endpoints (abc1235)
- test(auth): 15 unit tests, 5 integration tests

## Decisions Made
- Token expiry: 15 min access, 7 day refresh
- Session store: Redis (matching ADR-0003)

## Open Questions
- [ ] Should rate limiting be per-user or per-IP?
- [ ] Password complexity rules not specified in issue

## Validation Results
- make lint: ✅
- make typecheck: ✅
- make test-unit: 15/15 ✅
- make test-int: 5/5 ✅
- make coverage: 94% ✅

## File Changes
- src/auth/views.py (new)
- src/auth/models.py (new)
- src/auth/serializers.py (new)
- src/auth/test_*.py (new)
- docs/modules/auth.md (new)
```

The manifest is saved at `docs/handoffs/agent-dev-to-review-2026-06-10.md` and the receiving agent reads it as its first action.

---

## Dynamic Workflows

For large-scale operations that need more coordination than a single agent conversation can handle — codebase audits, 500-file migrations, multi-model cross-checks.

### When to Use

| Scenario | Why Dynamic Workflow |
|---|---|
| Codebase-wide bug sweep | Too many files for one context window |
| Language migration (Python 3.11 → 3.14) | Repetitive pattern across N files |
| Dependency audit | Check every package against CVE database |
| Style reformat across 500+ files | Parallel execution, deterministic output |
| Multi-model validation | Run same task with Claude, GPT, Gemini, compare results |

### How It Works

```
1. Orchestrator Agent writes a workflow script (JS/Python)
   that defines: what agents to spawn, what tools they get,
   how results are collected, what counts as success

2. Workflow script is saved as `.opencode/workflows/<name>.mjs`
   and version-controlled

3. Runtime executes the script, spawning sub-agents:
   - Each sub-agent gets isolated context
   - Sub-agents read files, make edits, run commands
   - Results stream back to orchestrator

4. Orchestrator collects all results, resolves conflicts,
   and produces a summary
```

### Example: Codebase Audit Workflow

```javascript
// .opencode/workflows/audit-eslint.mjs
const audit = new Workflow();

const files = await glob("src/**/*.{ts,tsx}");

// Spawn 8 parallel sub-agents, each auditing a file batch
const batches = chunk(files, Math.ceil(files.length / 8));

for (const batch of batches) {
  audit.spawn({
    agent: "code-reviewer",
    task: `Audit these files for eslint violations. 
           For each file: run `npx eslint`, parse errors,
           fix auto-fixable issues, report remaining.`,
    files: batch,
    tools: ["read_file", "edit_file", "run_terminal"],
  });
}

const results = await audit.collect();
const allPassed = results.every(r => r.passed);

if (!allPassed) {
  audit.report({
    summary: `Audited ${files.length} files, ${results.filter(r => !r.passed).length} need manual review`,
    failedFiles: results.filter(r => !r.passed).map(r => r.file),
  });
}
```

### Constraints

| Constraint | Reason |
|---|---|
| No mid-run human input | Workflow must be fully scripted |
| Up to 16 concurrent sub-agents | Resource bound on local machine |
| 1,000 total agent calls per run | Prevents runaway loops |
| Each sub-agent gets isolated context | No context window overflow |

### Configuration

Add to `.opencode/opencode.json`:

```jsonc
{
  "workflows": {
    "dir": ".opencode/workflows",
    "maxConcurrentAgents": 16,
    "maxAgentCallsPerRun": 1000,
    "timeoutPerAgent": 180000
  }
}
```

---

## Human-AI Collaboration Patterns

### Pattern 1: Pair Programming

```
Human writes the tricky algorithm → Agent handles everything else

Human:  [commits core algorithm in utils.py]
Agent:  "I'll add type hints, param validation, 3 test cases, 
         and document the edge cases you handled"
```

### Pattern 2: Review Loop

```
Agent opens PR → Human reviews → Agent addresses feedback → CI re-runs → Merge

[Agent PR]
   ↓
Human: "This should handle null user case"
   ↓
Agent reads comment → fixes → re-runs CI → "Fixed in 8a3f12c"
   ↓
Human approves → merged
```

### Pattern 3: Escalation

```
Agent hits a blocker → summarizes options → assigns to human

Agent: "Two approaches for session storage:
        1. Redis (fast, needs infra)
        2. SQLite (simple, doesn't scale)
        Context: we already have Redis for caching.
        Recommend: use Redis. @arjun please confirm."
```

### Pattern 4: Human-Required Gates

```yaml
# In CI: staged approval
deploy:
  environment: production
  steps:
    - name: Wait for human approval
      uses: trstringer/manual-approval@v1
      with:
        approvers: tech-lead
    - name: Deploy
      run: make deploy
```

### Pattern 5: Intern + Agent Pairing

```
1. Intern writes issue with specs
2. Agent generates implementation + tests
3. Intern reviews — checks understanding, not just correctness
4. Intern merges — owns the outcome
5. Intern learns from the agent's reasoning (why this pattern, not that one)
```

**Productivity gain:** Intern ships features at senior-dev velocity while building understanding of architecture patterns.

### Pattern 6: Plan Mode

Before writing code, the agent researches the codebase, asks clarifying questions, and produces a reviewable plan:

```
Agent: "I'll plan before coding. Here's what I found:
       - auth/models.py has the User model
       - Existing tests use pytest fixtures
       - Project uses JWT via pyjwt library

       My plan:
       1. Add EmailValidator to UserSerializer
       2. Add test cases: valid email, invalid email, empty
       3. Update docs/modules/auth.md

       Is this correct, or should I handle anything else?"

Human: "Also validate on the model level, not just serializer"
  → Agent adjusts plan
  → Writes code
  → Validates
  → Merges
```

Use when: ambiguous requirements, high-risk changes, or when the human wants to steer before code is written.

---

## Validation Pipeline Reference

### Layer Details

| Layer | Tool | Scope | Target Time | Failure Action |
|---|---|---|---|---|
| **Lint** | ruff, eslint, prettier | Style, anti-patterns, imports | <5s | Fix formatting, re-run |
| **Typecheck** | mypy, tsc, pyright | Type safety, null safety, interface conformance | <10s | Fix type errors, re-run |
| **Unit tests** | pytest, vitest | Logic correctness per function/class | <30s | Debug failing test, fix code, re-run |
| **Integration tests** | testcontainers, drizzle | API contracts, DB queries, cross-module | <3m | Check agent logs, fix contract |
| **Coverage** | diff-cover | New code ≥ 90%, no regressions | <10s | Add missing tests, re-run |
| **Doc lint** | markdownlint, redocly | Documentation validity, link health | <5s | Fix broken links, re-run |
| **Doc build** | mdbook, mkdocs, sphinx | Doc generation compiles | <10s | Fix doc errors, re-run |
| **Build** | docker, npm, maven | Artefact compiles, container builds | <2m | Fix build errors, re-run |

### Expected Iteration Count

| Task Type | Avg Iterations | Max Iterations | Escalate After |
|---|---|---|---|
| Simple bugfix | 1 | 3 | 5 failures |
| New small feature | 2 | 5 | 8 failures |
| New module | 4 | 10 | 15 failures |
| Refactor | 3 | 8 | 12 failures |
| Cross-module change | 5 | 12 | 20 failures |

### Failure Escalation

When an agent exceeds max iterations:

```
1. Agent logs a summary of every attempt and why it failed
2. Creates a GitHub Discussion or issue tagged `blocked` with the summary
3. Mentions the relevant human via @mention
4. Assignes the blocker to the human
5. Moves on to the next task (if orchestrator) or waits
```

---

## Checkpoints & State Recovery

Automatic snapshots before significant changes, enabling rollback without polluting git history.

### How Checkpoints Work

```
Before any state-changing operation (multi-file edit, migration, refactor):

  1. Agent creates checkpoint: snapshot of all modified files
  2. Agent stamps it with: timestamp, task description, current git HEAD
  3. Agent proceeds with changes
  4. If validation fails → agent can restore to checkpoint
  5. If validation passes → checkpoint is tagged as "verified"
```

### Checkpoint Storage

```
.opencode/
  checkpoints/
    2026-06-10T14:30:00Z/
      task.json          # Description, issue ref, git HEAD
      files/             # Copy of all files before changes
        src/auth/views.py
        src/auth/models.py
      verified           # File exists if validation passed
```

### Recovery Scenarios

| Scenario | Action |
|---|---|
| Validation fails after edit | Restore checkpoint, analyze failure, retry |
| Agent context window fills | Save checkpoint, start new session, load checkpoint |
| Wrong approach discovered mid-task | Restore checkpoint, document why approach was wrong |
| CI detects regression after merge | Revert merge, checkpoint has the "before" state |

### Long-Running Session Recovery

For sessions that span hours (large refactors, migrations):

```
1. Initializer agent runs first:
   - Sets up project structure
   - Writes `PROGRESS.md` with full feature list (all marked "failing")
   - Creates initial git commit
   - Creates checkpoints directory

2. Coding agent runs each subsequent session:
   - Reads PROGRESS.md to understand what's done
   - Reads latest checkpoint to restore working state
   - Makes incremental progress
   - Updates PROGRESS.md (mark features as "passing")
   - Commits to git with descriptive message
   - Writes checkpoint

3. If agent crashes or context overflows:
   - New session starts
   - Reads PROGRESS.md
   - Reads latest checkpoint
   - Continues where previous left off
```

### PROGRESS.md Format

```json
{
  "project": "Paperwriter",
  "features": [
    {"id": "auth-login",     "description": "User can log in with email + password",   "passes": true},
    {"id": "auth-signup",    "description": "User can create an account",              "passes": true},
    {"id": "auth-oauth",     "description": "User can log in with Google/GitHub",      "passes": false},
    {"id": "doc-create",     "description": "User can create a new document",          "passes": false}
  ],
  "current_sprint": "Authentication",
  "checkpoints": [
    {"id": "ckpt-001", "time": "2026-06-10T14:30Z", "status": "verified", "features": 2},
    {"id": "ckpt-002", "time": "2026-06-10T15:45Z", "status": "verified", "features": 2},
    {"id": "ckpt-003", "time": "2026-06-10T17:00Z", "status": "active", "features": 2}
  ]
}
```

The agent **only** edits the `passes` field — never removes features. This ensures the full scope is always visible.

---

## Documentation as Code

Every documentation artifact is generated alongside code and validated in CI.

### What to Generate

| Artifact | When | Agent | Validated By |
|---|---|---|---|
| `README.md` | Scaffolding | DevOps | Links work, setup instructions executable |
| `CONTRIBUTING.md` | Scaffolding | DevOps | Steps match actual workflow |
| `ADR-0001.md` | Architecture | Architect | Consistent format, referenced in code |
| `ARCHITECTURE.md` | Integration | Integration | Mermaid renders, module list complete |
| `docs/modules/auth.md` | Module done | Dev Agent | Schema matches migration, examples work |
| `api/openapi.yaml` | Module done | Dev Agent | `redocly lint` passes |
| `CHANGELOG.md` | Integration | Orchestrator | Entries match conventional commits |
| `docs/deploy.md` | Integration | Integration | Steps work in `--dry-run` |
| `docs/troubleshooting.md` | Integration | Integration | Known errors and solutions |
| `codemeta.json` | Scaffolding | DevOps | Schema valid |

### Documentation Validation

```makefile
# docs-lint target
docs-lint:
	markdownlint docs/ --ignore docs/api/
	redocly lint docs/api/openapi.yaml
	# Verify all internal links resolve
	find docs/ -name "*.md" -exec grep -oP '\[.*?\]\(\K[^)]+' {} \; | while read link; do
		if echo "$$link" | grep -q '^http'; then continue; fi
		if [ ! -f "docs/$$link" ]; then echo "Broken link: $$link"; exit 1; fi
	done
```

---

## Knowledge & Memory System

Persistent context that survives across sessions — the agent's long-term memory about the project.

### Three-Tier Knowledge

| Tier | Location | Scope | Persistence | Created By |
|---|---|---|---|---|
| **Project Knowledge** | `docs/knowledge/` | This repo | Version-controlled | Agent auto-generates, humans curate |
| **Agent Memory** | `.opencode/memory/` | This repo | Local only, not committed | Agent auto-generates |
| **Global Knowledge** | `~/.opencode/knowledge/` | All projects | Machine-local | Agent auto-generates |

### Project Knowledge (`docs/knowledge/`)

Auto-generated and version-controlled facts about the codebase:

```
docs/knowledge/
  structure.md       # Module map: what each directory does, language, toolchain
  decisions.md       # Key decisions with rationale (why not X, why Y)
  patterns.md        # Recurring code patterns (error handling, DB queries, API style)
  gotchas.md         # Tricky parts: known footguns, subtle behaviors
  glossary.md        # Domain-specific terms and abbreviations
  team.md            # Team conventions, PR preferences, reviewer assignments
```

**How it gets created:**

```
1. After Phase 1 (Architecture): Agent generates structure.md from module breakdown
2. After each module: Agent appends patterns and gotchas discovered during implementation
3. After code review: Agent captures review feedback as patterns (avoid this, prefer that)
4. After bug fix: Agent adds root cause to gotchas.md
```

**Example: `patterns.md`**

```markdown
# Code Patterns

## Error Handling
- All API errors return `{"error": "<code>", "detail": "<message>"}`
- Use `AppException` base class, never raise raw HTTPException
- Always log the full traceback server-side, return sanitized message to client

## Database Queries
- Use async SQLAlchemy 2.0 style (`select()` not `Query()`)
- Always use `with_for_update()` for transactional balance updates
- Add `limit` + `offset` to all list endpoints (default 50, max 500)

## Testing
- One factory per model (factory_boy)
- Use pytest marks: `@pytest.mark.slow` for integration tests
- Snapshot test all API response schemas
```

### Agent Memory (`.opencode/memory/`)

Local-only, session-to-session memory. The agent writes notes about what it learned, what it tried, and what didn't work:

```json
{
  "sessions": [
    {
      "id": "session-2026-06-10-auth",
      "task": "Implement JWT auth",
      "learnings": [
        "pyjwt >= 2.8 required for Ed25519 keys",
        "Redis session timeout must match token expiry"
      ],
      "attempted": [
        {"approach": "PyJWT standalone", "result": "failed", "reason": "no refresh token support"},
        {"approach": "PyJWT + django-rest-framework-simplejwt", "result": "passed"}
      ],
      "preferred_approach": "simplejwt for standard JWT, custom for refresh rotation"
    }
  ]
}
```

Before starting a new task, the agent reads `.opencode/memory/` to avoid repeating failed approaches.

### Memory Lifecycle

```
Creation:
  → Agent discovers a pattern during implementation
  → Writes to patterns.md (or memory.json for per-session notes)

Refinement:
  → On next related task, agent reads existing knowledge
  → If knowledge is wrong or outdated → agent corrects it
  → If knowledge is still accurate → agent reaffirms it

Eviction:
  → Knowledge that hasn't been referenced in 10 sessions
  → Agent prompts: "This knowledge hasn't been used. Delete or keep?"
  → Human decides
```

### Configuration

Add to `.opencode/opencode.json`:

```jsonc
{
  "knowledge": {
    "projectDir": "docs/knowledge",
    "memoryDir": ".opencode/memory",
    "maxMemorySessions": 100,
    "autoGenerate": true,
    "autoEvictAfterSessions": 10
  }
}
```

---

## Quick-Start Checklist

- [ ] Create repo with README, LICENSE, .gitignore
- [ ] Set up `.github/ISSUE_TEMPLATE/` — feature, bug, epic
- [ ] Create `.github/workflows/ci.yml` with layered pipeline
- [ ] Create `Makefile` with lint, typecheck, test, coverage, docs, build targets
- [ ] Create `Dockerfile` + `docker-compose.yml`
- [ ] Run `make validate` — should pass on empty/initial project
- [ ] Set up `.opencode/opencode.json` with validate command
- [ ] Push to GitHub — CI should run and pass

### Day 1 — Architecture

- [ ] Write ADR-0001: Tech stack decisions
- [ ] Write ADR-0002: Module breakdown
- [ ] Write ADR-0003: Database schema (if applicable)
- [ ] Create GitHub Project board with epic columns
- [ ] Create issues for each module

### Per Module

- [ ] Issue filed with acceptance criteria
- [ ] Agent assigned
- [ ] Branch created: `feat/<issue-number>-<name>`
- [ ] Code written with tests
- [ ] Module README generated
- [ ] CI green
- [ ] PR opened with summary
- [ ] Human reviewed / agent reviewed
- [ ] Merged to main
- [ ] Issue closed

### Per Release

- [ ] Integration tests pass end-to-end
- [ ] ARCHITECTURE.md regenerated
- [ ] CHANGELOG.md updated
- [ ] Deployment guide validated
- [ ] Tag and release created

---

## Example: Full Project Lifecycle

### Project: Paperwriter (AI-powered academic paper editor)

| Phase | Duration | Activity |
|---|---|---|
| **Architecture** | Day 1 | Architect agent writes 5 ADRs: Django REST + React + PostgreSQL + Gemini API + GitHub Pages docs |
| **Scaffolding** | Day 1-2 | DevOps agent creates: repo structure, CI/CD, Docker, Makefile, issue templates, CONTRIBUTING.md |
| **Auth module** | Day 2-3 | Dev agent: JWT auth, user model, login/signup pages, tests |
| **Document module** | Day 3-5 | Dev agent: document CRUD, rich text editor, version history, tests |
| **AI module** | Day 5-7 | Dev agent: Gemini API integration, prompt templates, streaming response, tests |
| **Export module** | Day 7-8 | Dev agent: LaTeX export, PDF generation, citation formatting, tests |
| **Integration** | Day 8-9 | Integration agent: cross-module tests, E2E (docker compose), load tests. Generates ARCHITECTURE.md, deployment guide |
| **Polish** | Day 9-10 | Performance agent: caching, query optimization. Security agent: auth audit, input sanitization. Docs agent: final README, troubleshooting |
| **Ship** | Day 10 | Release agent: tag v1.0.0, generate changelog, deploy to staging |

Each day produces **merged, validated, documented** output. At any point you can stop and have a working product.

---

## Troubleshooting & Escalation

### Common Failures

| Symptom | Likely Cause | Fix |
|---|---|---|
| CI fails on lint | Agent didn't run formatter | Re-run with `make format && make lint` |
| Typecheck fails | Wrong type annotation or missing import | Read error, fix signature |
| Unit test fails | Logic error or wrong assumption | Read test output, fix implementation |
| Integration test fails | Module contract mismatch | Check the API response format |
| Coverage below threshold | Missing edge case tests | Add parameterized tests |
| Docker build fails | Missing dependency or config change | Check Dockerfile against requirements |
| Doc links broken | File renamed without updating docs | Search and replace references |

### Escalation Process

When an agent cannot resolve after max iterations:

```
1. Agent writes to issue: "BLOCKER: [summary]"
2. Lists 3 attempted solutions and why each failed
3. Adds `blocked` label
4. @mentions the human assigned to the module
5. Attaches CI logs from failed attempts

The human can then:
  - Provide guidance ("Use approach X, not Y")
  - Override ("Skip this validation for now")
  - Take over ("I'll handle this, move to next task")
```

### Recovery

If a merge causes regression:

```
1. CI on main fails
2. Rollback agent: revert the merge commit
3. Analyzes what went wrong
4. Opens fix PR
5. Re-applies the original feature + fix
```

---

## Comparative Analysis: What Each System Does Best

| System | Best-In-Class Feature | Why It Matters | Where to Integrate |
|---|---|---|---|
| **GitHub Copilot** | Custom agents as `.agent.md` in `.github/agents/` with YAML frontmatter + handoffs | Standardized, shareable, version-controlled agent definitions | Adopt `.agent.md` format + handoffs protocol |
| **GitHub Copilot** | Skills (`SKILL.md` with `description` — auto-injected by relevance) | Agent auto-discovers relevant instructions without prompting | Add skills dir to project structure |
| **Devin (Cognition)** | Knowledge system — auto-generated repo knowledge, persistent across sessions | Agent doesn't re-learn the codebase every session | Three-tier knowledge system (project/agent/global) |
| **Devin** | Parallel managed Devins — coordinator breaks task into parallel sub-agents | Scales to large codebases; one orchestrator + N workers | Dynamic Workflows section |
| **Devin** | Confidence scoring — agent auto-analyzes tickets and scores feasibility | Helps humans prioritize; surfaces vague issues before work starts | Add confidence score to issue triage |
| **Claude Code** | Dynamic workflows — JS script orchestrates 16 parallel sub-agents | Context window overflow solved: script holds the loop, not the LLM | Full section added above |
| **Claude Code** | Sprint contracts — generator + evaluator negotiate "done" before coding | Prevents building wrong thing; shared definition of done | Full section added above |
| **Claude Code** | Multi-context window harness — initializer sets up, coding agents make incremental progress | Sessions can run for hours without context overflow | Checkpoints & State Recovery section |
| **Claude Code** | Ultracode — auto-plans workflow for every substantive task | No manual decision to use workflow; agent escalates automatically | Add as configuration option |
| **OpenHands** | Event-sourced state — append-only event log, deterministic replay | Debug sessions by replaying every step | Future enhancement for agent SDK |
| **OpenHands** | Workspace abstraction — same agent runs locally or in Docker without code changes | Development → CI → production parity | Adopt `Workspace` abstraction in agent config |
| **Cursor** | Checkpoints — automatic snapshots before significant changes (separate from git) | Safe exploration without git pollution; restore to any point | Checkpoints & State Recovery section |
| **Cursor** | Plan mode — research codebase, ask questions, generate reviewable plan before coding | Catches misunderstandings early; human steers before code written | Human-AI Pattern 6: Plan Mode |
| **Cursor** | Multi-root workspaces — one agent session across multiple repos | Cross-repo refactors in a single session | Future: cross-repo workflows |
| **Windsurf** | Rules hierarchy — Global → `.windsurfrules` → Workspace Rules → Memories | Clear precedence; different scopes for different concerns | Adopt 4-tier rules hierarchy |
| **Windsurf** | Memories — persistent facts across sessions, auto-generated | Agent remembers context without manual knowledge files | Part of Knowledge & Memory section |
| **Windsurf** | Workflows — reusable `.md` files as slash commands | Repeatable procedures without prompting | `.opencode/workflows/` dir |

### Key Takeaways

1. **Agent definitions in `.agent.md` files** (GitHub Copilot pattern) — this is becoming the industry standard. Adopt it over raw JSON config.

2. **Three-tier knowledge** (Devin + Windsurf) — separate project rules from agent memory from global preferences. Each has different persistence and scope.

3. **Checkpoints + Progress files** (Cursor + Claude Code) — essential for long-running sessions. Without them, a single context overflow loses all progress.

4. **Sprint contracts** (Claude Code) — adds a negotiation step before coding that prevents the most common agent failure: building the wrong thing.

5. **Dynamic workflows** (Claude Code + Devin) — the only way to scale past a single agent's context window. Write the orchestration as a script, not as a prompt.

### Concrete Recommendations for Your First Project

```
Day 1 setup priorities:
  1. .agent.md agent definitions  (from GitHub Copilot)
  2. Four-tier rules file         (from Windsurf)
  3. docs/knowledge/ directory    (from Devin)
  4. make validate                (from closed-loop core)

Day 1 architecture:
  5. ADRs in docs/adr/            (from closed-loop core)
  6. Sprint contract template     (from Claude Code)

First module:
  7. Handoff manifests            (from GitHub Copilot)
  8. Checkpoints on every edit    (from Cursor)
  9. PROGRESS.md for long sessions(from Claude Code)

After first module:
  10. Capture patterns in docs/knowledge/patterns.md
  11. Archive failed attempts in .opencode/memory/
```

---

## Summary

| Aspect | Approach |
|---|---|
| **Granularity** | One issue = one unit of work, small or large |
| **Validation** | Layered: lint → typecheck → test → coverage → docs → build |
| **Agents** | Specialized per role (dev, review, test, architect, integration) |
| **Humans** | Write ADRs, review PRs, handle blockers, approve deploys |
| **Docs** | Generated alongside code, validated in CI |
| **Scale** | N agents = N features in parallel |
| **Recovery** | Auto-revert on CI failure, analyze, fix, re-apply |

Every project starts the same way: scaffolding + ADRs. Every feature follows the same loop: plan → code → validate → fix → merge. Every agent reports through the same channel: GitHub issues + PRs.

The workflow doesn't change between a 10-line bugfix and a 20,000-line monorepo. Only the validation depth and iteration count scale.
