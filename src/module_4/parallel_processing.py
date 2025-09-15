import json
from random import randint
import math
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import time


def generate_data(n):
    return [randint(1, 1000) for i in range(n)]


def is_prime(number):
    if number < 2:
        return False
    else:
        for i in range(2, int(math.sqrt(number)) + 1):
            if number % i == 0:
                return False
    return True


def process_number(number):
    return is_prime(number)


def process_with_threads(data):
    result = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_number, num) for num in data]
        for f in as_completed(futures):
            result.append(f.result())
    return result


def process_with_multiprocessing_pool(data):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(process_number, data)
    return results


def worker(input_queue, output_queue):
    while True:
        number = input_queue.get()
        if number is None:
            break
        output_queue.put(process_number(number))


def process_with_queue(data):
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()

    num_procs = multiprocessing.cpu_count()
    processes = [
        multiprocessing.Process(target=worker, args=(input_queue, output_queue))
        for _ in range(num_procs)
    ]

    for p in processes:
        p.start()

    for num in data:
        input_queue.put(num)

    for _ in range(num_procs):
        input_queue.put(None)

    results = [output_queue.get() for _ in range(len(data))]

    for p in processes:
        p.join()

    return results


def process_sequential(data):
    return [process_number(num) for num in data]


def measure_time(func, data):
    start = time.time()
    result = func(data)
    end = time.time()
    return result, end - start


def main():
    N = 1000000
    data = generate_data(N)

    results = {}
    seq_result, seq_time = measure_time(process_sequential, data)
    results["Sequential"] = {"time": seq_time, "data": seq_result}

    th_result, th_time = measure_time(process_with_threads, data)
    results["ThreadPool"] = {"time": th_time, "data": th_result}

    mp_result, mp_time = measure_time(process_with_multiprocessing_pool, data)
    results["Multiprocessing"] = {"time": mp_time, "data": mp_result}

    qu_result, qu_time = measure_time(process_with_queue, data)
    results["Multiprocessing_queue"] = {"time": qu_time, "data": qu_result}

    # with open('results.json', 'w', encoding='utf-8') as f:
    #     json.dump(results, f, ensure_ascii=False)

    print("all results")
    for method, info in results.items():
        print(f"{method}: {info['time']:.2f} s")

    methods = list(results.keys())
    times = [info["time"] for info in results.values()]

    plt.figure(figsize=(8, 5))
    plt.bar(methods, times)
    plt.ylabel("Время (секунды)")
    plt.title("Сравнение производительности разных методов")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig("results.png")
    plt.show()


if __name__ == "__main__":
    main()
