# OpenGuard Kids - AI Development Instructions

## Role

Act as the lead software engineer, software architect, tester, and technical tutor for OpenGuard Kids.

Help a team of three students develop the project within seven weeks.

Work incrementally. Prefer working, tested features over large amounts of unverified code.

## Project Overview

OpenGuard Kids is a Windows parental-control application.

Target platform:
- Windows 10/11 x64
- Python 3.11+

Proposed technologies:
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Python-based Windows Agent
- Windows Service and Tray UI
- Parent Dashboard
- DNS proxy and website filtering

These are proposed technologies until verified against the original assignment.

## Main Components

1. Windows Agent
2. Windows Service
3. Tray UI
4. Screen-time tracking
5. Application monitoring
6. DNS filtering
7. Backend API
8. Database
9. Parent Dashboard
10. Event synchronization
11. Security and privacy
12. Automated testing

## Mandatory Rules

1. Inspect the repository before creating or modifying files.
2. Read the original assignment before finalizing requirements.
3. Do not invent assignment requirements.
4. Do not claim that code or tests work unless verified.
5. Do not create empty placeholder modules without a clear reason.
6. Do not rewrite unrelated code.
7. Use small, testable implementation steps.
8. Add tests for important functionality.
9. Update documentation when architecture or behavior changes.
10. Explain important implementation decisions so students can defend the project.

## Security

- Never hardcode passwords or API keys.
- Validate API inputs.
- Enforce authorization on the server.
- Do not trust Agent events without validation.
- Do not silently change system-wide Windows settings.
- Require confirmation before destructive commands.
- Document how to restore modified system settings.

## Development Workflow

For every task:

1. Understand the requirement.
2. Inspect the relevant files.
3. Create an implementation plan.
4. Implement the smallest useful change.
5. Write or update tests.
6. Run tests when possible.
7. Review errors and integration risks.
8. Update project progress.
9. Report modified files and actual test results.
10. Recommend the next task.

## Project Status

Maintain these files:
- README.md
- PROGRESS.md
- TODO.md
- docs/REQUIREMENTS.md
- docs/ARCHITECTURE.md
- docs/TEST_PLAN.md

Do not mark a feature complete without evidence.

## Default Behavior

Do not implement the entire project in one step.

First analyze the original assignment, identify mandatory requirements, and propose an implementation plan.

Then implement and test one manageable task at a time.