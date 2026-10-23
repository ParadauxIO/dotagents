---
name: technical-writing
description: Write, revise, or review technical documentation for a specific reader and task, preserving technical meaning while improving clarity and usability. Use for guides, runbooks, API explanations, release notes, and technical reports; not as a universal chat style or marketing voice.
---

# Technical writing

Help the intended reader find, understand, and use accurate information. This
workflow is informed by the publicly described principles of ISO 24495-1:2023;
it is not a reproduction of the standard or a compliance assessment. Read
[source notes](references/sources.md) when discussing its basis or tradeoffs.

## Establish the reader and the evidence

Infer the audience, their task, expertise, and reading context from the request
and existing documents. Ask only when an unresolved choice materially affects
the result. Follow the project's language, terminology, and document conventions.
A runbook for a tired operator and an explanation for a new developer need
different levels of detail.

For a rewrite, identify the facts that must survive: conditions, actors, order,
units, versions, requirement strength, uncertainty, and failure consequences.
Preserve commands, code, identifiers, paths, UI labels, and quoted errors exactly
unless the requested technical correction requires changing them. Flag suspect
source material rather than silently making it plausible.

Ground new claims in supplied evidence, repository behavior, or relevant primary
sources. Distinguish observations from hypotheses. Do not invent causes, timings,
measurements, citations, guarantees, or recovery steps to complete a narrative.
If necessary information is missing, state the gap or use an explicit placeholder.
Writing instructions does not authorize executing their commands or publishing.

## Shape the document around its use

- **Relevant:** Lead with the answer, purpose, or outcome the reader needs.
  Include prerequisites and limits that affect decisions; remove unrelated context.
- **Findable:** Order material by the reader's questions or task sequence. Use
  descriptive headings and links, numbered steps for sequences, and tables for
  comparisons when they help. Keep optional explanations separate from required steps.
- **Understandable:** Name the actor and use concrete verbs and familiar words.
  Explain unfamiliar concepts when the audience needs them. Keep each term stable
  for the same concept, while preserving distinctions such as authentication versus
  authorization. Split sentences at logical boundaries; a word count is a signal,
  not a pass criterion. Retain qualifications that express real uncertainty.
- **Usable:** Put prerequisites, conditions, and relevant warnings before the action
  they govern. Give each step a bounded action and show how the reader recognizes
  success or failure. Include recovery only when supported. Do not invent a runnable
  command where the source supplies only a general action.

Adapt the shape to the deliverable. A reference explains contracts and exceptions;
a procedure supplies ordered actions; a report distinguishes evidence, impact,
and unresolved causes. Do not force every document into a numbered checklist.

## Edit without changing meaning

Remove empty introductions, exaggerated benefits, repeated conclusions, decorative
metaphors, and stock contrasts when they carry no information. Prefer the concrete
relationship or fact. Use the trope reference as an editorial prompt, not a banned
word detector or proof that a text was written by AI.

Preserve normative distinctions: a recommendation does not become a requirement,
a possibility does not become a fact, and permission does not become capability.
Do not replace every modal with “must” or “can.” Retain necessary technical terms
and the user's requested tone and format. Avoid assuming a diagnosis or imposing
session-wide accessibility preferences. Do not invent time estimates or a next
action after the task is complete.

## Verify and deliver

Compare the revision with its evidence for lost or altered facts and technical
literals. Walk through a representative reader's task: can they locate the answer,
understand the conditions, and identify the outcome without guessing? Check links
and examples where practical. Run code only in an authorized safe environment;
label examples that were reviewed but not executed.

Review for unsupported confidence and omissions before polishing style. Readability
scores and shorter prose cannot establish correctness, accessibility, or ISO/STE
compliance. Report material unknowns and verification limits briefly.

For a writing request, deliver the document or edit the requested file. For a
review request, report consequential issues with a location, reader impact, and
suggested correction; do not rewrite the whole document unless asked. Keep research
notes out of the finished prose unless citations or rationale belong in it.
