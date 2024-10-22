document.getElementById('filterButton').addEventListener('click', function() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const dateFilter = document.getElementById('dateFilter').value;
    const table = document.getElementById('historiqueTable');
    const rows = table.getElementsByTagName('tr');

    // Parcours des lignes du tableau, à partir de la deuxième (ignorer l'en-tête)
    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let showRow = true; // Variable pour déterminer si la ligne doit être affichée

        // Filtrer par recherche
        if (searchInput) {
            const filename = cells[0].textContent.toLowerCase();
            const professor = cells[1].textContent.toLowerCase();
            showRow = filename.includes(searchInput) || professor.includes(searchInput);
        }

        // Filtrer par date
        if (dateFilter) {
            const rowDate = cells[3].textContent.split(" ")[0]; // Récupérer uniquement la date
            showRow = showRow && (rowDate === dateFilter); // Comparer la date du tableau avec celle du filtre
        }

        // Afficher ou masquer la ligne
        rows[i].style.display = showRow ? '' : 'none';
    }
});
document.getElementById("printButton").addEventListener("click", function() {
    window.print(); // Ouvrir la boîte de dialogue d'impression
});
