"""
Note: time.sleep is not awaitable
"""
import asyncio
from time import time


class CFG:
    batch = False


async def cook_rice() -> str:
    print("Start cook_rice()...")
    await asyncio.sleep(5)
    print("End cook_rice()!")

    return "Rice cooked!"


async def chop_vegetable() -> str:
    print("Start chop_vegetable()...")
    await asyncio.sleep(2)
    print("End chop_vegetable()!")

    return "Vegetable chopped!"


async def make_dinner():
    print(f">>> Make Dinner - SYNC <<<")
    t1 = time()
    if CFG.batch:
        # Gather coroutine objects, not normal function calls
        batch = asyncio.gather(cook_rice(), chop_vegetable())
        rice_res, vegetable_res = await batch 
    else:
        rice_task = asyncio.create_task(cook_rice())
        vegetable_task = asyncio.create_task(chop_vegetable())

        rice_res = await rice_task
        vegetable_res = await vegetable_task
    t2 = time()

    print(f"Result of cook_rice: {rice_res}")
    print(f"Result of chop_vegetable: {vegetable_res}")
    print(f"-> Elapsed {t2 - t1:.4f} sec")


if __name__ == "__main__":
    asyncio.run(make_dinner())
