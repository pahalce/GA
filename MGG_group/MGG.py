import random
import copy

import Tour as T
from init import CITY_NUM, POPULATION, GENERATION_COMBINE, GENERATION_MAX, GENERATION_STEP, MUTATION, GROUP_N, rand_cities, c_dist_list
from Draw import draw_tour


def c_tour(society, num, create_gene=True):
    for _ in range(num):
        society.append(T.Tour(create_gene))
    return society


def show_society_gene(society):
    for tour in society:
        tour.show_gene()


def show_society_fitness(society):
    for tour in society:
        tour.show_fitness()


def find_subtour(par_a, par_b):
    # inverse of parent-lists (in_par_a[2] :gets the index in par_a where city=2)
    in_par_a = []
    in_par_b = []
    for i in range(CITY_NUM):
        in_par_a.append(par_a.index(i))
        in_par_b.append(par_b.index(i))
    # store list of subtours: list of dictionaries {length of subtour, start index in a, start index in b}
    subtour_list = []
    l_a = l_b = 0
    r_a = r_b = len(par_a)-1
    flag = 0
    l = 1
    for i in range(1, CITY_NUM):
        l_a = i
        l_b = in_par_b[par_a[l_a]]
        if flag == 0:
            left_a = l_a
            left_b = l_b
            right_b = l_b
            flag = 1
        else:
            if abs(right_b - l_b) == 1:
                right_a = l_a
                right_b = l_b
                l += 1
            else:
                if l > 1:
                    l_a = left_a
                    r_a = right_a
                    l_b = left_b
                    r_b = right_b
                    if par_a[min(l_a, l_b):max(l_a, r_a)+1] != par_b[min(l_b, r_b):max(l_b, r_b)+1]:
                        subtour_list.append(
                            {"length": l, "start_a": min(l_a, r_a), "start_b": min(l_b, r_b)})
                flag = 0
                l = 1
    return subtour_list


def find_all_children_a(par_a, par_b, subtour_list, child_genes, i):

    if i == len(subtour_list):
        return
    temp_array = par_a.copy()
    s_l_a = subtour_list[i]["start_a"]
    s_r_a = subtour_list[i]["start_a"] + subtour_list[i]["length"]
    s_l_b = subtour_list[i]["start_b"]
    s_r_b = subtour_list[i]["start_b"] + subtour_list[i]["length"]
    temp_array[s_l_a: s_r_a] = par_b[s_l_b: s_r_b]
    child_genes.append(temp_array)
    find_all_children_a(par_a, par_b, subtour_list, child_genes, i+1)
    find_all_children_a(temp_array, par_b, subtour_list, child_genes, i+1)
    return child_genes


def find_all_children_b(par_a, par_b, subtour_list, child_genes, i):

    if i == len(subtour_list):
        return
    temp_array = par_b.copy()
    s_l_a = subtour_list[i]["start_a"]
    s_r_a = subtour_list[i]["start_a"] + subtour_list[i]["length"]
    s_l_b = subtour_list[i]["start_b"]
    s_r_b = subtour_list[i]["start_b"] + subtour_list[i]["length"]
    temp_array[s_l_b: s_r_b] = par_a[s_l_a: s_r_a]
    child_genes.append(temp_array)
    find_all_children_b(par_a, par_b, subtour_list, child_genes, i+1)
    find_all_children_b(par_a, temp_array, subtour_list, child_genes, i+1)
    return child_genes


def cross(par_a, par_b, subtour_list):
    child_genes = []
    find_all_children_a(par_a, par_b, subtour_list, child_genes, 0)
    find_all_children_b(par_a, par_b, subtour_list, child_genes, 0)
    return child_genes


def c_children(par_a, par_b):
    subtour_list = find_subtour(par_a, par_b)
    children = cross(par_a, par_b, subtour_list)
    return children


def select_par():
    i_par_a = random.randint(0, POPULATION-1)
    i_par_b = random.randint(0, POPULATION-1)
    while(i_par_b == i_par_a):
        i_par_b = random.randint(0, POPULATION-1)
    if i_par_a > i_par_b:
        i_par_a, i_par_b = i_par_b, i_par_a
    return i_par_a, i_par_b


def society_grow(society):
    child = None
    while child == None:
        i_par_a, i_par_b = select_par()
        par_a = society[i_par_a].gene
        par_b = society[i_par_b].gene
        child = c_children(par_a, par_b)

    society_gene_list = []
    for tour in society:
        society_gene_list.append(tour.gene)

    child_tours = []
    for gene in child:
        if gene not in society_gene_list:
            child_tours.append(T.Tour(False))
            child_tours[-1].set_gene(gene)
    family = [society[i_par_a], society[i_par_b]]
    family.extend(child_tours)
    # replaces 1 with the best gene in the family
    family.sort()
    society[i_par_a].set_gene(family[0].gene.copy())
    # roullette selection
    selected = roullette_selection(family)
    society[i_par_b].set_gene(family[selected].gene.copy())
    # mutation
    mutate(society[i_par_a])
    mutate(society[i_par_b])


def roullette_selection(tours):
    sum_fit = 0
    num = len(tours)
    add = 0
    r = random.random()
    for i in range(num):
        sum_fit += tours[i].fitness
    for i in range(num):
        add += round(tours[i].fitness/sum_fit, 5)
        if r <= add:
            return i
    return i


def mutate(tour):
    mutate = random.random()
    if mutate > MUTATION:
        return
    ii = random.randint(0, CITY_NUM-1)
    jj = random.randint(0, CITY_NUM-1)

    while (ii == jj):
        jj = random.randint(0, CITY_NUM-1)
    tour.gene[ii], tour.gene[jj] = tour.gene[jj], tour.gene[ii]


def mutate_(tour):
    mutate = random.random()
    if mutate > MUTATION:
        return
    ii = random.randint(0, CITY_NUM-1)
    jj = ii+1
    if jj >= CITY_NUM:
        jj = ii-1
    tour.gene[ii], tour.gene[jj] = tour.gene[jj], tour.gene[ii]


def get_best_fitness(society):
    best = society[0].fitness
    for tour in society:
        if best > tour.fitness:
            best = tour.fitness
    return str(round(best, 1))


def main():
    rand_cities(CITY_NUM)
    c_dist_list()
    generation = 1
    society = []
    for g_i in range(GROUP_N):
        society.append([])
        c_tour(society[g_i], POPULATION)
        draw_tour(society[g_i][0].gene, "files/before"+str(g_i))

    while generation <= int(GENERATION_COMBINE):
        for g_i in range(GROUP_N):
            society_grow(society[g_i])

        if generation % GENERATION_STEP == 0:
            print("generation:", generation)
            for g_i in range(GROUP_N):
                print("best tour"+str(g_i)+":", get_best_fitness(society[g_i]))
        generation += 1

    for g_i in range(GROUP_N):
        draw_tour(society[g_i][0].gene, "files/mid_society_" +
                  str(g_i), "fitness: "+get_best_fitness(society[g_i]))

    society_c = []
    while (generation <= GENERATION_MAX):
        new_society = society[0][:int(POPULATION/GROUP_N)].copy()
        for g_i in range(1, GROUP_N):
            society_c.append(society[g_i][:int(POPULATION/GROUP_N)].copy())
            new_society += society_c[g_i-1].copy()
        POPULATION = len(new_society)
        society_grow(new_society)
        if generation % GENERATION_STEP == 0 or generation == GENERATION_MAX:
            print("generation:", generation)
            print("best tour combine:", get_best_fitness(new_society))
        generation += 1
    print("--finished--")
    draw_tour(new_society[0].gene, "files/final_result_best",
              "fitness: "+get_best_fitness(new_society))
    for i in range(1, POPULATION, int(POPULATION/GROUP_N)):
        draw_tour(new_society[i].gene, "files/final_result"+str(i),
                  "fitness: "+str(round(new_society[i].fitness, 1)))
