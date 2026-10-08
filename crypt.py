"""Création du compte administrateur.

Les identifiants sont lus depuis le fichier .env (ADMIN_EMAIL, ADMIN_PASSWORD),
ou saisis au clavier s'ils ne sont pas définis.
"""
import os
from getpass import getpass

import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def main():
    client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
    users = client.voiture_db['users']

    email = os.getenv('ADMIN_EMAIL') or input("E-mail de l'administrateur : ").strip()
    password = os.getenv('ADMIN_PASSWORD') or getpass("Mot de passe : ")

    if not email or not password:
        print("E-mail et mot de passe obligatoires.")
        return

    if users.find_one({'email': email}):
        print(f"Un utilisateur avec l'e-mail {email} existe déjà.")
        return

    users.insert_one({
        'email': email,
        'password': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()),
        'role': 'admin',
        'nom': 'Admin',
        'prenom': 'Admin',
    })
    print("Compte administrateur créé avec succès.")


if __name__ == '__main__':
    main()
