##############################
# algorithm idea
# 
# asume there is a plane with 6n free places (n triples)
# 
# 1) using Edmonds algorithm of blossom contraction choose 2n pairs of passengers
#                                                   having the most number of interests in common
# 2) use the hungarian algorithm to find maximal matching beetween these pairs and alones
#
##############################

import json
import sys
import my_numpy as np
import random
import itertools


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


# reading data
#
# python3 --generate <file_with_names.json> <file_with_interests.json>
# python3 --from_file <file_with_passengers.json>
# python3 --stdin
#
def follow_the_road(passengers, n):
    print(len(passengers))
    random.shuffle(passengers)
    passengers = passengers[:n]
    seat_rows = [random.randint(1, 25) for _ in range(n)]
    for p, seat_row in zip(passengers, seat_rows):
        val = json.dumps({"interests" : p.interests,
                          "seat": str(seat_row) + random.choice('A', 'B', 'C', 'D', 'E', 'F')})
        print(val)
        subprocess.run(['curl', '-X', 'POST', '-H', 
                        'Content-type: application/json', 
                        '--data', val, 'http://arm-cloud:7777/request_seat'])


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
        plane.append(Passenger(name, name_interests, seat=None, age=random.randint(1, 70)))
else:
    with sys.stdin if sys.argv[1] == '--stdin' else open(sys.argv[2]) as passengers_file:
        passengers = json.load(passengers_file)
        assert(0 == len(passengers) % 6)

        for name, data in passengers.items():
            plane.append(Passenger(name, **data))
            if 'seat' in data:
                reserved.append(data['seat'])


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
           (max(ord(p1.seat[-1]), ord(p2.seat[-1])) <= ord('C') or \
            min(ord(p1.seat[-1]), ord(p2.seat[-1])) >  ord('C'))

i = 0
formed_triples = 0
while i < len(fixed_passengers):
    if i + 2 < len(fixed_passengers) and \
        are_neighbours(plane[fixed_passengers[i]], plane[fixed_passengers[i + 1]]) and \
        are_neighbours(plane[fixed_passengers[i]], plane[fixed_passengers[i + 2]]):
        alones.remove(fixed_passengers[i])
        alones.remove(fixed_passengers[i + 1])
        alones.remove(fixed_passengers[i + 2])
        formed_triples += 1
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

pairs_greedy = [pair for pair in pairs]
alones_copy_for_greedy_algo = [alone for alone in alones]

################################################
#   Edmonds algorithm 
#################################################
n = len(alones)
p, used, blossom = [], [], []
match = [-1 for _ in range(seats_number)]
base = [-1 for _ in range(seats_number)]
q = [0 for _ in range(seats_number)]

# least common ancestor
def lca(a, b):
    global match, p, base

    used1 = [False for _ in range(seats_number)]

    while True:
        a = base[a]
        used1[a] = True
        if match[a] == -1:
            break
        a = p[match[a]]

    while True:
        b = base[b]
        if used1[b]:
            return b
        b = p[match[b]]


def mark_path(v, b, children):
    global base, blossom, match, p

    while base[v] != b:
        blossom[base[v]] = blossom[base[match[v]]] = True
        p[v] = children
        children = match[v]
        v = p[match[v]]


def find_path(root):
    global used, p, q, base, blossom, n, match, alones

    used = [False for _ in range(seats_number)]
    p = [-1 for _ in range(seats_number)]

    for i in alones:
        base[i] = i

    used[root] = True
    q[0] = root
    qh, qt = 0, 1

    while qh < qt:
        v = q[qh]
        qh += 1

        alones_copy = [u for u in alones if u != v]
        for to in alones_copy:
            if base[v] == base[to] or match[v] == to:
                continue
            if to == root or (match[to] != -1 and p[match[to]] != -1):
                
                # blossom contraction
                curbase = lca(v, to)
                blossom = [0 for _ in range(seats_number)]
                mark_path(v, curbase, to)
                mark_path(to, curbase, v)

                for i in alones:
                    if blossom[base[i]]:
                        base[i] = curbase
                        if not used[i]:
                            used[i] = True
                            q[qt] = i
                            qt += 1
            elif p[to] == -1:
                p[to] = v
                if match[to] == -1:
                    return to
                to = match[to]
                used[to] = True
                q[qt] = to
                qt += 1

    return -1

# answer restoring
for i in alones:
    if match[i] == -1:
        v = find_path(i)
        while v != -1:
            pv = p[v]
            ppv = match[pv]
            match[v] = pv
            match[pv] = v
            v = ppv

for i in sorted(filter(lambda x: match[x] != -1, alones), 
                key=lambda j: -w(plane[j], plane[match[j]])):
    if len(pairs) == triples_number - formed_triples:
        break
    if i in alones:
        pairs.append((i, match[i]))
        alones.remove(i), alones.remove(match[i])

#########################################
#        Greedy algorithm
##########################################

product = filter(lambda x: x[0] != x[1], itertools.product(alones_copy_for_greedy_algo, 
                                                           alones_copy_for_greedy_algo))
product = sorted(product, key=lambda x: -w(plane[x[0]], plane[x[1]]))


for pair in product:
    if len(pairs_greedy) == triples_number - formed_triples:
        break

    if pair[0] in alones_copy_for_greedy_algo and \
       pair[1] in alones_copy_for_greedy_algo:
        pairs_greedy.append(pair)
        alones_copy_for_greedy_algo.remove(pair[0])
        alones_copy_for_greedy_algo.remove(pair[1])    


# Choose the best option
w_edm = sum([w(plane[pair[0]], plane[pair[1]]) for pair in pairs])
w_gredy = sum([w(plane[pair[0]], plane[pair[1]]) for pair in pairs_greedy])

if w_gredy > w_edm:
    pairs = pairs_greedy
    alones = alones_copy_for_greedy_algo

# add delayed passengers
alones += forever_alones

assert(len(alones) == len(pairs))


#############################################
#       Hungarian algo
############################################

# initializing needed lists
u = [0 for _ in range(triples_number + 1)]
v = [0 for _ in range(triples_number + 1)]
p = [0 for _ in range(triples_number + 1)]
way = [0 for _ in range(triples_number + 1)]

INF = 1e5
n = len(alones)

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

    if all(tpl):
        pass
    elif any(tpl):
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
