from flask import Flask , redirect , render_template , request, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = "sad2dfhvcbsd3258"


#redirect visitors to index and load Login 
@app.route("/")
def get_welcome():
    return redirect("index")

def Login_required(test):
    @wraps(test)
    def wrap(*arg, **kwargs):
        if "logged_in" in session:
            return test(*arg, **kwargs)
        else:
            flash("Nejdriv se prihlas...")
            return redirect("/index")
    return wrap

@app.route("/index" , methods=["post","get"])
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
@Login_required
def main_page():
    return render_template("Main_page.html")
    
            

app.run(debug=True)
