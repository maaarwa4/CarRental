<div align="center">

# 🚗 CarRental

**Application web de gestion de location de voitures**

`Python` · `Flask` · `MongoDB` · `Jinja2` · `bcrypt`

</div>

---

## 📌 Présentation

CarRental centralise la gestion d'une agence de location de voitures : parc automobile, clients et réservations.
L'application repose sur une **gestion des accès par rôle** : chaque utilisateur ne voit que les fonctionnalités qui le concernent.

---

## 👥 Rôles et fonctionnalités

### 🛡️ Administrateur
- Tableau de bord avec indicateurs clés (nombre de gestionnaires, de clients…)
- Création, modification et suppression des comptes **gestionnaires**

### 🧑‍💼 Gestionnaire
- **Parc automobile** : ajout, modification et suppression de véhicules (avec photo)
- **Clients** : gestion de son portefeuille clients
- **Réservations** : création, modification, acceptation ou refus
- Tableau de bord personnel

---

## ⚙️ Règles métier

- ✅ Une réservation n'est possible que sur un véhicule **disponible**
- 📅 Contrôle des **chevauchements de dates** : un véhicule ne peut pas être réservé deux fois sur la même période
- 🔄 Cycle de vie des réservations : **en attente → confirmée / annulée**
- 🚘 Disponibilité du véhicule mise à jour automatiquement à chaque réservation
- 📧 Unicité des adresses e-mail des utilisateurs

---

## 🔐 Sécurité

- Mots de passe **hachés avec bcrypt**
- Sessions Flask et **contrôle d'accès par rôle** sur chaque route
- Upload d'images sécurisé (`secure_filename`)
- Configuration sensible externalisée dans des variables d'environnement

---

## 🛠️ Stack technique

| Couche | Technologie |
|---|---|
| Backend | Python, Flask |
| Base de données | MongoDB (PyMongo) |
| Frontend | Templates Jinja2, HTML, CSS |
| Sécurité | bcrypt, Werkzeug |
| Notifications | Flask-Mail |

---

## 📁 Structure du projet

```
CarRental/
├── app.py            # Application Flask : routes et logique métier
├── crypt.py          # Script de création du compte administrateur
├── requirements.txt  # Dépendances Python
├── .env.example      # Modèle de configuration
├── templates/        # Vues Jinja2 (tableaux de bord, formulaires, listes)
└── static/
    ├── images/       # Ressources visuelles
    └── uploads/      # Photos des véhicules
```

---

## 🚀 Installation

**Prérequis :** Python 3.8+ et MongoDB lancé en local (`mongodb://localhost:27017`)

```bash
# 1. Cloner le dépôt
git clone https://github.com/maaarwa4/CarRental.git
cd CarRental

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env    # puis renseigner les valeurs

# 4. Créer le compte administrateur
python crypt.py

# 5. Lancer l'application
python app.py
```

> 🔒 Les informations sensibles (clé secrète, identifiants) sont lues depuis le fichier `.env`, qui n'est jamais versionné.

---

<div align="center">

Réalisé par **Marwa BOUNOUA** · [LinkedIn](https://linkedin.com/in/marwa-bounoua-877300263) · [GitHub](https://github.com/maaarwa4)

</div>
