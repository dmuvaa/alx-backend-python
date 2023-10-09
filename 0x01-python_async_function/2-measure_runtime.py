#!/usr/bin/env python3

"""Imports 3 modules- asyncio, 1-concurrent_coroutines, and List"""

import asyncio
import time
wait_n = __import__('1-concurrent_coroutines').wait_n


"""creates an asynchronous function"""


def measure_time(n: int, max_delay: int) -> float:
    """Measure the total execution time for wait_n and returns total_time"""
    start_time = time.time()
    asyncio.run(wait_n(n, max_delay))
    end_time = time.time()
    total_time = end_time - start_time

    return total_time / n
