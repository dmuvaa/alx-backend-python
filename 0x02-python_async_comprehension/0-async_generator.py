#!/usr/bin/env python3

"""Imports several Modules: asyncio, and random"""

import asyncio
import random
from typing import List


"""Create a Function for the async generator"""


async def async_generator() -> List[float]:
    """coroutine will loop 10 times, each time asynchronously wait 1 second"""
    for _ in range(10):
        await asyncio.sleep(1)
        yield random.uniform(0, 10)
