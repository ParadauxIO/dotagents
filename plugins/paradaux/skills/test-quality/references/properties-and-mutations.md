# Property and mutation testing

Use the project's existing tools first. Introduce a library only when it serves
a concrete testing need and fits the repository's dependency policy. These
techniques supplement representative examples; neither is mandatory for every
change.

## Properties with independent meaning

Choose a rule from the domain contract, then define valid inputs and observable
failures. Useful candidates include:

| Rule | Example | Missing protection to consider |
| --- | --- | --- |
| Round trip | Decoding an encoded value preserves its meaning | Both operations can share a bug; add independently known encodings |
| Idempotence | Normalizing twice equals normalizing once | Returning the input unchanged also satisfies this; assert canonical form |
| Conservation | A transfer preserves total funds | No-op transfers also conserve funds; check each account's change |
| Ordering and preservation | Sorted output is ordered and preserves the input multiset | Sortedness alone accepts an empty result |
| Trusted comparison | An optimized implementation agrees with a reviewed reference | The reference must be independent and valid for the generated domain |
| Metamorphic relation | Permuting a set-like input preserves its semantic result | Establish that ordering is actually irrelevant to the contract |

Combine properties when necessary to exclude trivial implementations. A no-crash
property can be appropriate for resilience or parsing hostile input, but does not
establish functional correctness. Do not invent algebraic laws for rounding,
floating point, or order-sensitive operations without checking their domain.

Generate valid structured data directly rather than discarding most inputs with
assumptions. Include meaningful boundary values and separately test invalid input
contracts. Preserve library health checks: a property that exercises almost no
cases offers little evidence. For stateful behavior, generate command sequences
with explicit preconditions and check transitions against an independent model;
isolated calls cannot establish retry or lifecycle behavior.

When a property fails, retain the shrunk counterexample and reproduction details.
Determine whether the property, generator, reference, or product is wrong before
editing. Keep a focused regression example for a confirmed defect. Use the
framework's replay mechanism and record a failing seed when available; a fresh
random run passing does not invalidate an earlier failure.

Small pure functions can expose valuable properties hidden inside I/O-heavy code.
If extraction is outside the requested scope, explain the specific benefit and
continue with the available boundary; do not redesign production code merely to
accommodate a testing technique.

## Mutation testing and fault injection

Start with a clean focused test run. Use the installed mutation tool, or introduce
one plausible defect at a time in a disposable copy: change a comparison at its
boundary, remove a state write, choose the wrong argument, or omit validation.
Keep user changes intact and leave mutations out of the final patch. Bound the
run to changed or important logic before considering a broad campaign.

Interpret each outcome rather than optimizing a score blindly:

- **Caught:** verify which assertion failed and whether it reflects the intended
  behavioral difference. Setup, compilation, or unrelated failures do not prove
  meaningful detection even if a tool counts them favorably.
- **Survived:** determine whether the changed behavior is reachable and wrong.
  Add a discriminating input or assertion when it reveals missing protection.
- **Equivalent or outside the valid domain:** document the reason. A survivor
  does not automatically imply a missing test or authorize production changes.
- **Timeout, infrastructure failure, or flaky result:** report inconclusive
  evidence and investigate before assigning a quality verdict.

Verify a new check passes against the original and fails against the relevant
mutation. Rerun against the final unmutated implementation. Never rewrite syntax
solely to make a mutation disappear or silently exclude difficult subjects.
Report the tested scope and exclusions; raw scores from different configurations
are not directly comparable.

For integration/E2E checks, targeted faults can be more practical than rebuilding
the application for every mutation: reject a dependency call, lose an acknowledgment,
or disable the relevant write in a disposable environment. Check the specified
recovery or failure behavior. Inverting an assertion establishes that it executes,
but does not establish that it observes the right system effect.
