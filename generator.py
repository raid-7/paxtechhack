import json
import sys
import numpy as np
import random
import itertools


class Passenger:
    name: str
    interests: np.array

    def __init__(self, name, interests):
        self.name = name
        self.interests = interests

def w(p1: Passenger, p2: Passenger):
    return len(np.intersect1d(p1.interests, p2.interests))


# list of passengers
plane = []


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


seats_number = len(plane)
triples_number = seats_number // 3

pairs, alones = [], list(range(seats_number))

product = filter(lambda x: x[0] != x[1], itertools.product(alones, alones))
product = sorted(product, key=lambda x: -w(plane[x[0]], plane[x[1]]))

for pair in product:
    if pair[0] in alones and pair[1] in alones:
        pairs.append(pair)
        alones.remove(pair[0]), alones.remove(pair[1])
    
    if len(pairs) == triples_number:
        break


# hungarian algo
u = [0 for _ in range(triples_number + 1)]
v = [0 for _ in range(triples_number + 1)]
p = [0 for _ in range(triples_number + 1)]
way = [0 for _ in range(triples_number + 1)]

a = [[-w(plane[pairs[i][0]], plane[alones[j]]) 
      -w(plane[pairs[i][1]], plane[alones[j]]) for j in range(triples_number)] 
                                               for i in range(triples_number)]

INF = 1e5

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

def next_place():
    current = '0F'

    def _get():
        nonlocal current
        if current[-1] == 'F':
            current = str(int(current[:-1]) + 1) + 'A'
        else:
            current = current[:-1] + chr(ord(current[-1]) + 1)
        return current

    return _get

gen = next_place()

places = {}
for j in range(triples_number):
    places[plane[pairs[p[j + 1] - 1][0]].name] = gen()
    places[plane[pairs[p[j + 1] - 1][1]].name] = gen()
    places[plane[alones[j]].name] = gen()

print(json.dumps(places))
