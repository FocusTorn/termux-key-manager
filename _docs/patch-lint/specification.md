# Patch Lint Specification

## 1. Scope

Patch Lint is the policy-driven successor to \`~/bin/patch-gate\`.

It accepts a complete Patch Gate command stream, analyzes it, reports diagnostics, and conditionally executes the original input.

Its scope is limited to the Patch Gate contract and the local development policies that govern Patch Gates. It is not a general Bash linter, Python linter, formatter, or automatic rewrite engine.

## 2. Normative principles

1. **Never silently rewrite input.**
2. **Never execute when an effective error exists.**
3. **Diagnostics identify the actual submitted source.**
4. **Rules have stable IDs.**
5. **Rule status and severity are independent.**
6. **Policy belongs in configuration when practical.**
7. **The engine owns lint mechanics, not local conventions.**
8. **A rule must be testable independently.**
9. **Compatibility takes precedence over cosmetic migration.**
10. **The framework must support a small initial ruleset.**

## 3. Input and output

### Input

Standard input contains one Patch Gate.

The Patch Gate remains a shell command stream beginning with the selected project/repository root and containing the Python surgical modification heredoc plus required result handling.

Patch Lint should preserve the input byte-for-byte for execution.

### Output

Diagnostics are written to stderr.

Successful execution preserves the existing command execution behavior.

A lint failure must not execute the submitted Patch Gate.

The process exit status must distinguish lint rejection from successful execution. The exact numeric status should be selected during implementation and documented as a compatibility decision.

## 4. Diagnostic model

Conceptual diagnostic object:

\`\`\`jsonc
{
  "rule_id": "PG-PATH-001",
  "severity": "error",
  "status": "stable",
  "line": 7,
  "column": 13,
  "message": "Path uses /tmp/",
  "guidance": "Termux temporary paths must not use /tmp/.",
  "canonical": "$PREFIX/tmp/"
}
\`\`\`

Optional fields may include:

\`\`\`jsonc
{
  "end_line": 7,
  "end_column": 25,
  "source": "stdin",
  "notes": [],
  "related": []
}
\`\`\`

The minimum required location is line and column. End positions are useful but not required for the first implementation.

### Rendering

Human-readable output should follow an ESLint-like shape:

\`\`\`
stdin:7:13  error  PG-PATH-001
Path uses /tmp/

  Termux temporary paths must not use /tmp/.
  Canonical: $PREFIX/tmp/
\`\`\`

Final summary:

\`\`\`
✖ 2 problems (1 error, 1 warning)
\`\`\`

A clean lint result should be concise and should not claim success before execution has actually completed.

## 5. Severity

Supported severities:

- \`info\`
- \`warning\`
- \`error\`

Effective behavior:

- \`info\`: report only
- \`warning\`: report and continue unless future policy explicitly changes warning behavior
- \`error\`: block execution

The implementation should make severity behavior centralized rather than encoded separately inside each rule.

## 6. Rule lifecycle status

Supported statuses:

- \`experimental\`
- \`stable\`
- \`deprecated\`

Status is metadata about rule maturity and migration state. It does not directly determine execution behavior.

Examples:

\`\`\`
experimental + info
experimental + warning
stable + error
stable + warning
deprecated + error
deprecated + warning
\`\`\`

A deprecated rule may remain enforced while a replacement is evaluated.

Optional future metadata:

\`\`\`jsonc
{
  "replaced_by": "PG-PATH-007"
}
\`\`\`

## 7. Policy schema

Top-level shape:

\`\`\`jsonc
{
  "path_rules": [],
  "executable_rules": [],
  "root_rules": [],
  "structure_rules": []
}
\`\`\`

A rule should generally contain:

\`\`\`jsonc
{
  "id": "PG-PATH-001",
  "status": "stable",
  "severity": "error",
  "patterns": ["/tmp/"],
  "message": "Path uses /tmp/",
  "guidance": "Termux temporary paths must not use /tmp/.",
  "canonical": "$PREFIX/tmp/"
}
\`\`\`

Not every rule needs every field.

### Pattern versus canonical

\`patterns\` describe what the detector recognizes.

\`canonical\` describes the preferred practice.

Do not name the latter \`replacement\`. The linter is not promising to transform the input.

A canonical value may be a path, command form, or conceptual practice:

\`\`\`jsonc
"canonical": "~/"
\`\`\`

or:

\`\`\`jsonc
"canonical": "command name only"
\`\`\`

## 8. Rule families

### 8.1 Path rules

Detect prohibited or noncanonical path forms.

Initial known policies include:

- reject \`/tmp/\` for Termux temporary paths;
- prefer \`~/\` over \`$HOME/\` and absolute \`/home/\` forms where the policy applies.

Do not automatically reject \`$TMPDIR\` merely because it is an environment variable. Its current value may resolve to the same Termux temporary location. If a future policy wants deterministic spelling, that should be a separately defined rule.

### 8.2 Executable rules

Detect prohibited invocation forms.

Known policy:

- do not directly invoke \`~/bin/*\`, \`$HOME/bin/*\`, or equivalent absolute home-bin paths;
- invoke installed utilities by command name.

This rule applies to executable invocation, not merely mentioning a file path.

### 8.3 Root rules

Detect Patch Gates operating from known inappropriate roots.

Known policy distinctions:

- the current project root is the governing root;
- \`~/bin\` may legitimately be the target of a Patch Gate;
- \`~/bin\` is nevertheless not the normal Patch Gate execution root;
- \`~/_rules\` is rules infrastructure and not a normal project Patch Gate root.

The engine must not hardcode the assumption that \`~/bin\` is never a valid target path.

### 8.4 Structure rules

Encode the existing surgical Patch Gate contract.

The initial migrated rules should cover:

- exactly one Python Patch Gate heredoc;
- exactly one relevant target read;
- exactly one \`old\` literal;
- exactly one \`new\` literal;
- old occurrence check before replacement;
- exactly one candidate construction using the intended replacement;
- candidate postcondition assertion;
- exactly one target write;
- required immediate result handling;
- prohibited explicit \`exit\`/\`return\` forms and unsafe chaining where already enforced.

The exact rule decomposition should favor independent diagnostics over one monolithic "Patch Gate invalid" rule.

## 9. Source analysis

The analyzer should preserve the original input and associate findings with source positions.

It may use line-oriented scanning plus narrowly scoped lexical recognition.

It should not attempt to become a complete shell or Python parser.

A practical progression is:

1. retain the existing regex/count checks as internal detectors;
2. attach source spans to their matches;
3. extract common helper functions for location and diagnostic creation;
4. only introduce more structure when a rule actually requires it.

## 10. Rule execution

Conceptual pipeline:

\`\`\`
stdin
  |
  v
read complete source
  |
  v
load policy
  |
  v
analyze
  |
  v
collect diagnostics
  |
  +---- errors ----> render + reject
  |
  +---- no errors -> execute original source
                         |
                         v
                    capture status
                         |
                         v
                  existing result path
\`\`\`

Rules should not mutate the source.

## 11. Rule coexistence

The framework must permit old and replacement rules to run together.

Example:

\`\`\`jsonc
{
  "id": "PG-PATH-002",
  "status": "deprecated",
  "severity": "error",
  "replaced_by": "PG-PATH-007"
}
\`\`\`

alongside:

\`\`\`jsonc
{
  "id": "PG-PATH-007",
  "status": "experimental",
  "severity": "info"
}
\`\`\`

This allows the replacement detector to be tested against real input without changing enforcement.

The renderer should make the rule IDs visible so duplicate or overlapping findings can be diagnosed.

## 12. Policy validation

Invalid policy must fail before analyzing or executing user input.

At minimum validate:

- unique rule IDs;
- supported status;
- supported severity;
- required fields for each rule family;
- valid pattern representation;
- valid references such as \`replaced_by\`;
- no impossible duplicate identifiers.

Policy parsing errors are tool/configuration failures, not user Patch Gate violations, and should have a distinct diagnostic category or exit path.

## 13. Configuration format

JSONC is preferred because the policy is documentation as well as configuration.

Comments should explain policy intent, not restate obvious JSON field names.

The exact configuration location is an implementation decision that must align with the TKM rules/configuration architecture. Do not hardcode a location merely because \`~/_rules\` exists.

## 14. Safety requirements

The migration must preserve these guarantees:

- linting reads the complete input before execution;
- an effective error prevents execution;
- linting does not write target files;
- linting does not modify the submitted source;
- execution occurs at most once;
- execution uses the original submitted source;
- execution result is captured immediately;
- result reporting does not introduce a second execution path.

## 15. Compatibility

The existing \`patch-gate\` command is the compatibility reference during migration.

Do not remove it until the replacement behavior is demonstrated.

A compatibility wrapper may eventually invoke Patch Lint, but the wrapper must not duplicate rule logic.

The desired end state is one implementation of the policy engine.

## 16. Testing requirements

Tests must cover:

### Diagnostics

- rule ID
- severity
- status
- line
- column
- message
- guidance
- canonical form

### Rule behavior

Each rule needs valid and invalid fixtures.

### Lifecycle

Test experimental, stable, and deprecated rules independently of severity.

### Coexistence

Run old and replacement rules on the same fixture and verify both diagnostics can be emitted without changing execution behavior.

### Safety

Verify that any effective error prevents target modification and command execution.

### Execution

Verify clean input still executes exactly once and returns the expected execution status.

### Policy

Verify malformed JSONC and invalid rule definitions fail safely before Patch Gate execution.

## 17. Non-goals

Patch Lint is not:

- a general Bash linter;
- a Python linter;
- a formatter;
- an automatic source rewriter;
- a project-wide style checker;
- a replacement for the repository validator;
- a mechanism for silently correcting agent commands.

Its purpose is the Patch Gate policy boundary.
