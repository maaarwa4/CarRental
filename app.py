from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson import ObjectId
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from bson import ObjectId
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta  # Ajoutez timedelta ici
import re




app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'votre.email@gmail.com'
app.config['MAIL_PASSWORD'] = 'votre_mot_de_passe'
mail = Mail(app)

app.secret_key = 'secret_key'

UPLOAD_FOLDER = 'BD/static/uploads'  # Dossier pour sauvegarder les images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.voiture_db
users_collection = db['users']
managers_collection = db['managers']

##############login et logout####################

@app.route("/")
def landing():
    cars = list(db.cars.find())
    return render_template('landing.html', cars=cars)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users_collection.find_one({'email': email})
        if user and 'password' in user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])
            session['role'] = user.get('role', '')
            flash('Connexion réussie', 'success')
            if user.get('role') == 'manager':
                return redirect(url_for('manager_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Email ou mot de passe incorrect', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('landing'))

############login et logout ###############




############ Dashboard Admin  ###########

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))


    stats = {
        'total_managers': db.users.count_documents({ 'role': 'manager'}),
        'total_client': db.users.count_documents({'role': 'client'}),
        'total_reservations': db.reservations.count_documents({}),
        'total_cars': db.cars.count_documents({})
    }

    return render_template(
        'admin_dashboard.html',
        stats=stats
    )
    
# Liste des Managers
@app.route('/managers')
def liste_managers():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    managers = list(db.users.find({'role': 'manager'})
                 .skip((page-1)*per_page)
                 .limit(per_page))
    total_managers = db.users.count_documents({'role': 'manager'})
    
    return render_template(
        'liste_managers.html',
        managers=managers,
        current_page=page,
        total_pages=(total_managers // per_page) + 1
    )

    
@app.route('/admin/managers/add', methods=['GET', 'POST'])
def add_manager():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation des données
        if not all([nom, prenom, email, telephone, password, confirm_password]):
            flash('Tous les champs sont obligatoires', 'error')
            return redirect(url_for('add_manager'))

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
            return redirect(url_for('add_manager'))

        # Vérifier si l'email existe déjà
        if db.users.find_one({'email': email}):
            flash('Cet email est déjà utilisé', 'error')
            return redirect(url_for('add_manager'))

        # Hachage du mot de passe avec bcrypt (comme dans votre exemple)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Création du manager
        manager_data = {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'password': hashed_password,
            'created_at': datetime.now(),
            'role': 'manager'
        }

        try:
            db.users.insert_one(manager_data)
            flash(f'Manager {prenom} {nom} ajouté avec succès', 'success')
            return redirect(url_for('liste_managers'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout: {str(e)}', 'error')
            return redirect(url_for('add_manager'))

    return render_template('add_manager.html')


@app.route('/admin/managers/edit/<manager_id>', methods=['GET', 'POST'])
def edit_manager(manager_id):
    # Vérification de l'authentification admin
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    # Récupérer le manager depuis la collection users
    manager = db.users.find_one({'_id': ObjectId(manager_id), 'role': 'manager'})
    
    if not manager:
        flash('Manager non trouvé', 'error')
        return redirect(url_for('liste_managers'))

    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        status = request.form.get('status', 'active')

        # Validation de base
        if not all([nom, prenom, email, telephone]):
            flash('Les champs obligatoires sont manquants', 'error')
            return redirect(url_for('edit_manager', manager_id=manager_id))

        # Vérifier si l'email est déjà utilisé par un autre manager
        existing_manager = db.users.find_one({
            'email': email,
            '_id': {'$ne': ObjectId(manager_id)},
            'role': 'manager'
        })
        
        if existing_manager:
            flash('Cet email est déjà utilisé par un autre manager', 'error')
            return redirect(url_for('edit_manager', manager_id=manager_id))

        # Préparation des données de mise à jour
        update_data = {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'status': status,
            'updated_at': datetime.now()
        }

        # Mise à jour du mot de passe si fourni
        if password and confirm_password:
            if password != confirm_password:
                flash('Les mots de passe ne correspondent pas', 'error')
                return redirect(url_for('edit_manager', manager_id=manager_id))
            
            update_data['password'] = generate_password_hash(password)

        try:
            # Mise à jour dans la base de données
            db.users.update_one(
                {'_id': ObjectId(manager_id)},
                {'$set': update_data}
            )
            
            flash('Manager mis à jour avec succès', 'success')
            return redirect(url_for('liste_managers'))
        
        except Exception as e:
            flash(f'Erreur lors de la mise à jour: {str(e)}', 'error')
            return redirect(url_for('edit_manager', manager_id=manager_id))

    # Si méthode GET, afficher le formulaire pré-rempli
    return render_template('edit_manager.html', manager=manager)

@app.route('/admin/managers/delete/<manager_id>', methods=['GET', 'POST'])
def delete_manager(manager_id):
    # Vérification de l'authentification admin
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    try:
        # Vérifier d'abord si le manager existe
        manager = db.users.find_one({
            '_id': ObjectId(manager_id),
            'role': 'manager'
        })
        
        if not manager:
            flash('Manager non trouvé', 'error')
            return redirect(url_for('liste_managers'))

        # Vérifier si le manager a des dépendances (ex: réservations associées)
        has_dependencies = False
        # Exemple: vérifier s'il a des réservations
        # has_dependencies = mongo.db.reservations.count_documents({'manager_id': ObjectId(manager_id)}) > 0
        
        if has_dependencies:
            flash('Ce manager a des éléments associés et ne peut pas être supprimé', 'error')
            return redirect(url_for('liste_managers'))

        # Suppression du manager
        result = db.users.delete_one({'_id': ObjectId(manager_id)})
        
        if result.deleted_count == 1:
            flash(f'Manager {manager["prenom"]} {manager["nom"]} supprimé avec succès', 'success')
        else:
            flash('Erreur lors de la suppression du manager', 'error')
            
    except Exception as e:
        flash(f'Erreur technique lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('liste_managers'))

############ Dashboard Admin  ###########







############# Manager Dashboard  ###########

@app.route('/manager')
def manager_dashboard():
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    
    # Calcul des statistiques
    stats = {
        'nb_voitures': db.cars.count_documents({}),
        'nb_clients': db.users.count_documents({'manager_id': manager_id, 'role': 'client'}),
        'nb_reservations': db.reservations.count_documents({'manager_id': manager_id}),  # Correction ici
        'revenu_mois': 0  # Initialisation par défaut
    }
    
    # Calcul du revenu du mois
    revenue_pipeline = [
        {'$match': {
            'manager_id': manager_id,
            'date': {'$gte': datetime.now() - timedelta(days=30)},
            'status': 'completed'
        }},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    
    revenue_result = list(db.payments.aggregate(revenue_pipeline))
    if revenue_result:
        stats['revenu_mois'] = revenue_result[0]['total']
    
    # Dernières réservations
    dernieres_reservations = list(db.reservations.find({'manager_id': manager_id})
                                .sort('created_at', -1)
                                .limit(5))
    
    return render_template(
        'manager_dashboard.html',
        stats=stats,
        reservations=dernieres_reservations,
        active_page='dashboard'
    )

@app.route('/manager/voitures')
def manager_voitures():
    voitures = db.cars.find()
    return render_template('manager_voitures.html', active_page='voitures', voitures=voitures)

@app.route('/manager/voitures/ajouter', methods=['GET', 'POST'])
def ajouter_voiture():
    if request.method == 'POST':
        marque = request.form['marque']
        modele = request.form['modele']
        immatriculation = request.form['immatriculation'].upper().strip()
        prix_journalier = float(request.form['prix_journalier'])
        ville = request.form['ville']
        disponible = request.form['disponible'] == 'Oui'
        caracteristiques = [c.strip() for c in request.form.get('caracteristiques', '').split(',') if c.strip()]
        
        # Vérifier si l'immatriculation existe déjà
        if db.cars.find_one({'immatriculation': immatriculation}):
            flash('Cette immatriculation existe déjà', 'error')
            return redirect(url_for('ajouter_voiture'))
        
        image_url = ""
        image = request.files.get('image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"/static/uploads/{filename}"
        
        # Ne pas utiliser immatriculation comme _id, laisser MongoDB générer un ObjectId
        db.cars.insert_one({
            'marque': marque,
            'modele': modele,
            'immatriculation': immatriculation,
            'prix_journalier': prix_journalier,
            'ville': ville,
            'disponible': disponible,
            'caracteristiques': caracteristiques,
            'image_url': image_url,
            'created_at': datetime.now()
        })
        
        flash('Voiture ajoutée avec succès', 'success')
        return redirect(url_for('manager_voitures'))
    
    return render_template('ajouter_voiture.html')

@app.route('/manager/voitures/modifier/<voiture_id>', methods=['GET', 'POST'])
def modifier_voiture(voiture_id):
    voiture = db.cars.find_one({'_id': ObjectId(voiture_id)})
    if not voiture:
        flash('Voiture introuvable', 'danger')
        return redirect(url_for('manager_voitures'))
    
    if request.method == 'POST':
        marque = request.form['marque']
        modele = request.form['modele']
        nouvelle_immatriculation = request.form['immatriculation'].upper().strip()  # Normaliser la nouvelle immatriculation
        prix_journalier = float(request.form['prix_journalier'])
        ville = request.form['ville']
        disponible = request.form['disponible'] == 'true'
        caracteristiques = [c.strip() for c in request.form.get('caracteristiques', '').split(',') if c.strip()]
        image_url = voiture.get('image_url', '')
        
        # Vérifier si l'immatriculation a changé
        if nouvelle_immatriculation != voiture.get('immatriculation', ''):
            # Vérifier si la nouvelle immatriculation existe déjà
            if db.cars.find_one({'immatriculation': nouvelle_immatriculation, '_id': {'$ne': ObjectId(voiture_id)}}):
                flash('Cette immatriculation est déjà utilisée par une autre voiture', 'error')
                return redirect(url_for('modifier_voiture', voiture_id=voiture_id))
        
        # Traitement de l'image
        image = request.files.get('image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"/static/uploads/{filename}"
        
        # Mise à jour des données
        db.cars.update_one(
            {'_id': ObjectId(voiture_id)},
            {'$set': {
                'marque': marque,
                'modele': modele,
                'immatriculation': nouvelle_immatriculation,
                'prix_journalier': prix_journalier,
                'ville': ville,
                'disponible': disponible,
                'caracteristiques': caracteristiques,
                'image_url': image_url,
                'updated_at': datetime.now()  # Ajout d'un champ de mise à jour
            }}
        )
        flash('Voiture modifiée avec succès', 'success')
        return redirect(url_for('manager_voitures'))
    
    return render_template('modifier_voiture.html', voiture=voiture)

@app.route('/manager/voitures/supprimer/<voiture_id>', methods=['GET', 'POST'])
def supprimer_voiture(voiture_id):
    voiture = db.cars.find_one({'_id': ObjectId(voiture_id)})
    if request.method == 'POST':
        db.cars.delete_one({'_id': ObjectId(voiture_id)})
        flash('Voiture supprimée', 'success')
        return redirect(url_for('manager_voitures'))
    return render_template('supprimer_voiture.html', voiture=voiture)


@app.route('/manager/clients')
def manager_clients():
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    clients = db.users.find({'role': 'client', 'manager_id': manager_id})
    return render_template('manager_clients.html', clients=clients)

@app.route('/manager/clients/ajouter', methods=['GET', 'POST'])
def ajouter_client():
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form['telephone']
        adresse = request.form.get('adresse', '')
        info = request.form.get('info', '')
        date_inscription = datetime.now()

        # Vérifier si l'email existe déjà
        if db.users.find_one({'email': email}):
            flash('Cet email existe déjà.', 'danger')
            return render_template('ajouter_client.html')

        db.users.insert_one({
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'adresse': adresse,
            'info': info,
            'role': 'client',
            'manager_id': manager_id,  # Ajout de l'ID du manager
            'date_inscription': date_inscription
        })
        flash('Client ajouté avec succès', 'success')
        return redirect(url_for('manager_clients'))
    return render_template('ajouter_client.html')

@app.route('/manager/clients/modifier/<client_id>', methods=['GET', 'POST'])
def modifier_client(client_id):
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    client = db.users.find_one({'_id': ObjectId(client_id), 'manager_id': manager_id})
    
    if not client:
        flash("Client introuvable ou non autorisé.", "danger")
        return redirect(url_for('manager_clients'))
    
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form['telephone']
        adresse = request.form.get('adresse', '')
        info = request.form.get('info', '')
        
        db.users.update_one(
            {'_id': ObjectId(client_id)},
            {'$set': {
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'telephone': telephone,
                'adresse': adresse,
                'info': info
            }}
        )
        flash('Client modifié avec succès', 'success')
        return redirect(url_for('manager_clients'))
    
    return render_template('modifier_client.html', client=client)

@app.route('/manager/clients/supprimer/<client_id>', methods=['GET', 'POST'])
def supprimer_client(client_id):
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    client = db.users.find_one({'_id': ObjectId(client_id), 'manager_id': manager_id})
    
    if not client:
        flash("Client introuvable ou non autorisé.", "danger")
        return redirect(url_for('manager_clients'))
    
    if request.method == 'POST':
        db.users.delete_one({'_id': ObjectId(client_id)})
        flash('Client supprimé avec succès', 'success')
        return redirect(url_for('manager_clients'))
    
    return render_template('supprimer_client.html', client=client)


@app.route('/manager/reservations')
def manager_reservations():
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    
    # Récupérer seulement les clients de ce manager
    clients_ids = [client['_id'] for client in db.users.find({'role': 'client', 'manager_id': manager_id})]
    
    # Récupérer les réservations pour ces clients
    reservations = list(db.reservations.find({'client_id': {'$in': clients_ids}}))
    
    # Récupérer les clients et voitures
    clients = {str(client['_id']): client for client in db.users.find({'_id': {'$in': clients_ids}})}
    voitures = {str(voiture['_id']): voiture for voiture in db.cars.find()}
    
    # Ajouter les noms aux réservations
    for reservation in reservations:
        client_id = str(reservation.get('client_id'))
        voiture_id = str(reservation.get('voiture_id'))
        reservation['client_nom'] = clients.get(client_id, {}).get('nom', 'Inconnu') + " " + clients.get(client_id, {}).get('prenom', '')
        reservation['voiture_nom'] = voitures.get(voiture_id, {}).get('marque', 'Inconnue') + " " + voitures.get(voiture_id, {}).get('modele', '')
    
    return render_template('manager_reservations.html', reservations=reservations)

@app.route('/manager/reservations/ajouter', methods=['GET', 'POST'])
def ajouter_reservation():
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        client_email = request.form['client_email'].strip().lower()
        immatriculation = request.form['immatriculation'].upper().strip()
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin']
        statut = request.form.get('statut', 'en attente')

        # Vérifier que le client existe et appartient à ce manager
        client = db.users.find_one({
            'email': client_email,
            'role': 'client',
            'manager_id': manager_id
        })
        
        if not client:
            flash('Client non trouvé ou ne vous appartient pas', 'error')
            return redirect(url_for('ajouter_reservation'))

        # Vérifier que la voiture existe ET est disponible
        voiture = db.cars.find_one({
            'immatriculation': immatriculation,
            'disponible': True  # Ajout de cette condition
        })
        
        if not voiture:
            flash('Voiture non trouvée ou non disponible', 'error')
            return redirect(url_for('ajouter_reservation'))

        # Vérifier la disponibilité de la voiture pour cette période
        reservation_existante = db.reservations.find_one({
            'voiture_id': voiture['_id'],
            '$or': [
                {'date_debut': {'$lte': date_debut}, 'date_fin': {'$gte': date_debut}},
                {'date_debut': {'$lte': date_fin}, 'date_fin': {'$gte': date_fin}},
                {'date_debut': {'$gte': date_debut}, 'date_fin': {'$lte': date_fin}}
            ],
            'statut': {'$ne': 'annulée'}  # Exclure les réservations annulées
        })
        
        if reservation_existante:
            flash('La voiture est déjà réservée pour cette période', 'error')
            return redirect(url_for('ajouter_reservation'))

        # Créer la réservation
        db.reservations.insert_one({
            'client_id': client['_id'],
            'voiture_id': voiture['_id'],
            'date_debut': date_debut,
            'date_fin': date_fin,
            'statut': statut,
            'manager_id': manager_id,
            'created_at': datetime.now(),
            'client_email': client_email,
            'immatriculation': immatriculation
        })
        
        # Mettre à jour la disponibilité de la voiture
        db.cars.update_one(
            {'_id': voiture['_id']},
            {'$set': {'disponible': False}}
        )
        
        flash('Réservation ajoutée avec succès', 'success')
        return redirect(url_for('manager_reservations'))
    
    # Pour la méthode GET, récupérer seulement les voitures disponibles
    voitures = list(db.cars.find({'disponible': True}))  # Changé de 'Oui' à True
    immatriculations = [v['immatriculation'] for v in voitures]
    
    return render_template(
        'ajouter_reservation.html',
        immatriculations=immatriculations
    )
@app.route('/manager/reservations/accepter/<reservation_id>')
def accepter_reservation(reservation_id):
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    reservation = db.reservations.find_one({'_id': ObjectId(reservation_id), 'manager_id': manager_id})
    
    if not reservation:
        flash('Réservation non trouvée', 'error')
        return redirect(url_for('manager_reservations'))
    
    db.reservations.update_one(
        {'_id': ObjectId(reservation_id)},
        {'$set': {'statut': 'confirmée'}}
    )
    
    flash('Réservation acceptée avec succès', 'success')
    return redirect(url_for('manager_reservations'))

@app.route('/manager/reservations/refuser/<reservation_id>')
def refuser_reservation(reservation_id):
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    manager_id = ObjectId(session['user_id'])
    reservation = db.reservations.find_one({'_id': ObjectId(reservation_id), 'manager_id': manager_id})
    
    if not reservation:
        flash('Réservation non trouvée', 'error')
        return redirect(url_for('manager_reservations'))
    
    db.reservations.update_one(
        {'_id': ObjectId(reservation_id)},
        {'$set': {'statut': 'annulée'}}
    )
    
    flash('Réservation refusée avec succès', 'success')
    return redirect(url_for('manager_reservations'))


@app.route('/manager/reservations/modifier/<reservation_id>', methods=['GET', 'POST'])
def modifier_reservation(reservation_id):
    reservation = db.reservations.find_one({'_id': ObjectId(reservation_id)})
    if not reservation:
        flash("Réservation introuvable.", "danger")
        return redirect(url_for('manager_reservations'))

    clients = list(db.users.find({'role': 'client'}))
    voitures = list(db.cars.find())

    if request.method == 'POST':
        client_id = request.form['client_id']
        voiture_id = request.form['voiture_id']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin']
        statut = request.form.get('statut', 'en attente')

        db.reservations.update_one(
            {'_id': ObjectId(reservation_id)},
            {'$set': {
                'client_id': ObjectId(client_id),
                'voiture_id': ObjectId(voiture_id),
                'date_debut': date_debut,
                'date_fin': date_fin,
                'statut': statut
            }}
        )
        flash('Réservation modifiée avec succès', 'success')
        return redirect(url_for('manager_reservations'))

    return render_template(
        'modifier_reservation.html',
        reservation=reservation,
        clients=clients,
        voitures=voitures
    )

@app.route('/manager/reservations/supprimer/<reservation_id>', methods=['GET', 'POST'])
def supprimer_reservation(reservation_id):
    reservation = db.reservations.find_one({'_id': ObjectId(reservation_id)})
    if not reservation:
        flash("Réservation introuvable.", "danger")
        return redirect(url_for('manager_reservations'))

    if request.method == 'POST':
        db.reservations.delete_one({'_id': ObjectId(reservation_id)})
        flash('Réservation supprimée avec succès', 'success')
        return redirect(url_for('manager_reservations'))

    return render_template('supprimer_reservation.html', reservation=reservation)

############# Manager Dashboard  ###########



if __name__ == "__main__":
    app.run(debug=True)