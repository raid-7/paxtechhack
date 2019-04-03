def argsort(arr):
    return sorted(list(range(len(arr))),
                  key=lambda x: arr[x])

def argmax(arr):
    ans = 0
    for i, a in enumerate(arr):
        if a > arr[ans]:
            ans = i
    return ans

def argmin(arr):
    ans = 0
    for i, a in enumerate(arr):
        if a < arr[ans]:
            ans = i
    return ans    

def intersect1d_len(arr1, arr2):
    return len(arr1) + len(arr2) - len(set(arr1 + arr2))

array = list
