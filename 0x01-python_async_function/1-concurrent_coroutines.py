#!/usr/bin/env python3

"""Imports the wait_random from 0-basic_async_syntax"""

import asyncio
from typing import List
wait_random = __import__('0-basic_async_syntax').wait_random


"""create a function to execute multiple coroutines at the same time with async"""


async def wait_n(n: int, max_delay: int) -> List[float]:
    """function that takes in 2 int arguments n and max_delay"""
    delay_tasks = [wait_random(max_delay) for _ in range(n)]
    delays = []
    for i in asyncio.as_completed(delay_tasks):
        delay = await i
        delays.append(delay)
    return delays