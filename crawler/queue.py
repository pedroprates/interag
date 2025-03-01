from collections import deque

class URLQueue:
    def __init__(self):
        self.queue = deque()
        self.seen = set()
        self.len = 0

    def add(self, item: str):
        item = item.split("#")[0]
        self.len += 1

        if item not in self.seen:
            self.queue.append(item)
            self.seen.add(item)

    def pop(self) -> str:
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
