from model.Ressource import RessourceType
from model.Upgrades import Upgrades

class Player:
    """
    Un joueur dans le jeu.
    
    Attributs:
    ----------
    pid : int
        L'identifiant du joueur.
    ressources : dict
        Les ressources du joueur.
    ressource_update_callback : function
        La fonction de rappel pour mettre à jour les ressources.
    upgrades : Upgrades
        Les améliorations du joueur.
    """

    __slots__ = ["pid", "ressources", "ressource_update_callback", "upgrades"]

    PID = 0

    def __init__(self, ressource_update_callback) -> None:
        # On initialise les attributs du joueur
        Player.PID += 1
        self.pid = Player.PID 
        delta = 0.05 # On ajoute un delta pour éviter les erreurs de calcul avec les flottants
        self.ressources = {
            RessourceType.FOOD: 200 + delta,
            RessourceType.WOOD: 150 + delta,
            RessourceType.STONE: delta,
            RessourceType.GOLD: delta, 
            RessourceType.COPPER: delta,
            RessourceType.IRON: delta,
            RessourceType.CRYSTAL: delta,
            RessourceType.VULCAN: delta
        }
        self.ressource_update_callback = ressource_update_callback
        self.upgrades = Upgrades()

    def add_ressource(self, ressource_type, quantity):
        """
        Ajoute une quantité de ressource au joueur.

        Parametres:
        -----------
        ressource_type : RessourceType
            Le type de ressource à ajouter.
        quantity : int
            La quantité de ressource à ajouter.
        """
        old_ressource = self.ressources[ressource_type]
        self.ressources[ressource_type] += quantity
        if int(old_ressource) < int(old_ressource + quantity):
            self.ressource_update_callback()

    def get_ressource(self, ressource_type):
        """
        Retourne la quantité de ressource du joueur.

        Parametres:
        -----------
        ressource_type : RessourceType
            Le type de ressource à récupérer.
        """
        return self.ressources.get(ressource_type, 0)