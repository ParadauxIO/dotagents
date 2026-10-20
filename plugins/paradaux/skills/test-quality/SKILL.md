---
name: test-quality
description: Write, review, or strengthen unit, integration, and end-to-end tests around behavioral contracts, meaningful assertions, and demonstrated fault detection. Use for test design, regression coverage, weak or over-mocked suites, and property or mutation testing; preserve review-only scope.
---

# Test quality

Build a small, trustworthy body of evidence for the behavior that matters. Judge
tests by the defects they detect, the requirements they protect, and their cost
to maintain. Test count and coverage alone do not establish correctness.

## Establish the contract

Read project instructions, relevant production code, existing tests, and runner
configuration. Reuse the project's framework, fixtures, and commands. Run a
focused baseline when practical; distinguish existing failures from new ones.

Identify the intended behavior from the request, documented contract, acceptance
criteria, or a confirmed bug. Derive expected results independently of the
implementation under test: reviewed examples, hand calculations, protocol rules,
or a trusted reference. Reading implementation is useful for finding risks; it
does not make existing output correct. Label tests that merely record current
behavior as characterization tests. Ask about ambiguity only when different
interpretations change the expected result; continue independent work meanwhile.

Preserve the requested mode. A review produces findings and evidence without
editing; a test-only task does not authorize changing production semantics to
satisfy a new expectation. For a demonstrated product bug outside scope, report
the reproducer and unresolved behavior rather than encoding the bug as correct.

For each meaningful behavior, be able to name:

- The trigger and expected observable outcome, including relevant side effects.
- A plausible defect the test should detect.
- The narrowest test boundary that can expose that defect faithfully.

Use a short behavior/risk/check table for a complex change; do not require a plan
document for a straightforward regression test. Prioritize changed contracts,
reported bugs, permissions, data integrity, and costly failure paths. Include
boundaries and rejected inputs where relevant, not a mechanical list of every
possible edge case.

## Choose the evidence

| Concern | Useful starting point |
| --- | --- |
| Calculations, branching, validation, state transitions | Fast unit tests through a stable callable interface |
| Serialization, parsing, normalization, broad input domains | Examples plus meaningful property-based tests |
| SQL, migrations, persistence, queues, service wiring | Integration tests with the relevant real components |
| Consumer/provider compatibility | Contract tests checked against both sides |
| A critical user journey crossing application layers | A small set of end-to-end tests with observable outcomes |
| Whether existing assertions detect broken behavior | Targeted mutation testing or controlled fault injection |

Choose by the failure mechanism, not a fixed unit/integration/E2E ratio. Put
combinatorial cases in cheaper tests and retain higher-level checks for wiring
and journeys. Some overlap is useful when the layers protect different risks.
Do not add a test for a trivial forwarding method just to mirror every function;
test the meaningful contract at its consumer.

Read only the relevant supporting guidance:

- [Property and mutation testing](references/properties-and-mutations.md) when
  generating inputs, checking invariants, or assessing assertion strength.
- [Integration and end-to-end testing](references/integration-and-e2e.md) when
  testing real dependencies, contracts, browser flows, or unstable execution.

## Write tests that can disagree with the code

Prefer assertions on returned values, persisted state, emitted events, or visible
behavior. Check exact values where the contract requires them; check semantic
properties where ordering, identifiers, or presentation are intentionally variable.
An existence check or successful status is insufficient when content or side
effects define success. For rejected operations, check absence of forbidden
effects as well as the error when that distinction matters.

Keep expected values independent: do not call the production helper to compute
both actual and expected results or reproduce its algorithm in the assertion.
Use small, distinguishable fixtures so a wrong argument, omitted item, or swapped
field cannot accidentally yield the same answer. Parameterize cases with a shared
contract; keep unrelated behaviors separate. A test may need several assertions
to establish one outcome. Favor readable fixtures over a second framework of
test abstractions, and make failure messages identify the failing case.

Keep the behavior under test real. Replace slow, unavailable, nondeterministic,
or external boundaries only where the substitution preserves the behavior being
checked. Match the relevant dependency contract and model failure responses too.
Call counts, arguments, and ordering are valid assertions when they express a
real obligation such as bounded retries or one notification; incidental internal
call structure is not a contract. If elaborate mocks reproduce the application,
move the check to an integration boundary. Do not test the test double itself.

## Demonstrate detection and verify

For new behavior or a bug fix, prefer a short red/green cycle: write the check,
observe failure for the intended reason, implement, and rerun. Import errors,
missing services, and broken setup are not evidence of behavioral detection.
If implementation already exists, retain it and demonstrate sensitivity using a
known faulty baseline or targeted mutation in an isolated copy. Never delete
useful work merely to recreate test-first chronology.

When strengthening an existing suite, start with the highest-risk unprotected
behavior. Use coverage to find unexercised paths and mutation results to find
weak assertions; do not generate tests solely to satisfy a percentage. A passing
mutant check still cannot establish that the underlying requirement is correct.

When a test fails, distinguish a product defect, an intentional contract change,
a faulty assertion, and an environment problem. Change expectations only with
evidence of the intended contract. Do not remove assertions, widen tolerances,
skip failures, approve snapshots, or add retries merely to obtain a green suite.
For intentional changes, update the relevant checks and preserve unrelated
regression protection. Review snapshot differences as expected behavior.

Run focused checks during iteration, then affected neighboring tests and all
repository-required checks on the final state. For a small suite, run it in full;
for an expensive suite, use documented selection and disclose what was not run.
Control clocks, randomness, and data ownership where needed. Do not mistake a
passing retry for evidence that a flaky test is repaired.

## Report the evidence

State the behavior covered, defects detected or gaps found, commands and results,
and any material unverified boundary. Say whether sensitivity was executed or
only reasoned about. Keep review findings concrete: location, missing protection,
plausible escaped defect, and a focused improvement. Do not claim the whole
system is verified from a unit suite or a local browser check.

For live browser investigation, `paradaux:verify-webapp` can supply the execution
workflow when available. For unexplained failures, `paradaux:systematic-debugging`
can help establish cause. Neither skill is required to use this one.

Design influences and deliberate adaptations are recorded in
[sources](references/sources.md); they are not required reading during a task.
