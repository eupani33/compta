#!/usr/bin/env python3
import csv
import os
import sqlite3
from sqlite3 import Error
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Treeview

from dictionnaire import *


class GestionBD(object):
    def __init__(self):
        try:
            self.connexion = sqlite3.connect(database)
        except Error as e:
            print(e)
        else:
            self.cursor = self.connexion.cursor()
            # uniquement pour les tests
            # self.creer_tables()

    def creer_tables(self):
        for table in dicoTables:
            req = "CREATE TABLE %s" % table
            pk = ''
            for descr in dicoTables[table]:
                req = req + descr
            self.executerReq(req)
            self.create_donnees()

    def create_donnees(self):
        for donnee in dicoLocaux:
            req = "INSERT INTO local(id_local, local) VALUES(?,?)"
            self.executerReq(req, donnee)
        for donnee in dicoCategories:
            req = "INSERT INTO categories(id_categories, categorie, sous_categorie, parent_id) VALUES(?,?,?,?)"
            self.executerReq(req, donnee)

    def maj_categories(self):

        for donnee in dicoAssocies:
            req = "UPDATE ecritures SET id_categories = ? WHERE  libelle = ?"
            self.executerReq(req, donnee)

        for donnee in dicoLocataires:
            req = "UPDATE ecritures SET id_local = ?, id_categories = 4 WHERE  libelle = ? "
            self.executerReq(req, donnee)

        for donnee in dicoSyndicats:
            req = "UPDATE ecritures SET id_categories = ?, id_local = ? WHERE  libelle = ? "
            self.executerReq(req, donnee)

        for donnee in dicoFournisseurs:
            req = "UPDATE ecritures SET id_categories = ? WHERE  libelle = ? "
            self.executerReq(req, donnee)

        for donnee in dicoType:
            req = "UPDATE ecritures SET type = ? WHERE type = ? "
            self.executerReq(req, donnee)
        req = "DELETE FROM ecritures  WHERE date LIKE '%Compte%'"
        self.executerReq(req)

    def executerReq(self, req, param=None):

        try:
            if param:
                valeurs = self.cursor.execute(req, param)
            else:
                valeurs = self.cursor.execute(req)
        except Exception as e:
            print(e)
        else:
            self.connexion.commit()
            return valeurs

    def lecture_fichier(self):
        fichier = askopenfilename()
        file = open(fichier, "r", encoding="ISO-8859-1")
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            for cle, valeur in dicoEcritures.items():
                if cle in row[1]:
                    row[1] = valeur
                if cle in row[3]:
                    row[3] = valeur
            param = [row[0], row[1], row[3], row[5]]
            req = "INSERT INTO ecritures (date, type, libelle, montant) VALUES(?, ?,?,?) "
            self.executerReq(req, param)
        file.close()
        self.maj_categories()

    def liste_Treeview(self):
        #req = "SELECT * FROM ecritures e , categories c, local l WHERE e.id_categories = c.id_categories AND e.id_local = l.id_local AND e.date"
        req = "SELECT * FROM ecritures e , categories c, local l WHERE e.id_categories = c.id_categories AND e.id_local = l.id_local AND e.date LIKE '%/01/2021'"
        self.cursor = self.executerReq(req)
        return self.cursor


class Fenetre_MAJ(Toplevel):
    def __init__(self, **Arguments):
        Toplevel.__init__(self, **Arguments)
        self.geometry("250x200+100+240")


class Application(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.fdonnee = GestionBD()
        self.message = StringVar

        icones = ('icons5', 'icons6', 'icons8', 'icons4', 'icons1')
        actions = ('import', 'export', 'liste', 'transfert', 'quit')

        nbBoutons = len(icones)
        self.icones = [None]*nbBoutons
        self.arg = [None]*nbBoutons

        self.winfo_toplevel().title("Simple Programme")

        self.barOut = Frame()
        for b in range(nbBoutons):
            self.icones[b] = PhotoImage(
                file=os.path.join("icons", icones[b]+'.gif'))
            self.arg[b] = actions[b]
            self.bouton = Button(
                self.barOut, image=self.icones[b], command=lambda arg=actions[b]: self.action(arg))
            self.bouton.grid(row=0, column=b, padx=5, pady=5)
        self.barOut.pack(expand=YES, fill=X)

        self.frame_message = Frame(self, width=400, height=50, bg="ivory")
        self.information = Label(
            self.frame_message, text="clic sur la ligne du tableau", font=14, bg='red')
        self.information.pack()
        self.frame_message.pack(side=TOP)
        self.travail = Frame(self, width=800, height=1200, bg='lightgrey')
        self.tableau = Treeview(self.travail, height=40, columns=(
            'date',  'type', 'libelle', 'montant', 'categorie', 'local'))
        self.tableau.tag_bind(self, '<Button-2>', self.toto())
        self.tableau.heading('date', text='date')
        self.tableau.heading('type', text='Type')
        self.tableau.heading('libelle', text='Libelle')
        self.tableau.heading('montant', text='Montant')
        self.tableau.heading('categorie', text='Catégorie')
        self.tableau.heading('local', text='Local')
        self.tableau.column('date', width=90, anchor=E)
        self.tableau.column('type', width=120, anchor=E)
        self.tableau.column('libelle', width=200, anchor=E)
        self.tableau.column('montant', width=120, anchor=E)
        self.tableau.column('categorie', width=120, anchor=E)
        self.tableau.column('local', width=120, anchor=E)
        self.refresh()
        self.tableau['show'] = 'headings'
        self.tableau.pack()
        self.travail.pack()
        self.pack()

    def action(self, arg):
        if arg == 'import':
            self.fdonnee.lecture_fichier()
            self.refresh()
            return
        if arg == 'export':
            return
        if arg == 'liste':
            return
        if arg == 'transfert':
            self.fdonnees.maj_categories()
            self.refresh()
            return
        if arg == 'quit':
            exit()

    def refresh(self):
        self.cursor = self.fdonnee.liste_Treeview()
        for enreg in self.cursor:
            self.tableau.insert('', 'end', iid=enreg[0], values=(
                enreg[1], enreg[2], enreg[3], enreg[4], enreg[10], enreg[13]), tags=('selection',))

    def toto(event):
        print(event)


if __name__ == "__main__":
    database = mes_variables["sgbd"]
    Application().mainloop()
