# Benchmark Runtime Contract

Benchmark tests BookFix production AI behavior. It is not a separate AI path.

## Required Parity

- One queued word per Ollama request.
- Same `BookfixAIService.analyze_contextualized_homograph` call used by BookFix.
- Same sentence, candidates, definitions, rule evidence, POS tag, keywords, and reviewed examples.
- Same runtime configuration and response validation.
- No text replacement. Benchmark records recommendation, failure, abstention, latency, and comparison with verified answer.

## Recorded Runtime Decisions

| Date | Finding | BookFix requirement |
| --- | --- | --- |
| 2026-07-12 | Qwen3 thinking defaults on in Ollama. One curated request exhausted 1,024 generated tokens without final JSON. | Send top-level Ollama API field `think: false` through `ollama_think: false` in AI config. |

## Change Rule

Any benchmark setting that fixes or changes model behavior must be added to BookFix production configuration, covered by regression test, and recorded here before results are used for model selection.
