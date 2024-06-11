import random
import numpy as np
import math

class Perlin:
    """
    Générateur de bruit de Perlin (algorithme non trivial).

    Attributs:
    ----------
    seed : int
        La graine du générateur.
    octave : int
        Le nombre d'octaves du générateur.
    persistence : float
        La persistance du générateur.
    lacunarity : float
        La lacunarité du générateur.
    scale : float
        L'échelle du générateur.
    amplitude : float
        L'amplitude du générateur.
    chunks : dict
        Les chunks générés par le générateur.
    gradients : list
        Les gradients du générateur.
    permutation : list
        La table de permutation du générateur.
    x_offset : int
        Le décalage x du générateur.
    y_offset : int
        Le décalage y du générateur.
    """

    __slots__ = ["seed", "octave", "persistence", "lacunarity", "scale", "amplitude", "chunks", "gradients", "permutation", "x_offset", "y_offset"]

    CHUNK_SIZE = 32

    def __init__(self, seed = 1, octave = 1, persistence = 1.0, lacunarity = 1.0, scale = 1.0, amplitude = 1.0) -> None:
        # On initialise les paramètres du générateur
        self.seed = seed
        self.octave = octave
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.scale = scale
        self.amplitude = amplitude
        self.chunks = {}
        self.gradients = []
        self.permutation = []

        # On initialise la graine du générateur
        self.set_seed(seed)

    def set_seed(self, seed):
        """
        Initialise la graine du générateur.

        Parametres:
        -----------
        seed : int
            La graine du générateur.
        """
        # On initialise la graine du générateur de nombres aléatoires
        random.seed(seed)

        # On initialise les décalages x et y du générateur
        self.x_offset = random.randrange(-100, 100)
        self.y_offset = random.randrange(-100, 100)
        
        # On génère la table de permutation et les gradients
        self.generate_permutation_table()
        self.generate_gradients()
        
    def generate_permutation_table(self):
        """
        Génère la table de permutation du générateur.
        """
        permutation = list(range(256))
        random.shuffle(permutation)
        self.permutation = permutation * 2

    def generate_gradients(self):
        """
        Génère les gradients du générateur.
        """
        for _ in range(256):
            self.gradients.append((random.uniform(-1, 1), random.uniform(-1, 1)))

    def fade(self, t):
        """
        Fonction de fondu pour l'interpolation.

        Parametres:
        -----------
        t : float
            Le paramètre de la fonction.
        """
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3 # t*t*t*(t*(t*6 - 15) + 10)

    def lerp(self, a, b, t):
        """
        Fonction de lerp pour l'interpolation entre deux valeurs.

        Parametres:
        -----------
        a : float
            La première valeur.
        b : float
            La deuxième valeur.
        t : float
            Le paramètre de l'interpolation.
        """
        return a + t * (b - a)

    def dot_product(self, grad, x, y):
        """
        Produit scalaire entre un gradient et un vecteur.

        Parametres:
        -----------
        grad : tuple
            Le gradient.
        x : float
            La coordonnée x du vecteur.
        y : float
            La coordonnée y du vecteur.
        """
        return grad[0] * x + grad[1] * y

    def noise(self, x, y):
        """
        Génère une valeur de bruit de Perlin pour un point donné.

        Parametres:
        -----------
        x : float
            La coordonnée x du point.
        y : float
            La coordonnée y du point.
        """
        X = math.floor(x) & 255
        Y = math.floor(y) & 255

        xf = x - math.floor(x)
        yf = y - math.floor(y)

        u = self.fade(xf)
        v = self.fade(yf)

        # Coordonnées (hachées) des coins
        aa = self.permutation[X] + Y
        ab = self.permutation[X] + Y + 1
        ba = self.permutation[X + 1] + Y
        bb = self.permutation[X + 1] + Y + 1

        # Vecteurs gradients
        g_aa = self.gradients[self.permutation[aa] % 256]
        g_ab = self.gradients[self.permutation[ab] % 256]
        g_ba = self.gradients[self.permutation[ba] % 256]
        g_bb = self.gradients[self.permutation[bb] % 256]

        # Produits scalaires
        n_aa = self.dot_product(g_aa, xf, yf)
        n_ab = self.dot_product(g_ab, xf, yf - 1)
        n_ba = self.dot_product(g_ba, xf - 1, yf)
        n_bb = self.dot_product(g_bb, xf - 1, yf - 1)

        # Interpolation
        x1 = self.lerp(n_aa, n_ba, u)
        x2 = self.lerp(n_ab, n_bb, u)

        # Interpolation finale
        return self.lerp(x1, x2, v)

    def generate_chunk(self, x, y):
        """
        Génère un chunk de bruit de Perlin.

        Parametres:
        -----------
        x : int
            La coordonnée x du chunk.
        y : int
            La coordonnée y du chunk.
        """
        # On initialise le chunk
        chunk = np.empty((self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=float)

        # On initialise les valeurs min et max du bruit
        max_noise_height = -math.inf
        min_noise_height = +math.inf

        # On génère le bruit de Perlin pour chaque case du chunk
        for xi in range(self.CHUNK_SIZE):
            for yi in range(self.CHUNK_SIZE):
                amplitude = self.amplitude
                freq = 1
                noise_height = 0

                for _ in range(self.octave):
                    px = (self.CHUNK_SIZE * x + xi + self.x_offset) / self.scale * freq + self.x_offset
                    py = (self.CHUNK_SIZE * y + yi + self.y_offset) / self.scale * freq + self.y_offset

                    perlin_value = self.noise(px, py)
                    noise_height += perlin_value * amplitude

                    # Augmenter l'amplitude et la fréquence
                    amplitude *= self.persistence
                    freq *= self.lacunarity

                # On met à jour les valeurs min et max du bruit
                if noise_height > max_noise_height:
                    max_noise_height = noise_height
                elif noise_height < min_noise_height:
                    min_noise_height = noise_height

                chunk[xi, yi] = noise_height

        # On ajoute le chunk au dictionnaire des chunks
        self.chunks[(x, y)] = (chunk, min_noise_height, max_noise_height)
    
    def get_chunk(self, x, y):
        """
        Retourne un chunk de bruit de Perlin.

        Parametres:
        -----------
        x : int
            La coordonnée x du chunk.
        y : int
            La coordonnée y du chunk.
        """
        # On génère le chunk si il n'existe pas
        if self.chunks.get((x, y)) == None:
            self.generate_chunk(x, y)

        return self.chunks[(x, y)]
    
    def get_chunk_data(self, x, y):
        """
        Retourne les données d'un chunk de bruit de Perlin.

        Parametres:
        -----------
        x : int
            La coordonnée x du chunk.
        y : int
            La coordonnée y du chunk.
        """
        if self.chunks.get((x, y)) == None:
            self.generate_chunk(x, y)

        return self.chunks[(x, y)][0]