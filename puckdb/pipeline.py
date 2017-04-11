import asyncio

class Pipeline(object):
    def __init__(self, workers: int = 5, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.workers = workers
        self.loop = loop
        self.queue = asyncio.Queue(loop=loop)
        self.transforms = []
        self.data = []

    async def _work(self):
        while True:
            data = await self.queue.get()
            for transform in self.transforms:
                data = await transform(data)
            self.queue.task_done()

    def transform(self, transform):
        self.transforms.append(transform)
        return self

    def add(self, data: object):
        pass

    async def run_async(self):
        workers = [asyncio.Task(self._work(), loop=self.loop) for _ in range(self.workers)]
        await self.queue.join()
        for worker in workers:
            worker.cancel()

    def run(self):
        self.loop.run_until_complete(self.run_async())
