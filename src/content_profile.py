from __future__ import annotations

import os

from typing import Any

from config import ROOT_DIR


REQUIRED_STRATEGY_FIELDS = {
    "strongest_scene": (
        "Required because scene strength decides whether the content starts from a real moment of tension "
        "instead of a generic thesis."
    ),
    "expected_attribute": (
        "Required because it defines the one promise that must be delivered with certainty instead of "
        "burying the core value under decorative details."
    ),
    "desired_identity": (
        "Required because the content should speak to the kind of person the reader is trying to become, "
        "not only to a broad segment label."
    ),
}


def _split_items(value: Any) -> list[str]:
    """
    Normalizes comma/newline separated values into a compact string list.

    Args:
        value (Any): Raw user-provided value

    Returns:
        items (list[str]): Cleaned list of strings
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if not isinstance(value, str):
        return [str(value).strip()] if str(value).strip() else []

    normalized = value.replace("\n", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def get_required_strategy_fields() -> dict[str, str]:
    """
    Returns the required strategy fields and why they matter.

    Returns:
        fields (dict[str, str]): Field -> reason mapping
    """
    return REQUIRED_STRATEGY_FIELDS.copy()


def normalize_content_profile(content_profile: dict | None) -> dict:
    """
    Returns a normalized content profile used by service-led content prompts.

    Args:
        content_profile (dict | None): Raw profile data from the account cache

    Returns:
        profile (dict): Normalized profile
    """
    raw = content_profile or {}

    profile = {
        "content_mode": str(raw.get("content_mode", "") or "").strip().lower(),
        "content_variant": str(raw.get("content_variant", "") or "").strip().lower(),
        "asset_type": str(raw.get("asset_type", "") or "").strip().lower(),
        "capture_type": str(raw.get("capture_type", "") or "").strip().lower(),
        "monetization_type": str(raw.get("monetization_type", "") or "").strip().lower(),
        "target_customer": str(raw.get("target_customer", "") or "").strip(),
        "desired_identity": str(raw.get("desired_identity", "") or "").strip(),
        "avoided_identity": str(raw.get("avoided_identity", "") or "").strip(),
        "self_investment": str(raw.get("self_investment", "") or "").strip(),
        "offer_name": str(raw.get("offer_name", "") or "").strip(),
        "asset_name": str(raw.get("asset_name", "") or "").strip(),
        "strongest_scene": str(raw.get("strongest_scene", "") or "").strip(),
        "trigger_moment": str(raw.get("trigger_moment", "") or "").strip(),
        "feared_outcome": str(raw.get("feared_outcome", "") or "").strip(),
        "primary_problem": str(raw.get("primary_problem", "") or "").strip(),
        "desired_outcome": str(raw.get("desired_outcome", "") or "").strip(),
        "expected_attribute": str(raw.get("expected_attribute", "") or "").strip(),
        "delighter": str(raw.get("delighter", "") or "").strip(),
        "reverse_attribute": str(raw.get("reverse_attribute", "") or "").strip(),
        "cta_url": str(raw.get("cta_url", "") or "").strip(),
        "case_brief_file": str(raw.get("case_brief_file", "") or "").strip(),
        "review_notes": str(raw.get("review_notes", "") or "").strip(),
        "proof_points": _split_items(raw.get("proof_points")),
        "content_pillars": _split_items(raw.get("content_pillars")),
        "value_mix": _split_items(raw.get("value_mix")),
        "supporter_roles": _split_items(raw.get("supporter_roles")),
        "blocker_roles": _split_items(raw.get("blocker_roles")),
    }

    if not profile["content_mode"]:
        has_strategy_data = any(
            [
                profile["target_customer"],
                profile["desired_identity"],
                profile["avoided_identity"],
                profile["self_investment"],
                profile["offer_name"],
                profile["asset_type"],
                profile["capture_type"],
                profile["monetization_type"],
                profile["asset_name"],
                profile["strongest_scene"],
                profile["trigger_moment"],
                profile["feared_outcome"],
                profile["primary_problem"],
                profile["desired_outcome"],
                profile["value_mix"],
                profile["expected_attribute"],
                profile["delighter"],
                profile["reverse_attribute"],
                profile["cta_url"],
                profile["case_brief_file"],
                profile["review_notes"],
                profile["proof_points"],
                profile["content_pillars"],
                profile["supporter_roles"],
                profile["blocker_roles"],
            ]
        )
        profile["content_mode"] = "asset_printer" if has_strategy_data else "legacy"

    if not profile["content_variant"]:
        profile["content_variant"] = "general"

    return profile


def missing_required_strategy_fields(content_profile: dict | None) -> list[str]:
    """
    Returns the missing high-priority strategy fields for asset-printer generation.

    Args:
        content_profile (dict | None): Account content profile

    Returns:
        missing (list[str]): Missing required field names
    """
    profile = normalize_content_profile(content_profile)
    return [
        field_name
        for field_name in REQUIRED_STRATEGY_FIELDS
        if not str(profile.get(field_name, "") or "").strip()
    ]


def build_required_field_status(content_profile: dict | None) -> str:
    """
    Builds a prompt-friendly block explaining required-field status and downgrade logic.

    Args:
        content_profile (dict | None): Account content profile

    Returns:
        status (str): Compact status block
    """
    missing = missing_required_strategy_fields(content_profile)

    if not missing:
        return "Required strategy fields status: all present."

    notes = [
        "Required strategy fields status: missing -> " + ", ".join(missing),
        "Explicit downgrade rule:",
        "- Do not pretend the missing fields are known facts.",
        "- Stay conservative and concrete.",
        "- Prefer using the available trigger/problem context instead of inventing a richer persona or scene.",
    ]

    for field_name in missing:
        notes.append(f"- {field_name}: {REQUIRED_STRATEGY_FIELDS[field_name]}")

    return "\n".join(notes)


def has_service_strategy(content_profile: dict | None) -> bool:
    """
    Determines whether an account should use the personalized service-led prompts.

    Args:
        content_profile (dict | None): Account content profile

    Returns:
        enabled (bool): True when service-led prompts should be used
    """
    profile = normalize_content_profile(content_profile)
    return profile["content_mode"] in {"service_case_study", "asset_printer"}


def build_profile_context(content_profile: dict | None) -> str:
    """
    Serializes the normalized profile into prompt-friendly bullet points.

    Args:
        content_profile (dict | None): Account content profile

    Returns:
        context (str): Compact text block
    """
    profile = normalize_content_profile(content_profile)

    lines = []
    if profile["target_customer"]:
        lines.append(f"Target customer: {profile['target_customer']}")
    if profile["desired_identity"]:
        lines.append(f"Desired identity: {profile['desired_identity']}")
    if profile["avoided_identity"]:
        lines.append(f"Avoided identity: {profile['avoided_identity']}")
    if profile["self_investment"]:
        lines.append(f"Self-investment already in motion: {profile['self_investment']}")
    if profile["content_variant"]:
        lines.append(f"Content variant: {profile['content_variant']}")
    if profile["asset_type"]:
        lines.append(f"Primary asset type: {profile['asset_type']}")
    if profile["capture_type"]:
        lines.append(f"Capture type: {profile['capture_type']}")
    if profile["monetization_type"]:
        lines.append(f"Monetization type: {profile['monetization_type']}")
    if profile["offer_name"]:
        lines.append(f"Offer: {profile['offer_name']}")
    if profile["asset_name"]:
        lines.append(f"Asset name: {profile['asset_name']}")
    if profile["strongest_scene"]:
        lines.append(f"Strongest scene: {profile['strongest_scene']}")
    if profile["trigger_moment"]:
        lines.append(f"Trigger moment: {profile['trigger_moment']}")
    if profile["feared_outcome"]:
        lines.append(f"Feared outcome: {profile['feared_outcome']}")
    if profile["primary_problem"]:
        lines.append(f"Primary problem solved: {profile['primary_problem']}")
    if profile["desired_outcome"]:
        lines.append(f"Desired customer outcome: {profile['desired_outcome']}")
    if profile["value_mix"]:
        lines.append("Value mix: " + "; ".join(profile["value_mix"]))
    if profile["expected_attribute"]:
        lines.append(f"Expected attribute: {profile['expected_attribute']}")
    if profile["delighter"]:
        lines.append(f"Delighter: {profile['delighter']}")
    if profile["reverse_attribute"]:
        lines.append(f"Reverse attribute to avoid: {profile['reverse_attribute']}")
    if profile["proof_points"]:
        lines.append("Proof points: " + "; ".join(profile["proof_points"]))
    if profile["content_pillars"]:
        lines.append("Content pillars: " + "; ".join(profile["content_pillars"]))
    if profile["supporter_roles"]:
        lines.append("Supporter roles: " + "; ".join(profile["supporter_roles"]))
    if profile["blocker_roles"]:
        lines.append("Blocker roles: " + "; ".join(profile["blocker_roles"]))
    if profile["cta_url"]:
        lines.append(f"CTA URL: {profile['cta_url']}")
    if profile["case_brief_file"]:
        lines.append(f"Case brief file: {profile['case_brief_file']}")
    if profile["review_notes"]:
        lines.append(f"Review notes: {profile['review_notes']}")

    return "\n".join(lines)


def resolve_case_brief_path(content_profile: dict | None) -> str:
    """
    Resolves an optional case brief file path relative to the repo root.

    Args:
        content_profile (dict | None): Account content profile

    Returns:
        path (str): Absolute case brief path or empty string
    """
    profile = normalize_content_profile(content_profile)
    raw_path = profile["case_brief_file"]

    if not raw_path:
        return ""

    if os.path.isabs(raw_path):
        return raw_path

    return os.path.join(ROOT_DIR, raw_path)


def load_case_brief(content_profile: dict | None) -> str:
    """
    Loads an optional reusable case brief from disk.

    Args:
        content_profile (dict | None): Account content profile

    Returns:
        brief (str): Case brief text or empty string
    """
    resolved = resolve_case_brief_path(content_profile)

    if not resolved or not os.path.exists(resolved):
        return ""

    with open(resolved, "r", errors="ignore") as handle:
        return handle.read().strip()
