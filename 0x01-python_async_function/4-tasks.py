#!/usr/bin/env python3

"""imports a few modules"""

import asyncio
from typing import List
task_wait_random = __import__('3-tasks').task_wait_random


"""creates a class"""


async def task_wait_n(n: int, max_delay: int) -> List[float]:
    """function that takes in 2 int arguments n and max_delay"""
    delay_tasks = [task_wait_random(max_delay) for _ in range(n)]
    delays = []
    for i in asyncio.as_completed(delay_tasks):
        delay = await i
        delays.append(delay)
    return delays
