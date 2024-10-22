// script.js
document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Empêche l'envoi par défaut du formulaire

    var fileInput = document.getElementById('file');
    var file = fileInput.files[0];
    
    if (!file) {
        document.getElementById('statusMessage').textContent = "Veuillez sélectionner un fichier.";
        return;
    }

    // Vérification de la taille du fichier (par exemple, 10 Mo max)
    if (file.size > 10 * 1024 * 1024) {
        document.getElementById('statusMessage').textContent = "Le fichier est trop volumineux. Taille maximale : 10 Mo.";
        return;
    }

    // Si la validation est réussie, on peut envoyer le formulaire
    this.submit();
});
