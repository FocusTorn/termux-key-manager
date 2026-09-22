# Patch Lint Primer

## Purpose

TKM's current \`~/bin/patch-gate\` is a safety boundary around surgical file modifications. It validates a submitted Patch Gate before allowing it to execute.

The next evolution is **Patch Lint**: an ESLint-inspired, policy-driven linter for Patch Gates.

Patch Lint is not primarily a rewrite tool. It is a **self-correcting and teaching policy boundary**. When an agent submits an invalid Patch Gate, Patch Lint should identify the exact infraction, explain the rule, show the canonical practice when one exists, and refuse execution until the agent corrects its own input.

The framework must be complete before the rule catalog is complete. A small initial ruleset is intentionally acceptable.

## Agent starting point

An implementation agent should be able to begin from this document and the companion specification, implementation plan, and roadmap without rediscovering the design through ad-hoc investigation.

The existing implementation is \`~/bin/patch-gate\`. The migration target is \`patch-lint\`, with compatibility preserved during the transition.

Do not begin by rewriting every rule. Build the rule/diagnostic framework first, migrate the existing proven checks into it, and then grow the policy.

## Core philosophy

Patch Lint has four jobs:

1. **Detect** policy and structural violations.
2. **Explain** what was detected and why it matters.
3. **Teach** the canonical local practice when one exists.
4. **Gate** execution when policy says the submitted Patch Gate is not safe to execute.

It must not silently rewrite the submitted Patch Gate.

The agent should be able to take a diagnostic such as:

\`\`\`
stdin:7:13  error  PG-PATH-001
Path uses /tmp/

  Termux temporary paths must not use /tmp/.
  Canonical: $PREFIX/tmp/
\`\`\`

and correct its own Patch Gate.

The desired feedback loop is:

\`\`\`
agent generates Patch Gate
        |
        v
     patch-lint
        |
   +----+----+
   |         |
violations  clean
   |         |
   v         v
diagnose   execute
   |
   v
agent self-corrects
   |
   +------> patch-lint
\`\`\`

## ESLint is the inspiration

The intended mental model is a linter, not a collection of shell checks.

Rules have stable identities, lifecycle status, severity, source locations, messages, guidance, and optional canonical forms.

The policy should be externalized in JSONC wherever practical so adding or evolving policy does not require continually expanding the Bash implementation.

## Two independent rule dimensions

**Status** describes rule maturity:

- \`experimental\`: being developed or evaluated
- \`stable\`: established policy
- \`deprecated\`: retained during migration and scheduled for removal

**Severity** describes enforcement:

- \`info\`: informational only
- \`warning\`: report but normally do not block execution
- \`error\`: block execution

Status and severity are deliberately independent.

An experimental rule can run as \`info\` or \`warning\` beside an older stable rule. A deprecated rule can remain an \`error\` while its replacement is validated in parallel.

This makes policy evolution testable without immediately changing enforcement.

## Diagnostic contract

Every actionable diagnostic should identify:

- rule ID
- severity
- source line
- source column
- concise message
- useful guidance
- canonical form when applicable

Example:

\`\`\`
stdin:12:1  error  PG-EXEC-001
Direct ~/bin executable invocation

  Invoke ~/bin utilities by command name.
  Canonical: command name only
\`\`\`

The source location must refer to the actual Patch Gate input submitted to the linter. Do not report locations against a reconstructed or silently rewritten source.

## What belongs in policy

The initial policy model has four rule families:

\`\`\`jsonc
{
  "path_rules": [],
  "executable_rules": [],
  "root_rules": [],
  "structure_rules": []
}
\`\`\`

Examples include:

- Termux path policy such as rejecting \`/tmp/\`
- canonical home-relative path policy
- direct \`~/bin/\` executable invocation policy
- Patch Gate working-root policy
- structural Patch Gate requirements

The categories are organizational. The rule engine should remain generic enough that additional categories can be introduced without redesigning diagnostics.

## Important Termux distinctions

Do not conflate these concepts:

- \`/tmp/\` is not the canonical Termux temporary path.
- \`$PREFIX/tmp/\` is the explicit Termux prefix temporary path.
- \`$TMPDIR\` may resolve to the same location in the current environment, but it is an environment variable and is not inherently equivalent as a policy representation.
- \`~\` is the preferred canonical home-relative form for Patch Gates.
- \`~/bin/foo\` may be a valid target path, but directly invoking \`~/bin/foo\` is a separate executable-policy violation. A Patch Gate may legitimately modify a utility under \`~/bin\`.

Therefore path, executable, and root rules must remain distinct.

## Do not overreach into language parsing

Patch Lint needs enough source awareness to produce reliable line/column diagnostics and understand the Patch Gate contract.

It should not become a general Bash or Python parser.

The target is a small, deterministic Patch Gate analyzer with explicit rules and known structural constructs.

Avoid rules that attempt to infer arbitrary programming-language semantics when a focused Patch Gate rule can express the policy.

## Execution safety is non-negotiable

The existing Patch Gate contract has an important safety property:

- validate first
- execute only when validation permits
- capture the execution result immediately
- report the result directly

A lint failure must prevent the submitted Patch Gate from executing.

The migration must not accidentally create a path where warnings, malformed diagnostics, or partial validation allow an invalid Patch Gate to run.

## Migration philosophy

The framework is the product. The initial rule catalog is not.

Preserve the existing safety behavior while moving the implementation behind the new framework:

\`\`\`
current patch-gate
      |
      +--> extract diagnostic model
      |
      +--> introduce policy loader
      |
      +--> migrate existing checks
      |
      +--> add source locations
      |
      +--> add lifecycle/severity
      |
      +--> run replacement rules beside old rules
      |
      +--> promote tested rules
      |
      +--> rename/retire compatibility layer
\`\`\`

Do not perform a large all-at-once rewrite merely to make the name change.

## Things to watch closely

### False positives

A linter that teaches the wrong lesson is worse than one that reports less. Every rule needs representative valid and invalid cases.

### Diagnostic accuracy

Line and column are part of the user experience, not decoration. Test them explicitly.

### Rule overlap

During migration, old and replacement rules may both report the same source. The framework needs stable IDs and lifecycle controls so this is understandable rather than noisy.

### Policy versus mechanism

Keep reusable lint mechanics in the engine. Keep local conventions and environment-specific policy in configuration.

### Canonical is not always a substitution

\`canonical\` means "the preferred form or practice", not necessarily "replace this literal automatically". Patch Lint should teach rather than rewrite.

### Root context

The current project root is normally known by the agent, but an agent can drift into \`~/bin\` or another unrelated root later. Root rules should catch known unsafe Patch Gate roots without pretending the linter can magically infer project intent.

### Compatibility

Existing users and automation should not lose the current execution-safety contract while the framework is being introduced.

## Completion definition

The project is successful when Patch Lint can:

1. load policy;
2. analyze a submitted Patch Gate;
3. emit stable, precise diagnostics;
4. distinguish status from severity;
5. run experimental rules beside established rules;
6. block execution on configured errors;
7. explain canonical practices without rewriting input;
8. execute a clean Patch Gate using the existing safety contract; and
9. accept additional rules without requiring architectural changes to the engine.

The initial release does **not** need every conceivable policy rule. It needs a sound framework and a small, trustworthy ruleset.
