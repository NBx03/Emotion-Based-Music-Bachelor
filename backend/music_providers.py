import os
from abc import ABC, abstractmethod

import requests


class MusicGenerationError(Exception):
    pass


def _track(track_id, title, audio_url, duration):
    return {"id": track_id, "title": title, "audio_url": audio_url, "duration": duration}


class MusicProvider(ABC):
    """Strategy interface for third-party Suno-style music generation services."""

    name: str

    @abstractmethod
    def generate(self, prompt: str, style: str, title: str, instrumental: bool, negative_tags: str) -> dict:
        """Kick off a generation task. Returns {"task_id": str | None, "raw": <provider response>}."""

    @abstractmethod
    def get_status(self, task_id: str) -> dict:
        """Poll a task. Returns {"state": str, "tracks": [track, ...], "raw": <provider response>}."""

    @abstractmethod
    def normalize_webhook_payload(self, payload: dict) -> dict:
        """Given a webhook POST body, return {"task_id": str | None, "state": str, "tracks": [track, ...]}."""


class SunoApiBoxProvider(MusicProvider):
    """https://docs.api.box/suno-api/quickstart - Bearer token, nested {"data": {...}} envelope."""

    name = "sunoapi_box"
    API_URL = "https://apibox.erweima.ai/api/v1/generate"
    STATUS_URL = "https://apibox.erweima.ai/api/v1/generate/record-info"

    def __init__(self, token: str, model: str = "V3_5", callback_url: str = ""):
        self.token = token
        self.model = model
        self.callback_url = callback_url

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def generate(self, prompt, style, title, instrumental, negative_tags):
        payload = {
            "prompt": prompt,
            "style": style,
            "title": title,
            "customMode": True,
            "instrumental": instrumental,
            "model": self.model,
            "negativeTags": negative_tags,
            "callBackUrl": self.callback_url,
        }
        resp = requests.post(self.API_URL, json=payload, headers=self._headers(), timeout=30)
        if resp.status_code != 200:
            raise MusicGenerationError(f"api.box: HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        task_id = (data.get("data") or {}).get("taskId")
        return {"task_id": task_id, "raw": data}

    def _tracks_from(self, container: dict):
        raw_tracks = ((container.get("response") or {}).get("data")) or []
        return [
            _track(t.get("id"), t.get("title"), t.get("audio_url") or t.get("audioUrl"), t.get("duration"))
            for t in raw_tracks
        ]

    def get_status(self, task_id):
        resp = requests.get(
            self.STATUS_URL, params={"taskId": task_id}, headers=self._headers(), timeout=30
        )
        resp.raise_for_status()
        payload = resp.json()
        record = payload.get("data") or {}
        return {"state": record.get("status", "unknown"), "tracks": self._tracks_from(record), "raw": payload}

    def normalize_webhook_payload(self, payload):
        record = payload.get("data") or {}
        tracks = self._tracks_from(record)
        task_id = record.get("task_id") or record.get("taskId")
        return {"task_id": task_id, "state": "succeeded" if tracks else "unknown", "tracks": tracks}


class MusicApiProvider(MusicProvider):
    """https://docs.musicapi.ai/ (Sonic/Suno) - Bearer token, flat {"data": [...]} envelope."""

    name = "musicapi"
    BASE_URL = "https://api.musicapi.ai"
    CREATE_PATH = "/api/v1/sonic/create"
    STATUS_PATH = "/api/v1/sonic/task/{task_id}"
    CREDITS_PATH = "/api/v1/get-credits"

    def __init__(self, token: str, model: str = "sonic-v3-5"):
        self.token = token
        self.model = model

    def _headers(self):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}

    def generate(self, prompt, style, title, instrumental, negative_tags):
        # custom_mode=False + gpt_description_prompt: this project generates a scene/mood
        # description (not literal lyrics), so we let musicapi.ai write the lyrics itself
        # instead of forcing our description into the lyrics-only "prompt" field.
        payload = {
            "custom_mode": False,
            "mv": self.model,
            "gpt_description_prompt": (prompt or "")[:400],
            "title": title,
            "tags": style,
            "negative_tags": negative_tags or None,
            "make_instrumental": instrumental,
        }
        payload = {k: v for k, v in payload.items() if v not in (None, "")}
        resp = requests.post(self.BASE_URL + self.CREATE_PATH, json=payload, headers=self._headers(), timeout=30)
        if resp.status_code != 200:
            raise MusicGenerationError(self._format_error(resp))
        data = resp.json()
        return {"task_id": data.get("task_id"), "raw": data}

    @staticmethod
    def _format_error(resp) -> str:
        try:
            body = resp.json()
        except ValueError:
            return f"musicapi.ai: HTTP {resp.status_code}: {resp.text}"
        message = body.get("error") or body.get("message") or resp.text
        if body.get("retriable"):
            message += " - сервис сообщает, что запрос можно повторить позже (retriable)"
        return f"musicapi.ai: HTTP {resp.status_code}: {message}"

    _SUCCESS_STATES = {"succeeded", "success"}
    _FAILURE_STATES = {"failed", "error"}

    def _tracks_from(self, payload: dict):
        raw_tracks = payload.get("data") or []
        tracks = []
        for t in raw_tracks:
            duration = t.get("duration")
            try:
                duration = float(duration) if duration is not None else None
            except (TypeError, ValueError):
                pass
            tracks.append(_track(t.get("clip_id") or t.get("id"), t.get("title"), t.get("audio_url"), duration))
        return tracks

    def _overall_state(self, payload: dict) -> str:
        # musicapi.ai's actual response (undocumented) puts "state" per-track inside the
        # "data" array, not at the top level - despite what the docs say. Derive an overall
        # state from the individual clips instead of trusting a top-level state/status field.
        raw_tracks = payload.get("data") or []
        if not raw_tracks:
            return payload.get("state") or payload.get("status") or "unknown"
        track_states = {(t.get("state") or t.get("status") or "").lower() for t in raw_tracks}
        if track_states & self._SUCCESS_STATES:
            return "succeeded"
        if track_states and track_states <= self._FAILURE_STATES:
            return "failed"
        return "pending"

    def get_status(self, task_id):
        url = self.BASE_URL + self.STATUS_PATH.format(task_id=task_id)
        resp = requests.get(url, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        return {"state": self._overall_state(payload), "tracks": self._tracks_from(payload), "raw": payload}

    def normalize_webhook_payload(self, payload):
        return {
            "task_id": payload.get("task_id"),
            "state": self._overall_state(payload),
            "tracks": self._tracks_from(payload),
        }

    def get_credits(self) -> dict:
        resp = requests.get(self.BASE_URL + self.CREDITS_PATH, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Переменная окружения {name} не задана. Она нужна для выбранного "
            f"MUSIC_PROVIDER (см. backend/.env.example)."
        )
    return value


_PROVIDER_FACTORIES = {
    "musicapi": lambda: MusicApiProvider(
        token=_require_env("MUSICAPI_TOKEN"),
        model=os.environ.get("MUSICAPI_MODEL", "sonic-v3-5"),
    ),
    "sunoapi_box": lambda: SunoApiBoxProvider(
        token=_require_env("SUNO_TOKEN"),
        model=os.environ.get("SUNOAPI_BOX_MODEL", "V3_5"),
        callback_url=os.environ.get(
            "SUNOAPI_BOX_CALLBACK_URL", "https://flamingo-key-owl.ngrok-free.app/api/webhook"
        ),
    ),
}


def get_music_provider() -> MusicProvider:
    """Reads MUSIC_PROVIDER from the environment and builds the matching strategy.
    Called lazily (per-request), not at import time, so the server can start and
    serve /api/upload without any music-provider token configured."""
    provider_name = os.environ.get("MUSIC_PROVIDER", "musicapi").strip().lower()
    try:
        factory = _PROVIDER_FACTORIES[provider_name]
    except KeyError:
        raise RuntimeError(
            f"Неизвестный MUSIC_PROVIDER={provider_name!r}. "
            f"Доступные варианты: {', '.join(_PROVIDER_FACTORIES)}"
        )
    return factory()
