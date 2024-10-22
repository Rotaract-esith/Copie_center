from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
from datetime import datetime
from flask_mail import Mail, Message
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = '123456789'  # Nécessaire pour les sessions

# Configuration pour l'envoi d'email avec Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yasyasharoual123@gmail.com'  # Remplacez par votre adresse Gmail
app.config['MAIL_PASSWORD'] = 'been qltx wpda ipfu'          # Remplacez par votre mot de passe Gmail
app.config['MAIL_DEFAULT_SENDER'] = 'yasyasharoual123@gmail.com'

mail = Mail(app)

# Chemin du fichier Excel contenant les informations des professeurs
df_professeurs = pd.read_excel('professeurs.xlsx')

# Chemin du fichier Excel contenant les informations des administrateurs
df_admins = pd.read_excel('admin.xlsx')

# Chemin du dossier pour stocker les fichiers téléchargés
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route pour la page de connexion
@app.route('/')
def home():
    return render_template('login.html')

# Route pour traiter la connexion
@app.route('/login', methods=['POST'])
def login():
    user_type = request.form['user_type']  # Récupérer le type d'utilisateur (professeur ou admin)
    email = request.form['email']
    password = request.form['password']
    
    if user_type == 'professeur':
        df_professeurs['Email'] = df_professeurs['Email'].astype(str).str.strip()
        df_professeurs['Mot de passe'] = df_professeurs['Mot de passe'].astype(str).str.strip()

        for index, row in df_professeurs.iterrows():
            if row['Email'] == email and row['Mot de passe'] == password:
                session['professeur_name'] = row['Nom']
                session['professeur_email'] = row['Email']
                return redirect(url_for('acceuil'))

    elif user_type == 'administrateur':
        df_admins['Email'] = df_admins['Email'].astype(str).str.strip()
        df_admins['Mot de passe'] = df_admins['Mot de passe'].astype(str).str.strip()

        for index, row in df_admins.iterrows():
            if row['Email'] == email and row['Mot de passe'] == password:
                session['admin_name'] = row['Nom']
                return redirect(url_for('acceuil_admin'))

    return render_template('login.html', error="Identifiants invalides, veuillez réessayer.")

# Route pour la page de téléchargement
@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if 'professeur_name' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        file = request.files['file']
        copies = request.form['copies']
        color_choice = request.form['colorChoice']

        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)  # Sauvegarder le fichier téléchargé

            # Créer le fichier d'information
            info_file_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(file.filename)[0]}_info.txt")
            with open(info_file_path, 'w') as info_file:
                info_file.write(f"Nombre de copies: {copies}\n")
                info_file.write(f"Choix d'impression: {'Couleur' if color_choice == 'color' else 'Noir et blanc'}\n")
                info_file.write(f"Professeur: {session['professeur_name']}\n")
                info_file.write(f"Email: {session['professeur_email']}\n")  
                info_file.write(f"Fichier: {file.filename}\n")
                info_file.write(f"Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                info_file.write(f"Statut: En attente\n")  # Statut par défaut

            # Enregistrement des informations dans l'historique
            historique_file_path = os.path.join(UPLOAD_FOLDER, 'historique_prof.txt')
            with open(historique_file_path, 'a', encoding='latin-1') as historique_file:
                historique_file.write(
                    f"{file.filename}|{session['professeur_name']}|{session['professeur_email']}|"
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{copies}|{'Couleur' if color_choice == 'color' else 'Noir et blanc'}|En attente\n"
                )

            # Envoi de l'email de confirmation
            try:
                validation_link = url_for('validate_file', filename=file.filename, _external=True)
                msg = Message("Confirmation de votre demande d'impression",
                              recipients=[session['professeur_email']])
                msg.body = (f"Bonjour {session['professeur_name']},\n\n"
                            f"Votre demande d'impression pour le fichier '{file.filename}' a été reçue.\n"
                            f"Nombre de copies: {copies}\n"
                            f"Choix d'impression: {'Couleur' if color_choice == 'color' else 'Noir et blanc'}\n"
                            f"Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"Veuillez valider votre demande en cliquant sur le lien suivant : {validation_link}")
                mail.send(msg)
            except Exception as e:
                return f"Erreur lors de l'envoi de l'email : {str(e)}"

            return render_template('confirmation.html', professeur_name=session['professeur_name'], file_name=file.filename, copies=copies, color_choice=color_choice)

    return render_template('upload.html', professeur_name=session['professeur_name'])


# Route pour valider un fichier
@app.route('/validate/<path:filename>')
def validate_file(filename):
    info_file_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(filename)[0]}_info.txt")
    
    if os.path.exists(info_file_path):
        with open(info_file_path, 'r', encoding='latin-1') as info_file:
            lines = info_file.readlines()

        for i in range(len(lines)):
            if lines[i].startswith("Statut:"):
                lines[i] = "Statut: Validé\n"

        with open(info_file_path, 'w', encoding='latin-1') as info_file:
            info_file.writelines(lines)

        return "Votre demande a été validée avec succès !"
    else:
        return "Erreur : Fichier non trouvé."

@app.route('/historique')
def historique():
    if 'professeur_name' not in session:
        return redirect(url_for('home'))

    historique = []
    professeur_name = session['professeur_name']
    historique_file_path = os.path.join(UPLOAD_FOLDER, 'historique_prof.txt')

    if os.path.exists(historique_file_path):
        with open(historique_file_path, 'r', encoding='latin-1') as historique_file:
            for line in historique_file:
                details = line.strip().split('|')
                if len(details) == 7 and details[1] == professeur_name:  # Vérifier la longueur
                    historique.append({
                        'filename': details[0],
                        'professor': details[1],
                        'email': details[2],
                        'date_time': details[3],
                        'copies': details[4],
                        'color_choice': details[5],
                        'status': details[6],
                    })

    return render_template('historique.html', professeur_name=professeur_name, historique=historique)



# Route pour afficher la page des fichiers pour l'administrateur
@app.route('/files')
def files():
    if 'admin_name' not in session:
        return redirect(url_for('home'))

    files_list = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith('_info.txt'):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file_time = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')

            with open(file_path, 'r', encoding='latin-1') as info_file:
                details = {}
                for line in info_file:
                    key, value = line.split(': ', 1)
                    details[key.strip()] = value.strip()

                files_list.append({
                    'name': details.get('Fichier', filename),
                    'professor': details.get('Professeur', 'Inconnu'),
                    'email': details.get('Email', 'Inconnu'),  # Ajout de l'email
                    'date_sent': file_date,
                    'copies': details.get('Nombre de copies', '0'),
                    'print_choice': details.get('Choix d\'impression', 'Inconnu'),
                    'status': details.get('Statut', 'Inconnu'),
                })

    return render_template('files.html', files=files_list)

@app.route('/notify_ready/<filename>', methods=['POST'])
def notify_ready(filename):
    # Rechercher les informations du fichier
    file_info_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(filename)[0]}_info.txt")
    
    if os.path.exists(file_info_path):
        with open(file_info_path, 'r', encoding='latin-1') as info_file:
            details = {}
            for line in info_file:
                key, value = line.split(': ', 1)
                details[key.strip()] = value.strip()
        
        # Récupérer l'email du professeur depuis les détails du fichier
        professor_email = details.get('Email')  # Utiliser le bon champ "Email" dans le fichier info

        if professor_email:
            try:
                # Envoi de l'email au professeur
                msg = Message("Vos copies sont prêtes !", recipients=[professor_email])
                msg.body = (f"Bonjour {details.get('Professeur')},\n\n"
                            f"Vos copies pour le fichier '{filename}' sont prêtes.\n"
                            "Merci de venir les récupérer à votre convenance.")
                mail.send(msg)
                
                return redirect(url_for('files'))
            except Exception as e:
                return f"Erreur lors de l'envoi de l'e-mail : {str(e)}"
    
    return f"Le fichier d'informations pour {filename} n'a pas été trouvé."
# Route pour récupérer un fichier
@app.route('/recuperer/<filename>', methods=['POST'])
def recuperer(filename):
    info_file_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(filename)[0]}_info.txt")

    if os.path.exists(info_file_path):
        # Lire les informations du fichier
        with open(info_file_path, 'r', encoding='latin-1') as info_file:
            details = {}
            for line in info_file:
                key, value = line.split(': ', 1)
                details[key.strip()] = value.strip()
        
        # Ajouter l'information à l'historique de l'administrateur
        historique_file_path = os.path.join(UPLOAD_FOLDER, 'historique_admin.txt')
        with open(historique_file_path, 'a', encoding='latin-1') as historique_file:
            historique_file.write(
                f"{details.get('Fichier')}|{details.get('Professeur')}|{details.get('Email')}|"
                f"{details.get('Date et heure')}|{details.get('Nombre de copies')}|"
                f"{details.get('Choix d\'impression')}|Récupéré\n"
            )
        
        # Supprimer le fichier d'information original
        os.remove(info_file_path)

        return redirect(url_for('files'))

    return "Erreur : Fichier non trouvé."

# Route pour afficher l'historique des administrateurs
@app.route('/historique_admin')
def historique_admin():
    if 'admin_name' not in session:
        return redirect(url_for('home'))
    
    historique = []
    historique_file_path = os.path.join(UPLOAD_FOLDER, 'historique_admin.txt')

    if os.path.exists(historique_file_path):
        with open(historique_file_path, 'r', encoding='latin-1') as historique_file:
            details = historique_file.readlines()
            # Transformez chaque ligne en liste de valeurs
            historique = [line.strip().split('|') for line in details]

    return render_template('historique_admin.html', historique=historique)
# to download files for print
@app.route('/uploads/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Route pour la page d'accueil des professeurs
@app.route('/acceuil')
def acceuil():
    if 'professeur_name' in session:
        return render_template('acceuil.html', professeur_name=session['professeur_name'])
    return redirect(url_for('home'))

# Route pour la page d'accueil des administrateurs
@app.route('/acceuil_admin')
def acceuil_admin():
    if 'admin_name' in session:
        return render_template('acceuil_admin.html', admin_name=session['admin_name'])
    return redirect(url_for('home'))

# Route pour déconnecter l'utilisateur
@app.route('/logout')
def logout():
    # Vider la session pour déconnecter l'utilisateur
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)