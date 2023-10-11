#!/usr/bin/env python3

"""Import the async_generator from 0-async_generator"""

import asyncio
from typing import List
async_generator = __import__('0-async_generator').async_generator


"""Create a function known as async comprehension"""


async def async_comprehension() -> List[float]:
    """Function that creates async comprehension"""
    return [i async for i in async_generator()]
