#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:11:03 2024

@author: mpougnard
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


import csv
import json
import tkinter as tk
import csv
from tkinter import messagebox, scrolledtext
import math
from operator import itemgetter
import folium as f
from PIL import ImageTk
import sys
import os
import time
from affichage_carte import cree_map
from cree_chemins_3 import dijkstra_rues, graphe_final


"""
with open("adresses-69.csv", newline = "") as csvfile:
    reader = csv.reader(csvfile, delimiter = ";")
    dicotemp = dict()
    dico_num_rue = dict()
    reader.__next__() #supression 1ere ligne
    for ligne in reader :
        liste_temp = dicotemp.get(ligne[4], [])
        liste_temp.append([int(ligne[2]), ligne[4], float(ligne[13]), float(ligne[12])]) #num rue lat long
        dicotemp[ligne[4]] = liste_temp
        
        liste_num_rue_temp = dico_num_rue.get(ligne[4], [])
        liste_num_rue_temp.append(int(ligne[2]))
        dico_num_rue[ligne[4]] = liste_num_rue_temp

with open("adresses-69.json", "w") as json_file:
    json.dump(dico_num_rue, json_file)
"""
with open("adresses-69.json", "r") as json_file:
    dico_num_rue_2 = json.load(json_file)
    dico_num_rue = {}
    for element in dico_num_rue_2.keys():
        lst = dico_num_rue_2[element]
        ele2 = element.lower()
        dico_num_rue[ele2] = lst


"""
dico_deb_fin = dict()
for element in dicotemp.values():
    elem_temp = list() 
    elem_temp.append((element[0][2], element[0][3]))
    elem_temp.append((element[len(element) - 1][2], element[len(element) - 1][3]) )
    dico_deb_fin[element[0][1]] = elem_temp
"""

class TrajetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Choix de Trajet")

        # Charger l'image de fond
        self.dico_num_rue = dico_num_rue
        self.image = Image.open("wazer.png")
        self.background_image = ImageTk.PhotoImage(self.image)
        
        
        # Créer un label pour l'image de fond
        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)
        self.background_label.image = self.background_image  # Référence persistante
        self.dico = dico_num_rue
        style = ttk.Style()
        style.theme_use("clam")  # Choisir le thème "clam"
        self.creer_widgets()

    def creer_widgets(self):
        self.depart_label = ttk.Label(self, text="Rue de départ :")
        self.depart_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.ruedep = tk.StringVar()
        self.depart_entry = ttk.Entry(self, textvariable=self.ruedep)
        self.depart_entry.grid(row=0, column=1, padx=10, pady=5)
        
        self.rue_dep_ok = tk.Checkbutton(self, text = 'cliquez ici lorsque la rue est entrée')
        self.rue_dep_ok.grid(row=1, column = 1, padx=10, pady=5)
        self.rue_dep_ok.bind('<Button-1>', self.rue_depart)
        

        self.arrivee_label = ttk.Label(self, text="Rue d'arrivée :")
        self.arrivee_label.grid(row=3, column=0, padx=10, pady=5)

        self.ruearrivee = tk.StringVar()
        self.arrivee_entry = ttk.Entry(self, textvariable=self.ruearrivee)
        self.arrivee_entry.grid(row=3, column=1, padx=10, pady=5)
        
        self.rue_arr_ok = tk.Checkbutton(self, text = "cliquez ici lorsque la rue d'arrivée est entrée")
        self.rue_arr_ok.grid(row=4, column = 1, padx=10, pady=5)
        self.rue_arr_ok.bind('<Button-1>', self.rue_arrivee)

        self.trajet_type_label = ttk.Label(self, text="Type de trajet :")
        self.trajet_type_label.grid(row=6, column=0, padx=10, pady=5)

        self.trajet_type = tk.StringVar()

        self.trajet_court_radio = ttk.Radiobutton(self, text="Trajet court", variable=self.trajet_type, value="court")
        self.trajet_court_radio.grid(row=6, column=1, padx=10, pady=5, sticky="w")

        self.trajet_rapide_radio = ttk.Radiobutton(self, text="Trajet rapide", variable=self.trajet_type, value="rapide")
        self.trajet_rapide_radio.grid(row=7, column=1, padx=10, pady=5, sticky="w")

        self.trajet_ecologique_radio = ttk.Radiobutton(self, text="Trajet écologique", variable=self.trajet_type, value="ecologique")
        self.trajet_ecologique_radio.grid(row=8, column=1, padx=10, pady=5, sticky="w")

        self.ajouts = ttk.Label(self, text="D'autres spécificités ?")
        self.ajouts.grid(row=9, column=0, padx=10, pady=5)

        self.tunnels_var = tk.BooleanVar()
        self.tunnels = ttk.Checkbutton(self, text='Voulez-vous éviter les tunnels ?', variable=self.tunnels_var)
        self.tunnels.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        self.radars_var = tk.BooleanVar()
        self.radars = ttk.Checkbutton(self, text='Voulez-vous éviter les radars ?', variable=self.radars_var)
        self.radars.grid(row=10, column=1, padx=10, pady=5, sticky="w")

        self.traffic_var = tk.BooleanVar()
        self.traffic = ttk.Checkbutton(self, text='Voulez-vous éviter le traffic ?', variable=self.traffic_var)
        self.traffic.grid(row=11, column=1, padx=10, pady=5, sticky="w")

        self.depasser_limite_checkbutton_var = tk.BooleanVar()
        self.depasser_limite_checkbutton_var.set(False)
        self.depasser_limite_checkbutton = ttk.Checkbutton(self, text="Dépasser la limite de vitesse ?", variable=self.depasser_limite_checkbutton_var)
        self.depasser_limite_checkbutton.grid(row=12, column=1, pady=10, padx=5, sticky="w")
        self.depasser_limite_checkbutton.bind('<Button-1>', self.rahh)

        self.submit_button = tk.Button(self, text="Valider", command=self.valider_trajet, activebackground = 'deeppink2')
        self.submit_button.grid(row=15, columnspan=2, padx=10, pady=10)
        self.submit_button.bind('<Button-1>', self.crea_carte)
        
        self.bind("<Configure>", self.on_window_resize)
        
    def on_window_resize(self, event):
        print("redim")
        width = event.width
        height = event.height
        image_redimensionnee = self.image.resize((width,height))
        self.background_image = ImageTk.PhotoImage(image_redimensionnee)
        self.background_label.configure(image=self.background_image)

        
    def rahh(self, event):
        self.rahyan_var = tk.BooleanVar()
        self.rahyan_var.set(False)
        self.rahyan_button = ttk.Checkbutton(self, text="Vous voulez aller plus vite que Rahyan ?", variable=self.rahyan_var)
        self.rahyan_button.grid(row=13, column=1, pady=10, padx=5, sticky="w")
        self.rahyan_button.bind('<Button-1>', self.entree)

    def entree(self, event):
        if self.rahyan_var.get():
            if hasattr(self, 'entree_entry'):
                self.entree_entry.destroy()
                del self.entree_entry
        else:
            if not hasattr(self, 'entree_entry'):
                self.entree_text = "de combien de km/h ?"
                self.kmh = tk.StringVar()
                self.entree_entry = tk.Entry(self, textvariable=self.kmh)
                self.entree_entry.insert(0, self.entree_text)
                self.entree_entry.bind("<FocusIn>", self.clear_entry)
                self.entree_entry.bind("<FocusOut>", self.restore_text)
                self.entree_entry.grid(row=14, column=1, pady=10, padx=5, sticky="w")
    
    def rue_depart(self,event):
        if self.ruedep.get() in self.dico_num_rue.keys():
            numeros = self.dico_num_rue[self.ruedep.get()]
            self.depart_combobox = ttk.Combobox(self, values=numeros)
            self.depart_combobox.grid(row=2, column=1, padx=10, pady=5)
        else:
            self.entree_rue = "Ceci n'est pas le nom d'une rue !"
            self.pasbonnerue = tk.Label(self, text = "Ceci n'est pas le nom d'une rue !")
            self.pasbonnerue.grid(row=2, column = 1, padx=10, pady=5)
        
    def rue_arrivee(self,event):
        if self.ruearrivee.get() in self.dico_num_rue.keys():
            numeros = self.dico_num_rue[self.ruearrivee.get()]
            self.arrivee_combobox = ttk.Combobox(self, values=numeros)
            self.arrivee_combobox.grid(row=5, column=1, padx=10, pady=5)
        else:
            self.entree_rue = "Ceci n'est pas le nom d'une rue !"
            self.pasbonnerue = tk.Label(self, text = "Ceci n'est pas le nom d'une rue !")
            self.pasbonnerue.grid(row=5, column = 1, padx=10, pady=5)
    
    def clear_entry(self, event):
        if self.entree_entry.get() == self.entree_text:
            self.entree_entry.delete(0, tk.END)

    def restore_text(self, event):
        if not self.entree_entry.get():
            self.entree_entry.insert(0, self.entree_text)
            
    def valider_trajet(self):
        rue_depart = self.ruedep.get()
        num_depart = self.depart_combobox.get()
        rue_arrivee = self.ruearrivee.get()
        num_arrivee = self.arrivee_combobox.get()
        type_trajet = self.trajet_type.get()
        eviter_peages = self.tunnels_var.get()
        eviter_radars = self.radars_var.get()
        eviter_traffic = self.traffic_var.get()
        if self.depasser_limite_checkbutton_var.get():
            kmsup = self.entree_entry.get()
        else:
            kmsup = "0"
        print("rue de départ :", rue_depart)
        print(f"numéro de départ :", num_depart)
        print("Ville d'arrivée :", rue_arrivee)
        print(f"numéro d'arrivée' :", num_arrivee)
        print("Type de trajet :", type_trajet)
        print("Eviter les péages :", eviter_peages)
        print("Eviter les radars :", eviter_radars)
        print("Eviter le traffic :", eviter_traffic)
        print("km/h en plus de la limite :", kmsup)
        # Vous pouvez stocker ces valeurs ou les utiliser comme vous le souhaitez
            

    def crea_carte(self, event):
        dep = self.ruedep.get()
        arr = self.ruearrivee.get()
        if self.trajet_type.get() == 'court':
            metrique = 'distance'
        elif self.trajet_type.get() == 'rapide':
            metrique = 'temps'
        listes_rues = dijkstra_rues(graphe_final, dep , arr , metrique)
        cree_map(listes_rues)

    

if __name__ == "__main__":
    Trajet = TrajetApp()
    Trajet.mainloop()

