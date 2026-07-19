#!/usr/bin/env python
"""
Быстрая ручная проверка, что musicapi.ai (https://docs.musicapi.ai/) реально
работает с твоим токеном. Не трогает backend - только requests.

Сначала проверяет баланс кредитов (бесплатно, ничего не тратит).
Если не передан --skip-generate - запускает одну тестовую генерацию и
опрашивает статус, пока трек не будет готов (это тратит кредиты).

Примеры:
    python scripts/test_musicapi.py --token a7fc13bfc2...
    MUSICAPI_TOKEN=a7fc13bfc2... python scripts/test_musicapi.py
    python scripts/test_musicapi.py --skip-generate           # только проверить баланс
    python scripts/test_musicapi.py --check-task <task_id>    # достать результат уже
                                                                # запущенной задачи (например,
                                                                # если предыдущий запуск скрипта
                                                                # не дождался - генерация может
                                                                # занимать больше 3 минут)
"""
import argparse
import os
import sys
import time
from typing import Optional

import requests

# На Windows консоль по умолчанию не в UTF-8 - без этого кириллица в print() превращается в кракозябры
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://api.musicapi.ai"


def check_credits(token: str) -> dict:
    resp = requests.get(
        f"{BASE_URL}/api/v1/get-credits",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def start_generation(token: str, description: str, model: str) -> dict:
    payload = {
        "custom_mode": False,
        "mv": model,
        "gpt_description_prompt": description,
        "make_instrumental": True,
    }
    resp = requests.post(
        f"{BASE_URL}/api/v1/sonic/create",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=30,
    )
    print(f"POST /api/v1/sonic/create -> HTTP {resp.status_code}")
    resp.raise_for_status()
    return resp.json()


def get_task(token: str, task_id: str) -> dict:
    resp = requests.get(
        f"{BASE_URL}/api/v1/sonic/task/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def poll_status(token: str, task_id: str, max_wait: int, interval: int) -> Optional[dict]:
    waited = 0
    while waited <= max_wait:
        data = get_task(token, task_id)
        state = data.get("state") or data.get("status")
        print(f"  [{waited}s] state={state}")
        if state in ("succeeded", "failed", "error"):
            return data
        time.sleep(interval)
        waited += interval
    print("Таймаут ожидания - генерация может занимать дольше. Проверь результат позже:")
    print(f"  python scripts/test_musicapi.py --check-task {task_id}")
    return None


def print_result(data: dict) -> None:
    print("\nОтвет:", data)
    tracks = data.get("data") or []
    if tracks:
        print("\nГотовые треки:")
        for t in tracks:
            print(f"  - {t.get('title')}: {t.get('audio_url')}")
    else:
        print("В ответе нет треков - смотри поле state/status выше.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--token", default=os.environ.get("MUSICAPI_TOKEN"), help="Токен musicapi.ai")
    parser.add_argument("--model", default="sonic-v3-5")
    parser.add_argument(
        "--prompt",
        default="A short cheerful acoustic guitar melody, sunny morning mood",
        help="Описание сцены/настроения для генерации",
    )
    parser.add_argument("--skip-generate", action="store_true", help="Только проверить баланс кредитов")
    parser.add_argument("--check-task", metavar="TASK_ID", help="Только проверить результат уже существующей задачи")
    parser.add_argument("--max-wait", type=int, default=600, help="Макс. время ожидания опроса статуса, сек")
    parser.add_argument("--interval", type=int, default=15, help="Интервал опроса статуса, сек")
    args = parser.parse_args()

    if not args.token:
        print("Нужен токен: --token ... или переменная окружения MUSICAPI_TOKEN")
        sys.exit(1)

    if args.check_task:
        print(f"Проверяю результат task_id={args.check_task}...")
        try:
            print_result(get_task(args.token, args.check_task))
        except requests.HTTPError as e:
            body = e.response.text if e.response is not None else ""
            print(f"Не удалось получить статус: {e}\n{body}")
            sys.exit(1)
        return

    print("Проверяю баланс кредитов (бесплатно)...")
    try:
        credits = check_credits(args.token)
        print("Кредиты:", credits)
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else ""
        print(f"Не удалось получить баланс: {e}\n{body}")
        sys.exit(1)

    if args.skip_generate:
        print("\n--skip-generate указан, генерацию не запускаю.")
        return

    print(f"\nЗапускаю тестовую генерацию: {args.prompt!r} (model={args.model})")
    try:
        result = start_generation(args.token, args.prompt, args.model)
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else ""
        print(f"Ошибка генерации: {e}\n{body}")
        sys.exit(1)

    task_id = result.get("task_id")
    print("Ответ:", result)
    if not task_id:
        print("В ответе нет task_id - дальше опрашивать нечего.")
        return

    print(f"\ntask_id={task_id}. Опрашиваю статус каждые {args.interval} сек (максимум {args.max_wait} сек)...")
    final = poll_status(args.token, task_id, args.max_wait, args.interval)
    if final:
        print_result(final)


if __name__ == "__main__":
    main()
