from math import sqrt

class Line():
    def __init__(self, coord1, coord2):
        self.coord1 = coord1
        self.coord2 = coord2

    def distance(self):
        x1, y1 = self.coord1
        x2, y2 = self.coord2
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def slope(self):
        x1, y1 = self.coord1
        x2, y2 = self.coord2
        return (y2 - y1) / (x2 - x1)

def main():
    coordinate1 = (3,2)
    coordinate2 = (8,10)
                
    li = Line(coordinate1, coordinate2)

    print(f"Відстань між точками: {li.distance()}")
    print(f"Нахил лінії: {li.slope()}")

if __name__ == "__main__":
    main()




