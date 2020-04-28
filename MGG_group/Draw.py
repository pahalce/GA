from reportlab.graphics.shapes import Drawing, Circle, PolyLine, String
from reportlab.graphics import renderPDF
from init import draw_size, center, CITY_NUM, city_pos


def draw_tour(gene, file_name, text=""):
    d = Drawing(draw_size, draw_size)
    tour_xy = []
    for i in range(CITY_NUM):
        tour_i = gene[i]
        if i == 0:
            color = "red"
        else:
            color = "black"
        c = Circle(city_pos[tour_i][0], city_pos[tour_i]
                   [1], 5, fillColor=color)
        d.add(c)
        tour_xy.append(city_pos[tour_i])
    tour_xy.append(city_pos[gene[0]])
    l = PolyLine(tour_xy[1:], strokeColor="blue")
    d.add(l)
    l = PolyLine(tour_xy[:2], strokeColor="red")
    d.add(l)
    if text != "":
        s = String(center, 10, text, textAnchor="middle")
        d.add(s)
    renderPDF.drawToFile(
        d, "{}.pdf".format(file_name))
