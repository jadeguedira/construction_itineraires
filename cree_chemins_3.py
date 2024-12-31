import csv, json, math
import heapq

#Lecture de fichiers

fichier_json = 'graphe_final_3.json'
with open(fichier_json, "r") as f:
    graphe_final_json = json.load(f)

graphe_final = {}
for mini_dico in graphe_final_json:
    k = tuple( mini_dico['key'] )
    v = mini_dico['value']
    for i in range(len(v)):
        v[i]['coord'] = tuple(v[i]['coord'])
    graphe_final[ k ] = mini_dico['value']



fichier_json = 'dico_infos_rues.json'
with open(fichier_json, "r") as f:
    dico_infos_rues = json.load(f)



fichier_json =  'dico_coordonnee_associee.json'
with open(fichier_json, "r") as f:
    dico_coordonnee_associee_json = json.load(f)

dico_coordonnee_associee = {}
for mini_dico in dico_coordonnee_associee_json:
    k = tuple( mini_dico['key'] )
    v = tuple( mini_dico['value'] )
    dico_coordonnee_associee[ k ] = v


def dijkstra(graphe, depart, arrivee, metrique='distance'):
    file_priorite = [(0, depart, [], [])]  # (valeur_metrique, noeud_courant, chemin, rues)
    visites = set()
    metriques = {depart: 0}

    while file_priorite:
        (metrique_courante, noeud_courant, chemin, rues) = heapq.heappop(file_priorite) #On récupère l'élément qui a la distance minimale et le supprime de la liste

        if noeud_courant in visites:
            continue

        chemin = chemin + [noeud_courant]
        visites.add(noeud_courant)

        if noeud_courant == arrivee:
            return (metrique_courante, chemin, rues)

        for voisin in graphe.get(noeud_courant, []):
            noeud_voisin = voisin['coord']
            valeur_metrique = voisin[metrique]
            nouvelle_metrique = metrique_courante + valeur_metrique

            if noeud_voisin not in visites and (noeud_voisin not in metriques or nouvelle_metrique < metriques[noeud_voisin]):
                metriques[noeud_voisin] = nouvelle_metrique
                nouvelles_rues = rues + [voisin['rue']]
                heapq.heappush(file_priorite, (nouvelle_metrique, noeud_voisin, chemin, nouvelles_rues)) #on ajoute le sommet avec la distance totale pour l'atteindre dans la liste


    return (float('inf'), [], [])


def get_rue_coords(nom_rue):
    c1,c2 = dico_infos_rues[nom_rue.lower()]['coords']
    r1 = dico_coordonnee_associee.get(tuple(c1), c1)
    r2 = dico_coordonnee_associee.get(tuple(c2), c2)
    return tuple(r1), tuple(r2)

def dijkstra_rues(graphe, rue_depart, rue_arrivee, metrique='temps'):
    dep = get_rue_coords(rue_depart)[0]
    arr = get_rue_coords(rue_arrivee)[1]
    temps, chemin, rues = dijkstra(graphe, dep, arr, metrique)
    return chemin

def verifier_points_non_voisins(graph):
    for point, voisins in graph.items():
        for voisin in voisins:
            if point == voisin['coord']:
                print(f"Le point {point} est voisin de lui-même.")
                return False
    return True
#verifier_points_non_voisins(graphe_final)

"""
depart = (45.7578935, 4.721895)
arrivee = (45.7609496667, 4.7212453333)

temps, chemin, rues = dijkstra(graphe_final, depart, arrivee, metrique='temps')


print("Temps le plus court:", temps)
print("Chemin:", chemin)
print("Rues empruntées:", rues)
"""
print(graphe_final[(45.759875, 4.7302385)])

rue_dep = 'rue Georges Kayser'
rue_arr = 'avenue marcel merieux'
rues_final = dijkstra_rues(graphe_final, rue_dep, rue_arr, metrique='temps')
print(rues_final)
