# Design influences

This skill is an independently written synthesis, not a vendored copy or a claim
that all upstream instructions are endorsed. Links document provenance; runtime
use does not require fetching these sources.

- [Superpowers TDD](https://github.com/obra/superpowers/tree/main/skills/test-driven-development)
  and its [test-quality reference](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/writing-good-tests.md):
  behavioral assertions, independent expectations, and observed red/green evidence.
  This version retains existing implementation, permits contract-relevant mock
  assertions, and scales testing to the requested change.
- [Trail of Bits property-based testing](https://github.com/trailofbits/skills/tree/master/plugins/property-based-testing):
  domain properties, useful generated inputs, and detection of vacuous assertions.
  This version emphasizes complementary properties and independent known examples.
- [Testcontainers skills](https://github.com/testcontainers/claude-skills):
  disposable real infrastructure and lifecycle management. This version stays
  language-neutral and uses the project's existing infrastructure when appropriate.
- [Playwright Test Agents](https://github.com/microsoft/playwright/blob/main/docs/src/test-agents-js.md)
  and [Anthropic webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing):
  scenario planning, live inspection, execution, and debugging evidence. This
  version uses observable readiness and preserves assertions during test repair;
  it does not require subagents or a particular browser tool provider.
- [Mutant skill](https://github.com/mbj/mutant/blob/master/SKILL.md):
  analyzing surviving mutations and verifying that added tests detect them. This
  version scopes campaigns by risk and distinguishes equivalent mutations and
  inconclusive runs without requiring a universal mutation-score target.
- [Simon Willison: Red/green TDD](https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/),
  [Thoughtworks: Mutation testing](https://www.thoughtworks.com/radar/techniques/mutation-testing),
  and [Birgitta Böckeler: Maintainability sensors for coding agents](https://www.martinfowler.com/articles/sensors-for-coding-agents.html):
  executable feedback and the distinction between executed code, effective
  assertions, and correct requirements.

The dotagents repository's `evaluations/test-quality.md` defines behavioral
evaluation criteria. Those scenarios are not evidence of measured superiority
over these sources and are not bundled in the installed plugin.
