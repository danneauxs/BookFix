# Findings Report: Homograph Choice Module

## Purpose
This report captures the current findings about the choice module, the current decision architecture, and the strongest next steps for improving accuracy without relying on AI for every ambiguous case.

## Current architecture summary
The current system already has a multi-stage design:

- Rules-only mode
  - uses lexical rules, dependency rules, POS rules, and learned patterns
- Hybrid mode
  - runs rules first and sends uncertain cases to AI
- Verify-all mode
  - sends more cases through AI review

The review window is also a key part of the system. User corrections are saved and later used to improve decisions.

## Main findings

### 1. The current flow is safe but too conservative
The system tends to defer to review or AI whenever evidence is weak or mixed. That is safe, but it leaves too many homographs unresolved by rules alone.

### 2. Phrase-level evidence is more reliable than generic keywords
High-signal phrases such as:

- lead pipe
- live wire
- close the door
- object to
- read the report
- wound around

are much stronger than single-word context clues.

### 3. The replace-text workflow should feed the choice engine
The existing replace-style workflow is useful not only as a literal text replacement tool, but also as a source of phrase rules. User-added phrases should be treated as reusable evidence for future homograph decisions.

### 4. The learning path exists but should become more central
The system already saves user corrections and derives patterns from them. The next step is to use those learned patterns as a first-class signal in the core decision engine rather than as a side feature.

### 5. The current scoring model should be upgraded
The system should move from a mostly rule-or-defers model to a weighted evidence model where multiple signals contribute to a confidence score for each candidate spelling.

## Proposed direction
The best next step is not a full rewrite, but a structured refactor in three layers:

1. Phrase-evidence layer
   - match short phrases and collocations around the target word
   - assign high weight to clear phrases

2. Weighted evidence layer
   - combine syntax, keyword evidence, learned patterns, and phrase matches
   - score each candidate spelling and apply the best-supported one when confidence is high

3. Learning layer
   - store user corrections with context, POS, dependency structure, and nearby words
   - promote those examples into phrase-level and keyword-level guidance for future runs

## Current tools and whether they are sufficient

### Tools currently in use
The main tools and components appear to be:

- spaCy POS tagging and dependency parsing
- RoBERTa-based NLI for zero-shot sense classification
- hybrid deciders for some specific homographs
- AI review workflow for uncertainty handling
- learning storage and pattern extraction

### Are these sufficient?
They are sufficient as a baseline, but not ideal for high-accuracy production behavior.

They are good for:
- basic syntactic analysis
- proving the architecture
- handling obvious cases
- providing a fallback path

They are weaker for:
- subtle or highly ambiguous homograph contexts
- long-distance contextual clues
- domain-specific phrase patterns
- consistent behavior across many document types

## Tool and model suggestions
The current stack is reasonable, but there are better alternatives depending on the goal.

### A. For POS and dependency parsing
Best current options:

- spaCy
  - good default, simple integration
  - especially when paired with custom rules and learned patterns
- spaCy transformer model
  - better accuracy for syntax and context
  - heavier and slower
- Stanza
  - strong alternative for POS and dependency parsing
  - often more accurate on some linguistic tasks than spaCy in practice

Recommended direction:
- keep spaCy for speed unless accuracy needs improve sharply
- consider spaCy transformer or Stanza if the system is moved toward more serious WSD-style disambiguation

### B. For semantic/contextual disambiguation
Current NLI approach is useful, but there are better options:

- DeBERTa-v3-based NLI models
  - often stronger than older RoBERTa-based NLI models
  - a good upgrade path
- sentence-transformers embeddings
  - useful for comparing a sentence context against candidate sense definitions
  - often efficient and easy to run locally
- fine-tuned word-sense disambiguation models
  - best long-term option if enough labeled examples are available

Recommended direction:
- keep a lightweight semantic classifier as a fallback
- add phrase-level evidence first, because it should improve accuracy more quickly than just swapping models

### C. For local / offline inference
If the goal is to keep the system local and avoid heavy cloud dependencies, good options include:

- small encoder models for similarity-based sense matching
- lightweight NLI models
- compact instruction-tuned local LLMs as a last-resort fallback for only the hardest cases

This would be especially useful if the system is meant to work fully offline or with limited GPU support.

## Practical recommendation
The strongest near-term plan is:

1. Keep the current tools as the baseline.
2. Add phrase-level rules and local evidence scoring.
3. Improve the learning layer so user corrections become reusable evidence.
4. Consider upgrading the semantic toolchain later, especially if AI fallback remains too common.

## Best upgrade path
If we want the maximum gain for the least disruption, the order should be:

1. Phrase rules and collocation matching
2. Weighted evidence scoring
3. Stronger keyword cleanup
4. Better learned pattern promotion
5. Upgrade the semantic model if needed

## Bottom line
The current tools are a solid starting point, but they are not enough by themselves for high-confidence homograph disambiguation across many contexts. The best improvement comes from combining better phrase handling, better scoring, stronger learning, and then optionally upgrading the semantic model stack.
