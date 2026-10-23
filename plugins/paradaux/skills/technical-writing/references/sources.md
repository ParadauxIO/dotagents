# Research and design decisions

Researched 2026-10-23. These are influences and editorial judgments, not a claim
that the skill implements every clause of a standard. The instructions are
independently written; no standard, dictionary, or third-party skill is bundled.

## Standards and documentation practice

- [ISO 24495-1:2023 catalog](https://www.iso.org/standard/78907.html) identifies
  the standard and its scope, including technical writing. The complete licensed
  standard was not consulted. No clause-level or conformity claim is made.
- [CLEO's plain-language practice](https://www.cleo.on.ca/en/publications/house-style-guide/plain-language)
  publicly explains the four principles as relevance, findability, understanding,
  and use. CLEO is a practitioner source describing its own approach, not ISO's
  normative text. This skill translates those outcomes into reader/task checks.
- [Google's documentation highlights](https://developers.google.com/style/highlights)
  recommend explicit actors, conditions ahead of instructions, ordered sequences,
  descriptive links, and accessible presentation. We use these structural ideas
  while leaving spelling and voice to the project. This is independently phrased
  guidance, informed by Google's CC BY 4.0 material.
- [Microsoft Learn's AI-content principles](https://learn.microsoft.com/en-us/principles-for-ai-generated-content)
  describe author review and testing of generated code before publication.
  We adopt evidence checks and honest execution status. Microsoft's disclosure
  practice is its publishing policy, not a universal requirement imposed here.

## Exact skill sources inspected

Names alone are ambiguous: directories contain forks and unrelated skills.
The following primary repositories were selected as the upstream projects; no
claim is made that every skill with these names is identical.

- [ayghri/i-have-adhd, skills/i-have-adhd/SKILL.md](https://github.com/ayghri/i-have-adhd/blob/1ecea1993b7fce257ffbd686c070948b5e07eda6/skills/i-have-adhd/SKILL.md)
  (MIT; revision `1ecea1993b7fce257ffbd686c070948b5e07eda6`).
  It favors immediate actions, bounded steps, visible progress, and reduced
  tangents. Our judgment: these help procedures, but universal action-first replies,
  persistent session rules, concrete duration estimates, and generalized clinical
  claims are inappropriate defaults for a documentation skill. We retain task
  focus without assuming the reader's diagnosis or manufacturing estimates.
- [AminBlg/SimpleEnglish, skills/simple-english/SKILL.md](https://github.com/AminBlg/SimpleEnglish/blob/a6fcb4fde098b33617cc1578d151ebf58774b883/skills/simple-english/SKILL.md)
  (MIT; revision `a6fcb4fde098b33617cc1578d151ebf58774b883`, frontmatter 2.1.1).
  It distinguishes procedures from explanations and protects technical literals.
  Our judgment: retain those ideas, but do not adopt fixed sentence limits,
  universal prose-only replies, modal replacement, or vocabulary substitutions
  that collapse distinct concepts. Its strict mode concerns ASD-STE100, a separate
  controlled-language standard; it does not establish ISO plain-language compliance.
  We did not reproduce its rule catalog or official dictionary.

## AI prose guidance supplied by the user

[tropes.md](https://tropes.fyi/tropes-md) catalogs recognizable rhetorical and
formatting patterns in generated prose. It is an editorial collection, not a
controlled study, accessibility standard, or authorship detector. Our judgment:
use it to question padding and unsupported emphasis while keeping useful contrast,
structure, and qualifications. A global punctuation blacklist could damage useful
technical explanations. No catalog text is copied into the skill.

## Evidence limits and evaluation

The sources establish what their authors recommend. They do not demonstrate that
this combination improves task success. No popularity, clinical efficacy, or
productivity claims follow from inspecting them. See the repository's
[evaluation cases](../../../../../evaluations/technical-writing.md) for original
inputs, candidate outputs, and same-agent checks. Independent reader testing and
cross-client repeated trials remain future work; structural package checks alone
cannot validate writing quality.
