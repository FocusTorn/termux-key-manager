# Patch Lint Roadmap

## Roadmap principle

The framework should reach maturity before the policy catalog does.

A usable Patch Lint with ten trustworthy rules is preferable to a large rule catalog built on an unstable engine.

The roadmap therefore progresses from **framework -> migration -> coexistence -> policy growth -> cleanup**.

## Stage 1: Foundation

### Goal

Establish the Patch Lint identity without changing policy.

### Deliverables

- diagnostic model;
- severity model;
- lifecycle status model;
- renderer;
- validation/execution separation;
- minimal policy loader;
- initial test harness.

### Exit condition

A single policy-driven rule can produce a precise diagnostic and prevent execution when configured as an error.

## Stage 2: Baseline migration

### Goal

Move the current proven Patch Gate behavior into the new framework.

### Deliverables

- structural rules;
- path rules;
- executable rules;
- root rules;
- compatibility entry point;
- regression coverage.

### Exit condition

The new engine enforces the existing Patch Gate safety contract.

## Stage 3: Diagnostic maturity

### Goal

Make diagnostics genuinely useful to an agent.

### Deliverables

- accurate line/column reporting;
- stable rule IDs;
- concise messages;
- guidance;
- canonical forms;
- multi-diagnostic rendering;
- useful summary counts.

### Exit condition

An agent can correct a failing Patch Gate from the diagnostics without needing a separate explanation.

## Stage 4: Experimental policy channel

### Goal

Allow new policy to be tested without immediately changing enforcement.

### Deliverables

- experimental status;
- info/warning severities;
- side-by-side old/new rules;
- optional replacement metadata;
- tests for coexistence.

Example:

\`\`\`
PG-PATH-002  deprecated    error
PG-PATH-007  experimental  info
\`\`\`

### Exit condition

A new detector can run against real Patch Gates while the previous stable behavior remains authoritative.

## Stage 5: Rule promotion workflow

### Goal

Make policy evolution deliberate.

### Lifecycle

\`\`\`
experimental
     |
     v
   stable
     |
     v
 deprecated
     |
     v
  removed
\`\`\`

Status is independent of severity, so promotion may happen in smaller steps:

\`\`\`
experimental + info
        |
        v
experimental + warning
        |
        v
stable + warning
        |
        v
stable + error
\`\`\`

A different path may be appropriate for each rule.

### Exit condition

Rule changes no longer require engine changes merely to change maturity or enforcement.

## Stage 6: Policy expansion

### Goal

Capture more of the local development contract.

Potential future areas include:

- additional path conventions;
- more executable invocation constraints;
- additional root/context rules;
- more precise structural diagnostics;
- policy for command chaining;
- future Patch Gate syntax evolution.

Every new rule should answer:

1. What does it detect?
2. Why is it policy?
3. What is the canonical practice?
4. What severity should it have?
5. What evidence makes it trustworthy?
6. What valid cases must not trigger it?

### Exit condition

The policy catalog grows without increasing architectural complexity.

## Stage 7: Tooling and ergonomics

### Goal

Make Patch Lint pleasant for both humans and coding agents.

Potential deliverables:

- stable machine-readable diagnostics;
- optional compact output;
- optional verbose teaching output;
- deterministic rule ordering;
- filtering by rule ID;
- filtering by severity;
- explicit policy versioning;
- test fixtures for rule examples.

These are secondary to correctness and safety.

## Stage 8: Compatibility transition

### Goal

Move from Patch Gate terminology to Patch Lint terminology without breaking existing workflows.

### Deliverables

- canonical \`patch-lint\` command;
- \`patch-gate\` compatibility entry point;
- documentation updates;
- migration guidance;
- deprecation policy for the old command.

The compatibility command should be a thin adapter, not a second implementation.

## Stage 9: Legacy retirement

### Goal

Remove migration scaffolding after the new framework is proven.

### Deliverables

- remove duplicated validators;
- retire obsolete rule implementations;
- retire old command when appropriate;
- remove temporary compatibility logic;
- document the stable Patch Lint contract.

### Exit condition

There is one policy engine and one source of truth for Patch Gate validation.

# Milestones

## M1: Lint engine exists

The engine can:

- load policy;
- create diagnostics;
- render diagnostics;
- block execution on error.

## M2: Existing Patch Gate behavior migrated

All currently enforced safety rules have equivalent Patch Lint coverage.

## M3: Teaching diagnostics

Violations have useful line/column locations and guidance.

## M4: Experimental rules work

A replacement rule can run alongside a prior rule without changing its enforcement.

## M5: Stable policy framework

Rules can move through lifecycle states without modifying engine architecture.

## M6: Canonical Patch Lint

\`patch-lint\` is the canonical interface and \`patch-gate\` is only compatibility during the defined transition.

# Decision log

## ESLint-inspired architecture

Adopted.

The tool is intentionally modeled as a linter with a policy/rule system, stable IDs, diagnostics, severity, and lifecycle metadata.

## Self-correction instead of rewriting

Adopted.

Patch Lint diagnoses and teaches. It does not silently rewrite submitted Patch Gates.

## Status and severity are independent

Adopted.

This enables experimental rules to be evaluated beside stable rules and allows gradual enforcement changes.

## JSONC policy

Adopted as the preferred policy representation.

The exact storage location remains an implementation decision that must fit the TKM configuration/rules architecture.

## Rule categories

Initial categories:

\`\`\`
path_rules
executable_rules
root_rules
structure_rules
\`\`\`

The engine should not make these categories a hard architectural ceiling.

## Framework before complete ruleset

Adopted.

The project is intentionally usable before every desired rule exists.

# Risks and watch points

### Overfitting the engine to today's rules

The engine should provide generic diagnostics and lifecycle behavior. Rules should provide policy.

### Confusing canonical guidance with automatic replacement

Canonical guidance is instructional. It does not authorize mutation.

### Diagnostic noise during migration

Stable IDs and lifecycle metadata are essential when old and new rules overlap.

### False positives

Every rule needs positive and negative fixtures.

### Accidental execution

The most serious regression is allowing an invalid Patch Gate to execute.

### Path-policy overreach

Do not treat every environment variable or absolute path as an error. Detect the specific forms the policy actually prohibits.

### Root-policy overreach

A valid target path such as \`~/bin/script\` must not be confused with an invalid Patch Gate execution root or a prohibited direct executable invocation.

### General-parser creep

Patch Lint needs source awareness, not a complete Bash/Python language implementation.

# Definition of done

The migration is complete when:

- Patch Lint is the canonical engine;
- diagnostics are precise and actionable;
- policy is externally configurable;
- rule status and severity are independent;
- experimental rules can run beside stable rules;
- errors reliably prevent execution;
- clean input executes exactly once;
- existing Patch Gate behavior is covered by regression tests;
- the framework accepts new rules without architectural changes;
- \`patch-gate\` contains no duplicate policy implementation.
