# -*- coding: utf8 -*-
from flask import Flask , redirect , render_template , request, session, flash
from functools import wraps
from os import walk , urandom , listdir

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

@app.route("/index" , methods=["POST","GET"])
def try_login_pass():
    if request.method == "POST":
        if request.form["name"] != "admin" or request.form["password"] != "aaaa":
            flash("Neplatny login nebo heslo")
        else:
            session["logged_in"] = True
            return redirect ("Main_page")
    return render_template ("index.html")
 
            
@app.route("/LogOut")
def logOut():
    session.pop("logged_in", None)
    flash("Byl jste odhlasen")
    return redirect("index")
            
            
@app.route("/Main_page")
#@Login_required
def main_page_for_admin():
    return render_template("Basic_template.html")

@app.route("/Entering", methods=["POST","GET"])
#@Login_required
def list_of_works():
    list_of_works=[]
    for (root, dirs, files) in walk('works'):
        list_of_works=list_of_works+files                
    return render_template("Entering.html",list_of_works=list_of_works)

@app.route("/Entering/<name_of_work>", methods=["POST","GET"])
def work_with_object(name_of_work):
    way_to_file = "works/%s" %name_of_work
    if request.method == "POST":
        
        #Zobrazí obsah souboru Name_of_work v defaultní složce "works"
        if request.form.get("display",None) == "Zobrazit":
                view_work = open(way_to_file, 'r')
                return view_work.read()
            
        #Povolí načítání do klasických uživatelských účtů    
        elif request.form.get("post_on",None) == "Zveřejnit":
            return "zveřejni"
        
        #Čtení/zápis povolen,vypíše do textboxu a násladně přepíše soubor
        elif request.form.get("edit",None) == "Upravit":
            return "uprav"
        
        #Vymaže soubor,musí vyskočit potvrzovací tabulka
        elif request.form.get("delet",None) == "Smazat":
            return "smaž"
 
            

app.run(debug=True)
