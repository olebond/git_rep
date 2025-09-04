from math import sqrt

class Line:
    def __init__(self, point1, point2):
        """
        Ініціалізація лінії з двома точками
        point1: tuple (x1, y1)
        point2: tuple (x2, y2)
        """
        self.point1 = point1
        self.point2 = point2

    def get_slope(self):
        """
        Обчислює нахил лінії
        Повертає: float або None (якщо лінія вертикальна)
        """
        x1, y1 = self.point1
        x2, y2 = self.point2
        
        # Перевірка на вертикальну лінію
        if x2 - x1 == 0:
            return None
            
        return (y2 - y1) / (x2 - x1)

    def get_distance(self):
        """
        Обчислює відстань між двома точками
        Повертає: float
        """
        x1, y1 = self.point1
        x2, y2 = self.point2
        
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def main():
    # Приклад 1: Звичайна лінія
    line1 = Line((1, 2), (3, 4))
    print("Приклад 1:")
    print(f"Точки: (1, 2) та (3, 4)")
    print(f"Нахил лінії: {line1.get_slope()}")
    print(f"Відстань між точками: {line1.get_distance()}")
    print()

    # Приклад 2: Вертикальна лінія
    line2 = Line((1, 1), (1, 5))
    print("Приклад 2:")
    print(f"Точки: (1, 1) та (1, 5)")
    print(f"Нахил лінії: {line2.get_slope()}")
    print(f"Відстань між точками: {line2.get_distance()}")
    print()

    # Приклад 3: Горизонтальна лінія
    line3 = Line((1, 1), (5, 1))
    print("Приклад 3:")
    print(f"Точки: (1, 1) та (5, 1)")
    print(f"Нахил лінії: {line3.get_slope()}")
    print(f"Відстань між точками: {line3.get_distance()}")

if __name__ == "__main__":
    main() 