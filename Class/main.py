import tkinter as tk
import config as c
import MGG


class App(tk.Frame):
    center = c.draw_size/2
    button_w = 10
    button_h = 2
    font_size = 36

    def __init__(self, master, tsp):
        self.running = True
        super().__init__(master)
        self.tsp = tsp
        self.pack()
        master.geometry("800x600")
        master.title("GA application-main")

        self.window = []
        self.sub = []

        self.canvas = tk.Canvas(master, width=c.draw_size,
                                height=c.draw_size, background="white")
        self.canvas.place(x=0, y=0)

        self.f_buttons = tk.Frame(master)
        self.f_buttons.place(x=c.draw_size, y=0)
        self.b_rand = tk.Button(
            self.f_buttons, text="random", command=self.city_rand, width=App.button_w)
        self.b_rand.grid(column=0, row=0)
        self.b_circular = tk.Button(
            self.f_buttons, text="circualr", command=self.city_circular, width=App.button_w)
        self.b_circular.grid(column=0, row=1)
        self.b_start = tk.Button(
            self.f_buttons, text="start", command=self.start, width=App.button_w)
        self.b_start.grid(column=0, row=2)
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.draw_cities()

    def c_sub(self, tsp, society):
        self.tsp = tsp
        self.window.append(tk.Toplevel())
        self.sub.append(
            Sub(self, self.window[-1], tsp, society))

    def check_subs_closed(self):
        if Sub.running == False:
            self.destroy_subs()
            return True
        else:
            return False

    def city_rand(self):
        self.tsp.c_rand(c.CITY_NUM)
        self.draw_cities()

    def city_circular(self):
        self.tsp.c_circular(c.CITY_NUM)
        self.draw_cities()

    def draw_cities(self):
        self.canvas.delete("city")
        for pos in self.tsp.city_pos:
            self.canvas.create_oval(pos[0]-c.city_r, pos[1]-c.city_r,
                                    pos[0]+c.city_r, pos[1]+c.city_r, tag="city", fill="blue")

    def start(self):
        self.draw_text(App.center, App.font_size, "Processing...", "state")
        self.update()
        self.tsp.c_dist_list()

        ga = MGG.GA(self.tsp)
        ga.init_s_list()
        for s in ga.s_list:
            self.c_sub(self.tsp, s)
        Sub.running = True

        while ga.generation <= c.GENERATION_COMBINE:
            if self.check_subs_closed():
                return
            ga.generation += 1
            for s_i, s in enumerate(ga.s_list):
                s.society_grow()
                self.sub[s_i].draw_best_tour()
                self.sub[s_i].draw_stats(ga.generation)

            ga.show_stats(ga.s_list)
            self.update()

        print("--COMBINED SOCIETIES--")
        ga.combine_society()
        self.c_sub(self.tsp, ga.s_combined)
        window_combined = self.sub[-1]
        while (ga.generation <= c.GENERATION_MAX):
            if self.check_subs_closed():
                return
            ga.generation += 1
            ga.s_combined.society_grow()
            window_combined.draw_best_tour()
            window_combined.draw_stats(ga.generation)
            self.update()
        self.draw_text(App.center, App.font_size, "Done", "state")
        print("--finished--")

    def draw_text(self, x, y, txt, tag):
        self.canvas.delete(tag)
        self.canvas.create_text(x, y, text=txt, tag=tag,
                                anchor="center", font="arial "+str(App.font_size), fill="black")

    def destroy_subs(self):
        self.canvas.delete("state")
        for sub in self.sub:
            sub.master.destroy()
        Sub.running = False
        self.sub.clear()

    def on_closing(self):
        self.destroy_subs()
        self.master.destroy()


class Sub(tk.Frame):
    button_w = 200
    button_h = 50
    count = 0
    font_size = int(App.font_size * c.scale)
    draw_size = int(c.draw_size*c.scale)
    center = draw_size/2
    city_r = c.city_r * c.scale
    city_pos = []
    running = False

    def __init__(self, app, master, tsp, society):
        super().__init__(master)
        self.app = app
        Sub.city_pos.clear()
        for pos in tsp.city_pos:
            Sub.city_pos.append((pos[0]*c.scale, pos[1]*c.scale))
        self.pack()
        Sub.count += 1
        self.num = Sub.count
        self.s = society
        master.geometry(str(Sub.draw_size)+"x"+str(Sub.draw_size))
        master.title("sub window:"+str(self.num))
        self.tsp = tsp
        self.canvas = tk.Canvas(master, width=Sub.draw_size,
                                height=Sub.draw_size, background="grey")
        self.canvas.place(x=0, y=0)
        self.draw_cities()
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def draw_cities(self):
        self.canvas.delete("city")
        for pos in Sub.city_pos:
            self.canvas.create_oval(pos[0]-Sub.city_r, pos[1]-Sub.city_r,
                                    pos[0]+Sub.city_r, pos[1]+Sub.city_r, tag="city", fill="blue")

    def get_best_tour(self):
        return self.s.get_best_tour()

    def draw_best_tour(self):
        tour = self.get_best_tour()
        gene = tour.gene
        self.canvas.delete("tour")
        for i in range(c.CITY_NUM-1):
            city = gene[i]
            city_next = gene[i+1]
            x_1 = Sub.city_pos[city][0]
            y_1 = Sub.city_pos[city][1]
            x_2 = Sub.city_pos[city_next][0]
            y_2 = Sub.city_pos[city_next][1]
            self.canvas.create_line(x_1, y_1, x_2, y_2, width=2, tag="tour")
        self.canvas.create_line(
            x_2, y_2, Sub.city_pos[gene[0]][0], Sub.city_pos[gene[0]][1], width=2, tag="tour", fill="red")

    def draw_text(self, x, y, txt, tag):
        self.canvas.delete(tag)
        self.canvas.create_text(x, y, text=txt, tag=tag,
                                anchor="center", font="arial "+str(Sub.font_size), fill="black")

    def draw_stats(self, generation):
        best_tour = self.get_best_tour()
        self.draw_text(
            Sub.center, Sub.font_size, "generation: "+str(generation), "generation")
        self.draw_text(
            Sub.center, Sub.draw_size-Sub.font_size, "fitness: "+str(best_tour.fitness), "fitness")

    def on_closing(self):
        Sub.running = False
        self.app.destroy_subs()


def main():
    tsp = MGG.TSP()
    root = tk.Tk()
    app = App(root, tsp)
    app.mainloop()


if __name__ == '__main__':
    main()
