param(
  [string]$ProjectDir = (Get-Location),
  [string]$Lang = "python",
  [string]$WorkflowDoc = "$env:USERPROFILE\AppData\Local\Temp\opencode\AI_CLOSED_LOOP_WORKFLOW.md"
)

Write-Host "==> Bootstrapping closed-loop AI workflow in: $ProjectDir" -ForegroundColor Cyan

# --------------- .opencode/ ---------------
New-Item -ItemType Directory -Force -Path "$ProjectDir\.opencode\checkpoints" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectDir\.opencode\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectDir\.opencode\workflows" | Out-Null

@'
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md"],
  "references": {
    "workflow": {
      "path": "AI_CLOSED_LOOP_WORKFLOW.md",
      "description": "Closed-loop AI development workflow: validation pipeline, agent roles, handoff protocol, sprint contracts"
    }
  },
  "command": {
    "validate":      { "description": "Run full validation pipeline", "prompt": "Run make validate" },
    "coverage":      { "description": "Check test coverage (≥90% new code)", "prompt": "Run make coverage && make coverage-check" },
    "handoff":       { "description": "Write a handoff manifest", "prompt": "Write a handoff manifest to docs/handoffs/ with completed, decisions, open questions, validation results, file changes" },
    "sprint-sign":   { "description": "Negotiate a sprint contract before module work", "prompt": "Read the ADRs and issue spec, then propose a sprint contract. Save to docs/contracts/ when agreed." },
    "checkpoint":    { "description": "Create a state checkpoint before significant changes", "prompt": "Create a checkpoint snapshot under .opencode/checkpoints/<timestamp>/ before proceeding" }
  },
  "agent": {
    "dev-agent": {
      "description": "Writes implementation code per issue specs and validates via CI",
      "mode": "subagent",
      "prompt": "You are a dev agent. Read the issue body, ADRs, and sprint contract. Write code, tests, and module docs. Run `make validate` before committing. Create a checkpoint before any multi-file edit. Write a handoff manifest when done."
    },
    "review-agent": {
      "description": "Reviews PRs against sprint contracts and ADRs",
      "mode": "subagent",
      "permission": { "edit": "deny", "bash": "ask" },
      "prompt": "You are a review agent. Check PRs for: deviations from ADRs, security issues, missing edge cases, coverage <90%, missing docs, sprint contract violations. Reject with specific reasons."
    },
    "architect-agent": {
      "description": "Designs system architecture and writes ADRs",
      "mode": "subagent",
      "prompt": "You are an architect agent. Read the epic issue and write ADRs covering: context, decision, consequences, status. Include Mermaid diagrams. Save to docs/adr/."
    }
  },
  "skills": {
    "paths": [".opencode/skills"]
  }
}
'@ | Set-Content -Path "$ProjectDir\.opencode\opencode.json" -Encoding UTF8

# --------------- .opencode/skills/workflow/SKILL.md ---------------
New-Item -ItemType Directory -Force -Path "$ProjectDir\.opencode\skills\workflow" | Out-Null
@'
---
name: workflow
description: Use when setting up project structure, writing CI, creating agent configs, or following the closed-loop development workflow.
---

# Workflow Skill

Follow the closed-loop AI development workflow from @workflow.

1. **Project Setup** — `.github/workflows/ci.yml`, `Makefile`, `Dockerfile`, `.opencode/`, `AGENTS.md`
2. **Architecture** — Architect agent writes ADRs with Mermaid diagrams
3. **Sprint Contract** — Before coding a module, negotiate scope/verification/dependencies
4. **Implementation** — Dev agent writes code, tests, docs; validates with `make validate`; creates checkpoints before multi-file edits
5. **Handoff** — After completing work, write a handoff manifest
6. **Integration** — Cross-module tests, E2E, final docs
'@ | Set-Content -Path "$ProjectDir\.opencode\skills\workflow\SKILL.md" -Encoding UTF8

# --------------- AGENTS.md ---------------
@'
# Project Workflow

This project follows the closed-loop AI development workflow in `AI_CLOSED_LOOP_WORKFLOW.md` (@workflow).

## Rules
- Run `make validate` before every commit
- Every issue: issue → plan → code → validate → fix → pass → merge → close
- New modules: negotiate sprint contract first
- After work: write handoff manifest to docs/handoffs/
- Before multi-file edits: create checkpoint
- Capture patterns in docs/knowledge/

## Commands
- `@validate` — full validation
- `@coverage` — test coverage check
- `@handoff` — write handoff manifest
- `@sprint-sign` — negotiate sprint contract
- `@checkpoint` — create checkpoint

## Agents
- `@architect-agent` — ADRs and architecture
- `@dev-agent` — implementation
- `@review-agent` — PR review
'@ | Set-Content -Path "$ProjectDir\AGENTS.md" -Encoding UTF8

# --------------- AI_CLOSED_LOOP_WORKFLOW.md (copy) ---------------
if (Test-Path $WorkflowDoc) {
  Copy-Item -Path $WorkflowDoc -Destination "$ProjectDir\AI_CLOSED_LOOP_WORKFLOW.md"
  Write-Host "  -> Copied workflow document" -ForegroundColor Gray
}

# --------------- Makefile ---------------
@'
.PHONY: validate lint typecheck test coverage coverage-check docs-lint docs-build build format

validate: lint typecheck test coverage-check docs-lint build

lint:
	@echo "==> Lint"
	ruff check .

typecheck:
	@echo "==> Typecheck"
	mypy src/

test:
	@echo "==> Tests"
	pytest -x --timeout=30

coverage:
	@echo "==> Coverage"
	pytest --cov=src/ --cov-report=term --cov-report=xml

coverage-check:
	@echo "==> Coverage check"
	diff-cover coverage.xml --fail-under=90

docs-lint:
	@echo "==> Docs lint"
	markdownlint docs/ --ignore docs/api/

docs-build:
	@echo "==> Docs build"
	mdbook build docs/

build:
	@echo "==> Build"
	docker compose build

format:
	@echo "==> Format"
	ruff format .
'@ | Set-Content -Path "$ProjectDir\Makefile" -Encoding UTF8

# --------------- .github/ ---------------
New-Item -ItemType Directory -Force -Path "$ProjectDir\.github\ISSUE_TEMPLATE" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectDir\.github\workflows" | Out-Null

@'
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make lint
      - run: make typecheck

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test

  coverage:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make coverage
      - run: make coverage-check

  build:
    needs: coverage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build
'@ | Set-Content -Path "$ProjectDir\.github\workflows\ci.yml" -Encoding UTF8

# --------------- docs/ ---------------
New-Item -ItemType Directory -Force -Path "$ProjectDir\docs\adr" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectDir\docs\contracts" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectDir\docs\handoffs" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectDir\docs\knowledge" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProjectDir\docs\modules" | Out-Null

@'
# docs/knowledge/structure.md

## Module Map

| Directory | Language | Toolchain | Status |
|-----------|----------|-----------|--------|
| src/      | -        | -         | planned |

## Conventions

(Add project-specific conventions here as they are discovered.)
'@ | Set-Content -Path "$ProjectDir\docs\knowledge\structure.md" -Encoding UTF8

# --------------- .gitignore ---------------
@'
.opencode/checkpoints/
.opencode/memory/
.env
*.pyc
__pycache__/
node_modules/
dist/
build/
.coverage
coverage.xml
'@ | Set-Content -Path "$ProjectDir\.gitignore" -Encoding UTF8

# --------------- Done ---------------
Write-Host ""
Write-Host "Done! Workflow bootstrapped in: $ProjectDir" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. cd $ProjectDir"
Write-Host "  2. opencode"
Write-Host "  3. Say '@architect-agent Write ADR-0001 for this project'"
Write-Host ""
