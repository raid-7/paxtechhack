import json
import sys
import my_numpy as np
import random
import itertools
import subprocess


class Passenger:
    name: str
    interests: list #of str
    seat: str
    age: int
    together_with: list #of str

    def __init__(self, name, interests, seat=None, age=None, together_with=[]):
        self.name = name
        self.interests = interests
        self.seat = seat
        self.age = age
        self.together_with = together_with


def bin_search(arr, n):
    l, r = 0, len(arr)
    while r - l > 1:
        m = (l + r) // 2
        if arr[m] <= n:
            l = m
        else:
            r = m
    return l
        
def w(p1: Passenger, p2: Passenger):
    def w_age(p1, p2):
        age_zones = [5, 12, 18, 30, 45, 65]
        coeffs = [.5, 0., -.5, -.5, -1., 0.]
        if p1.age is None or p2.age is None:
            return 0
        z1, z2 = bin_search(age_zones, p1.age), bin_search(age_zones, p2.age)
        return coeffs[int(abs(z1 - z2))]

    return np.intersect1d_len(p1.interests, p2.interests) + w_age(p1, p2)


# list of passengers
plane = []
reserved = []


def follow_the_road(passengers, n):
    print(len(passengers))
    random.shuffle(passengers)
    passengers = passengers[:n]
    for p in passengers:
        val = json.dumps({"interests" : p.interests})
        print(val)
        subprocess.run(['curl', '-X', 'POST', '-H', 'Content-type: application/json', '--data', val, 'http://arm-cloud:7777/request_seat'])

# reading data
#
# python3 --generate <file_with_names.json> <file_with_interests.json>
# python3 --from_file <file_with_passengers.json>
# python3 --stdin
#
if sys.argv[1] == "--free-list":
    all_places = list(map(
        lambda p: str(p[0]) + str(p[1]),
        itertools.product(range(1, 26), ['A', 'B', 'C', 'D', 'E', 'F'])
    ))
    with sys.stdin if sys.argv[2] == '--stdin' else open(sys.argv[2]) as file:
        reserved_places = json.load(file)
    for res in reserved_places:
        all_places.remove(res)
    print(json.dumps(all_places))
    exit(0)
    
elif sys.argv[1] == '--generate':
    with open(sys.argv[2]) as names_file:
        names = json.load(names_file)
        assert(0 == len(names) % 6)
        
    with open(sys.argv[3]) as interests_file:
        interests = json.load(interests_file)

    for name in names:
        name_interests = []
        for _ in range(0, random.randint(2, 4)):
            name_interests.append(random.choice(interests))
        plane.append(Passenger(name, name_interests, seat=None, age=random.randint(1, 70)))

    follow_the_road(plane, int(sys.argv[4]) if len(sys.argv) > 4 else 10)
    exit(0)
else:
    with sys.stdin if sys.argv[1] == '--stdin' else open(sys.argv[2]) as passengers_file:
        passengers = json.load(passengers_file)
        assert(0 == len(passengers) % 6)

        for name, data in passengers.items():
            plane.append(Passenger(name, **data))
            if 'seat' in data:
                reserved.append(data['seat'])
            if 'together_with' in data and len(data['together_with']) > 0:
                pass


# seats number
seats_number = len(plane)
triples_number = seats_number // 3

pairs, alones, forever_alones = [], list(range(seats_number)), []
places = {}

# determining passengers with fixed seats
fixed_passengers = sorted(list(filter(lambda i: plane[i].seat is not None, alones)),
                          key=lambda i: int(plane[i].seat[:-1]) * 6 + (ord(plane[i].seat[-1]) - ord('A')))

def are_neighbours(p1, p2):
    return p1.seat[:-1] == p2.seat[:-1] and \
           (min(ord(p1.seat[-1]), ord(p2.seat[-1])) <= ord('C') or \
            max(ord(p1.seat[-1]), ord(p2.seat[-1])) >  ord('C'))

i = 0
while i < len(fixed_passengers):
    if i + 2 < len(fixed_passengers) and \
        are_neighbours(plane[fixed_passengers[i]], plane[fixed_passengers[i + 1]]) and \
        are_neighbours(plane[fixed_passengers[i]], plane[fixed_passengers[i + 2]]):
        alones.remove(fixed_passengers[i])
        alones.remove(fixed_passengers[i + 1])
        alones.remove(fixed_passengers[i + 2])
        places[plane[fixed_passengers[i]].name] = plane[fixed_passengers[i]].seat
        places[plane[fixed_passengers[i + 1]].name] = plane[fixed_passengers[i + 1]].seat
        places[plane[fixed_passengers[i + 2]].name] = plane[fixed_passengers[i + 2]].seat
        i += 3
    elif i + 1 < len(fixed_passengers) and \
        are_neighbours(plane[fixed_passengers[i]], plane[fixed_passengers[i + 1]]):
        alones.remove(fixed_passengers[i])
        alones.remove(fixed_passengers[i + 1])
        places[plane[fixed_passengers[i]].name] = plane[fixed_passengers[i]].seat
        places[plane[fixed_passengers[i + 1]].name] = plane[fixed_passengers[i + 1]].seat
        pairs.append((fixed_passengers[i], fixed_passengers[i + 1]))
        i += 2
    else:
        forever_alones.append(fixed_passengers[i])
        alones.remove(fixed_passengers[i])
        places[plane[fixed_passengers[i]].name] = plane[fixed_passengers[i]].seat
        i += 1

product = filter(lambda x: x[0] != x[1], itertools.product(alones, alones))
product = sorted(product, key=lambda x: -w(plane[x[0]], plane[x[1]]))


for pair in product:
    if pair[0] in alones and pair[1] in alones:
        pairs.append(pair)
        alones.remove(pair[0]), alones.remove(pair[1])
    
    if len(pairs) == triples_number:
        break

alones += forever_alones
# hungarian algo

# initializing needed lists
u = [0 for _ in range(triples_number + 1)]
v = [0 for _ in range(triples_number + 1)]
p = [0 for _ in range(triples_number + 1)]
way = [0 for _ in range(triples_number + 1)]

INF = 1e5
n = len(alones)

assert(len(alones) == len(pairs))

# graph matrix
a = [[-w(plane[pairs[i][0]], plane[alones[j]]) 
      -w(plane[pairs[i][1]], plane[alones[j]]) for j in range(len(alones))] 
                                               for i in range(len(alones))]

for i in range(1, n + 1):
    p[0] = i
    j0 = 0
    minv = [INF for _ in range(n + 1)]
    used = [False for _ in range(n + 1)]
    while True:
        used[j0] = True
        i0 = p[j0]
        delta = INF
        j1 = 0
        
        for j in range(1, n + 1):
            if not used[j]:
                cur = a[i0 - 1][j - 1] - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j] = cur
                    way[j] = j0
                if minv[j] < delta:
                    delta = minv[j]
                    j1 = j
        for j in range(n + 1):
            if used[j]:
                u[p[j]] += delta
                v[j] -= delta
            else:
                minv[j] -= delta
        j0 = j1

        if p[j0] == 0:
            break
    while True:
        j1 = way[j0]
        p[j0] = p[j1]
        j0 = j1

        if j0 == 0:
            break


# seats generator
def next_place():
    current = '0F'

    def _get():
        nonlocal current
        if current[-1] == 'F':
            current = str(int(current[:-1]) + 1) + 'A'
        else:
            current = current[:-1] + chr(ord(current[-1]) + 1)
        
        return current if current not in reserved else _get()

    return _get

gen = next_place()


# neighbours' seats
def get_neighbours_for_one(seat):
    row = seat[:-1]
    c1 = ['A', 'B', 'C']
    c2 = ['D', 'E', 'F']
    c = c1 if seat[-1] in c1 else c2
    ans = [row + cc for cc in c]
    ans.remove(seat)
    return ans

def get_neighbour_for_two(seat1, seat2):
    ans = get_neighbours_for_one(seat1)
    ans.remove(seat2)
    return ans[0]


# answer
for z in range(n):
    i, j, k = plane[pairs[p[z + 1] - 1][0]],\
              plane[pairs[p[z + 1] - 1][1]],\
              plane[alones[z]]
    
    tpl = (i.name in places, j.name in places, k.name in places)
    assert(not all(tpl))

    if any(tpl):
        if list(itertools.accumulate(tpl, lambda acc, x: acc ^ x))[-1]:
            y = [i, j, k][np.argmax(np.array(tpl))]
            seats = get_neighbours_for_one(y.seat)

            y = 0
            for pas in [i, j, k]:
                if pas.seat is None:
                    places[pas.name] = seats[y]
                    reserved.append(seats[y])
                    y += 1
        else:
            y = np.argsort(np.array(tpl))
            seat = get_neighbour_for_two([i, j, k][y[1]].seat, [i, j, k][y[2]].seat)
            places[[i, j, k][y[0]].name] = seat
            reserved.append(seat)
    else:
        places[i.name] = gen()
        places[j.name] = gen()
        places[k.name] = gen()

print(json.dumps(places))
