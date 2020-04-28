import random
from init import city_pairs, dist_list, CITY_NUM


class Tour:
    count = 0

    def __init__(self, create_gene=True):
        self.index = Tour.count+1
        Tour.count += 1
        self.fitness = None
        self.gene = []
        if create_gene == True:
            self.c_rand_gene()

    def __lt__(self, other):
        return self.fitness < other.fitness

    def c_rand_gene(self):
        r = random.randint(0, CITY_NUM-1)
        for _ in range(CITY_NUM):
            while(r in self.gene):
                r = random.randint(0, CITY_NUM-1)
            self.gene.append(r)
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
        for i in range(CITY_NUM-1):
            index = city_pairs.index(set([self.gene[i], self.gene[i+1]]))
            self.fitness += dist_list[index]
        round(self.fitness, 1)
