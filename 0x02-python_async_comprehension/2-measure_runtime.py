#!/usr/bin/env python3

"""Import both async_generator and async_comprehension modules"""

import asyncio
import time
async_comprehension = __import__('1-async_comprehension').async_comprehension


"""Create a new function"""


async def measure_runtime():
    """Function that measures the run time for the coroutines"""
    start_time = time.time()
    await asyncio.gather(*(async_comprehension() for _ in range(4)))
    end_time = time.time()
    return end_time - start_time
