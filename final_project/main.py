import os
import sys

from chat import ChatSession
from config import load_config
from file_chunk import run_file_chunk


def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def main() -> None:
    cfg = load_config()
    session = ChatSession(cfg)

    print('AI Ассистент запущен. Введите \\q для выхода, /reset для сброса чата.')

    while True:
        try:
            user_input = input('>>> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nВыход.')
            sys.exit(0)

        if user_input == r'\q':
            print('Выход.')
            sys.exit(0)

        if user_input == '/reset':
            clear_screen()
            session.reset()
            print('Чат сброшен.')
            continue

        if user_input.startswith('/file_chunk') or user_input.startswith('/filechunk'):
            run_file_chunk(user_input, cfg)
            continue

        if not user_input:
            continue

        reply = session.send(user_input)
        if reply is None:
            print('Запрос прерван. Введите новое сообщение.')
        else:
            print(f'>>> {reply}')


if __name__ == '__main__':
    main()