# Twitter Bot

This bot is designed to automate the process of growing a Twitter account. Once you created a new account, provide the path to the Firefox Profile and the bot will start posting tweets based on the subject you provided during the account creation.

## Acceptance Baseline

As of `2026-04-15`, the current Twitter/X generation baseline is frozen at commit:

- `2b39413` `Stabilize Twitter bad-instinct rendering`

This baseline is not a general "best possible tweet" baseline.
It is a narrow acceptance baseline for the current deployment-content lane.

### What This Baseline Must Preserve

For the current Twitter/X chain, the minimum accepted output structure is:

1. a concrete scene
2. a valid `bad_instinct`
3. a valid `first_move`

And the final tweet must also satisfy:

- no CTA shadow
- no `expected_attribute` leak
- complete sentence rendering

### Programmatic Constraints

The current Twitter/X chain is intentionally locked to a narrow structure.

The final tweet should be rendered only from:

1. `scene`
2. `bad_instinct`
3. `first_move`

Current hard rules:

- `bad_instinct` must be an explicit wrong-idea sentence, not a vague status description
- `first_move` must be a product-internal / deployment-internal action
- CTA is off by default
- CTA shadow is not allowed
- `expected_attribute` wording or close paraphrases are not allowed in the final tweet
- rendering must keep complete sentences and avoid half-cut endings

### Current Stop Rule

Do not continue optimizing this Twitter/X chain by default.

Only reopen this lane if at least one of the following changes:

- the model changes
- the platform constraints change
- the acceptance target changes

Until then, treat the current behavior as the working baseline rather than an open-ended optimization target.

### Why It Is Frozen

The current baseline already passed the narrow acceptance gate for:

- `scene`
- `bad_instinct`
- `first_move`
- `cta shadow`
- `expected_attribute leak`
- `render_complete`

So the next default action is not more Twitter tuning.
The next default action is to leave this lane stable and spend attention elsewhere.

### Baseline Runtime

- provider: `LM Studio local API`
- model: `qwen2.5:3b`
- temperature: `0`
- stream: `false`
- num_predict: `220`

Regression reference:

- `docs/RegressionSamples.md`

## Relevant Configuration

In your `config.json`, you need the following attributes filled out, so that the bot can function correctly.

```json
{
  "twitter_language": "Any Language, formatting doesn't matter",
  "headless": true,
  "llm": "The Large Language Model you want to use, check Configuration.md for more information",
}
```
