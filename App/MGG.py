import math
import random
import copy

import config as c


class TSP:

    def __init__(self):
        self.city_pos = []  # stores x,y position of cities
        self.city_pairs = []  # list of pairs of cities
        self.dist_list = []  # stores distance b/w all the cities
        self.c_circular(c.CITY_NUM)

    def c_circular(self, num):
        self.city_pos.clear()
        center = c.draw_size/2
        step = math.pi*2/((num/2))
        for i in range(int(num/2)):
            deg = step*i
            self.city_pos.append((round(center+c.r*math.cos(deg), 0),
                                  round(center+c.r*math.sin(deg), 0)))
            self.city_pos.append((round(center+c.R*math.cos(deg), 0),
                                  round(center+c.R*math.sin(deg), 0)))

    def c_rand(self, num):
        self.city_pos.clear()
        for _ in range(num):
            self.city_pos.append((random.randint(c.city_r*2, c.draw_size-c.city_r*2),
                                  random.randint(c.city_r*2, c.draw_size-c.city_r*2)))

    def c_dist_list(self):
        for i in range(int(len(self.city_pos))):
            for j in range(i+1, len(self.city_pos)):
                if i == j:
                    continue
                self.city_pairs.append(set([i, j]))
                self.dist_list.append(self.calc_dist(i, j))

    def calc_dist(self, i, j):
        dist_x = self.city_pos[i][0] - self.city_pos[j][0]
        dist_y = self.city_pos[i][1] - self.city_pos[j][1]
        return math.sqrt(dist_x**2 + dist_y**2)


class GA:

    def __init__(self, tsp):
        self.tsp = tsp
        self.s_list = []  # list of societies before they are combined
        self.s_combined = None  # for society after they are combined
        self.generation = 0

    def init_s_list(self):
        for _ in range(c.GROUP_N):
            self.s_list.append(Society(self.tsp))

    def combine_society(self):  # combine all the society into one
        society_c = []
        self.s_combined = Society(self.tsp, init_tour=False)
        for s in self.s_list:
            s.society.sort()
        self.s_combined.society = self.s_list[0].society[:int(
            c.POPULATION/c.GROUP_N)].copy()
        for g_i in range(1, c.GROUP_N):
            society_c.append(
                self.s_list[g_i].society[:int(c.POPULATION/c.GROUP_N)+1].copy())
            self.s_combined.society += society_c[g_i-1].copy()
        if len(self.s_combined.society) != c.POPULATION:
            self.s_combined.society = self.s_combined.society[:c.POPULATION+1]

    def show_stats(self, societies):
        print("generation:", self.generation)
        if type(societies) == Society:
            print("best tour"+":",
                  societies.get_best_fitness())
            return
        for g_i, society in enumerate(societies):
            print("best tour"+str(g_i)+":",
                  society.get_best_fitness())


class Society:

    def __init__(self, tsp, init_tour=True):
        self.tsp = tsp
        self.society = []
        if init_tour == True:
            for _ in range(c.POPULATION):
                self.c_tour(len(self.tsp.city_pos))

    def c_tour(self, num, create_gene=True):
        for _ in range(num):
            self.society.append(Tour(self.tsp, create_gene))
        return self.society

    def show_society_gene(self):
        for tour in self.society:
            tour.show_gene()

    def show_society_fitness(self):
        for tour in self.society:
            tour.show_fitness()

    def find_subtour(self, par_a, par_b):
        # inverse of parent-lists (in_par_a[2] :gets the index in par_a where city=2)
        in_par_a = []
        in_par_b = []
        for i in range(len(self.tsp.city_pos)):
            in_par_a.append(par_a.index(i))
            in_par_b.append(par_b.index(i))

        # store list of subtours: list of dictionaries {length of subtour, start index in a, start index in b}
        subtour_list = []
        l_a = l_b = 0
        r_a = r_b = len(par_a)-1
        flag = 0
        l = 1
        for i in range(1, len(self.tsp.city_pos)):
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

    def find_all_children_a(self, par_a, par_b, subtour_list, child_genes, i):

        if i == len(subtour_list):
            return
        temp_array = par_a.copy()
        s_l_a = subtour_list[i]["start_a"]
        s_r_a = subtour_list[i]["start_a"] + subtour_list[i]["length"]
        s_l_b = subtour_list[i]["start_b"]
        s_r_b = subtour_list[i]["start_b"] + subtour_list[i]["length"]
        temp_array[s_l_a: s_r_a] = par_b[s_l_b: s_r_b]
        child_genes.append(temp_array)
        self.find_all_children_a(par_a, par_b, subtour_list, child_genes, i+1)
        self.find_all_children_a(
            temp_array, par_b, subtour_list, child_genes, i+1)
        return child_genes

    def find_all_children_b(self, par_a, par_b, subtour_list, child_genes, i):

        if i == len(subtour_list):
            return
        temp_array = par_b.copy()
        s_l_a = subtour_list[i]["start_a"]
        s_r_a = subtour_list[i]["start_a"] + subtour_list[i]["length"]
        s_l_b = subtour_list[i]["start_b"]
        s_r_b = subtour_list[i]["start_b"] + subtour_list[i]["length"]
        temp_array[s_l_b: s_r_b] = par_a[s_l_a: s_r_a]
        child_genes.append(temp_array)
        self.find_all_children_b(par_a, par_b, subtour_list, child_genes, i+1)
        self.find_all_children_b(
            par_a, temp_array, subtour_list, child_genes, i+1)
        return child_genes

    def cross(self, par_a, par_b, subtour_list):
        child_genes = []
        self.find_all_children_a(par_a, par_b, subtour_list, child_genes, 0)
        self.find_all_children_b(par_a, par_b, subtour_list, child_genes, 0)
        return child_genes

    def c_children(self, par_a, par_b):
        subtour_list = self.find_subtour(par_a, par_b)
        children = self.cross(par_a, par_b, subtour_list)
        return children

    def select_par(self, ):
        i_par_a = random.randint(0, c.POPULATION-1)
        i_par_b = random.randint(0, c.POPULATION-1)
        while(i_par_b == i_par_a):
            i_par_b = random.randint(0, c.POPULATION-1)
        if i_par_a > i_par_b:
            i_par_a, i_par_b = i_par_b, i_par_a
        return i_par_a, i_par_b

    def society_grow(self):
        child = None
        while child == None:
            i_par_a, i_par_b = self.select_par()
            par_a = self.society[i_par_a].gene
            par_b = self.society[i_par_b].gene
            child = self.c_children(par_a, par_b)
        society_gene_list = []
        for tour in self.society:
            society_gene_list.append(tour.gene)

        child_tours = []
        for gene in child:
            if gene not in society_gene_list:
                child_tours.append(Tour(self.tsp, False))
                child_tours[-1].set_gene(gene)
        family = [self.society[i_par_a], self.society[i_par_b]]
        family.extend(child_tours)

        # replaces 1 with the best gene in the family
        family.sort()
        self.society[i_par_a].set_gene(family[0].gene.copy())

        # roullette selection
        selected = self.roullette_selection(family)
        self.society[i_par_b].set_gene(family[selected].gene.copy())

        # mutation
        self.mutate(self.society[i_par_a])
        self.mutate(self.society[i_par_b])

    def roullette_selection(self, tours):
        sum_fit = 0
        num = len(tours)
        add = 0
        r = random.random()
        for i in range(num):
            sum_fit += tours[i].fitness
        for i in range(num):
            add += tours[i].fitness/sum_fit
            if r <= add:
                return i
        return i

    def mutate(self, tour):
        r = random.random()
        if r > c.MUTATION:
            return
        ii = random.randint(0, len(self.tsp.city_pos)-1)
        jj = random.randint(0, len(self.tsp.city_pos)-1)

        while (ii == jj):
            jj = random.randint(0, len(self.tsp.city_pos)-1)
        tour.gene[ii], tour.gene[jj] = tour.gene[jj], tour.gene[ii]

    def get_best_fitness(self):
        best = self.society[0].fitness
        for tour in self.society:
            if best > tour.fitness:
                best = tour.fitness
        return str(best)

    def get_best_tour(self):
        best = self.society[0].fitness
        best_i = 0
        for i, tour in enumerate(self.society):
            if best > tour.fitness:
                best = tour.fitness
                best_i = i
        return self.society[best_i]


class Tour:
    count = 0

    def __init__(self, tsp, create_gene=True):
        Tour.count += 1
        self.index = Tour.count
        self.tsp = tsp
        self.fitness = None
        self.gene = []
        if create_gene == True:
            self.c_rand_gene()

    def __lt__(self, other):
        return self.fitness < other.fitness

    def c_rand_gene(self):
        for i in range(len(self.tsp.city_pos)):
            self.gene.append(i)
            random.shuffle(self.gene)
        self.calc_fitness()

    def set_gene(self, gene):
        self.gene = gene
        self.calc_fitness()

    def show_gene(self):
        print(str(self.index) + ":" + str(self.gene))

    def show_fitness(self):
        print(str(self.index) + ":" + str(self.fitness))

    def calc_fitness(self):
        self.fitness = 0
        for i in range(len(self.tsp.city_pos)-1):
            index = self.tsp.city_pairs.index(
                set([self.gene[i], self.gene[i+1]]))
            self.fitness += self.tsp.dist_list[index]
        self.fitness += self.tsp.dist_list[self.tsp.city_pairs.index(
            set([self.gene[0], self.gene[-1]]))]
        return self.fitness


def main():
    tsp = TSP()
    tsp = TSP()
    tsp.c_rand(c.CITY_NUM)
    tsp.c_dist_list()

    ga = GA(tsp)
    ga.init_s_list()

    while ga.generation <= c.GENERATION_COMBINE:
        ga.generation += 1
        for g_i in range(c.GROUP_N):
            ga.s_list[g_i].society_grow()

        if ga.generation % c.GENERATION_STEP == 0:
            ga.show_stats(ga.s_list)

    print("--COMBINED SOCIETIES--")
    while (ga.generation <= c.GENERATION_MAX):
        ga.generation += 1
        ga.combine_society()
        ga.s_combined.society_grow()

        if ga.generation % c.GENERATION_STEP == 0:
            ga.show_stats(ga.s_combined)

    print("--finished--")


if __name__ == '__main__':
    main()
