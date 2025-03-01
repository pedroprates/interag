from collections import deque

class UniqueQueue:
    def __init__(self):
        self.queue = deque()
        self.seen = []
        self.len = 0

    def add(self, item: str | dict):
        if isinstance(item, str):
            item = item.split("#")[0]

        self.len += 1

        if item not in self.seen:
            self.queue.append(item)
            self.seen.append(item)

    def pop(self) -> str | dict:
        self.len -= 1

        if self.queue:
            item = self.queue.popleft()

            return item

        raise IndexError("Queue is empty!")

    def empty(self) -> bool:
        return self.len == 0

    def __len__(self) -> int:
        return self.len

    def __contains__(self, item) -> bool:
        return item in self.seen
