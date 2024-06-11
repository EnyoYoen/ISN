class Point:
    """
    Un point dans un espace 2D.

    Attributs:
    ----------
    x : int
        La coordonnée x du point.
    y : int
        La coordonnée y du point.
    """
    __slots__ = ["x", "y"]

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        """
        Ajoute deux points ensemble.

        Parametres:
        -----------
        other : Point
            Le point à ajouter à ce point.
        """
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """
        Soustrait un point à ce point.

        Parametres:
        -----------
        other : Point
            Le point à soustraire à ce point.
        """
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """
        Multiplie ce point par un scalaire.

        Parametres:
        -----------
        scalar : int
            Le scalaire par lequel multiplier ce point.
        """
        return Point(self.x * scalar, self.y * scalar)
    
    def __div__(self, scalar):
        """
        Divise ce point par un scalaire.

        Parametres:
        -----------
        scalar : int
            Le scalaire par lequel diviser ce point.
        """
        return Point(self.x / scalar, self.y / scalar)
    
    def __floordiv__(self, scalar):
        """
        Divise ce point par un scalaire et retourne le résultat entier.

        Parametres:
        -----------
        scalar : int
            Le scalaire par lequel diviser ce point.
        """
        return Point(self.x // scalar, self.y // scalar)
    
    def __mod__(self, scalar):
        """
        Prend le modulo de ce point par un scalaire.

        Parametres:
        -----------
        scalar : int
            Le scalaire par lequel prendre le modulo de ce point.
        """
        return Point(self.x % scalar, self.y % scalar)

    """
    Même chose que les méthodes précédentes, mais avec les opérateurs d'affectation.
    """
    def __radd__(self, other):
        self.x += other.x
        self.y += other.y
    
    def __rsub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __rmul__(self, scalar):
        self.x *= scalar
        self.y *= scalar
    
    def __rdiv__(self, scalar):
        self.x /= scalar
        self.y /= scalar
    
    def __rfloordiv__(self, scalar):
        self.x //= scalar
        self.y //= scalar
    
    def __rmod__(self, scalar):
        self.x %= scalar
        self.y %= scalar

    def __eq__(self, other):
        """
        Vérifie si deux points sont égaux.

        Parametres:
        -----------
        other : Point
            L'autre point à comparer à ce point.
        """
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """
        Retourne le hash (nombre entier identifiant) du point.
        """
        return hash((self.x, self.y))
    
    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères du point.
        """
        return f"Point({self.x}, {self.y})"

    def opposite(self):
        """
        Retourne le point opposé à ce point.
        """
        self.x = -self.x
        self.y = -self.y

    def invert(self):
        """
        Inverse les coordonnées x et y du point.
        """
        tmp = self.x
        self.x = self.y
        self.y = tmp
    
    def distance(self, other):
        """
        Calcule la distance euclidienne entre ce point et un autre point.

        Parametres:
        -----------
        other : Point
            L'autre point pour calculer la distance.
        """
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def origin():
        """
        Retourne le point (0, 0).
        """
        return Point(0, 0)

class Rectangle:    
    """
    Un rectangle dans un espace 2D.

    Attributs:
    ----------
    x1 : int
        La coordonnée x du coin supérieur gauche du rectangle.
    y1 : int
        La coordonnée y du coin supérieur gauche du rectangle.
    x2 : int
        La coordonnée x du coin inférieur droit du rectangle.
    y2 : int
        La coordonnée y du coin inférieur droit du rectangle.
    """

    __slots__ = ["x1", "y1", "x2", "y2"]

    def __init__(self, x1, y1, x2, y2) -> None:
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    @staticmethod
    def fromPoints(p1, p2):
        """
        Crée un rectangle à partir de deux points.
        """
        x1 = p1.x
        x2 = p2.x
        y1 = p1.y
        y2 = p2.y
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        return Rectangle(x1, y1, x2, y2)
    
    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères du rectangle.
        """
        return f"Rectangle({self.x1}, {self.y1}, {self.x2}, {self.y2})"
    

    def width(self):
        """
        Retourne la largeur du rectangle.
        """
        return self.x2 - self.x1
    
    def height(self):
        """
        Retourne la hauteur du rectangle.
        """
        return self.y2 - self.y1
    
    def containsPoint(self, point):
        """
        Vérifie si un point est contenu dans le rectangle.

        Parametres:
        -----------
        point : Point
            Le point à vérifier.
        """
        return (self.x1 <= point.x and point.x <= self.x2 and
                self.y1 <= point.y and point.y <= self.y2)
    
    def containsCoords(self, x, y):
        """
        Vérifie si des coordonnées sont contenues dans le rectangle.

        Parametres:
        -----------
        x : int
            La coordonnée x à vérifier.
        y : int
            La coordonnée y à vérifier.
        """
        return (self.x1 <= x and x <= self.x2 and
                self.y1 <= y and y <= self.y2)

    def overlap(self, other):
        """
        Vérifie si un autre rectangle chevauche ce rectangle.

        Parametres:
        -----------
        other : Rectangle
            L'autre rectangle à vérifier.
        """
        return self.containsCoords(other.x1, other.y1) or self.containsCoords(other.x2, other.y2)
    
    def toPointList(self):
        """
        Retourne une liste de points représentant les cases du rectangle.
        """
        points = []
        for y in range(self.y1, self.y2 + 1):
            for x in range(self.y1, self.y2 + 1):
                points.append(Point(x, y))
        return points
    
class Circle:
    """
    Un cercle dans un espace 2D.

    Attributs:
    ----------
    center : Point
        Le centre du cercle.
    radius : int
        Le rayon du cercle.
    """
    
    __slots__ = ["center", "radius"]

    def __init__(self, center, radius) -> None:
        self.center = center
        self.radius = radius

    def contains(self, point):
        """
        Vérifie si un point est contenu dans le cercle.

        Parametres:
        -----------
        point : Point
            Le point à vérifier.
        """
        return self.center.distance(point) <= self.radius

    def overlap(self, other):
        """
        Vérifie si un autre cercle chevauche ce cercle.

        Parametres:
        -----------
        other : Circle
            L'autre cercle à vérifier.
        """
        return self.center.distance(other.center) <= self.radius + other.radius
    
class Polygon:
    """
    Un polygone dans un espace 2D.

    Attributs:
    ----------
    points : list
        La liste des points du polygone.
    """

    __slots__ = ["points"]

    def __init__(self, points) -> None:
        self.points = points

    def contains(self, point):
        """
        Vérifie si un point est contenu dans le polygone.

        Parametres:
        -----------
        point : Point
            Le point à vérifier.
        """
        length = len(self.points)
        intersections = 0

        dx2 = point[0] - self.points[0][0]
        dy2 = point[1] - self.points[0][1]
        i = 1

        contained = False

        while i < length and not contained:
            dx  = dx2
            dy  = dy2
            dx2 = point[0] - self.points[i][0]
            dy2 = point[1] - self.points[i][1]

            f = dx * dy2 - dy * dx2 #f = (dx - dx2) * dy - dx * (dy - dy2)
            if f == 0.0 and dx * dx2 <= 0: # and dy * dy2 <= 0:
                contained = True
            elif (dy>=0 and dy2<0) or (dy2>=0 and dy<0):
                if f > 0:
                    intersections += 1
                elif f < 0:
                    intersections -= 1

            i += 1

        return intersections != 0 or contained