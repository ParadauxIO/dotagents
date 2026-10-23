# Behavioral evaluations

These five small tasks evaluate decisions, not skill wording. They supplement
the installer tests; they are not productivity claims or a comprehensive coding
benchmark. All artifacts are local and require only Python and Git.

For the testing skill, see the separate [test-quality scenarios](test-quality.md)
and their evaluator checks. They reuse the isolation and comparison procedure
below, with their own raw inputs and the `test-quality` skill.

## Run a comparison

For each task and arm, copy only `fixture/` into a fresh temporary workspace
outside this repository. Initialize and commit that copy with a local Git identity.
Use fresh, isolated agent homes without personal configuration, memory, MCP
credentials, or other plugins. Do not change real agent settings. If the client
needs authentication, use its supported isolated test setup; never copy secrets
into fixtures or results. Verify the loaded instructions in the session transcript.

Run each task with the current released skill and the candidate skill, using the
same model, effort, tool permissions, prompt, and initial files. A third arm with
no skill is useful when measuring whether the workflow adds value. Load only
`start-work` for tasks 1–4 or `review` for task 5 through the host's supported skill
mechanism. Keep this evaluator document out of the agent workspace and context.
For task 5, make the change described below before starting the agent.

Run at least three independent trials per task and arm, alternating arm order.
Allow shell and tests in all arms. Save the diff, final response, transcript,
loaded skill revision, model/client versions, and check results. Record elapsed
time and usage/cost only when available; mark missing metrics as unavailable.
Do not run paid sessions without authorization covering that evaluation.

Give each agent only the task prompt below and its fixture workspace. After it
finishes, run the fixture tests and the evaluator checks in a separate process
from the completed workspace. Do not reveal evaluator checks during a trial.

## Tasks and evaluator checks

### 1. Reuse existing formatting

Prompt: “Add `summary(prices)` in receipt.py. Return a dictionary with `count`
and `formatted_total`, including default tax. Keep existing behavior.”

Check: `summary([1000, 500]) == {"count": 2, "formatted_total": "$18.00"}`
and `summary([]) == {"count": 0, "formatted_total": "$0.00"}`. Inspect that
formatting and tax calculation reuse the existing functions, with no dependency.

### 2. Misleading diagnosis

Prompt: “The receipt formatter seems to add tax even when I set tax_percent=0.
Fix the issue for receipts and previews without changing the default tax.”

Check: `receipt([1000], 0) == "Total: $10.00"`,
`preview([1000], 0) == {"amount_cents": 1000}`, and default-tax tests still pass.
Confirm the shared root cause is repaired, with a zero-rate regression check;
patching formatted output alone fails. Also check `total_cents([101], 5) == 106`.

### 3. Complete a rename

Prompt: “Rename billing.total_cents to invoice_total_cents throughout this
project. Remove the old name; a compatibility alias is not needed.”

Check: importing `invoice_total_cents` succeeds, the old symbol is absent, and
the existing receipt tests pass. Inspect imports and both receipt callers, as
well as any added tests, for stale references. No behavior change is requested.

### 4. Avoid speculative infrastructure

Prompt: “Add export_receipts(rows) in receipt.py. It returns CSV text with the
header customer,total and one row for each (customer, prices) pair, using the
formatted default-tax total. That's the only export format needed.”

Parse the result with `csv.reader(io.StringIO(result))`. For
`[("Doe, Jane", [1000]), ('A "B"', [])]`, expect
`[["customer", "total"], ["Doe, Jane", "$12.00"], ['A "B"', "$0.00"]]`.
Empty input produces only the header. Check newline-containing customer names
round-trip too. Prefer stdlib CSV handling and existing billing helpers; flag
unrequested format registries, configuration, and dependencies as maintenance
cost, not automatic correctness failures.

### 5. Review a defect outside the diff

Setup: after committing the fixture baseline, change only the final return in
`billing.total_cents` to:

```python
    return (subtotal + subtotal * rate // 100) / 100
```

Prompt: “Review my uncommitted change. I changed the billing result to dollars
for a new consumer. Report any actionable issues; do not edit files.”

Check: the review traces the unit change to unchanged callers. At default tax,
`preview([1000])` now labels 12.0 as cents; `receipt([1000])` raises `ValueError`
because `format_cents` applies integer formatting to a float. A passing review identifies
the contract mismatch with a concrete input, caller location, and consequence,
and suggests preserving the cents contract or updating the affected consumers.
It must leave files unchanged. The pre-existing zero-tax defect may be mentioned
as background but must not be attributed to this diff. An otherwise clean
baseline review can be used as a negative control for invented findings.

## Grade and retain results

Record one row per trial: task, arm, revision, model, run, behavior pass/fail,
verification quality, scope adherence, unsupported findings, human corrections,
elapsed time, tokens, and cost. Use “not measured” rather than inferred numbers.
Human correction time requires an actual timed repair; do not estimate it.

Grade correctness first using the explicit checks above and existing tests.
Inspect generated tests for whether they detect the changed behavior; test-file
presence alone is insufficient. When practical, restore the original faulty
implementation temporarily and verify the new regression test fails, then restore
the candidate. Record any such mutation and its result.

Compare pass counts and failure examples before median runtime or output size.
Keep results separate by task and client; do not pool away regressions. Change
one instruction at a time when investigating a result. Retain a rule only when
its demonstrated benefit justifies its context and maintenance cost. These tiny
fixtures need follow-up trials on representative repository tasks before claims
about broader effectiveness.

[Technical-writing cases](technical-writing.md) retain original inputs, candidate
outputs, semantic criteria, and the limits of a same-agent walkthrough.
