# Regression Samples

更新日期：`2026-04-15`

这份文档只保存当前已经通过验收、后面可以直接复用的最小回归样例。

它不是策略文档。
它的作用只有两个：

1. 复现实验输入
2. 作为后续模型或平台变更时的固定对照组

## Shared Runtime

- provider: `Ollama local API`
- model: `qwen2.5:3b`
- temperature: `0`
- stream: `false`
- num_predict: `220`

## Twitter/X Baseline Sample

当前冻结基线：

- commit: `a8541d7` for documentation freeze
- code baseline commit: `2b39413`

### Test Input

- topic: `Why local success says nothing about production readiness`
- desired_identity: `calm operator who ships safely without looking amateur in front of real users`
- avoided_identity: `shiny-tool collector who breaks things in public`
- strongest_scene: `right before exposing the first public URL through nginx`
- expected_attribute: `clear first-pass deploy judgment with no obvious exposure mistakes`

### Expected Pass Conditions

- `scene`
- `bad_instinct`
- `first_move`
- `cta shadow = false`
- `expected_attribute leak = false`
- `render_complete = true`

### Representative Passing Output

```text
before exposing your first public URL. the bad instinct is to assume local success means prod-ready without verifying authentication and reverse proxy configurations. verify the production auth settings for your open-source AI tool
```

### Why This Sample Is Kept

它能稳定检验：

- 是否从具体时刻起笔
- 是否明确说出错误直觉
- 是否给出可执行第一动作
- 是否没有 CTA shadow
- 是否没有 expected_attribute leak
- 是否没有截断

## YouTube Acceptance Sample

当前不再继续优化 YouTube 链路，但保留最小验收样例，防止后续回归。

### Test Input

- topic angle: `What to check in the 30 minutes before putting your first public URL behind nginx`
- strongest_scene: `right before exposing the first public URL through nginx`
- desired_identity: `calm operator who ships safely`
- expected_attribute: `clear first-pass deploy judgment with no obvious exposure mistakes`

### Expected Structure

脚本至少应体现：

1. concrete scene
2. mistaken assumption / blind spot
3. why the usual approach fails in this scene
4. first concrete move
5. only then a natural next step

### Representative Passing Traits

- 开头不是行业大词，而是上线前 moment
- 中间不是泛风险提醒，而是具体误判
- 有立刻可执行动作
- 不靠 CTA 取代动作
