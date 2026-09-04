# Show HN + launch board copy (drafts — nothing posted, review and send yourself)

## Show HN title options

1. **Show HN: UnDeleted – backup CLI for Todoist/Asana/ClickUp, your data never leaves your machine** (leads with the mechanism, matches what HN rewards for "Show HN")
2. Show HN: I lost years of Todoist tasks to a sync bug, so I built a backup tool for it (leads with the origin story already on the landing page — more human, less feature-first)
3. Show HN: A $29 one-time backup tool for task apps, because subscriptions for a safety net felt wrong (leads with the pricing argument — sharpest hook if HN's audience skews toward "another SaaS tax" fatigue)

**Recommendation: #1.** HN's Show HN culture rewards technical specificity (BYO API token, local git repo as the diff engine, no hosted backend) over a founder-story hook — the origin story belongs in the first comment, not the title.

## First comment (post immediately after submitting, HN convention)

> Built this after Todoist silently dropped a batch of my own tasks during a sync — no error, no warning, just gone. Went looking for a backup tool and found two shapes: Todoist's own native backup (works, but only on paid tiers and only for Todoist), or ProBackup.io ($25-70/mo, covers Asana/ClickUp but not Todoist, and you lose the history the moment you stop paying).
>
> UnDeleted is the third shape: you bring your own API token, it snapshots your tasks into a local git repo you own, and it's a one-time $29 instead of a subscription for something you hope to never actually need. Covers Todoist, Asana, and ClickUp. Restore path is tested against real accounts, not just the export side.
>
> Source is on GitHub, MIT-licensed. Happy to answer questions about the diff/snapshot mechanism or why I picked git as the storage format over a database.

## Directory / launch-board submission text (short form, reusable across Dev Hunt / Smol Launch / Launching Next / Fazier / Microlaunch / Uneed / Peerlist Launchpad / Tiny Startups)

**Name:** UnDeleted

**One-liner:** A $29 one-time backup tool for Todoist, Asana, and ClickUp — because task apps lose data and subscriptions for a safety net don't make sense.

**Short description (2-3 sentences):**
UnDeleted snapshots your tasks into a local git repo you own, using your own API token — no hosted backend, no subscription, no vendor lock-in on your own backup. Built after a Todoist sync bug quietly deleted a batch of real tasks with no warning. Covers three platforms (Todoist, Asana, ClickUp) for a one-time $29, or $19/yr if you'd rather pay annually.

**Tags/categories:** productivity, developer tools, backup, CLI, open source

**Link:** [GitHub repo URL — fill in]
**Pricing:** $29 one-time / $19 annual
