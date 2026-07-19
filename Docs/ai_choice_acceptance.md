# AI Choice Workflow Acceptance

Qwen3:8B is the only reference model until this workflow is approved.

1. Every request contains target sentence, canonical candidates, definitions, rule evidence, and reviewed examples when available.
2. Every successful response is strict JSON with canonical choice, numeric confidence from 0 through 1, boolean rule agreement, and evidence-grounded justification.
3. Rule disagreement requires a separate disagreement reason.
4. Ambiguous evidence produces explicit abstention and manual review.
5. Missing, malformed, invented, or noncanonical output produces manual review with zero confidence.
6. AI output never enters trusted learning data without human acceptance or correction.
7. Human-reviewed learning data passes canonical spelling and conflict validation before storage or promotion.
8. End-to-end tests cover agreement, disagreement, abstention, malformed output, noncanonical output, and reviewed learning capture.
9. Live GUI verification confirms Qwen3:8B selection, server settings, request execution, review display, and accepted/corrected learning capture.
10. Fixed holdout benchmark records accuracy, abstention, incorrect recommendation rate, structured-output validity, latency, and failures.
11. Workflow requires zero invalid automatic decisions and zero unreviewed AI learning writes.
12. Multi-model testing remains blocked until explicit user approval.
13. Qwen3/Ollama production and benchmark requests send `think: false`; benchmark settings that affect results are recorded and applied to BookFix before approval.
