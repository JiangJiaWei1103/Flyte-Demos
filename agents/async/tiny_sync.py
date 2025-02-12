from time import sleep, time


def cook_rice() -> str:
    print("Start cook_rice()...")
    sleep(5)
    print("End cook_rice()!")

    return "Rice cooked!"


def chop_vegetable() -> str:
    print("Start chop_vegetable()...")
    sleep(2)
    print("End chop_vegetable()!")

    return "Vegetable chopped!"


def make_dinner():
    print(f">>> Make Dinner - SYNC <<<")
    t1 = time()
    rice_res = cook_rice()
    vegetable_res = chop_vegetable()
    t2 = time()

    print(f"Result of cook_rice: {rice_res}")
    print(f"Result of chop_vegetable: {vegetable_res}")
    print(f"-> Elapsed {t2 - t1:.4f} sec")


if __name__ == "__main__":
    make_dinner()
