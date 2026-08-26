---
name: init-agents
description: Initialize a new AGENTS.md file in the current repository. Use this when asked to create an AGENTS.md, initialize agent documentation, or set up a new project for AI agent collaboration.
version: 1.0.0
license: MIT
---

# Init Agents Skill

The **Init Agents** skill analyzes the current codebase and generates an `AGENTS.md` file — a documentation file that provides guidance to AI agents (such as Claude Code, Codex CLI, Gemini CLI) when operating in this repository.

## When to Use

- User asks to create, initialize, or set up an `AGENTS.md` file
- User invokes `/init-agents` or similar
- Starting work on a new repository that lacks agent guidance documentation
- After significant architectural changes that should be documented for AI agents

## Workflow

```
[Analyze Repository]
         │
         ▼
[Scan for Project Configurations]
         │
         ▼
[Identify Architecture & Patterns]
         │
         ▼
[Generate AGENTS.md]
         │
         ▼
[Write to Root Directory]
```

---

### Step 1: Analyze Repository Structure

1. Scan the root directory to identify project type (language, framework)
2. Check for build/test configuration files
3. Identify the main source directories and their organization

---

### Step 2: Scan for Project Configurations

Look for and read relevant configuration files:

| File | Purpose |
|------|---------|
| `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle` | Dependencies and build tooling |
| `tsconfig.json`, `jsconfig.json`, `.eslintrc*`, `pyrightconfig.json` | Language/linting configuration |
| `vite.config.js`, `webpack.config.js`, `next.config.js`, `astro.config.mjs` | Build tooling |
| `jest.config.js`, `vitest.config.ts`, `pytest.ini`, `tox.ini` | Test runners |
| `.cursorrules`, `.cursor/rules/*`, `.github/copilot-instructions.md` | AI agent rules |
| `CLAUDE.md` (if exists) | Existing Claude Code guidance |
| `README.md` | Project documentation |
| `~/.codex/config.toml`, `./.codex/`, `~/.gemini/settings.json`, `./.gemini/` | External AI agent configs |

---

### Step 3: Identify Architecture & Patterns

From the scanned files, extract:

1. **Build/Test Commands**: How to build, lint, test, and run the project
2. **Architecture Overview**: Main components, directory structure, and how they relate
3. **Key Conventions**: Important patterns, coding standards, and project-specific rules
4. **External AI Configs**: Any existing Codex or Gemini CLI configurations to reference

---

### Step 4: Generate AGENTS.md

Produce an `AGENTS.md` file with the following sections:

```markdown
# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Commands

[Build, test, lint commands]

## Architecture

[High-level code architecture and structure]

## Patterns & Conventions

[Important coding patterns and project-specific conventions]
```

### Required Sections

1. **Header**: Standard `# AGENTS.md` title with repository purpose statement
2. **Commands**: Build, test, lint, and development commands
3. **Architecture**: High-level overview of code organization and key components
4. **Patterns**: Important conventions and coding standards

### What to Include

- ✅ Commands for building, testing, and linting
- ✅ High-level architecture requiring reading multiple files to understand
- ✅ Cursor rules / Copilot instructions if present
- ✅ README.md key information
- ✅ External AI agent config references (Codex, Gemini CLI)

### What to Exclude

- ❌ Generic development practices (write tests, helpful errors, etc.)
- ❌ Every file/component that can be discovered by listing directory
- ❌ Sensitive information (API keys, tokens)
- ❌ Obvious instructions

---

### Step 5: Write to Root Directory

Save the generated content to `AGENTS.md` in the repository root. If `AGENTS.md` already exists, offer improvements instead of replacing.

---

## Quality Checklist

Before finalizing, verify the `AGENTS.md`:

- [ ] Uses `# AGENTS.md` header with purpose statement
- [ ] Contains a **Commands** section with working commands
- [ ] Contains an **Architecture** section explaining the big picture
- [ ] References Cursor rules / Copilot instructions if they exist
- [ ] Does not include obvious or generic content
- [ ] Does not expose sensitive information
