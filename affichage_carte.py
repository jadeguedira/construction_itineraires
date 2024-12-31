# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 13:20:21 2024

@author: rahya
"""

import folium as f
import webview
import json
import os
import sys

with open("dico_deb_fin.json", "r") as json_file:
    dico_deb_fin = json.load(json_file)

def cree_map(liste_coords):
    coord_chemin = liste_coords
    """
    dep = dico_deb_fin[liste_rues[0]][0]
    coord_chemin.append(dep)
    for i in (1, len(liste_rues)-1):
        coord_a_ajt, coord_a_ajt_2 = dico_deb_fin[liste_rues[i]][0], dico_deb_fin[liste_rues[i]][1]
        coord_chemin.append(coord_a_ajt)
        coord_chemin.append(coord_a_ajt_2)
    """
    carte = f.Map(location = coord_chemin[0], zoom_start = 5)
    f.PolyLine(coord_chemin, color = 'red', weight = 2.5, opacity = 1).add_to(carte)
    
    sauv = "cartes.html"
    carte.save(sauv) #on enregistre la carte pour pouvoir l'ouvrir juste après
    webview.create_window('Carte', sauv)
    webview.start()