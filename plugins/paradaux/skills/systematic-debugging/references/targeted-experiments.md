# Targeted experiments

Read the section matching the failure. Choose a probe based on its predicted
outcomes; this is not a checklist to run in full.

## Flaky tests and asynchronous work

Keep seeds, test order, worker count, timing, and failure artifacts. Compare the
failing test alone with the original suite/order to distinguish local timing from
shared-state pollution. Use controlled clocks, barriers, or explicit completion
signals to exercise the suspected interleaving. Wait for the actual required state
with a bounded timeout and a useful failure diagnostic. A longer sleep changes
probability without establishing synchronization.

Measure failures over a declared number of comparable runs before and after the
change. Report counts and conditions; zero observed failures is not proof of zero
failure probability. Avoid rerunning a flaky check until it happens to pass.

## Requests, queues, caches, and databases

Trace one operation through browser/client, gateway, service, queue, and persistence
only as far as relevant. Distinguish acceptance, durable commit, delivery, and user
visibility. Correlate identifiers rather than assuming timestamp order across hosts.
Inspect retry attempts, duplicate handling, cache keys/invalidation, transaction
boundaries, and replica lag when those mechanisms match the symptom.

To test stale-state explanations, compare the same operation against authoritative
state and the suspected stale reader. Do not flush a shared cache or replay a
state-changing request as an unapproved diagnostic shortcut. Prefer a local fixture,
a test tenant, or a scoped read that can distinguish the paths.

## CI, builds, and dependency regressions

Compare the failing job's actual command, working directory, runtime/toolchain,
lockfile, platform, flags, and artifact provenance with a successful run. Inspect
configuration sources and presence without printing secret values. Use clean
artifacts in an isolated directory to test a cache hypothesis before deleting
existing caches. If there is a known good revision and a reliable automated oracle,
consider bisecting in a separate checkout; preserve local work and mark unrelated
build failures as inconclusive rather than assigning them as the regression.

## Performance and resource failures

Define the affected workload and measure the relevant distribution, throughput,
and resource usage. Match dataset, warmup, concurrency, and environment across
comparisons. Profile to locate time or allocation cost before optimizing. Separate
queue delay, service time, external I/O, and resource contention. Report measurement
variance and sample size; a faster isolated run is insufficient to establish a
regression fix. Avoid unapproved load against shared or production systems.

## Agent, model, and tool workflows

Capture a sanitized failing input, model/configuration version, tool schema,
retrieval inputs, and execution trace. Locate whether failure occurred in retrieval,
model output, argument validation, tool execution, permissions, or downstream state.
Distinguish a rejected tool call from a successful call with an incorrect result.

Replay deterministic boundaries with fixtures or recorded tool responses where
possible. For stochastic behavior, use a small fixed set of representative inputs,
explicit success criteria, repeated trials, and held-out cases. Compare candidate
changes against the same baseline. Do not repair a general workflow by inserting
the known test answer into its prompt, or claim one successful generation proves a
fix. Tool-side mutations and private trace access retain their normal permissions.
