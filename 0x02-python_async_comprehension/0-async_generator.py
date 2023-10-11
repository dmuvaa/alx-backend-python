#!/usr/bin/env python3

"""Imports a Module"""

import asyncio
import random


"""Create a Function"""


async def async_generator():
    """coroutine will loop 10 times, each time asynchronously wait 1 second"""
    for _ in range(10):
        await asyncio.sleep(1)
        yield random.uniform(0, 10)
