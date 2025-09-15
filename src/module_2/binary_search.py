from typing import List


def search(sorted_list: List[int], number: int):
    left, right = 0, len(sorted_list) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_value = sorted_list[mid]

        if mid_value == number:
            return True
        elif mid_value < number:
            left = mid + 1
        else:
            right = mid - 1

    return False
