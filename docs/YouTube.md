# YouTube Shorts Automater

MPV2 uses a similar implementation of V1 (see [MPV1](https://github.com/FujiwaraChoki/MoneyPrinter)), to generate Video-Files and upload them to YouTube Shorts.

In contrast to V1, V2 uses AI generated images as the visuals for the video, instead of using stock footage. This makes the videos more unique and less likely to be flagged by YouTube. V2 also supports music right from the get-go.

## Acceptance Standard

The YouTube chain is not the current optimization focus, but it does have a minimum acceptance bar.

For the current deployment-content lane, a passing script should preserve:

1. a concrete scene
2. a mistaken assumption / blind spot
3. why the usual approach fails in that scene
4. a first concrete move
5. only then a natural next step

What this means in practice:

- the opening should be a real deployment moment, not a generic technical thesis
- the script should not reduce the middle to broad risk reminders
- the action step should remain an internal deployment/config action, not a generic CTA

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
  "firefox_profile": "The path to your Firefox profile (used to log in to YouTube)",
  "headless": true,
  "llm": "The Large Language Model you want to use to generate the video script.",
  "image_model": "What AI Model you want to use to generate images.",
  "threads": 4,
  "is_for_kids": true
}
```

## Roadmap

Here are some features that are planned for the future:

- [ ] Subtitles (using either AssemblyAI or locally assembling them)
