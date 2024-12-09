# Étape 1 : Utiliser une image Python officielle légère comme base
FROM python:3.10-slim

# Étape 2 : Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3 : Copier les fichiers nécessaires
COPY . .

# Étape 4 : Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : Exposer le port Flask (Cloud Run utilise ce port par défaut)
EXPOSE 8080

# Étape 6 : Définir la commande pour démarrer l'application
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
