BOOKFIX ENGINEERING PRINCIPLES

1. Never optimize for a single failing example.
2. Always identify the underlying algorithmic deficiency.
3. Rules must generalize to future unseen input.
4. Reject sentence-specific, author-specific, and book-specific fixes.
5. Prefer deterministic rules over AI whenever practical.
6. Explain the root cause before proposing a code change.
7. Consider false positives before adding a rule.
8. Simplicity is preferred over complexity.
9. Preserve backward compatibility unless an intentional redesign is approved.
10. If a proposal cannot be justified generally, do not implement it.



Before implementing any rule:

The homograph engine is a generalized language processor.
Rules should describe language patterns rather than examples.
Never write a rule because one sentence failed.
Instead determine:
Why did the algorithm fail?
What linguistic feature was missing?
Describe the underlying linguistic problem.
What evidence would distinguish the correct pronunciation?
Can that evidence be generalized?
Propose a generalized solution.
Estimate possible side effects.
Consider false positives.
Explain why this solution will help future unseen text.
If a proposed rule only fixes one sentence, reject it.
A rule should improve accuracy across future documents.
Prefer linguistic evidence over word memorization.
Prefer explainable scoring over hard-coded exceptions.

Avoid:
sentence-specific rules
book-specific rules
author-specific rules
one-off regexes

BookFix Project Charter

This project is intended to build a production-quality preprocessing engine for Text-to-Speech.

The system is designed to process arbitrary books, not specific test files.

Whenever there is a conflict between:

fixing one failing example
improving the overall algorithm

always choose the improvement to the algorithm.

Never introduce special-case logic solely to make one test sentence pass.

Every change should improve the engine's ability to correctly process future unseen text.

goals like:

deterministic whenever possible
AI only when rules cannot reliably solve the problem
explainable decisions
maintainable code
measurable improvements
benchmark before/after changes

Homograph Engine Goals

The homograph engine is a generalized language processor.

Rules should describe language patterns rather than examples.

Never write a rule because one sentence failed.

Instead determine:

Why did the algorithm fail?
What linguistic feature was missing?
What evidence would distinguish the correct pronunciation?
Can that evidence be generalized?

If a proposed rule only fixes one sentence, reject it.

A rule should improve accuracy across future documents.

Prefer linguistic evidence over word memorization.

Prefer explainable scoring over hard-coded exceptions.

Avoid:

sentence-specific rules
book-specific rules
author-specific rules
one-off regexes

3. Coding Principles

Then I'd have a third file.

Example:

Development Principles

Before implementing any rule:

Explain why the current algorithm failed.
Describe the underlying linguistic problem.
Propose a generalized solution.
Estimate possible side effects.
Consider false positives.
Explain why this solution will help future unseen text.

If you cannot explain why a rule generalizes,
do not implement it.

Rule Evaluation Checklist

Problem:
What failed?

Root Cause:
What evidence was missing?

Generalization:
Will this solve similar failures?

False Positives:
What incorrect cases could this create?

Complexity:
Is there a simpler solution?

Future Benefit:
Will this improve processing of unseen books?

Confidence:
High / Medium / Low

Recommendation:
Accept
Revise
Reject

BookFix Engineering Principles

It would be 5–10 pages and act as the governing document for the entire project. It would include:

The overall philosophy.
The goals of each subsystem (homographs, capitalization, AI routing, Roman numerals, etc.).
Design principles.
Performance goals.
AI usage guidelines.
Rule-writing standards.
Learning system standards.
Benchmarking requirements.
Code quality requirements.
A mandatory checklist every proposed change must satisfy before implementation.

You are working on BookFix.

The BookFix Engineering Principles are authoritative.

Never optimize for a specific failing input.

Always identify the underlying linguistic or algorithmic deficiency.

Every rule must generalize to future unseen text.

Reject sentence-specific fixes.

Explain the root cause before proposing code changes.

Prefer explainable algorithms over special-case logic.

AI is the last resort after deterministic rules have been considered.
