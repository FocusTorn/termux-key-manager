# Patch Lint Implementation Plan

## Objective

Convert the current \`~/bin/patch-gate\` from a hardcoded Bash validator into a policy-driven Patch Lint engine while preserving the existing surgical modification and execution-safety contract.

The implementation should be incremental. Each slice should leave a usable tool.

## Phase 0: Establish the baseline

### Tasks

1. Treat the current \`patch-gate\` behavior as the compatibility baseline.
2. Inventory every current validation check and classify it as:
   - structure
   - path
   - executable
   - root
   - execution safety
3. Record current output and exit behavior.
4. Identify all existing tests or fixtures that exercise Patch Gate validation.

### Result

A frozen behavioral baseline from which migration can proceed without guessing.

## Phase 1: Introduce the diagnostic model

Create a small internal representation for:

- rule ID
- severity
- status
- line
- column
- message
- guidance
- canonical

Keep it independent of any specific rule.

Add a renderer that can produce:

\`\`\`
stdin:line:column  severity  RULE-ID
message

  guidance
  canonical: ...
\`\`\`

Add summary rendering.

### Acceptance

Existing validation can emit diagnostics without changing the enforcement decision.

## Phase 2: Separate validation from execution

Refactor the current flow into explicit conceptual stages:

\`\`\`
read
 -> validate
 -> render
 -> gate
 -> execute
 -> report
\`\`\`

Do not change the actual policy yet.

The important property is that validation completes before execution can begin.

### Acceptance

A deliberately invalid Patch Gate is proven not to execute.

## Phase 3: Build the policy loader

Introduce JSONC policy loading.

The loader should:

- locate the configured policy;
- strip/parse JSONC using the project's existing JSONC capability where appropriate;
- validate schema;
- reject duplicate rule IDs;
- validate status/severity;
- produce useful configuration errors.

Keep policy loading separate from rule evaluation.

### Acceptance

A minimal policy containing one rule can load and produce a deterministic in-memory rule set.

## Phase 4: Build the rule registry

Create a generic registry keyed by rule ID.

Conceptually:

\`\`\`
rule id
   |
   +--> detector
   +--> metadata
   +--> lifecycle
   +--> severity
\`\`\`

Policy-driven rules should not require changing the registry's architecture.

A rule implementation may still be code-backed when its behavior cannot reasonably be expressed as data.

This is important: **policy-driven does not mean every detector must be a regex in JSONC.**

## Phase 5: Migrate structural rules

Move the current Patch Gate structural checks into independent rule implementations.

Prioritize:

1. exactly one Python heredoc;
2. old/new definitions;
3. old occurrence assertion;
4. candidate construction;
5. candidate postcondition;
6. exactly one write;
7. required result handling;
8. unsafe explicit exits/chaining.

Each finding should point to the most useful source location.

### Acceptance

The migrated structural rules reproduce the baseline enforcement behavior.

## Phase 6: Migrate path, executable, and root policy

Externalize the environment-specific rules into JSONC.

Initial policy families:

\`\`\`text
path_rules
executable_rules
root_rules
structure_rules
\`\`\`

Keep the engine generic.

### Important distinction

A path rule detects path spelling/use.

An executable rule detects executable invocation.

A root rule detects the Patch Gate's working root.

Do not solve all three with one broad path regex.

## Phase 7: Add lifecycle controls

Implement:

- experimental
- stable
- deprecated

and keep these independent from:

- info
- warning
- error

Add optional \`replaced_by\`.

### Acceptance

A replacement rule can run beside an old rule without changing the old rule's enforcement.

## Phase 8: Add coexistence and migration tooling

Support configurations such as:

\`\`\`text
old rule:       deprecated + error
new rule:       experimental + info
\`\`\`

The same input can therefore produce diagnostics from both.

Add tests demonstrating that promoting the new rule to stable/error changes only the intended enforcement behavior.

## Phase 9: Improve source locations

Once the rule engine is stable, improve location quality.

Priorities:

1. line;
2. column;
3. optional end position.

Do not build a general parser solely to improve locations.

Prefer exact spans from the existing structural detectors.

## Phase 10: Harden execution safety

Review every path from lint result to execution.

Required invariant:

\`\`\`
errors > 0
    => no execution
\`\`\`

Required execution invariant:

\`\`\`
clean
  => execute original source exactly once
  => capture status immediately
  => report result
\`\`\`

Retain the current result-handling semantics unless a compatibility-tested replacement is intentionally specified.

## Phase 11: Compatibility command

During migration, retain:

\`\`\`
patch-gate
\`\`\`

as the compatibility entry point.

The desired implementation shape is:

\`\`\`
patch-gate
    |
    v
patch-lint engine
\`\`\`

rather than two validators.

The compatibility layer should become thin enough that it contains no policy.

## Phase 12: Rename and cleanup

Only after behavior is established:

- make \`patch-lint\` the canonical command;
- retain \`patch-gate\` as a compatibility alias for an explicitly defined transition period;
- update documentation;
- remove duplicated legacy validation code;
- remove compatibility only when the migration policy says it is safe.

## Suggested internal boundaries

The implementation should converge toward small conceptual units:

\`\`\`
input
  |
  +--> source representation
  |
  +--> policy loader
  |
  +--> rule registry
  |
  +--> rule evaluation
  |
  +--> diagnostics
  |
  +--> renderer
  |
  +--> execution gate
  |
  +--> executor
\`\`\`

The exact filenames and module layout should follow the existing TKM code organization rather than introducing an unrelated framework.

## Testing strategy

### Unit tests

Test:

- policy parsing
- policy validation
- diagnostic construction
- diagnostic rendering
- source location
- individual rules
- severity behavior
- lifecycle behavior

### Integration tests

Test:

- complete valid Patch Gates;
- complete invalid Patch Gates;
- multiple simultaneous violations;
- old/new rule coexistence;
- execution blocked by error;
- execution allowed without error;
- execution result reporting.

### Regression tests

Every behavior currently enforced by \`patch-gate\` should have a regression test before its implementation is removed.

## Development discipline

This migration is a completed-slice workflow.

While iterating, run focused tests relevant to the changed subsystem.

At completed slices, run the repository's full test suite and the appropriate project validator.

Do not use broad rewrites when a surgical migration is sufficient.

## What not to do

Do not:

- encode the entire policy in Bash conditionals;
- make every policy a raw regex with no semantic identity;
- add automatic rewriting;
- silently normalize paths;
- make \`$HOME\` universally invalid outside the contexts defined by policy;
- treat \`$TMPDIR\` as inherently wrong;
- prohibit \`~/bin\` as a target path merely because direct execution of \`~/bin/*\` is prohibited;
- turn Patch Lint into a general shell parser;
- remove the old command before compatibility is proven;
- add every desired rule before the framework can be tested.

## First implementation slice

The first coding slice should be intentionally small:

1. diagnostic object;
2. severity/status enums or equivalent constants;
3. renderer;
4. one policy-loaded rule;
5. error gating;
6. tests proving invalid input does not execute.

Once that works, migrate the remaining current checks.

This gives the project a functioning Patch Lint framework early instead of spending the first implementation cycle on rule inventory.
