# TaskGuardian — Launch Plan

## Positioning

Incident-triggered audience, not broad. Headline for people arriving via search/Reddit after
a loss: **"Todoist just lost your tasks again. Get them back in 30 seconds."** Cold-traffic
variant: **"Every task app eventually loses data. Yours doesn't have to be gone for good."**

## Pricing

One-time lifetime license as the primary CTA, annual as the budget option. No monthly
subscription — a safety-net tool you hope to never use actively triggers "why am I still
paying for this" churn within one billing cycle. The license infra (Lemon Squeezy) supports
one-time cleanly, no dunning/cancellation flow needed.

| Tier | Price |
|---|---|
| Lifetime license | $29–39 one-time |
| Annual | $19/yr |

## Distribution — ranked by fit for this specific audience

1. **Todoist's own bug forum** (forum.todoist.com/c/-bugs) + **Asana forum** — where people
   report data loss directly to the vendor. Smallest audience, highest intent. Reply with a
   genuine fix, not a pitch.
2. **r/todoist, r/asana** — search "lost my tasks," "disappeared after update," reply in
   context. Check each sub's self-promo rules; frame as "this happened to me, so I built X."
3. **Hacker News "Show HN"** — best single channel. The Path A model (BYO-token, git as the
   diff engine, never touches your data) is exactly the shape HN rewards.
4. **Product Hunt** — do it, size expectations down. Too narrow a category for volume; treat
   as a backlink + credibility asset. Launch week 2, after HN gives a testimonial or two.
5. **Directories** (compounding value): terminal-trove.com, `awesome-cli-apps` GitHub list
   (PR, async review), alternativeto.net (captures long-tail "todoist backup" search).

## Launch-week sequence

- **Day 1** — Public GitHub repo + Lemon Squeezy live. Show HN post + r/todoist founder-story
  post, same day, same narrative (the GapScope-verified data-loss pattern).
- **Day 3** — Reply to every comment personally. Submit terminal-trove + alternativeto.net.
  Post a restore-demo GIF/thread.
- **Day 7** — PR to `awesome-cli-apps` (submit early, approval is async). Publish an SEO post
  targeting "todoist lost my tasks" directly — the compounding asset, not the launch spike.
  DM the handful of people who publicly complained.

## Pre-launch checklist

- [ ] Lemon Squeezy product created, price set ($29–39 lifetime / $19 annual)
- [ ] `TASKGUARDIAN_LICENSE_REQUIRED=1` set for the shipped/packaged build only — stays unset
      for Leon's own personal instance
- [ ] Cross-platform binaries built via `.github/workflows/release.yml` on a version tag
- [ ] Landing page live (see `landing/index.html`)
- [ ] At least one real live-account test run completed (`memory.md` tracks this)
