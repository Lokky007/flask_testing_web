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
import os
from datetime import datetime

md_ext1 = ['markdown.extensions.extra',
           'work_syntax_admin:WorkSyntax']

md_ext2 = ['markdown.extensions.extra',
           'work_syntax_user:WorkSyntax']

app = Flask(__name__)
app.secret_key = urandom(24)

def Login_required_for_admin(test):
    @wraps(test)
    def wrap(*arg, **kwargs):
        if "logged_in" in session and "access" in session:
            return test(*arg, **kwargs)
        else:
            flash("Nedostatečná práva...")
            return redirect("/index")
    return wrap

def Login_required_for_user(test):
    @wraps(test)
    def wrap(*arg, **kwargs):
        if "logged_in" in session:
            return test(*arg, **kwargs)
        else:
            flash("Nejdriv se prihlas...")
            return redirect("/index")
    return wrap

@app.route("/")
def get_welcome():
    return redirect("index")

@app.route("/index", methods=["POST", "GET"])
def try_login_pass():
    if request.method == "POST":
        password = request.form["password"]
        Login = request.form["name"]

        if Login == "user" and password == "user":
            print ("prihlasen Uživatel")
            session["user"] = Login
            session["logged_in"] = True
            return redirect("Main_user")

        elif Login == "admin" and password == "aaaa":
            print ("prihlášen Admin")
            session["user"] = Login
            session["access"] = True
            session["logged_in"] = True
            return redirect("Main_admin")

        else:
            flash("Neplatny Login nebo Heslo")
    return render_template("index.html")

@app.route("/LogOut")
def logOut():
    session.pop("logged_in", None)
    session.pop("access", None)
    flash("Byl jste odhlasen")
    return redirect("index")

@app.route("/Main_admin")
@Login_required_for_admin
def main_page_for_admin():
    return render_template("Basic_template.html")

@app.route("/Main_user")
@Login_required_for_user
def Main_page_for_user():
    list_works = []
    list_dir = []

    for (root, dirs, files) in walk('works'):
        for dir in dirs:
            for file in os.listdir("works/%s" % dir):
                if file.endswith(".txt"):
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

                    date_start = date_od.strftime("%Y-%m-%d %H:%M")
                    date_end = date_do.strftime("%Y-%m-%d %H:%M")
                    now = datetime.now()
                    print (file)
                    print ("start", date_start)
                    print ("-DNES", now)
                    print ("konec", date_end)
                    if (date_od < now < date_do) is True:
                        list_dir.append(dec)
                        list_works.append(file)

                    fil.close()
    print (list_works)
    print (list_dir)
    return render_template("basic_user_list.html", list_works=list_works,
                           list_dir=list_dir)

@app.route("/Main_user/<base>/<name_user_dir>/<name_user_file>")
@Login_required_for_user
def Work_user(base, name_user_dir, name_user_file):
    print (name_user_dir)
    print (name_user_file)
    if request.method == "POST":
        print(request.form["number"])
        print(request.form["choice"])
        print(request.form["text"])

    view_work = codecs.open("%s/%s/%s" % (base, name_user_dir, name_user_file),
                            'r', 'utf-8')
    view_work = markdown.markdown(view_work.read(), md_ext2)
    return render_template('work_user.html', work=view_work)

@app.route("/Entering", methods=["POST", "GET"])
@Login_required_for_admin
def list_of_works():
    list_of_dirs = []

    for (root, dirs, files) in walk('works'):
        list_of_dirs = list_of_dirs+dirs

    return render_template("Entering.html", list_of_dirs=list_of_dirs)


@app.route("/Entering/<path:name_of_work>", methods=["POST", "GET"])
@Login_required_for_admin
def open_class(name_of_work):
    list_of_files = []

    for (root, dirs, files) in walk('works/%s' % name_of_work):
        list_of_files = files

    return render_template("Entering.html", name_of_work=name_of_work,
                           list_of_files=list_of_files)

@app.route("/Entering/<name_of_work>/<path:name_of_files>",
           methods=["POST", "GET"])
@Login_required_for_admin
def open_file(name_of_work, name_of_files):
    if request.method == "POST":
        print(request.form["number"])
        print(request.form["choice"])
        print(request.form["text"])

    view_work = codecs.open("works/%s/%s" % (name_of_work, name_of_files), 'r',
                            'utf-8')
    view_work = markdown.markdown(view_work.read(), md_ext1)
    return render_template('work.html', work=view_work)

app.run(debug=True)