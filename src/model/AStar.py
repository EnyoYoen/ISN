from model.Geometry import Point
from model.Map import Map, Biomes
from model.Perlin import Perlin

class Node:
    """
    Un noeud dans l'algorithme A*.

    Attributs:
    ----------
    position : Point
        La position du noeud sur la carte.
    parent : Node
        Le noeud parent dans l'algorithme, le noeud atteint avant ce noeud.
    g : int
        Le coût du chemin du début jusqu'à ce noeud.
    h : int
        Le coût heuristique (cout potentiel) du chemin de ce noeud jusqu'à la fin.
    f : int
        La somme du coût du chemin et du coût heuristique.
    """

    __slots__ = ["position", "parent", "g", "h", "f"]

    def __init__(self, position, parent=None):
        """
        Initialise un noeud dans l'algorithme A*.
        
        Parametres:
        -----------
        position : Point
            La position du noeud sur la carte.
        parent : Node
            Le noeud parent dans l'algorithme, le noeud atteint avant ce noeud.
        """
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

CELL_CENTER = Point(Map.CELL_SIZE, Map.CELL_SIZE) // 2

def AStar(start, end, map):
    """
    Trouve le chemin le plus court entre deux points sur la carte en utilisant l'algorithme A*.

    Parametres:
    -----------
    start : Point
        Le point de départ du chemin.
    end : Point
        Le point d'arrivée du chemin.
    map : Map
        La carte du jeu.
    """
    open_list = [] # Liste des noeuds adjacents à explorer
    closed_list = [] # Liste des noeuds déjà explorés

    start_node = Node(start) # Noeud de départ
    end_node = Node(end) # Noeud d'arrivée

    open_list.append(start_node)

    # Tant qu'il reste des noeuds à explorer (et que la fin n'est pas atteinte)
    while open_list:
        current_node = open_list[0]
        current_index = 0

        # On cherche le noeud avec le coût f le plus bas
        for index, node in enumerate(open_list):
            if node.f < current_node.f:
                current_node = node
                current_index = index

        # On retire le noeud courant de la liste des noeuds à explorer et on l'ajoute à la liste des noeuds explorés
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Si on a atteint la fin, on reconstruit le chemin
        if current_node.position == end_node.position:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position * Map.CELL_SIZE + CELL_CENTER)
                current = current.parent
            return path[::-1]

        # On génère les voisins du noeud courant
        neighbors = []
        for new_position in [Point(0, -1), Point(0, 1), Point(-1, 0), Point(1, 0), Point(-1, -1), Point(-1, 1), Point(1, -1), Point(1, 1)]:
            node_position = current_node.position + new_position

            new_node = Node(node_position, current_node)
            neighbors.append(new_node)

        # On vérifie les voisins
        for neighbor in neighbors:
            if neighbor in closed_list:
                continue

            # On crée les coûts g, h et f du voisin
            neighbor.g = current_node.g + 1
            neighbor.h = abs(neighbor.position.x - end_node.position.x) + abs(neighbor.position.y - end_node.position.y)
            neighbor.f = neighbor.g + neighbor.h

            # Si le voisin est déjà dans la liste des noeuds à explorer et que son coût g est plus élevé, on l'ignore
            if neighbor in open_list:
                if neighbor.g > current_node.g:
                    continue

            open_list.append(neighbor)

    return None