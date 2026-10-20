# Integration and end-to-end testing

## Make the boundary faithful

Use real components for the behavior whose compatibility matters: the database
engine for SQL semantics, the broker for delivery behavior, or the service wiring
for serialization and authentication. Reuse existing disposable infrastructure;
use Testcontainers or an equivalent project fixture when suitable. Match relevant
versions and configuration without trying to recreate all production infrastructure.
An in-memory substitute cannot establish database-specific constraints or queries.

Start dependencies with explicit readiness checks, isolated data, dynamically
assigned ports where supported, and cleanup that runs on failure. Share expensive
containers only when per-test state stays independent. Use unique namespaces,
fresh schemas, or a documented reset; transaction rollback does not clean writes
made through other connections or asynchronous workers. Clean up only resources
the test owns. Verification does not authorize real purchases, messages, or
modifications to production/customer data.

Assert beyond the immediate response. For a successful write, read through a
fresh connection or subsequent request so a local cache cannot simulate persistence.
For rejected writes or rolled-back transactions, verify the forbidden state is
absent. For asynchronous work, wait with a bounded deadline for the correlated
result. Test duplicates, retry limits, or ordering only where those guarantees
belong to the contract. Use controllable barriers for concurrency bugs rather
than hoping thread scheduling reproduces them.

## Keep doubles and contracts honest

A consumer test against a stub proves only the consumer's interpretation. Check
the corresponding provider behavior or use the project's contract-verification
workflow to establish compatibility. Derive fixtures from reviewed contracts or
sanitized representative payloads; include relevant errors and optional/missing
fields. Do not fabricate fields just to satisfy the current implementation.

If a service is unavailable, a local fake can still test application decisions.
State which boundary remains unverified. A schema check establishes structure,
not business semantics, permissions, or side effects. A test cannot claim to
verify the database or remote service if it replaces that boundary with a mock.

## Plan browser checks around user outcomes

Turn requirements into a few explicit scenarios with setup, actions, and expected
outcomes before generating scripts. Inspect the running application to confirm
locators and feasibility; do not treat observed UI behavior as the specification.
Reuse the project's runner and server lifecycle helpers, and ensure a reused
server serves the intended build and configuration.

Prefer accessible roles, labels, and established test IDs over brittle DOM paths.
Use runner assertions that wait for the expected state, with bounded timeouts.
Fixed sleeps and generic network-idle waits are not readiness guarantees. Keep
sessions and data independent so test order or parallel workers cannot manufacture
a pass. Test prerequisites may use API fixtures; exercise the actual UI operation
whose behavior the scenario claims to verify.

Choose assertions across the relevant journey. For example, saving a record may
require checking displayed values after reload plus a persisted result; checkout
may require checking line items, totals, and a single created order. A screenshot,
toast, or HTTP 200 alone does not establish those outcomes. Keep backend assertions
at stable interfaces instead of coupling the browser suite to private internals.
Visual checks are useful for layout regressions, with reviewed baselines and
controlled rendering conditions; they do not replace functional assertions.

Capture traces, relevant requests, console errors, and screenshots when they help
explain a failure. Sanitize artifacts and distinguish existing background noise
from errors that affect the scenario.

## Repair tests without hiding defects

Classify a failure before changing the test: application regression, intended
behavior change, stale locator/fixture, timing race, or infrastructure fault.
Updating a locator is justified when evidence shows the same operation still
works. Deleting the operation, skipping a broken feature, weakening an assertion,
or approving a changed screenshot requires a contract-based reason, not a desire
for a pass. Report unresolved product failures rather than silently healing them.

For flakes, preserve the first failure and investigate shared state, clock control,
readiness, and teardown. Rerun under the relevant ordering or parallel conditions
after a targeted repair. A bounded repeat helps assess that repair; it does not
prove the flake is eliminated. Keep configured retries visible in results.
