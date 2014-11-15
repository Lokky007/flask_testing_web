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

md_ext = ['markdown.extensions.extra',
          'work_syntax:WorkSyntax'
          ]

app = Flask(__name__)
app.secret_key = urandom(24)

def Login_required(test):
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
        if (request.form["name"] == "admin" and
           request.form["password"] == "aaaa"):

                session["logged_in"] = True
                return redirect("Main_page")
        else:
            flash("Neplatny login nebo heslo")
    return render_template("index.html")

@app.route("/LogOut")
def logOut():
    session.pop("logged_in", None)
    flash("Byl jste odhlasen")
    return redirect("index")


@app.route("/Main_page")
@Login_required
def main_page_for_admin():
    return render_template("Basic_template.html")

@app.route("/Entering", methods=["POST", "GET"])
@Login_required
def list_of_works():
    list_of_dirs = []

    for (root, dirs, files) in walk('works'):
        list_of_dirs = list_of_dirs+dirs

    return render_template("Entering.html", list_of_dirs=list_of_dirs)


@app.route("/Entering/<path:name_of_work>", methods=["POST", "GET"])
@Login_required
def open_class(name_of_work):
    list_of_files = []

    for (root, dirs, files) in walk('works/%s' % name_of_work):
        list_of_files = files

    return render_template("Entering.html", name_of_work=name_of_work,
                           list_of_files=list_of_files)

@app.route("/Entering/<name_of_work>/<path:name_of_files>")
#@Login_required
def open_file(name_of_work, name_of_files):
    view_work = codecs.open("works/%s/%s" % (name_of_work, name_of_files), 'r',
                            'utf-8')
    view_work = markdown.markdown(view_work.read(), md_ext)
    return render_template('work.html', work=view_work)

app.run(debug=True)
