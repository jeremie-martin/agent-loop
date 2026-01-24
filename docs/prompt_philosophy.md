# Prompt Philosophy

Principles for writing effective agent prompts in iterative loops.

*For an overview of agent-loop, see the [README](../README.md).*

## 1. Describe the destination, not the steps

Smart agents respond better to understanding what "good" looks like than to being told what to do. Instead of "remove duplicates," say "concepts appear once." The agent concludes *on its own* that duplicates should go—which produces better judgment about *which* duplicates and *how* to consolidate.

## 2. Frame conciseness as quality, not constraint

"Keep it short" feels like a restriction fighting against helpfulness. But "every section earns its place" treats tightness as a quality marker rather than a constraint. The agent aims for quality rather than following rules.

## 3. Reader-centered language

Phrases like "reads as a coherent whole" and "easy to follow" put the agent in an editor's mindset rather than a writer's. Writers add; editors shape. You want the shaping mindset.

## 4. Neutral action verbs

"Correcting, clarifying, consolidating, or restructuring"—all presented as equally valid moves. No implicit hierarchy where adding is the default and removing requires justification.

## 5. Avoid expansion trigger words

"Comprehensive," "exhaustive," "thorough," "complete coverage"—these prime the agent toward more-is-better. Use "authoritative," "accurate," "coherent" instead.

## 6. Guard against over-correction

Phrases like "genuinely improve" and "don't reorganize for the sake of reorganizing" prevent over-correction. You want judgment, not zealotry.

## 7. One purpose per prompt

Clean separation lets each pass do its job well. agent-loop cycles through separate modes, each with a single focus.

## Example in practice

The built-in `docs-review` preset demonstrates these principles with three modes (accuracy, structure, clarity). Each mode has a single focus, uses destination-focused language, and treats conciseness as quality. See `src/agent_loop/presets/docs-review.yaml` for the full prompts.
