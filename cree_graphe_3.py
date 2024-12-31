import csv, json, math
import numpy as np
import os
from os.path import abspath, dirname
from geopy.distance import geodesic

os.chdir(dirname(abspath(__file__))) #Corrige le probleme sur VSCODE

#Fonctions generales utiles

def distance(coord1, coord2):
    return geodesic(coord1, coord2).meters


#Lecture de fichiers et creation de donnees associees

#Fichier 1 : coordonnees rues
def cree_dico_rues_coords(csv_file):
    """Dictionnaire dico_deb_fin :
    - clé : nom de rue
    - valeur : [coord_deb_rue, coord_fin_rue], ou coord est un tuple (lat, long)

    Dictionnaire dico_num_rue :
    - clé : nom de rue
    - valeur : Liste des numeros de rue""" #Ajouter coordonnees associees ?
    with open(csv_file, newline = "") as csvfile:
        reader = csv.reader(csvfile, delimiter = ";")
        dicotemp = dict()
        dico_num_rue = dict()
        reader.__next__() #suppression 1ere ligne
        for ligne in reader :
            liste_temp = dicotemp.get(ligne[4].lower(), [])
            liste_temp.append([int(ligne[2]), ligne[4].lower(), float(ligne[13]), float(ligne[12])]) #num, rue, lat, long
            dicotemp[ligne[4].lower()] = liste_temp
            
            liste_num_rue_temp = dico_num_rue.get(ligne[4], [])
            liste_num_rue_temp.append(int(ligne[2]))
            dico_num_rue[ligne[4].lower()] = liste_num_rue_temp

    dico_deb_fin = dict()
    for element in dicotemp.values():
        elem_temp = list() 
        elem_temp.append((element[0][2], element[0][3]))
        elem_temp.append((element[len(element) - 1][2], element[len(element) - 1][3]) )
        dico_deb_fin[element[0][1].lower()] = elem_temp

    return dico_deb_fin, dico_num_rue

dico_deb_fin, dico_num_rue = cree_dico_rues_coords("adresses_69.csv")

#Fichier 2 : Informations par rue : vitesse moyenne, etat, etc.
#On réalise ici un croisement des deux fichiers 

def corrige_texte(nom_rue):
    nom_rue = nom_rue.lower()
    if nom_rue[0:2] == 'r ':
        nom_rue = 'rue '+ nom_rue[2:]
    return nom_rue

def cree_dico_infos_rues(csv_file, dico_deb_fin):
    """Dico :
    - clé : nom de rue
    - valeur : {'etat': _, 'vitesse': _, 'distance': _, 'coords' : _}"""
    vit_moyen = 30
    with open(csv_file, 'r') as f:
        csvReader = csv.reader(f, delimiter=";")
        dico = {}
        csvReader.__next__()
        for row in csvReader:
            _, _, nom_rue, _, id_sens, distance, _, _, etat, vitesse, _, _, _, _ = row
            nom_rue = corrige_texte(nom_rue)
            coord1, coord2 = dico_deb_fin.get(nom_rue, (None, None))

            if vitesse == '' or vitesse[1] == 'i':
                vitesse = vit_moyen
            else:
                vitesse = vitesse[:-5]
            if etat == '*':
                etat = 'V'
            
            if coord1 != None:
                dico[nom_rue] = {'etat':etat, 'vitesse':float(vitesse), 'distance': float(distance), 'coords' : [coord1,coord2]}
    return dico
    

excel_vitesses = 'donnees_trafic_lyon.csv'  
dico_infos_rues = cree_dico_infos_rues(excel_vitesses, dico_deb_fin)

#Compléter données manquantes avec données moyennes

def completer_rues_manquantes(dico_infos_rues, dico_rues, lat, long, seuil):
    vit_moyen = 30
    for nom_rue, coords in dico_rues.items():
        coord1, coord2 = coords
        if (coord1 != None) and (coord1[0] < lat + seuil) and (coord1[0] > lat - seuil) and\
            (coord1[1] < long + seuil) and (coord1[1] > long - seuil):
            if dico_infos_rues.get(nom_rue, None) is None:
                dist = distance(coord1, coord2)
                if dist != 0:
                    dico_infos_rues[nom_rue] = {'etat': 'V', 'vitesse': vit_moyen, 'distance': dist, 'coords' : coords}

completer_rues_manquantes(dico_infos_rues, dico_deb_fin, 45.8, 4.6, seuil = 0.15)
print('etape1')

#Creation d'un dico associant les coordonnees voisines
    
def crea_dico_relie_rue(dico_deb_fin):
    """Dictionnaire rue_relie :
    - clé : (rue1, i1)
    - valeur : [(rue2, i2), (rue3, i3), ...]
    où rue est le nom de la rue et i est l'indice de la position de la coordoonnee dans dico_infos_rues

    On définit un ecart maximal de distance pour considerer que les deux points sont confondues
    """
    arr = 3
    rue_relie = {}
    for element in dico_deb_fin.keys():
        if (dico_deb_fin[element]["coords"][0]) != None and (dico_deb_fin[element]["coords"][1]) != None :
            coordonees_deb_ele = dico_deb_fin[element]["coords"][0]
            coordonees_fin_ele = dico_deb_fin[element]["coords"][1]
            for rue in dico_deb_fin.keys():
                if (dico_deb_fin[rue]["coords"][0]) != None and (dico_deb_fin[rue]["coords"][1]) != None and element != rue:
                    coord_deb_rue_2 = dico_deb_fin[rue]["coords"][0]
                    coord_fin_rue_2 = dico_deb_fin[rue]["coords"][1]
                    #if (coord_deb_rue_2[0] > coordonees_deb_ele[0] - seuil) and (coord_deb_rue_2[0] < coordonees_deb_ele[0] + seuil):
                    """
                    if distance(coord_deb_rue_2, coordonees_deb_ele) <= ecart_m:
                        liste_temp = rue_relie.get((element, 0), [])
                        liste_temp.append((rue, 0))
                        rue_relie[(element, 0)] = liste_temp
                    if distance(coord_fin_rue_2, coordonees_deb_ele) <= ecart_m:
                        liste_temp = rue_relie.get((element, 0), [])
                        liste_temp.append((rue, 1))
                        rue_relie[(element, 0)] = liste_temp
                    if distance(coord_deb_rue_2, coordonees_fin_ele) <= ecart_m:
                        liste_temp = rue_relie.get((element, 1), [])
                        liste_temp.append((rue, 0))
                        rue_relie[(element, 1)] = liste_temp
                    if distance(coord_fin_rue_2, coordonees_fin_ele) <= ecart_m:
                        liste_temp = rue_relie.get((element, 1), [])
                        liste_temp.append((rue, 1))
                        rue_relie[(element, 1)] = liste_temp   
                        """
                    if (round(coordonees_deb_ele[0], arr) == round(coord_deb_rue_2[0], arr)) and (round(coordonees_deb_ele[1], arr) == round(coord_deb_rue_2[1], arr)):
                        liste_temp = rue_relie.get((element, 0), [])
                        liste_temp.append((rue, 0))
                        rue_relie[(element, 0)] = liste_temp
                    if (round(coordonees_deb_ele[0], arr) == round(coord_fin_rue_2[0], arr)) and (round(coordonees_deb_ele[1], arr) == round(coord_fin_rue_2[1], arr)):
                        liste_temp = rue_relie.get((element, 0), [])
                        liste_temp.append((rue, 1))
                        rue_relie[(element, 0)] = liste_temp
                    if (round(coordonees_fin_ele[0], arr) == round(coord_deb_rue_2[0], arr)) and (round(coordonees_fin_ele[1], arr) == round(coord_deb_rue_2[1], arr)):
                        liste_temp = rue_relie.get((element, 1), [])
                        liste_temp.append((rue, 0))
                        rue_relie[(element, 1)] = liste_temp
                    if (round(coordonees_fin_ele[0], arr) == round(coord_fin_rue_2[0], arr)) and (round(coordonees_fin_ele[1], arr) == round(coord_fin_rue_2[1], arr)):
                        liste_temp = rue_relie.get((element, 1), [])
                        liste_temp.append((rue, 1))
                        rue_relie[(element, 1)] = liste_temp                           
    return rue_relie

dico_voisins_rues = crea_dico_relie_rue(dico_infos_rues)
print('etape2')
#Creation du graphe final associee

def i_else(i):
    return (i+1) % 2

"""Dico :
    - clé : nom de rue
    - valeur : {'etat': _, 'vitesse': _, 'distance': _, 'coords' : _}"""

def cree_graphe(dico_voisins_rues, dico_infos_rues):
    """ graphe est un dictionnaire :
    - clé : coordonnees du point (moyenne de toutes les coordonnees)
    - valeur : [voisin1, voisin2, ...] où voisin = {'coord' : _, 'rue':_, 'temps':_, 'distance':_}
    
    """
    dico_coordonnee_associee = {}
    graphe = {}
    for cle, valeur in dico_voisins_rues.items(): #{(rue1, i1) :  voisins} avec voisins = [(rue2, i2), (rue3, i3), ...]
        rue1, i1 = cle
        coord1 =  dico_infos_rues[rue1]['coords'][i1]
        liste_coords_communs = np.array( [ np.array(coord1) ] + [ np.array( dico_infos_rues[rue2]['coords'][i2] ) for rue2, i2 in valeur ] )
        coord_moyen = tuple( np.round(np.mean(liste_coords_communs, axis = 0), 10) )
        
        dico_coordonnee_associee[coord1] = coord_moyen

        coord_oppose1 = dico_infos_rues[rue1]['coords'][i_else(i1)]
        temps1 = dico_infos_rues[rue1]['distance'] / dico_infos_rues[rue1]['vitesse']
        graphe[coord_moyen] = graphe.get(coord_moyen, [])
        graphe[coord_moyen] = [{'coord' :  coord_oppose1, 'rue': rue1, 'temps': temps1, 'distance': dico_infos_rues[rue1]['distance']}]
        for rue2, i2 in valeur:
            coord2 = dico_infos_rues[rue2]['coords'][i2]
            dico_coordonnee_associee[coord2] = coord_moyen

            coord_oppose = dico_infos_rues[rue2]['coords'][i_else(i2)]
            temps = dico_infos_rues[rue2]['distance'] / dico_infos_rues[rue2]['vitesse'] 
            graphe[coord_moyen].append( {'coord' :  coord_oppose, 'rue': rue2, 'temps': temps, 'distance': dico_infos_rues[rue2]['distance']} )

    #Correction du graphe créé en associant les coordonnees moyennes des coordonnees confondues

    for coord, liste_voisins in graphe.items():
        for i in range(len(liste_voisins)):
            coord_moyen = dico_coordonnee_associee.get(graphe[coord][i]['coord'], None)
            if coord_moyen is not None:
                graphe[coord][i]['coord'] = coord_moyen

    return graphe, dico_coordonnee_associee

graphe_final, dico_coordonnee_associee = cree_graphe(dico_voisins_rues, dico_infos_rues)
print('etape3')
#creation du fichier json

def remap_keys(mapping):
    return [{'key':k, 'value': v} for k, v in mapping.items()]

nom_fichier = 'dico_infos_rues.json'
with open(nom_fichier,'w') as f:
    json.dump(dico_infos_rues, f, indent=2)
    
nom_fichier_rues = 'dico_deb_fin.json'
with open(nom_fichier_rues,'w') as f:
    json.dump(dico_deb_fin, f, indent = 2)

dico_coordonnee_associee_json = remap_keys(dico_coordonnee_associee)
nom_fichier = 'dico_coordonnee_associee.json'
with open(nom_fichier,'w') as f:
    json.dump(dico_coordonnee_associee_json, f, indent=2)

graphe_final_json = remap_keys(graphe_final)
nom_fichier = 'graphe_final_3.json'
with open(nom_fichier,'w') as f:
    json.dump(graphe_final_json, f, indent=2)

print(f'Graphe crée : il est enregistré dans {nom_fichier} et contient {len(graphe_final)} points')
"""Pour lire le fichier json (sur un autre programme dans le meme dossier) afin de recuperer le graphe, executez les lignes suivantes :

fichier_json = 'graphe_final.json'
with open(fichier_json, "r") as f:
    graphe_final_json = json.load(f)
graphe_final = {}
for mini_dico in graphe_final_json:
    k = tuple( mini_dico['key'] )
    v = mini_dico['value']
    for i in range(len(v)):
        v[i]['coord'] = tuple(v[i]['coord'])
    graphe_final[ k ] = mini_dico['value']

"""

    
