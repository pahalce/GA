# create cities with position and calculate distance between each city before hand
# contains properties(variables) that decides the situation

import math
import random

# TSP properties
CITY_NUM = 20  # needs to be an even number
R = 200
r = 100
city_pos = []  # stores x,y position of cities
city_pairs = []  # list of pairs of cities
dist_list = []  # stores distance b/w all the cities

# GA properties
POPULATION = 500
GENERATION_COMBINE = 20000  # when to combine groups
GENERATION_MAX = 30000
GENERATION_STEP = 100  # stats will be shown for every n steps
MUTATION = 0.03
GROUP_N = 5

# draw
draw_size = 1000
center = draw_size/2


def c_cities(num):
    step = math.pi*2/((num/2))
    for i in range(int(num/2)):
        deg = step*i
        city_pos.append((round(center+r*math.cos(deg), 1),
                         round(center+r*math.sin(deg), 1)))
        city_pos.append((round(center+R*math.cos(deg), 1),
                         round(center+R*math.sin(deg), 1)))


def rand_cities(num):
    for _ in range(num):
        city_pos.append((random.randint(0, draw_size),
                         random.randint(0, draw_size)))


def c_dist_list():
    for i in range(int(CITY_NUM)):
        for j in range(i+1, CITY_NUM):
            if i == j:
                continue
            city_pairs.append(set([i, j]))
            dist_list.append(calc_dist(i, j))


def calc_dist(i, j):
    dist_x = city_pos[i][0] - city_pos[j][0]
    dist_y = city_pos[i][1] - city_pos[j][1]
    return round(math.sqrt(dist_x**2 + dist_y**2), 1)


rand_cities(CITY_NUM)
c_dist_list()
