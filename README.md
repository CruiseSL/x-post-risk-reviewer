# X Post Risk Reviewer

Review draft X posts for likely policy, visibility, and account-risk issues before publishing. The Skill supports single posts, batches, compliant rewrites, and posting-plan audits.

## Install

Install directly from GitHub for Codex:

```bash
git clone https://github.com/CruiseSL/x-post-risk-reviewer.git ~/.codex/skills/x-post-risk-reviewer
```

Or install it for a project-level Agent skills directory:

```bash
mkdir -p .agents/skills
git clone https://github.com/CruiseSL/x-post-risk-reviewer.git .agents/skills/x-post-risk-reviewer
```

You can also copy this whole directory into your agent's skills directory.

Example paths:

```text
~/.codex/skills/x-post-risk-reviewer/
.agents/skills/x-post-risk-reviewer/
```

Then use a prompt like:

```text
Use $x-post-risk-reviewer to review these draft X posts before publishing.

Context:
- Account type:
- Region:
- Posting plan:
- Any media or links:

Posts:
1. ...
2. ...
3. ...
```

For batch review, include IDs if you have them:

```text
Use $x-post-risk-reviewer for this batch. Keep the IDs in your output and tell me the per-post risk plus batch-pattern risk.

post_001: ...
post_002: ...
post_003: ...
```

This skill helps reduce visible policy and enforcement risk. It does not guarantee reach, ranking, publication, or account safety, and it must not be used to disguise violating content.

## What It Reviews

- likely X Rules concerns in each draft
- privacy, harassment, hateful-conduct, violent-content, and authenticity risks
- batch patterns such as repeated copy, mass mentions, link-only runs, and coordinated posting signals
- whether context, media consent, legal review, or human review is still required
- compliant rewrites that remove the risky element instead of disguising it

## Optional Signal Runner

For local batch files, you can generate a signal file first. The default provider is local rules, so it needs no API key, network access, paid API, or model download:

```bash
python3 scripts/moderate_posts.py --input posts.json --output moderation-signals.json
```

Equivalent explicit form:

```bash
python3 scripts/moderate_posts.py --provider rules --input posts.json --output moderation-signals.json
```

The local `rules` provider checks obvious text and batch-pattern signals such as duplicate copy, near-duplicates, link-only posts, heavy hashtags, mass mentions, possible private data, possible credentials, and high-risk threat/scam terms. It is not a full content-safety model and it does not inspect image pixels or final URL destinations.

Supported input formats: `.json`, `.jsonl`, `.csv`.

Default fields:

- `id`
- `text`
- optional `image_url`

Then paste or attach `moderation-signals.json` to the agent with the original drafts and ask it to continue with `$x-post-risk-reviewer`. The script output is only a signal; the Skill still does the X-specific policy and context review.

Dry-run parsing check:

```bash
python3 scripts/moderate_posts.py --input examples/posts.sample.json --output /tmp/moderation-signals.sample.json --dry-run
```

### Optional Providers

OpenAI moderation signal:

```bash
python3 scripts/moderate_posts.py --provider openai --input posts.json --output moderation-signals.json
```

OpenAI's moderation endpoint is free to use according to OpenAI's docs, but it is not anonymous: the request still needs an OpenAI API key for authentication, quota, and abuse prevention. This is not an X API key. Only run this on drafts you are allowed to send to the moderation API.

Or keep the key in a temporary file outside the package:

```bash
python3 scripts/moderate_posts.py --provider openai --input posts.json --output moderation-signals.json --api-key-file /tmp/openai_api_key
```

Open-source model signals are optional and require local dependencies:

```bash
python3 scripts/moderate_posts.py --provider detoxify --input posts.json --output moderation-signals.json
python3 scripts/moderate_posts.py --provider cardiff-offensive --input posts.json --output moderation-signals.json
```

These providers do not require an OpenAI key, but they may require Python packages, local model files, CPU/GPU time, and their own license/privacy review. The CardiffNLP adapter uses cached model files by default; pass `--allow-model-download` only if downloading model weights is acceptable.

Custom CSV fields:

```bash
python3 scripts/moderate_posts.py --provider rules --input posts.csv --output moderation-signals.json --text-field body --id-field post_id
```
