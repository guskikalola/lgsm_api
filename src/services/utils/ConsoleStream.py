import asyncio
from fastapi import Request
from services.domain import Server
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import itertools

CONSOLE_SLEEP_TIME = 0.5
MAX_LINES_SENT=1000

class ConsoleChangeEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.buffer: list[str] = []
        self.currLine = 0

    def get_new_content(self, filepath: str):
        with open(filepath, "r") as consolelogs:
            tmp = []
            for line in itertools.islice(consolelogs, self.currLine, None, None):
                tmp.append(line)
                self.currLine+=1
            self.buffer.extend(tmp[-MAX_LINES_SENT:])
    def on_modified(self, event):
        if not event.is_directory:
            self.get_new_content(event.src_path)

    def new_content(self) -> bool:
        return len(self.buffer) > 0

    def flush(self) -> list[str]:
        new_data = self.buffer.copy()
        self.buffer.clear()
        return new_data


async def ConsoleStream(server: Server, request: Request):
    server_console_path = server.get_console_path()

    event_handler = ConsoleChangeEventHandler()
    event_handler.get_new_content(server_console_path)

    observer = Observer()
    observer.schedule(
        event_handler, path=server_console_path, recursive=False)
    observer.start()
    while True:
        if await request.is_disconnected():  # End when user closes connection
            observer.stop()
            observer.join()
            break
        if event_handler.new_content():  # There is new content to send
            yield "\\n".join(event_handler.flush())
        await asyncio.sleep(CONSOLE_SLEEP_TIME)
