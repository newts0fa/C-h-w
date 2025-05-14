def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left = arr[:mid]
        right = arr[mid:]
        
        merge_sort(left)
        merge_sort(right)
        
        i = j = k = 0
        
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
            
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
            
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

import unittest

class TestMergeSort(unittest.TestCase):
    def test_sort(self):
        test_cases = [
            ([38, 27, 43, 3, 9, 82, 10], [3, 9, 10, 27, 38, 43, 82]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            ([], []),
            ([1], [1])
        ]
        
        for arr, expected in test_cases:
            with self.subTest(arr=arr):
                arr_copy = arr.copy()
                merge_sort(arr_copy)
                self.assertEqual(arr_copy, expected)

if __name__ == '__main__':
    unittest.main()

def counting_sort(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    
    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1
        
    for i in range(1, 10):
        count[i] += count[i-1]
        
    i = n - 1
    while i >= 0:
        index = arr[i] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1
        i -= 1
        
    for i in range(n):
        arr[i] = output[i]

def radix_sort(arr):
    if len(arr) == 0:
        return
        
    max_num = max(arr)
    exp = 1
    while max_num // exp > 0:
        counting_sort(arr, exp)
        exp *= 10

import unittest

class TestRadixSort(unittest.TestCase):
    def test_sort(self):
        test_cases = [
            ([170, 45, 75, 90, 802, 24, 2, 66], [2, 24, 45, 66, 75, 90, 170, 802]),
            ([10, 300, 4, 2000, 50], [4, 10, 50, 300, 2000]),
            ([], []),
            ([5], [5])
        ]
        
        for arr, expected in test_cases:
            with self.subTest(arr=arr):
                arr_copy = arr.copy()
                radix_sort(arr_copy)
                self.assertEqual(arr_copy, expected)

if __name__ == '__main__':
    unittest.main()
    
def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return i + 1

def quick_sort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quick_sort(arr, low, pi-1)
        quick_sort(arr, pi+1, high)

import unittest

class TestQuickSort(unittest.TestCase):
    def test_sort(self):
        test_cases = [
            ([10, 7, 8, 9, 1, 5], [1, 5, 7, 8, 9, 10]),
            ([5, 3, 8, 6, 2, 7, 1, 4], [1, 2, 3, 4, 5, 6, 7, 8]),
            ([], []),
            ([3], [3])
        ]
        
        for arr, expected in test_cases:
            with self.subTest(arr=arr):
                arr_copy = arr.copy()
                quick_sort(arr_copy, 0, len(arr_copy)-1)
                self.assertEqual(arr_copy, expected)

if __name__ == '__main__':
    unittest.main()
