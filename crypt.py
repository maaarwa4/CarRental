import bcrypt
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.voiture_db
users = db['users']

password = "admin123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

users.insert_one({
    "email": "admin2@exemple.com",
    "password": hashed,  # stocké en binaire
    "role": "admin",
    "nom": "admin1",
    "prenom": "admin1"
})

if __name__ == "__main__":
    print("Utilisateur manager créé avec succès.")
