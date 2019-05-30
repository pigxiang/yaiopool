
import asyncio
from typing import Coroutine, AsyncGenerator


class Pool:

    def __init__(self, size: int = 0, loop=None):
        """ yet another asyncio pool ----simple,simple,simple

            async def do(msg):
                print(f"hello, {msg}")
                await asyncio.sleep(random.randint(0, 4))
                return msg


            async def args():
                for i in range(10):
                    await asyncio.sleep(0.4)
                    yield i


            pool = Pool(size=3)
            pool.map(do, args())
            results = pool.join()
            print(results)
        """

        self.loop = loop if loop else asyncio.get_event_loop()
        self.size = size
        self.results = []
        self.tasks = []
        self.index = -1

    def map(self, coro: Coroutine, arg_generator: AsyncGenerator = None):
        self.tasks = []
        for _ in range(self.size):
            self.tasks.append(
                self._task_wrapper(coro=coro, arg_generator=self._args_wrapper(arg_generator)))

    async def _args_wrapper(self, arg_generator):

        async for arg in arg_generator:
            self.index += 1
            yield self.index, arg

    def join(self) -> List[Any]:
        all_tasks = asyncio.gather(*self.tasks)
        self.loop.run_until_complete(all_tasks)
        return self.results

    def close(self):
        pass

    async def _task_wrapper(self, coro, arg_generator):
        async for seq, arg in arg_generator:
            try:
                result = await coro(arg)
            except Exception as e:
                result = e.__repr__()
            finally:
                self._result_gather(result, seq)

    def _result_gather(self, result, seq: int):
        length = len(self.results)
        if length < seq + 1:
            self.results.extend((None for _ in range(seq + 1 - length)))
        self.results[seq] = result
