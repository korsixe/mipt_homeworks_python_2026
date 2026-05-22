import os
import re
from typing import Any, cast

import httpx
from openai import OpenAI, APIStatusError
from openai.types.chat import ChatCompletionMessageParam

MAX_FILE_SIZE = 5 * 1024 * 1024

FILE_PATTERN = re.compile(r'@::(.+?)::', re.DOTALL)


def _attach_files(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        path = match.group(1).strip()
        try:
            size = os.path.getsize(path)
        except OSError:
            return f'[Ошибка: файл не найден: {path}]'
        if size > MAX_FILE_SIZE:
            return f'[Ошибка: файл превышает 5 МБ: {path}]'
        try:
            with open(path, encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f'[Ошибка чтения файла {path}: {e}]'

    return FILE_PATTERN.sub(replace, text)


def _trim_and_get_content(
    history: list[dict[str, Any]],
    new_content: str,
    limit_chars: int | None,
    limit_message: int | None,
) -> str:
    if limit_message is not None:
        while len(history) >= limit_message:
            history.pop(0)

    if limit_chars is not None:
        if len(new_content) >= limit_chars:
            new_content = new_content[-limit_chars:]
            history.clear()
            return new_content

        total = sum(len(m['content']) for m in history) + len(new_content)
        while total > limit_chars and history:
            removed = history.pop(0)
            total -= len(removed['content'])

    return new_content


class ChatSession:
    def __init__(self, cfg: dict[str, Any]):
        self.cfg = cfg
        self.client = OpenAI(
            api_key=cfg['api_key'],
            base_url=cfg['api_host'],
            http_client=httpx.Client(
                transport=httpx.HTTPTransport(),
                headers={'Accept-Encoding': 'identity'},
            ),
        )
        self.history: list[dict[str, Any]] = []
        self.system_prompt: str | None = cfg.get('system_prompt')

    def _build_messages(self) -> list[dict[str, Any]]:
        msgs = []
        if self.system_prompt:
            msgs.append({'role': 'system', 'content': self.system_prompt})
        msgs.extend(self.history)
        return msgs

    def _get_model(self) -> str:
        return str(self.cfg.get('model', 'gpt-4o-mini'))

    def send(self, user_input: str) -> str | None:
        content = _attach_files(user_input)
        content = _trim_and_get_content(
            self.history,
            content,
            self.cfg.get('limit_chars'),
            self.cfg.get('limit_message'),
        )

        self.history.append({'role': 'user', 'content': content})
        messages = self._build_messages()

        try:
            response = self.client.chat.completions.create(
                model=self._get_model(),
                messages=cast(list[ChatCompletionMessageParam], messages),
                temperature=self.cfg.get('temperature', 0.7),
            )
            reply: str | None = response.choices[0].message.content
            self.history.append({'role': 'assistant', 'content': reply})
            return reply
        except KeyboardInterrupt:
            self.history.pop()
            print()
            return None
        except APIStatusError as e:
            self.history.pop()
            print(f'Ошибка API ({e.status_code}): {e.message}')
            return None

    def reset(self) -> None:
        self.history.clear()
