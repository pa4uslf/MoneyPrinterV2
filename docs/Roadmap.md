# Frank MoneyPrinter Roadmap

This roadmap is now aligned to a different end state:

> Build a system that compounds content, audience, and monetizable assets into longer-term income channels.

The fork is no longer primarily optimized around "more client work".

## Progress Snapshot

As of 2026-03-31, the first strategy pass is no longer just a discussion thread.

The following decisions are now effectively locked unless a later strategy reset overrides them:

- this fork is optimizing for `Asset Printer` first, `Lead Printer` second, and `Cash Printer` only as bootstrap support
- the first capture path is a free deployment checklist, not a hard service CTA
- `fzhang.dev` should remain content-first rather than turning into a generic agency homepage
- the first monetization bridge is: free asset -> owned audience -> paid SOP / template -> later affiliate or low-touch offers

The following work is already represented in committed docs or repo changes:

- strategy docs exist for the overall specialization, monetization path, and first asset choice
- the content profile system has been reframed around asset-led prompts instead of only service-led positioning
- the first asset funnel has draft assets:
  - free checklist
  - download page copy
  - post-submit copy
  - first article draft
  - first short-content pack
  - first 10 long-tail topics
  - first paid SOP draft
- homepage direction and CTA hierarchy are drafted, but site implementation is still pending
- the first content batch and paid SOP path now have execution specs in `docs/assets/`
- a cross-project execution summary now exists in `docs/FinancialFreedomExecutionStack.md`
- a first-pass topic ledger / measurement spec now exists in `docs/TopicLedgerMeasurementSpec.md`
- a minimum distribution validation plan now exists in `docs/DistributionValidationPlan.md`
- a first distribution execution kit now exists in `docs/DistributionExecutionKit.md`
- a traffic strategy note now exists in `docs/FzhangTrafficStrategy.md`
- a real-demand guidance layer now exists in `docs/real-demand/`

Current gap summary:

- measurement is not wired yet
- repeated real-demand samples are still too thin
- the primary ICP is still not narrow enough
- the current direction still lacks a proper "reset validation" pass against substitute solutions, especially general-purpose AI
- topic scoring is not implemented yet
- affiliate-safe comparison / recommendation clusters are not defined yet
- welcome email, unsubscribe visibility, tagging, and low-frequency topic sends still need final verification
- English-thread outreach now has language routing support across key pages and locale-aware email tagging in `fzhang.dev`; the remaining task is to validate whether this actually improves checklist conversion and downstream engagement
- `shop.fzhang.dev` payment architecture is now decided in principle, but not yet implemented in code
- `InsForge` is intentionally deferred unless the shop backend becomes a real bottleneck after payment integration
- distribution validation has a plan, but still needs real channel actions and logged results

Current operating judgment:

- the direction is still considered viable
- but it is not yet a proven MoneyPrinter loop
- the repo is currently in a `direction right / evidence thin / legacy shell still present` state

Reference for this judgment:

- `docs/real-demand/2026-04-15-MoneyPrinter方向判断.md`
- `docs/real-demand/真实需求识别与验证SOP.md`
- `docs/real-demand/2026-04-15-90天推进路线图.md`

## North Star

The system should gradually make it easier to produce:

- long-tail traffic assets
- owned audience
- reusable monetization pages
- low-touch offers
- selective affiliate and digital-product revenue

## Success Criteria

The fork is moving in the right direction when one content unit can lead to multiple assets:

1. short-form content
2. written content
3. owned capture point
4. monetization path

The fork is drifting off course when outputs only support:

- more outreach
- more direct custom work
- more manual selling with no asset accumulation

Additional success criteria now apply:

- repeated outside users in concrete deployment scenarios express similar pain
- repeated users describe where README / issue / AI are still not enough
- article -> checklist movement is observable
- checklist unlocks lead to confirmed subscribers or deeper replies
- a future SOP is pushed by repeated demand, not only by internal planning confidence
- the project can explain whether its value is a standalone digital asset, a project-level judgment product, or a module inside a broader service

## Monetization Stack

### Layer 1: Owned Attention

- newsletter signups
- RSS / subscription growth
- bookmarkable site content

### Layer 2: Utility Assets

- checklists
- setup guides
- resource packs
- comparison pages
- template pages

### Layer 3: Revenue

- affiliate links where trust is earned
- paid SOPs
- paid template packs
- low-touch diagnostic or audit offers

### Layer 4: Bootstrap Revenue

- selective productized service work

This layer is allowed, but it should finance the earlier layers rather than dominate the system.

## Phase 1: Thesis Reset

- [x] Rewrite the fork strategy around asset compounding
- [x] Rewrite the roadmap around owned audience and reusable assets
- [ ] Remove or reframe old service-led messaging where it creates strategic confusion
- [x] Define the first primary asset type this fork will print

## Phase 2: Intent-Driven Content Engine

- [x] Replace broad service-led prompts with monetizable-intent prompts
- [ ] Narrow the primary ICP from broad "builders" to one main deployment-stage reader
- [ ] Build a substitute-solution map that includes README/docs, forums, consultants, managed services, and general-purpose AI
- [ ] Create content variants for:
- [x] deployment intent
- [x] risk / hardening intent
- [ ] tool comparison intent
- [ ] cost / trade-off intent
- [ ] affiliate-safe recommendation intent
- [ ] Add topic scoring based on searchability, evergreen value, and conversion potential

## Phase 3: Asset Expansion Pipeline

- [x] Turn one topic into short + post + article + capture hook
- [ ] Add support for article-outline generation from the same brief
- [x] Add support for downloadable asset hooks such as checklists or templates
- [ ] Create reusable asset-brief templates instead of only case-study briefs

Execution note:

- first-batch execution plan: `docs/assets/FirstContentBatchExecutionPlan.md`
- first paid SOP path spec: `docs/assets/PaidSOPPathSpec.md`

## Phase 4: Owned Capture

- [x] Define one primary capture target: checklist download first
- [ ] Add CTA variants that point to owned capture instead of direct call booking
- [ ] Turn resource capture and subscription follow-up into a stable, low-overhead email path
- [ ] Add measurement for capture conversion by topic type
- [ ] Confirm whether checklist traffic reflects execution intent rather than passive saving behavior
- [ ] Confirm whether checklist visitors were previously relying on AI, README, or community answers, and where those alternatives felt insufficient

Implementation note:

- live site now uses a custom `/api/subscribe` endpoint for the checklist flow
- current reality is `site unlock + Buttondown confirmation + welcome + low-frequency topic sends`
- resource delivery is not primarily email-driven in the current implementation
- still needs real inbox verification before this phase item can be closed

## Phase 5: Monetization Experiments

- [ ] Define the first affiliate-safe topic cluster
- [x] Define the first paid digital asset to test
- [x] Decide the payment architecture principle for `shop.fzhang.dev`
- [ ] Test whether the strongest paid form is a standalone SOP, a project-level deployment judgment offer, or a broader guided service
- [ ] Define the first low-touch offer, only if needed as bootstrap revenue
- [ ] Map which content types should lead to which monetization type
- [ ] Require repeated outside demand signals before pushing the paid SOP harder

Current working paid asset:

- `开源 AI 项目上线与基础加固 SOP`

Current payment architecture rule:

- `shop.fzhang.dev` should use a payment / billing platform plus internal order mirror model
- do not use `Payoneer receiving account` as the primary checkout solution
- current preferred direction is `Paddle` first, `Lemon Squeezy` second, `Stripe` later if deeper control becomes necessary
- re-evaluate `InsForge` only after payment integration and first paid-asset traction make backend coordination the bottleneck

Current gating rule:

- do not let payment architecture work outrun demand validation for the SOP itself
- `shop.fzhang.dev` remains downstream of proof, not upstream of proof

## Phase 6: Site Integration

- [x] Keep `fzhang.dev` primarily as a content site
- [ ] Add a lightweight conversion path from homepage to owned assets
- [x] Make resource pages clearly stronger than adjacent public articles
- [x] Replace RSS-only subscription positioning with email + RSS dual paths
- [ ] Add dedicated pages for resources, comparisons, or templates
- [ ] Avoid turning the whole site into a generic service homepage

Direction note:

- content-first site positioning is agreed and documented
- homepage conversion copy is drafted
- actual site implementation is still pending

## Phase 7: Measurement

- [ ] Track which topics produce:
- [ ] clicks
- [ ] subscribers
- [ ] saved resources
- [ ] affiliate conversions
- [ ] product interest
- [ ] optional service conversations
- [ ] Maintain a topic ledger of outputs vs downstream value
- [ ] Record real-demand samples, not only funnel metrics
- [ ] Add evidence fields for current workaround, AI tools used, AI limitations, and willingness to continue toward paid help

Execution note:

- first-pass measurement spec: `docs/TopicLedgerMeasurementSpec.md`
- seeded ledger file: `docs/topic-ledger.csv`
- seeded distribution log: `docs/distribution-log.csv`

## Phase 8: Distribution Validation

- [x] Define a minimum distribution validation plan for the deployment cluster
- [ ] Execute the first 3 to 5 real distribution actions
- [ ] Log channel-level results in `docs/distribution-log.csv`
- [ ] Distinguish whether the current bottleneck is traffic, CTA click-through, or capture conversion
- [ ] Distinguish which concrete user type and scenario each successful action is attracting
- [ ] Run a direction-reset validation pass: 100 problem samples, 10-15 user interviews, 10-20 AI-vs-us comparisons, and 5-10 concierge judgments

## Demand Gates

Before treating a topic, asset, or SOP path as validated, ask:

1. Are repeated real users describing this problem in a concrete deployment or self-hosting moment?
2. Can we name the current main ICP in one sentence?
3. Are readers moving from article to checklist, not only consuming content passively?
4. Are deeper replies or follow-up questions appearing?
5. Is the push toward a paid SOP coming from repeated outside signals rather than internal excitement?
6. When users already have README / issue / AI, do they still want a stronger judgment layer?

If the answer to most of these is "no", the next step is more validation, not broader expansion.

## Decision Filters

Before adding any new feature, ask:

1. Does this create or improve a reusable asset?
2. Does this help convert rented reach into owned audience?
3. Does this improve future monetization with less manual work?
4. If it mainly helps sell more hours, is it still worth building here?

If the answer to 1-3 is "no", it is probably off-strategy.

## Execution Guardrails

- Do not let the repo become "another freelance channel manager".
- Do not force every visitor into a service CTA.
- Do not build around hot takes when evergreen intent is available.
- Do not overfit to one platform's algorithm; prefer portable assets.
- Do not confuse traffic with durable value.
- Do not ship content that has no plausible owned-capture or monetization path.

## Immediate Next Tasks

- [x] Choose the first asset type to optimize for: free resource capture first, paid SOP/template second
- [x] Rewrite the current account profile system around asset destination, not only service offer
- [x] Draft the first 10 topic angles with monetizable intent
- [x] Define the first lead magnet
- [x] Define one homepage conversion block for `fzhang.dev` that points to an owned asset
- [x] Create one pilot downloadable asset draft
- [x] Create one pilot article draft and one short-content pack that lead into it
- [x] Design the second-stage paid SOP/template that the lead magnet should eventually feed into
- [x] Draft the first paid SOP body
- [x] Update `origin` / `upstream` remotes so this fork can be pushed cleanly
- [x] Add a dedicated upstream sync script for the fork workflow
- [ ] Record at least 15 real-demand samples by `2026-05-14`
- [ ] Execute and log at least 5 real distribution actions by `2026-05-14`
- [ ] Decide the current main ICP for the deployment cluster by `2026-05-14`
- [ ] Re-evaluate whether article 3 should move into regular rotation only after those samples exist

## Executable Shortlist

1. Execute the first 3 to 5 real distribution actions for article 1 / article 2 and log them in `docs/distribution-log.csv`.
2. Use the first real sample to distinguish whether the current bottleneck is traffic, article-to-checklist click-through, checklist / confirmation conversion, or wrong ICP targeting.
3. Collect enough user quotes and scenario notes to name the current main ICP and their highest-cost deployment moment.
4. Only after the first distribution sample exists, decide whether article 3 should move from bridge draft into regular distribution and SOP-intent testing.
5. Only after repeated outside demand signals exist, decide whether the paid SOP path or `shop.fzhang.dev` deserves more execution time.

## Portfolio Rule

This fork is not the entire financial-freedom system by itself.

It is the current main execution repo inside a broader stack:

- `MoneyPrinterV2` = asset printer
- `fzhang.dev` = trust + long-tail traffic + owned capture
- knowledge base = source material + evidence ledger + decision filters
- `social-auto-upload` = distribution multiplier
- `paperclip` = later-stage product optionality, not the current short-term cash engine

If future work starts to blur these roles, use `docs/FinancialFreedomExecutionStack.md` as the reset point.
