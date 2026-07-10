#!/usr/bin/env python3
"""Generate provider-neutral review signals for draft X posts.

The default provider is a local stdlib-only rules pass. Optional providers can
add model signals, but none of them make final X policy decisions.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from urllib import error, request


OPENAI_ENDPOINT = "https://api.openai.com/v1/moderations"
DEFAULT_OPENAI_MODEL = "omni-moderation-latest"
DEFAULT_DETOXIFY_MODEL = "original"
DEFAULT_CARDIFF_MODEL = "cardiffnlp/twitter-roberta-base-offensive"

URL_RE = re.compile(r"https?://[^\s)>\]}]+", re.IGNORECASE)
MENTION_RE = re.compile(r"(?<!\w)@[A-Za-z0-9_]{1,15}\b")
HASHTAG_RE = re.compile(r"(?<!\w)#[^\s#@]+")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d .()/-]{7,}\d)(?!\d)")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
TOKEN_RE = re.compile(r"\b(?:api[_-]?key|secret|password|private[_-]?key|seed phrase|2fa code|otp)\b", re.IGNORECASE)

IDENTITY_TERMS = (
    "race",
    "religion",
    "ethnicity",
    "nationality",
    "immigrants",
    "women",
    "men",
    "disabled",
    "gay",
    "trans",
    "muslim",
    "jewish",
    "christian",
    "black",
    "white",
    "asian",
    "latino",
)
IDENTITY_ATTACK_TERMS = (
    "are animals",
    "are criminals",
    "are inferior",
    "should be eliminated",
    "should be banned",
    "should be deported",
)

SEVERITY_RANK = {"LOW": 0, "NEEDS_CONTEXT": 1, "MEDIUM": 2, "HIGH": 3, "BLOCKER": 4}

OPENAI_CATEGORY_POLICY_MAP = {
    "harassment": "abuse_harassment",
    "harassment/threatening": "abuse_harassment",
    "hate": "hateful_conduct",
    "hate/threatening": "hateful_conduct",
    "self-harm": "self_harm",
    "self-harm/intent": "self_harm",
    "self-harm/instructions": "self_harm",
    "sexual": "adult_sensitive_media",
    "sexual/minors": "adult_sensitive_media",
    "violence": "violent_content",
    "violence/graphic": "violent_content",
    "illicit": "illegal_regulated_goods",
    "illicit/violent": "illegal_regulated_goods",
}

DETOXIFY_POLICY_MAP = {
    "toxicity": "abuse_harassment",
    "severe_toxicity": "abuse_harassment",
    "obscene": "adult_sensitive_media",
    "threat": "violent_content",
    "insult": "abuse_harassment",
    "identity_attack": "hateful_conduct",
    "sexual_explicit": "adult_sensitive_media",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate local, OpenAI, or open-source model signals for draft X posts."
    )
    parser.add_argument("--input", required=True, help="Input .json, .jsonl, or .csv file.")
    parser.add_argument("--output", required=True, help="Output JSON signal file.")
    parser.add_argument(
        "--provider",
        choices=("rules", "openai", "detoxify", "cardiff-offensive"),
        default="rules",
        help="Signal provider. Default: rules",
    )
    parser.add_argument(
        "--model",
        default="",
        help=(
            "Provider-specific model. Defaults: openai="
            f"{DEFAULT_OPENAI_MODEL}, detoxify={DEFAULT_DETOXIFY_MODEL}, "
            f"cardiff-offensive={DEFAULT_CARDIFF_MODEL}"
        ),
    )
    parser.add_argument("--id-field", default="id", help="Record ID field. Default: id")
    parser.add_argument("--text-field", default="text", help="Post text field. Default: text")
    parser.add_argument(
        "--image-field",
        default="image_url",
        help="Optional image URL field. Use a list in JSON or semicolon-separated URLs in CSV.",
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="Environment variable containing the OpenAI API key. Used only with --provider openai.",
    )
    parser.add_argument(
        "--api-key-file",
        default="",
        help="Optional file containing the OpenAI API key. Used only with --provider openai.",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds.")
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between OpenAI requests.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Model score threshold for flags.")
    parser.add_argument("--high-threshold", type=float, default=0.8, help="Model score threshold for high risk.")
    parser.add_argument(
        "--allow-model-download",
        action="store_true",
        help="Allow transformers to download a CardiffNLP model if it is not cached locally.",
    )
    parser.add_argument("--max-posts", type=int, default=0, help="Limit records processed; 0 means no limit.")
    parser.add_argument("--dry-run", action="store_true", help="Parse input and write output without provider calls.")
    parser.add_argument("--include-raw", action="store_true", help="Include raw provider response where available.")
    return parser.parse_args()


def load_records(path: Path, id_field: str, text_field: str, image_field: str) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = normalize_json_records(data, text_field)
    elif suffix == ".jsonl":
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    elif suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    else:
        raise ValueError("Input must be .json, .jsonl, or .csv")

    records: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        if isinstance(row, str):
            row = {text_field: row}
        if not isinstance(row, dict):
            raise ValueError(f"Record {index} must be an object or string")
        text = str(row.get(text_field, "")).strip()
        if not text and not row.get(image_field):
            raise ValueError(f"Record {index} has no text or image URL")
        post_id = str(row.get(id_field) or f"post_{index:03d}")
        records.append(
            {
                "id": post_id,
                "text": text,
                "image_urls": normalize_image_urls(row.get(image_field)),
                "source": row,
            }
        )
    return records


def normalize_json_records(data: Any, text_field: str) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("posts"), list):
            return data["posts"]
        if isinstance(data.get("items"), list):
            return data["items"]
        return [{"id": key, text_field: value} for key, value in data.items()]
    if isinstance(data, str):
        return [data]
    raise ValueError("JSON input must be an array, object, or string")


def normalize_image_urls(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        parts = [part.strip() for part in value.replace(",", ";").split(";")]
        return [part for part in parts if part]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def provider_model(provider: str, model_arg: str) -> str:
    if model_arg:
        return model_arg
    if provider == "openai":
        return DEFAULT_OPENAI_MODEL
    if provider == "detoxify":
        return DEFAULT_DETOXIFY_MODEL
    if provider == "cardiff-offensive":
        return DEFAULT_CARDIFF_MODEL
    return "local-rules-v1"


def text_preview(text: str, limit: int = 160) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "..."


def base_post(record: dict[str, Any], provider: str) -> dict[str, Any]:
    return {
        "id": record["id"],
        "text_preview": text_preview(record["text"]),
        "has_text": bool(record["text"]),
        "image_url_count": len(record["image_urls"]),
        "signal_provider": provider,
        "signal_ran": False,
        "risk_hint": "NEEDS_CONTEXT",
        "flags": [],
        "metrics": text_metrics(record["text"]),
        "not_supported": [],
        "error": None,
    }


def text_metrics(text: str) -> dict[str, Any]:
    urls = URL_RE.findall(text)
    mentions = MENTION_RE.findall(text)
    hashtags = HASHTAG_RE.findall(text)
    visible_text = URL_RE.sub("", text)
    visible_text = MENTION_RE.sub("", visible_text)
    visible_text = HASHTAG_RE.sub("", visible_text)
    return {
        "char_count": len(text),
        "url_count": len(urls),
        "mention_count": len(mentions),
        "hashtag_count": len(hashtags),
        "line_count": len([line for line in text.splitlines() if line.strip()]),
        "link_only": bool(urls) and len(visible_text.strip()) < 30,
    }


def add_flag(post: dict[str, Any], area: str, severity: str, reason: str, evidence: str | None = None) -> None:
    post["flags"].append(
        {
            "policy_area": area,
            "severity": severity,
            "reason": reason,
            "evidence": evidence,
        }
    )
    post["risk_hint"] = max_risk(post["risk_hint"], severity)


def max_risk(left: str, right: str) -> str:
    return left if SEVERITY_RANK.get(left, 0) >= SEVERITY_RANK.get(right, 0) else right


def finalize_risk(post: dict[str, Any]) -> None:
    if not post["flags"] and post["risk_hint"] == "NEEDS_CONTEXT":
        post["risk_hint"] = "LOW"


def run_dry(records: list[dict[str, Any]], provider: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    posts = []
    for record in records:
        post = base_post(record, provider)
        post["error"] = "dry_run"
        posts.append(post)
    return posts, empty_batch_signals("not_run")


def run_rules(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    posts = []
    for record in records:
        post = base_post(record, "rules")
        post["signal_ran"] = True
        apply_text_rules(record, post)
        if record["image_urls"]:
            post["not_supported"].append("image_content_review")
            add_flag(post, "media_not_reviewed", "NEEDS_CONTEXT", "Image URLs were present but local rules do not inspect images.")
        finalize_risk(post)
        posts.append(post)

    batch_signals = attach_batch_rule_flags(records, posts)
    for post in posts:
        finalize_risk(post)
    return posts, batch_signals


def apply_text_rules(record: dict[str, Any], post: dict[str, Any]) -> None:
    text = record["text"]
    lower = text.lower()
    metrics = post["metrics"]

    if EMAIL_RE.search(text) or PHONE_RE.search(text) or SSN_RE.search(text):
        add_flag(post, "private_content", "HIGH", "Possible private contact or identifier data appears in the text.")

    if TOKEN_RE.search(text):
        add_flag(post, "scam_phishing_malware", "HIGH", "Possible credential, token, or account-compromise term appears.")

    if re.search(r"\b(kill|murder|shoot|stab|bomb|burn)\b.{0,80}\b(you|him|her|them|@\w+)\b", lower):
        add_flag(post, "violent_content", "HIGH", "Possible direct violent threat or targeted violent language.")

    if re.search(r"\b(kill yourself|hurt yourself|harm yourself|end your life)\b", lower):
        add_flag(post, "self_harm", "BLOCKER", "Possible encouragement of self-harm.")

    if re.search(r"\b(phishing|malware|steal cookies|steal credentials|drain wallet)\b", lower):
        add_flag(post, "scam_phishing_malware", "HIGH", "Possible scam, malware, or account-compromise content.")

    if re.search(r"\b(send|deposit|transfer)\b.{0,60}\b(crypto|bitcoin|eth|usdt)\b", lower) and re.search(
        r"\b(double|guaranteed|airdrop|free|giveaway)\b", lower
    ):
        add_flag(post, "scam_phishing_malware", "MEDIUM", "Possible high-risk crypto promotion pattern.")

    if contains_any_whole_term(lower, IDENTITY_TERMS) and any(term in lower for term in IDENTITY_ATTACK_TERMS):
        add_flag(post, "hateful_conduct", "HIGH", "Possible attack or exclusion claim about a protected or identity group.")

    if metrics["url_count"] >= 3:
        add_flag(post, "authenticity_spam", "MEDIUM", "Multiple URLs in one post can look spammy or require link review.")

    if metrics["link_only"]:
        add_flag(post, "authenticity_spam", "MEDIUM", "Link-only post with little visible context.")
        add_flag(post, "links_not_reviewed", "NEEDS_CONTEXT", "Destination URLs were not reviewed by the local rules provider.")

    if metrics["hashtag_count"] > 5:
        add_flag(post, "authenticity_spam", "MEDIUM", "High hashtag count may look like hashtag stuffing.")

    if metrics["mention_count"] > 5:
        add_flag(post, "abuse_harassment", "MEDIUM", "High mention count may create targeting or mass-reply risk.")


def empty_batch_signals(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "exact_duplicate_groups": [],
        "near_duplicate_pairs": [],
        "link_only_post_ids": [],
        "high_hashtag_post_ids": [],
        "high_mention_post_ids": [],
    }


def contains_any_whole_term(text: str, terms: tuple[str, ...]) -> bool:
    return any(re.search(r"\b" + re.escape(term) + r"\b", text) for term in terms)


def attach_batch_rule_flags(records: list[dict[str, Any]], posts: list[dict[str, Any]]) -> dict[str, Any]:
    batch = empty_batch_signals("used")
    by_id = {post["id"]: post for post in posts}
    normalized: dict[str, list[str]] = {}
    similarity_inputs: list[tuple[str, str]] = []

    for record in records:
        post_id = record["id"]
        post = by_id[post_id]
        metrics = post["metrics"]
        if metrics["link_only"]:
            batch["link_only_post_ids"].append(post_id)
        if metrics["hashtag_count"] > 5:
            batch["high_hashtag_post_ids"].append(post_id)
        if metrics["mention_count"] > 5:
            batch["high_mention_post_ids"].append(post_id)

        key = normalize_for_similarity(record["text"])
        if len(key) >= 20:
            normalized.setdefault(key, []).append(post_id)
            similarity_inputs.append((post_id, key))

    for post_ids in normalized.values():
        if len(post_ids) > 1:
            batch["exact_duplicate_groups"].append(post_ids)
            for post_id in post_ids:
                add_flag(by_id[post_id], "authenticity_spam", "HIGH", "Exact duplicate copy appears in the batch.")

    exact_pair_keys = {
        tuple(sorted((post_ids[index], post_ids[index + 1])))
        for post_ids in batch["exact_duplicate_groups"]
        for index in range(len(post_ids) - 1)
    }
    for left_index, (left_id, left_text) in enumerate(similarity_inputs):
        for right_id, right_text in similarity_inputs[left_index + 1 :]:
            if left_text == right_text:
                continue
            if tuple(sorted((left_id, right_id))) in exact_pair_keys:
                continue
            if min(len(left_text), len(right_text)) < 40:
                continue
            ratio = difflib.SequenceMatcher(None, left_text, right_text).ratio()
            if ratio >= 0.92:
                pair = {"ids": [left_id, right_id], "similarity": round(ratio, 3)}
                batch["near_duplicate_pairs"].append(pair)
                add_flag(by_id[left_id], "authenticity_spam", "MEDIUM", "Near-duplicate copy appears in the batch.")
                add_flag(by_id[right_id], "authenticity_spam", "MEDIUM", "Near-duplicate copy appears in the batch.")

    return batch


def normalize_for_similarity(text: str) -> str:
    text = text.lower()
    text = URL_RE.sub(" URL ", text)
    text = MENTION_RE.sub(" USER ", text)
    text = HASHTAG_RE.sub(" TAG ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_moderation_input(record: dict[str, Any]) -> Any:
    text = record["text"]
    image_urls = record["image_urls"]
    if not image_urls:
        return text

    content: list[dict[str, Any]] = []
    if text:
        content.append({"type": "text", "text": text})
    for url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": url}})
    return content


def load_api_key(api_key_file: str, api_key_env: str) -> str:
    if api_key_file:
        return Path(api_key_file).read_text(encoding="utf-8").strip()
    return os.environ.get(api_key_env, "")


def call_openai_moderation(api_key: str, model: str, moderation_input: Any, timeout: float) -> dict[str, Any]:
    payload = json.dumps({"model": model, "input": moderation_input}).encode("utf-8")
    req = request.Request(
        OPENAI_ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI moderation request failed: HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"OpenAI moderation request failed: {exc.reason}") from exc


def run_openai(records: list[dict[str, Any]], args: argparse.Namespace, model: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    api_key = load_api_key(args.api_key_file, args.api_key_env)
    if not api_key:
        raise MissingConfiguration(
            f"Missing API key. Set {args.api_key_env}, pass --api-key-file, or use --provider rules."
        )

    posts = []
    for index, record in enumerate(records):
        post = base_post(record, "openai")
        try:
            raw = call_openai_moderation(api_key, model, build_moderation_input(record), args.timeout)
            post.update(summarize_openai_result(raw, args.include_raw))
        except RuntimeError as exc:
            post["error"] = str(exc)
        posts.append(post)
        if args.sleep > 0 and index < len(records) - 1:
            time.sleep(args.sleep)
    return posts, empty_batch_signals("not_run")


def summarize_openai_result(raw: dict[str, Any], include_raw: bool) -> dict[str, Any]:
    result = (raw.get("results") or [{}])[0]
    scores = result.get("category_scores") or {}
    categories = result.get("categories") or {}
    flags = []
    risk_hint = "LOW"
    for category, flagged in categories.items():
        if not flagged:
            continue
        area = OPENAI_CATEGORY_POLICY_MAP.get(category, "needs_context")
        severity = "HIGH" if category in {"sexual/minors", "self-harm/instructions"} else "MEDIUM"
        flags.append(
            {
                "policy_area": area,
                "severity": severity,
                "reason": f"OpenAI moderation flagged category: {category}",
                "evidence": None,
            }
        )
        risk_hint = max_risk(risk_hint, severity)

    top_scores = sorted(
        [{"category": key, "score": value} for key, value in scores.items()],
        key=lambda item: item["score"],
        reverse=True,
    )[:5]
    summary = {
        "signal_ran": True,
        "risk_hint": risk_hint,
        "flags": flags,
        "moderation_ran": True,
        "flagged": result.get("flagged"),
        "flagged_categories": [key for key, value in categories.items() if value],
        "categories": categories,
        "category_scores": scores,
        "top_scores": top_scores,
        "category_applied_input_types": result.get("category_applied_input_types", {}),
        "error": None,
    }
    if include_raw:
        summary["raw"] = raw
    return summary


def run_detoxify(records: list[dict[str, Any]], args: argparse.Namespace, model_name: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        from detoxify import Detoxify  # type: ignore
    except ImportError as exc:
        return unavailable_provider(records, "detoxify", "Install the optional detoxify package to use this provider."), empty_batch_signals("not_run")

    try:
        model = Detoxify(model_name)
        predictions = model.predict([record["text"] for record in records])
    except Exception as exc:  # noqa: BLE001 - optional provider errors should be reported in output.
        return unavailable_provider(records, "detoxify", str(exc)), empty_batch_signals("not_run")

    posts = []
    for index, record in enumerate(records):
        post = base_post(record, "detoxify")
        post["signal_ran"] = True
        scores = {
            label: float(values[index] if isinstance(values, list) else values[index].item())
            for label, values in predictions.items()
        }
        post["provider_scores"] = scores
        add_model_score_flags(post, scores, DETOXIFY_POLICY_MAP, args.threshold, args.high_threshold)
        if record["image_urls"]:
            post["not_supported"].append("image_content_review")
        finalize_risk(post)
        posts.append(post)
    return posts, empty_batch_signals("not_run")


def run_cardiff_offensive(records: list[dict[str, Any]], args: argparse.Namespace, model_name: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline  # type: ignore
    except ImportError:
        return unavailable_provider(records, "cardiff-offensive", "Install the optional transformers package to use this provider."), empty_batch_signals("not_run")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=not args.allow_model_download)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=not args.allow_model_download)
        classifier = TextClassificationPipeline(model=model, tokenizer=tokenizer, top_k=None, function_to_apply="softmax")
        raw_outputs = classifier([record["text"] for record in records])
    except Exception as exc:  # noqa: BLE001 - optional provider errors should be reported in output.
        hint = str(exc)
        if not args.allow_model_download:
            hint = f"{hint} Pass --allow-model-download if you want transformers to fetch the model."
        return unavailable_provider(records, "cardiff-offensive", hint), empty_batch_signals("not_run")

    posts = []
    for record, raw_output in zip(records, raw_outputs):
        post = base_post(record, "cardiff-offensive")
        post["signal_ran"] = True
        normalized_output = normalize_cardiff_output(raw_output)
        post["provider_scores"] = {item["label"]: item["score"] for item in normalized_output}
        if args.include_raw:
            post["raw"] = raw_output
        for item in normalized_output:
            label = item["label"].lower()
            score = item["score"]
            is_offensive = "offensive" in label or label in {"label_1", "label_2"}
            if is_offensive and score >= args.threshold:
                severity = "HIGH" if score >= args.high_threshold else "MEDIUM"
                add_flag(
                    post,
                    "abuse_harassment",
                    severity,
                    f"CardiffNLP offensive-language score crossed threshold for {item['label']}.",
                    f"score={score:.3f}",
                )
        if record["image_urls"]:
            post["not_supported"].append("image_content_review")
        finalize_risk(post)
        posts.append(post)
    return posts, empty_batch_signals("not_run")


def normalize_cardiff_output(raw_output: Any) -> list[dict[str, Any]]:
    if raw_output and isinstance(raw_output[0], list):
        raw_output = raw_output[0]
    return [
        {"label": str(item.get("label", "")), "score": float(item.get("score", 0.0))}
        for item in raw_output
    ]


def add_model_score_flags(
    post: dict[str, Any],
    scores: dict[str, float],
    policy_map: dict[str, str],
    threshold: float,
    high_threshold: float,
) -> None:
    for label, score in scores.items():
        if score < threshold:
            continue
        severity = "HIGH" if score >= high_threshold else "MEDIUM"
        area = policy_map.get(label, "needs_context")
        add_flag(
            post,
            area,
            severity,
            f"Provider score crossed threshold for {label}.",
            f"score={score:.3f}",
        )


def unavailable_provider(records: list[dict[str, Any]], provider: str, message: str) -> list[dict[str, Any]]:
    posts = []
    for record in records:
        post = base_post(record, provider)
        post["risk_hint"] = "NEEDS_CONTEXT"
        post["error"] = message
        posts.append(post)
    return posts


class MissingConfiguration(RuntimeError):
    pass


def write_output(
    output_path: Path,
    input_path: Path,
    provider: str,
    model: str,
    dry_run: bool,
    posts: list[dict[str, Any]],
    batch_signals: dict[str, Any],
) -> None:
    output = {
        "metadata": {
            "tool": "moderate_posts.py",
            "provider": provider,
            "model": model,
            "input_path": str(input_path),
            "record_count": len(posts),
            "dry_run": dry_run,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": (
                "Signals are advisory only. The x-post-risk-reviewer skill must still apply "
                "X-specific policy, media, link, account, and context review."
            ),
        },
        "batch_signals": batch_signals,
        "posts": posts,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    provider = args.provider
    model = provider_model(provider, args.model)

    try:
        records = load_records(input_path, args.id_field, args.text_field, args.image_field)
        if args.max_posts > 0:
            records = records[: args.max_posts]

        if args.dry_run:
            posts, batch_signals = run_dry(records, provider)
        elif provider == "rules":
            posts, batch_signals = run_rules(records)
        elif provider == "openai":
            posts, batch_signals = run_openai(records, args, model)
        elif provider == "detoxify":
            posts, batch_signals = run_detoxify(records, args, model)
        elif provider == "cardiff-offensive":
            posts, batch_signals = run_cardiff_offensive(records, args, model)
        else:
            raise ValueError(f"Unknown provider: {provider}")

        write_output(output_path, input_path, provider, model, args.dry_run, posts, batch_signals)
    except MissingConfiguration as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(posts)} {provider} signal record(s) to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
