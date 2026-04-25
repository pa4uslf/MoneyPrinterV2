#!/usr/bin/env python3
import json
import os
import shutil
import sys
from typing import Tuple

import requests


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def check_url(url: str, timeout: int = 3) -> Tuple[bool, str]:
    try:
        response = requests.get(url, timeout=timeout)
        return True, f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    if not os.path.exists(CONFIG_PATH):
        fail(f"Missing config file: {CONFIG_PATH}")
        return 1

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    failures = 0

    stt_provider = str(cfg.get("stt_provider", "local_whisper")).lower()

    ok(f"stt_provider={stt_provider}")

    imagemagick_path = cfg.get("imagemagick_path", "")
    if imagemagick_path and os.path.exists(imagemagick_path):
        ok(f"imagemagick_path exists: {imagemagick_path}")
    else:
        warn(
            "imagemagick_path is not set to a valid executable path. "
            "MoviePy subtitle rendering may fail."
        )

    firefox_profile = cfg.get("firefox_profile", "")
    if firefox_profile:
        if os.path.isdir(firefox_profile):
            ok(f"firefox_profile exists: {firefox_profile}")
        else:
            warn(f"firefox_profile does not exist: {firefox_profile}")
    else:
        warn("firefox_profile is empty. Twitter/YouTube automation requires this.")

    # LM Studio (LLM)
    lms_cli = shutil.which("lms")
    if lms_cli:
        ok(f"lms CLI found: {lms_cli}")
    else:
        fail("lms CLI is not found in PATH. Install LM Studio CLI or add it to PATH.")
        failures += 1

    base = str(cfg.get("lms_base_url", "http://127.0.0.1:1234/v1")).rstrip("/")
    reachable, detail = check_url(f"{base}/models")
    if not reachable:
        fail(
            f"LM Studio server is not reachable at {base}: {detail}. "
            "Start it with `lms daemon up`, then `lms server start`, and load a model with `lms load <model>`."
        )
        failures += 1
    else:
        ok(f"LM Studio server reachable at {base}")
        try:
            payload = requests.get(f"{base}/models", timeout=5).json()
            models = [m.get("id") for m in payload.get("data", []) if m.get("id")]
            if models:
                ok(f"LM Studio models available: {', '.join(models[:10])}")
                configured_model = str(cfg.get("lms_model", "")).strip()
                non_chat_markers = ("embedding", "embed", "rerank")
                chat_models = [
                    model
                    for model in models
                    if not any(marker in model.lower() for marker in non_chat_markers)
                ]
                if configured_model and configured_model not in models:
                    fail(
                        f"Configured lms_model={configured_model} is not loaded in LM Studio. "
                        "Load it with `lms load <model>` or clear lms_model to pick interactively."
                    )
                    failures += 1
                elif configured_model and configured_model not in chat_models:
                    fail(
                        f"Configured lms_model={configured_model} looks like a non-chat model. "
                        "Load a text generation model for MPV2."
                    )
                    failures += 1
                elif not chat_models:
                    fail(
                        "LM Studio only reports embedding/rerank-style models. "
                        "Load a text generation model with `lms load <model>` before running MPV2."
                    )
                    failures += 1
                elif not configured_model:
                    warn(
                        "lms_model is empty. MPV2 will prompt you to choose one of the loaded text models at startup."
                    )
            else:
                warn("No models found in LM Studio. Load a model with `lms load <model>` first.")
        except Exception as exc:
            warn(f"Could not validate LM Studio model list: {exc}")

    # Image generation
    image_provider = str(cfg.get("image_provider", "nanobanana2")).lower()
    ok(f"image_provider={image_provider}")

    if image_provider in {"nanobanana2", "gemini", "gemini_image"}:
        api_key = cfg.get("nanobanana2_api_key", "") or os.environ.get("GEMINI_API_KEY", "")
        nb2_base = str(
            cfg.get(
                "nanobanana2_api_base_url",
                "https://generativelanguage.googleapis.com/v1beta",
            )
        ).rstrip("/")
        if api_key:
            ok("nanobanana2_api_key is set")
        else:
            fail("nanobanana2_api_key is empty (and GEMINI_API_KEY is not set)")
            failures += 1

        reachable, detail = check_url(nb2_base, timeout=8)
        if not reachable:
            warn(f"Nano Banana 2 base URL could not be reached: {detail}")
        else:
            ok(f"Nano Banana 2 base URL reachable: {nb2_base}")
    elif image_provider == "local_automatic1111":
        automatic1111_base = str(
            cfg.get("automatic1111_base_url", "http://127.0.0.1:7860")
        ).rstrip("/")
        reachable, detail = check_url(f"{automatic1111_base}/sdapi/v1/sd-models")
        if reachable:
            ok(f"Automatic1111 reachable at {automatic1111_base}")
        else:
            warn(f"Automatic1111 is not reachable at {automatic1111_base}: {detail}")
        warn(
            "Current YouTube image generation code still calls Nano Banana 2. "
            "Use image_provider=nanobanana2 for full video generation, or add an Automatic1111 backend before relying on this provider."
        )
    else:
        warn(f"Unknown image_provider={image_provider}. Skipping image provider-specific checks.")

    if stt_provider == "local_whisper":
        try:
            import faster_whisper  # noqa: F401

            ok("faster-whisper is installed")
        except Exception as exc:
            fail(f"faster-whisper is not importable: {exc}")
            failures += 1

    if failures:
        print("")
        print(f"Preflight completed with {failures} blocking issue(s).")
        return 1

    print("")
    print("Preflight passed. Local setup looks ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
