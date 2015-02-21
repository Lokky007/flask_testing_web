# -*- coding: utf8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators

from flask import Flask, redirect, render_template, request, session, flash
from functools import wraps
from os import walk, urandom

import markdown
import codecs
import os, random
import psycopg2
import database
from datetime import datetime, time
from pony.orm import *
from database import Student, Akce, Test, Otazka_testu, Otazka, Odpoved,\
    Vysledek_testu

md_ext1 = ['markdown.extensions.extra',
           'work_syntax_admin:WorkSyntax']

md_ext2 = ['markdown.extensions.extra',
           'work_syntax_user:WorkSyntax']


app = Flask(__name__)
app.secret_key = urandom(24)

db = Database("postgres", host="localhost", user="postgres",
              password="postgres", database="test")



def Login_required_for_admin(test):
    """Testování přihlašení admina
    """
    @wraps(test)
    def wrap(*arg, **kwargs):
        if "admin" in session['user']:
            return test(*arg, **kwargs)
        else:
            flash("Nedostatečná práva... Byl jste odhlasen!")
            return redirect("/index")
    return wrap

def Login_required_for_user(test):
    """Testování přihlášení klasického uživatele
    """
    @wraps(test)
    def wrap(*arg, **kwargs):
        if "user" in session and "admin" not in session['user']:
            return test(*arg, **kwargs)
        else:
            flash("Nejdriv se prihlas...")
            return redirect("/index")
    return wrap

@app.route("/")
def get_welcome():
    """přesměrování na indexovou stránku
    """
    return redirect("index")

@app.route("/index", methods=["POST", "GET"])
@db_session
def try_login_pass():
    """indexová stránka s přihlášenim + kontrola přihlašovacích údajů
    """
    if request.method == "POST":
        password = request.form["password"]
        Login = request.form["name"]

        if ((Login == "user" and password == "user") or
            (Login == "doc32301" and password == "32301")): # pevně statovení studenti(pro test)
            print ("prihlasen Uživatel")
            session["user"] = Login
            ###DOČASNÉ!!! Vytvoření studenta v databázi, pokud tam již není
            if not exists(o for o in Student if o.login is Login):
                Student(login=Login, jmeno="adm", prijmeni="Das",
                        hash="13213156")
            i = datetime.now()
            p1 = select(o for o in Student if o.login is Login).get()
            Akce(cas=i.strftime('%Y/%m/%d %H:%M:%S'),
                 student=p1)
            select(c for c in Student).show()
            select(c for c in Akce).show()
            return redirect("Main_user")

        elif Login == "admin" and password == "aaaa": # pevně stanovená admin(pro test)
            print ("prihlášen Admin")
            session["user"] = Login
            ### DOČASNÉ!!! Vytvoření admina v databázi, pokud tam již není
            if not exists(o for o in Student if o.login is Login):
                Student(login=Login, jmeno="adasm", prijmeni="Das",
                        hash="13213156")
            i = datetime.now()
            p2 = select(o for o in Student if o.login is Login).get()
            print (p2)
            Akce(cas=i.strftime('%Y/%m/%d %H:%M:%S'), student=p2)
            select(c for c in Student).show()
            select(c for c in Akce).show()
            return redirect("Main_admin")

        else:
            flash("Neplatny Login nebo Heslo")
    citat = (random.choice(codecs.open("static/citaty.txt", 'r', 'UTF-8').readlines())).split('//')
    return render_template("index.html", citat=citat)

@app.route("/LogOut")
def logOut():
    """Odhlášení přihlášeného
    """
    flash("Byl jste odhlasen")

    ########################### Návrh zápisu odhlášení do databáze ###################
    #Login = session["user"]
    #i = datetime.now()
    #p1 = select(o for o in Student if o.login is Login).get()
    #Akce(cas=i.strftime('%Y/%m/%d %H:%M:%S'), student=p1")

    session.pop("logged_in", None)
    session.pop("access", None)
    return redirect("index")

@app.route("/Main_admin")
@Login_required_for_admin
def main_page_for_admin():
    """Hlavní stranka pro admina
    """
    return render_template("Basic_template.html")

@app.route("/Main_user")
@Login_required_for_user
def Main_page_for_user():
    """hlavni stranka pro obyč. uživatele. Vypsání dostupných testů 
       dle hlavičky dokumentu
    """
    list_works = []
    list_dir = []

    for (root, dirs, files) in walk('works'):
        for dir in dirs: #  otevře podložky ve složce /works
            for file in os.listdir("works/%s" % dir): #  čte soubory ve složce
                if file.endswith(".txt"): #  kontroluje koncovku souboru.
                                          #  POZOR! Pokud není soubor uložen pod koncovkou .txt
                                          #         nedojde ke kontrole a nevyobrazí se ani 
                                          #         pokud splňuje podmínku
                    dec = "works/%s/%s" % (dir, file)
                    fil = open(dec, "r")
                    f = fil.readline()
                    tag, datum_od, cas_od, datum_do, cas_do = f.split()

                    den_start, mesic_start, rok_start = datum_od.split(".")
                    hod_start, min_start = cas_od.split(":")

                    den_konec, mesic_konec, rok_konec = datum_do.split(".")
                    hod_konec, min_konec = cas_do.split(":")


                    date_od = datetime(int(rok_start), int(mesic_start),
                                       int(den_start), int(hod_start),
                                       int(min_start))

                    date_do = datetime(int(rok_konec), int(mesic_konec),
                                       int(den_konec), int(hod_konec),
                                       int(min_konec))

                    now = datetime.now()

                    if (date_od < now < date_do) is True: #  jestli je v rozmezi datumu platosti
                        list_dir.append(dec)              #  tak se zobrazí
                        list_works.append(file)
                    fil.close()
    return render_template("basic_user_list.html", list_works=list_works,
                           list_dir=list_dir)

@app.route("/Main_user/<base>/<name_user_dir>/<name_user_file>",
           methods=["POST", "GET"])
@Login_required_for_user
@db_session
def Work_user(base, name_user_dir, name_user_file):
    """Otevření zvoleného testu + vyobrazeni podle markdownu
       Přijímá a zaznamenává volbu uživatele u otázek
    """
    if request.method == 'POST':
        print (name_user_file)
        Login = session["user"]
        i = datetime.now()
        cela_otazka = ""
        text = ""
        check = open('works/%s/%s' % (name_user_dir, name_user_file), 'r')
        p1 = select(o for o in Student if o.login is Login).get()
        Akce(cas=i.strftime('%Y/%m/%d %H:%M:%S'), student=p1)

        i = 0
        for line in check.readlines():
            line = line.decode('utf-8')
            if line != "\n" and line != "\r\n":
                for l in line:
                    if l != ":":
                        cela_otazka = cela_otazka + line
                        break
                    elif l == ":":
                        if cela_otazka != "":
                            i += 1
                            text = request.form.get("%i" % i, "Nevyplneno")
                            p4 = select(o for o in Test if o.id is 2).get()
                            if not exists(o for o in Vysledek_testu if o.student is p1 and o.test is p4):
                                Vysledek_testu(student=p1, test=p4)
                            p2 = select(o for o in Otazka if o.text is cela_otazka).get()
                            p3 = select(o for o in Vysledek_testu if o.test is p4).get()
                            print ("cela otazka", cela_otazka)
                            print ("Volba", text, "\n------------------------")
                            print ("\n P1ka je", p1)
                            print ("\n P2ka je", p2)
                            print ("\n P3ka je", p3)
                            print ("\n P4ka je", p4)
                            Odpoved(otazka=p2, text=text, vysledky_testu=p3)
                            cela_otazka = ""
                        break

    view_work = codecs.open("%s/%s/%s" % (base, name_user_dir, name_user_file),
                            'r', 'utf-8')
    view_work = markdown.markdown(view_work.read(), md_ext2)
    return render_template('work_user.html', work=view_work)

@app.route("/Entering", methods=["POST", "GET"])
@Login_required_for_admin
def list_of_works():
    """Zobrazení všech složek tříd
    """
    list_of_dirs = []

    for (root, dirs, files) in walk('works'):
        list_of_dirs = list_of_dirs+dirs

    return render_template("Entering.html", list_of_dirs=list_of_dirs)


@app.route("/Entering/<path:name_of_work>", methods=["POST", "GET"])
@Login_required_for_admin
def open_class(name_of_work):
    """Zobrazení uložených testů ve zvolené složce třídy
    """
    list_of_files = []

    for (root, dirs, files) in walk('works/%s' % name_of_work):
        list_of_files = files

    return render_template("Entering.html", name_of_work=name_of_work,
                           list_of_files=list_of_files)

@app.route("/Entering/<name_of_work>/<path:name_of_files>",
           methods=["POST", "GET"])
@Login_required_for_admin
def open_file(name_of_work, name_of_files):
    """Otevře vybraný text pro náhled pomocí markdownu
    """
    view_work = codecs.open("works/%s/%s" % (name_of_work, name_of_files), 'r',
                            'utf-8')
    view_work = markdown.markdown(view_work.read(), md_ext1)
    return render_template('work.html', work=view_work)

@app.route("/create", methods=["POST", "GET"])
@Login_required_for_admin
@db_session
def create_entering():
    """import nového testu přes textbox či tlačítkem
    """
    def add_database(select, name):
        """funkce pro import přes textbox
           čte každý řádek a detekuje otázku či správnou odpověd
           provede import do databáze
        """
        print("Položka %s přidána" % (name))
        check = open('works/%s/%s' % (select, name), 'r')
        line = ""
        lin = ""

        for line in check.readlines(): #  čte řádky a detekuje části testu
            print(line)
            line = line.decode('utf-8')
            if line == "\r\n":
                None
            else:
                for l in line:
                    if l != ":":
                        lin = lin + line
                        print (lin)
                        break
                    break
                if line.split()[0] == ":+":
                    linka = line.replace(":+","")
                    print ("Otazka", lin)
                    print ("spravna odpoved", linka)
                    Otazka(text=lin,
                           spravna_odpoved=linka)
                    lin = ""

                elif line.split()[0] == "::number":
                    linka = line.split()[1]
                    print ("spravna odpoved", linka)
                    Otazka(text=lin,
                           spravna_odpoved=linka)
                    lin = ""

                elif line.split()[0] == "::open":
                    print ("Otevřená otázka")
                    Otazka(text=lin,
                           spravna_odpoved="Otevřená otázka")
                    lin = ""

    if request.method == 'POST':
        name = request.form["name"]
        text = request.form["entering"]
        select = request.form["select"]
        fil = request.form["file"]

        if name and text:
            ent = codecs.open('works/%s/%s' % (select, name), 'w', "utf-8")
            ent.write(text)
            ent.close()
            add_database(select, name)
            flash("Uloženo")

        elif fil:
            flash("Soubor zapsán")
            add_database(name)

        else:
            flash("Žádná vložená data")

    list_of_dirs = [] #  položky pro listbox. Výběr složky pro import testu  
    for (root, dirs, files) in walk('works/'):
        list_of_dirs = list_of_dirs + dirs
    return render_template('create_entering.html',
                           list_dir=list_of_dirs)

app.run(debug=True)