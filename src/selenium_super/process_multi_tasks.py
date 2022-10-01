from contextlib import suppress
import asyncio
from concurrent.futures import ThreadPoolExecutor


class MultiTask:
    def __init__(self, func, name, args=[]):
        self.func = func
        self.args = args
        self.name = name


def has_duplicate_task_names(tasks_list: list[MultiTask]) -> tuple[bool, list[str]]:
    seen = []
    duplicates = []
    uniques = []
    for task in tasks_list:
        if task.name not in seen:
            seen.append(task.name)
            uniques.append(task)
        else:
            duplicates.append(task.name)

    return False if len(duplicates) == 0 else True, duplicates, uniques


class ProcessMultiTasks:
    def __init__(self):
        self.executor = None
        self.pending = None
        self.loop = None

    async def run_task(self, func, name, *args):
        return {'args': [*args], 'task_name': name, 'data': await self.loop.run_in_executor(self.executor, func, *args)}

    def run(self, tasks: list[MultiTask], return_when=asyncio.ALL_COMPLETED):
        has_duplicates, duplicates, uniques_tasks = has_duplicate_task_names(tasks)
        if has_duplicates:
            print(f'Detected duplicate task names: {duplicates}, running only first task of each duplicates tasks')
            tasks = uniques_tasks

        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor(len(tasks))

        task_set = set()
        for task in tasks:
            task_set.add(self.loop.create_task(self.run_task(task.func, task.name, *task.args)))

        done, self.pending = self.loop.run_until_complete(
            asyncio.wait(task_set, return_when=return_when))

        self.cleanup()

        tasks_data = dict()
        for coroutine in done:
            tasks_data[coroutine.result().get('task_name')] = {
                'args': coroutine.result().get('args'), 'data': coroutine.result().get('data')}
        return tasks_data

    def cleanup(self) -> None:
        for p in self.pending:
            p.cancel()
            with suppress(asyncio.CancelledError):
                self.loop.run_until_complete(p)

        self.loop.close()
        self.executor = None
        self.pending = None
        self.loop = None
