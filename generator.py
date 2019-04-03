import json
import sys
import numpy as np
import random
import itertools


class Passenger:
    name: str
    interests: np.array
    seat: str

    def __init__(self, name, interests, seat=None):
        self.name = name
        self.interests = interests
        self.seat = seat

def w(p1: Passenger, p2: Passenger):
    return len(np.intersect1d(p1.interests, p2.interests))


# list of passengers
plane = []
reserved = []


# reading data
#
# python3 --generate <file_with_names.json> <file_with_interests.json>
# python3 --from_file <file_with_passengers.json>
# python3 --stdin
#
if sys.argv[1] == '--generate':
    with open(sys.argv[2]) as names_file:
        names = json.load(names_file)
        assert(0 == len(names) % 6)
        
    with open(sys.argv[3]) as interests_file:
        interests = json.load(interests_file)

    for name in names:
        name_interests = []
        for _ in range(0, random.randint(2, 4)):
            name_interests.append(random.choice(interests))
        plane.append(Passenger(name, np.array(name_interests)))
else:
    with sys.stdin if sys.argv[1] == '--stdin' else open(sys.argv[2]) as passengers_file:
        passengers = json.load(passengers_file)
        assert(0 == len(passengers) % 6)

        for name, data in passengers.items():
            plane.append(Passenger(name, np.array(data['interests'])))
            if 'seat' in data:
                reserved.append(data['seat'])
                plane[-1].seat = data['seat']


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


# graph matrix
a = [[-w(plane[pairs[i][0]], plane[alones[j]]) 
      -w(plane[pairs[i][1]], plane[alones[j]]) for j in range(triples_number)] 
                                               for i in range(triples_number)]

for i in range(1, triples_number + 1):
    p[0] = i
    j0 = 0
    minv = [INF for _ in range(triples_number + 1)]
    used = [False for _ in range(triples_number + 1)]
    while True:
        used[j0] = True
        i0 = p[j0]
        delta = INF
        j1 = 0
        
        for j in range(1, triples_number + 1):
            if not used[j]:
                cur = a[i0 - 1][j - 1] - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j] = cur
                    way[j] = j0
                if minv[j] < delta:
                    delta = minv[j]
                    j1 = j
        for j in range(triples_number + 1):
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

    def __get():
        nonlocal current
        if current[-1] == 'F':
            current = str(int(current[:-1]) + 1) + 'A'
        else:
            current = current[:-1] + chr(ord(current[-1]) + 1)
        return current

    def _get():
        global reserved
        seat = __get()
        if seat in reserved:
            return _get()
        return seat 

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
for z in range(triples_number):
    i, j, k = plane[pairs[p[z + 1] - 1][0]],\
              plane[pairs[p[z + 1] - 1][1]],\
              plane[alones[z]]
    
    tpl = (i.name in places, j.name in places, k.name in places)

    if all(tpl):
        pass
    elif any(tpl):
        if itertools.accumulate(tpl, lambda acc, x: acc ^ x):
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
            seat = get_neighbour_for_two(tpl[y[1]].seat, tpl[y[2]].seat)
            places[tpl[y[0]].name] = seat
            reserved.append(seat)
    else:
        places[i.name] = gen()
        places[j.name] = gen()
        places[k.name] = gen()

print(json.dumps(places))
