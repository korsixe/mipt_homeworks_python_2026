import os
from collections.abc import Iterator
from typing import Any

from openai import OpenAI, APIConnectionError, APIStatusError
from openai.types.chat import ChatCompletionMessageParam

MAX_FILE_SIZE = 5 * 1024 * 1024


def _read_file(path: str) -> str | None:
    path = path.strip()
    if not os.path.exists(path):
        print(f'Ошибка: файл не найден: {path}')
        return None
    if os.path.getsize(path) > MAX_FILE_SIZE:
        print('Ошибка: файл превышает 5 МБ')
        return None
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f'Ошибка чтения файла: {e}')
        return None


def _split_by_paragraphs(text: str, n: int) -> list[str]:
    lines = text.split('\n')
    chunks, buf = [], []
    count = 0
    for line in lines:
        buf.append(line)
        if line.strip() == '':
            count += 1
            if count >= n:
                chunks.append('\n'.join(buf).strip())
                buf = []
                count = 0
    if ''.join(buf).strip():
        chunks.append('\n'.join(buf).strip())
    return [c for c in chunks if c]


def _split_by_len(text: str, length: int) -> list[str]:
    return [text[i:i + length] for i in range(0, len(text), length)]


def _parse_command(cmd: str) -> tuple[int | None, int | None, bool]:
    paragraph = None
    length = None
    auto = '-y' in cmd

    for part in cmd.split():
        if part.startswith('paragraph='):
            try:
                val = int(part.split('=')[1])
                if val > 0:
                    paragraph = val
            except ValueError:
                pass
        elif part.startswith('len='):
            try:
                val = int(part.split('=')[1])
                if val > 0:
                    length = val
            except ValueError:
                pass

    return paragraph, length, auto


def _stream_chunk(
    client: OpenAI,
    model: Any,
    temperature: Any,
    user_prompt: str,
    chunk: str,
) -> Iterator[str]:
    messages: list[ChatCompletionMessageParam] = [
        {'role': 'user', 'content': f'{user_prompt}\n\n{chunk}'}
    ]
    with client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
    ) as stream:
        for chunk_data in stream:
            delta = chunk_data.choices[0].delta.content or ''
            if delta:
                yield delta


def run_file_chunk(cmd: str, cfg: dict[str, Any]) -> None:
    paragraph, length, auto = _parse_command(cmd)

    print('Введите путь до файла')
    path = input('>>> ').strip()

    text = _read_file(path)
    if text is None:
        return

    print('Принято. Что нужно сделать для каждого фрагмента (User Prompt)?')
    user_prompt = input('>>> ').strip()
    print('Принято. Начинаю обработку:')

    if length is not None:
        chunks = _split_by_len(text, length)
    elif paragraph is not None:
        chunks = _split_by_paragraphs(text, paragraph)
    else:
        chunks = _split_by_paragraphs(text, 1)

    client = OpenAI(api_key=cfg['api_key'], base_url=cfg['api_host'])
    model = cfg.get('model', 'gpt-4o-mini')
    temperature = cfg.get('temperature', 0.7)

    for chunk in chunks:
        if not auto:
            user_in = input('>>> ').strip()
            if user_in == r'\q':
                print('Обработка файла прервана.')
                return

        try:
            print('>>> ', end='', flush=True)
            for token in _stream_chunk(client, model, temperature, user_prompt, chunk):
                print(token, end='', flush=True)
            print()
        except KeyboardInterrupt:
            print('\nЗапрос прерван.')
            if not auto:
                continue
            else:
                return
        except (APIStatusError, APIConnectionError) as e:
            print(f'\nОшибка API: {e}')
            if not auto:
                continue
            else:
                return

    print('Обработка файла завершена.')
