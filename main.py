from multiprocessing import Pool
from time import perf_counter

def factorize(*numbers: int) -> list[list[int]]:
    dividers_list = []
    for num in numbers:
        dividers = [i for i in range(1, num//2 + 1) if num % i == 0]
        dividers.append(num)
        dividers_list.append(dividers)
    return dividers_list

def factorize_single(num: int) -> list[int]:
    dividers = [i for i in range(1, num // 2 + 1) if num % i == 0]
    dividers.append(num)
    return dividers

def pool_factorize(*numbers: int) -> list[list[int]]:
    with Pool() as pool:
        results = pool.map(factorize_single, numbers)
    return results


if __name__ == '__main__':
    time_before_single = perf_counter()
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    time_after_single = perf_counter()
    print(f"Single process:  {time_after_single - time_before_single:.6f} sec")
    print(a)
    print(b)
    print(c)
    print(d)

    time_before_pool = perf_counter()
    a, b, c, d = pool_factorize(128, 255, 99999, 10651060)
    time_after_pool = perf_counter()
    print(f"Multiprocessing: {time_after_pool - time_before_pool:.6f} sec")
    print(a)
    print(b)
    print(c)
    print(d)


    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]
