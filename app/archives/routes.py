from clue import app
from flask import render_template, request, flash, redirect, session, url_for, jsonify
from clue.archives.model import *
import random

#from flask_paginate import Pagination, get_page_args
#from jinja2 import Template, Environment, PackageLoader, environment

enigmes = [{ 'id' : 0 , 'difficulte' : 5, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : 'reponse1', 'indice' : 'indice1'},
           { 'id' : 1 , 'difficulte' : 6, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse2", 'indice' : 'indice2'},
           { 'id' : 2 , 'difficulte' : 3, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse3", 'indice' : 'indice3'},
           { 'id' : 3 , 'difficulte' : 2, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse4", 'indice' : 'indice4'},
           { 'id' : 4 , 'difficulte' : 3, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse5", 'indice' : 'indice5'},
           { 'id' : 5 , 'difficulte' : 3, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse6", 'indice' : 'indice6'},
           { 'id' : 6 , 'difficulte' : 3, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse7", 'indice' : 'indice7'},
           { 'id' : 7 , 'difficulte' : 3, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse8", 'indice' : 'indice8'},
           { 'id' : 8 , 'difficulte' : 3, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse9", 'indice' : 'indice9'},
           { 'id' : 9 , 'difficulte' : 1, 'question' : "Quelle est la réponse à cette question ? ", 'solution' : "reponse10", 'indice' : 'indice10'}]

userPass = "motdepasse"
app.secret_key = "me5GjOLMAQDzFBijhZ9NosTNlkS0J5SH"

@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")
@app.route('/connexion', methods=["GET", "POST"])
def connexion():

    form = LoginForm()
    print("THIS IS OK 0")
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful", "success")
                print("THIS IS OK 1")
                return redirect(url_for("profil"))
            else:
                print("THIS IS OK 2")
                flash("Wrong password", "warning")
        else:
            print("THIS IS OK 3")
            flash("That user does not exists!", "danger")

    return render_template("connexion.html", form = form)

@app.route('/deconnexion', methods=["GET", "POST"])
@login_required
def deconnexion():
    logout_user()
    flash("You have been disconnected!", 'success')
    return redirect(url_for("connexion"))
    #if request.method == "POST":
     #   session.clear()
      #  return render_template("connexion_old.html")
    #else:
     #   return render_template("deconnexion.html")

@app.route('/construction', methods=["GET", "POST"])
def construction():
    return render_template("construction.html")

@app.route('/jouer', methods=["GET","POST"])
def jouer():


    valid_ids = [enigma.id for enigma in Clues.query.with_entities(Clues.id).all()]

    if 'current_enigma_id' in session:
        index = session['current_enigma_id']
    else:
        session['current_enigma_id'] = random.choice(valid_ids)
        index = session['current_enigma_id']


    if request.method == "POST":
        if "change_clue_up" in request.form:
            if session['current_enigma_id'] < len(valid_ids):
                session['current_enigma_id'] += 1
            else:
                session['current_enigma_id'] = 1
            index = session['current_enigma_id']

        if "change_clue_down" in request.form:
            if session['current_enigma_id'] >= 2:
                session['current_enigma_id'] -= 1
            else:
                session['current_enigma_id'] = len(valid_ids)

            index = session['current_enigma_id']

        elif "submit_answer" in request.form:
            reponse = str(request.form['reponse'])
            current_enigma = Clues.query.get(index)
            solution = current_enigma.solution

            if reponse.lower() == solution:
                session['correct_answer'] = True
                #flash("Bien joué !", "success")
                #session['current_enigma_id'] = randint(0, len(enigmes) - 1)
                return redirect(url_for("liste"))
            else:
                flash("Mauvaise réponse, réessayez !", "danger")


    current_enigma = Clues.query.get(index)
    return render_template("jouer.html", enigme=current_enigma)

@app.route('/liste',methods=["GET", "POST"])
@login_required
def liste():

    perpage = 5
    page = request.args.get('page', session.get('current_page', 1), type=int)
    start = (page - 1) * perpage
    total_clues = Clues.query.count()
    clues = Clues.query.offset(start).limit(perpage).all()



    if request.method == "POST":
        enigmaID = int(request.form['id'])
        action = request.form.get('action')
        clue = Clues.query.get(enigmaID)

    total_pages = (total_clues + perpage - 1) // perpage
    page_enigmas = clues
    session['current_page'] = page

    return render_template("liste.html", liste=page_enigmas, page=page, total_pages=total_pages)

# ROUTE USE TO CALL THE INCREMENT DIFFICULTY FUNCTIONS
@app.route('/increment_difficulty', methods=["POST"])
def increment_difficulty():
    enigmaID = int(request.form['id'])
    clue = Clues.query.get(enigmaID)

    if clue:
        if clue.difficulty < 10:
            clue.difficulty += 1
            try:
                db.session.commit()
                return str(clue.difficulty)
            except Exception as e:
                db.session.rollback()
                return 'Error updating difficulty'
        else:
            return 'Niveau max!'
    else:
        return 'Clue not found'

# ROUTE USE TO CALL THE INCREMENT DIFFICULTY FUNCTIONS
@app.route('/decrement_difficulty', methods=["POST"])
def decrement_difficulty():
    enigmaID = int(request.form['id'])
    clue = Clues.query.get(enigmaID)

    if clue:
        if clue.difficulty >= 1:
            clue.difficulty -= 1
            try:
                db.session.commit()
                return str(clue.difficulty)
            except Exception as e:
                db.session.rollback()
                return 'Error updating difficulty'
        else:
            return 'Niveau min!'
    else:
        return 'Clue not found'



@app.route('/ajouter', methods=["GET","POST"])
def ajouter():

    global enigmes

    if request.method =="POST":

        enigme = request.form['enigme']
        solution = request.form['solution']
        indice = request.form['indice']
        difficulte = str(request.form['difficulte'])

        new_enigma = Clues(
            difficulty = difficulte,
            question = enigme,
            solution = solution,
            hint = indice
        )

        try:
            db.session.add(new_enigma)
            db.session.commit()
            flash("Clue added successfully ! ")
            return redirect(url_for("liste"))
        except Exception as e:
            db.session.rollback()
            flash("Error adding clue to the data !", 'error')

    return render_template("ajouter.html")

@app.route('/ajouternew', methods=["GET","POST"])
def ajouternew():

    form = ClueForm()

    question = None
    solution = None
    hint = None
    difficulty = None


    if form.validate_on_submit():
        question = form.question.data
        solution = form.solution.data
        hint = form.hint.data
        difficulty = form.difficulty.data

        new_enigma = Clues(
            difficulty = difficulty,
            question = question,
            solution = solution,
            hint = hint
        )

        try:
            db.session.add(new_enigma)
            db.session.commit()
            flash("Clue added successfully ! ")
            return redirect(url_for("liste"))
        except Exception as e:
            db.session.rollback()
            flash("Error adding clue to the data !", 'error')

        #form.question.data = ''
        #form.solution.data = ''
        #form.hint.data = ''
        #form.difficulty.data = None

    return render_template("ajouternew.html", form = form)



@app.route('/modifier', methods=["GET", "POST"])
def modifier():

    index = request.args.get('id', type=int)
    clue = Clues.query.get(index)

    page = request.args.get('page', type=int)

    if request.method == "POST":
        clue.solution = request.form.get('solution')
        clue.hint = request.form.get('indice')
        clue.difficulty = request.form.get('difficulte')
        clue.question = request.form.get('enigme')

        try:
            db.session.commit()
            flash('Clue updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating clue', 'danger')

        return redirect(url_for('modifier'))

    return render_template("modifier.html", enigme = clue)


@app.route('/supprimer', methods=["POST"])
def supprimer():

    index = request.form.get('id', type=int)

    enigma = Clues.query.get(index)

    try:
        db.session.delete(enigma)
        db.session.commit()
        flash('Clue deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting the clue !', 'warning')

    return redirect(url_for("liste"))

@app.route('/delete_user', methods=["GET", "POST"])
def delete_user():
    try:
        user_id = request.json['id']
        user = User.query.get(user_id)

        if user:
            db.session.delete(user)
            db.session.commit()
            users = User.query.order_by(User.date_added)
            return render_template("userlist.html", users=users)
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error deleting user'}), 500

@app.route('/profil', methods=["GET", "POST"])
@login_required
def profil():
    return render_template("profil.html")

@app.route('/page_not_found')
def page_not_found():
    requested_path = request.path
    return render_template("404.html", requested=requested_path)

@app.route('/infos')
def infos():
    return render_template("infos.html")

@app.route('/add_users', methods=["GET", "POST"])
def add_users():

    print("add_users route hit")
    form = UserForm()

    username = None
    email = None
    password_hash = None
    password_hash2 = None
    privileges = None

    print("add_users route hit2")

    if form.validate_on_submit():
        print("add_users route hit3")

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            privileges=form.privileges.data
        )
        new_user.password = form.password.data  # Use the setter

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User added successfully ! ")
            return redirect(url_for("userlist"))
        except Exception as e:
            db.session.rollback()
            flash("Error adding user to the data !", 'error')

    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f"Error in {fieldName}: {err}")

    return render_template("add_users.html", form = form)



@app.route('/userlist', methods =["GET", "POST"])
def userlist():
    users = User.query.order_by(User.date_added)

    return render_template("userlist.html", users = users)

@app.route('/modifier_user', methods=["GET", "POST"])
def modifier_user():

    if request.method == "POST":
        user_id = request.form.get('user_id', type=int)
    else:
        user_id = request.args.get('id', type=int)

    user = User.query.get(user_id) if user_id else None
    print("user id => " + str(user_id))
    old_password = request.form.get('oldPassword')

    Userform = UserForm(obj=user)

    if request.method == 'GET' and user_id:
        user = User.query.get(user_id)
        if user:
            Userform.username.data = user.username
            Userform.email.data = user.email
            Userform.privileges.data = user.privileges

    if Userform.validate_on_submit():
        username = Userform.username.data
        email = Userform.email.data
        privileges = Userform.privileges.data

        if check_password_hash(user.password_hash, old_password):
            user.password = generate_password_hash(Userform.password.data)
            user.email = Userform.email.data
            user.privileges = Userform.privileges.data

            if Userform.password.data:
                user.password = Userform.password.data

            try:
                db.session.commit()
                flash("User details modified successfully ! ", 'success')
                return redirect(url_for("userlist"))
            except Exception as e:
                db.session.rollback()
                flash("Error modifying user to the data !", 'error')

        else:
            flash("Password is not correct!", 'warning')
            return render_template("modifier_user.html", user_id=user_id, form = Userform)

    return render_template("modifier_user.html", user_id=user_id, form = Userform)

@app.route("/502", methods = ["GET"])
def badGateway():
    return render_template("502.html")


@app.errorhandler(404)
def page_not_found(e):
    requested_path = request.path

    return render_template("404.html", requested = requested_path)



