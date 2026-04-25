import requests

from config import get_lms_base_url

_selected_model: str | None = None


def _base_url() -> str:
    return get_lms_base_url().rstrip("/")


def list_models() -> list[str]:
    """
    Lists all models available on the local LM Studio server.

    Returns:
        models (list[str]): Sorted list of model names.
    """
    response = requests.get(f"{_base_url()}/models", timeout=5)
    response.raise_for_status()
    payload = response.json()
    return sorted(model["id"] for model in payload.get("data", []) if model.get("id"))


def select_model(model: str) -> None:
    """
    Sets the model to use for all subsequent generate_text calls.

    Args:
        model (str): An LM Studio model name.
    """
    global _selected_model
    _selected_model = model


def get_active_model() -> str | None:
    """
    Returns the currently selected model, or None if none has been selected.
    """
    return _selected_model


def generate_text(prompt: str, model_name: str = None) -> str:
    """
    Generates text using the local LM Studio server.

    Args:
        prompt (str): User prompt
        model_name (str): Optional model name override

    Returns:
        response (str): Generated text
    """
    model = model_name or _selected_model
    if not model:
        raise RuntimeError(
            "No LM Studio model selected. Call select_model() first or pass model_name."
        )

    response = requests.post(
        f"{_base_url()}/chat/completions",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()

    return payload["choices"][0]["message"]["content"].strip()
