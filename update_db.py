import sqlite3

conn = sqlite3.connect("LostAndFound.sqlite")
cursor = conn.cursor()

print("⚠️ ATTENTION : ceci va supprimer toutes les annonces.")
confirm = input("Tape 'OUI' pour continuer : ")

if confirm == "OUI":
    # Supprimer toutes les annonces
    cursor.execute("DELETE FROM Annonce;")
    print("✅ Toutes les annonces ont été supprimées.")

    # Réinitialiser les IDs (optionnel mais propre)
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='Annonce';")
    print("🔄 ID réinitialisés.")

else:
    print("❌ Opération annulée.")

# Ajouter la colonne created_at si elle n'existe pas
try:
    cursor.execute("ALTER TABLE Annonce ADD COLUMN created_at TEXT;")
    print("✅ Colonne created_at ajoutée.")
except Exception as e:
    print("ℹ️ Colonne déjà existante ou erreur :", e)

conn.commit()
conn.close()

print("✔️ Terminé.")