/* ============================================
   ANNONCES PAGE — AmuFound
   annonces.js
   ============================================

   Données attendues depuis Flask :
   La variable globale `window.ANNONCES` doit être injectée
   dans le template Jinja2 AVANT l'inclusion de ce script :

   <script>
     window.ANNONCES = {{ annonces | tojson }};
   </script>

   Chaque objet annonce doit avoir la structure :
   {
     id         : Number,
     type       : "perdu" | "trouve",
     categorie  : "Clés" | "Carte" | "Phone" | "Sac" | "Habit" | "Autre",
     localisation : String,   // ex: "Hexagone", "RU", …
     description  : String,
     date         : String    // ex: "dimanche 20 mars à 13h"
   }

   Si vous préférez charger en AJAX, remplacez fetchAnnonces()
   par un appel fetch('/api/annonces') et adaptez.
============================================ */

"use strict";

/* ──────────────────────────────────────────
   État global
────────────────────────────────────────── */
let currentMode = "perdu";       // "perdu" | "trouve"
let activeFiltersCategory = [];  // ex: ["Clés", "Phone"]
let activeFiltersLoc = [];       // ex: ["Hexagone"]
let allAnnonces = [];

/* Émojis par catégorie */
const CATEGORY_ICONS = {
  "Clés":  "🔑",
  "Carte": "🪪",
  "Phone": "📱",
  "Sac":   "👜",
  "Habit": "👕",
  "Autre": "📦",
};

/* ──────────────────────────────────────────
   Initialisation
────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  // Récupère les données depuis la variable globale injectée par Flask
  // Fallback sur des données de démo si non définies
  allAnnonces = (window.ANNONCES && Array.isArray(window.ANNONCES))
    ? window.ANNONCES
    : getDemoData();

  renderCards();
});

/* ──────────────────────────────────────────
   Bascule Perdu / Trouvé
────────────────────────────────────────── */
function setMode(mode) {
  currentMode = mode;

  // Toggle styles sur le body
  document.body.classList.toggle("mode-trouve", mode === "trouve");

  // Mise à jour du libellé dans le titre
  document.getElementById("mode-label").textContent = mode === "perdu" ? "perdus" : "trouvés";

  // Mise à jour des boutons
  document.getElementById("btn-perdu").classList.toggle("active", mode === "perdu");
  document.getElementById("btn-trouve").classList.toggle("active", mode === "trouve");

  renderCards();
}

/* ──────────────────────────────────────────
   Gestion des filtres tag
────────────────────────────────────────── */
function toggleFilter(btn) {
  const filterType = btn.dataset.filter;   // "category" | "localisation"
  const value = btn.dataset.value;
  const targetArray = filterType === "category" ? activeFiltersCategory : activeFiltersLoc;

  const idx = targetArray.indexOf(value);
  if (idx === -1) {
    targetArray.push(value);
    btn.classList.add("active");
  } else {
    targetArray.splice(idx, 1);
    btn.classList.remove("active");
  }

  renderCards();
}

function clearFilters() {
  activeFiltersCategory = [];
  activeFiltersLoc = [];

  document.querySelectorAll(".tag").forEach(t => t.classList.remove("active"));
  document.getElementById("search-input").value = "";

  renderCards();
}

/* ──────────────────────────────────────────
   Recherche textuelle
────────────────────────────────────────── */
function filterCards() {
  renderCards();
}

/* ──────────────────────────────────────────
   Rendu des cartes
────────────────────────────────────────── */
function renderCards() {
  const grid = document.getElementById("cards-grid");
  const emptyState = document.getElementById("empty-state");
  const searchTerm = document.getElementById("search-input").value.toLowerCase().trim();

  // Filtrage
  const filtered = allAnnonces.filter(a => {
    if (a.type !== currentMode) return false;

    if (activeFiltersCategory.length > 0 && !activeFiltersCategory.includes(a.categorie)) return false;
    if (activeFiltersLoc.length > 0 && !activeFiltersLoc.includes(a.localisation)) return false;

    if (searchTerm) {
      const haystack = `${a.categorie} ${a.localisation} ${a.description}`.toLowerCase();
      if (!haystack.includes(searchTerm)) return false;
    }

    return true;
  });

  // Vide la grille
  grid.innerHTML = "";

  if (filtered.length === 0) {
    emptyState.style.display = "block";
    return;
  }
  emptyState.style.display = "none";

  // Génère les cartes
  filtered.forEach((annonce, i) => {
    const card = buildCard(annonce, i);
    grid.appendChild(card);
  });
}

/* ──────────────────────────────────────────
   Construction d'une carte DOM
────────────────────────────────────────── */
function buildCard(annonce, index) {
  const card = document.createElement("div");
  card.className = `annonce-card ${annonce.type}`;
  card.style.animationDelay = `${index * 0.06}s`;

  const icon = CATEGORY_ICONS[annonce.categorie] || "📦";
  const btnLabel = annonce.type === "perdu" ? "J'ai trouvé cet objet" : "Je réclame cet objet";

  card.innerHTML = `
    <div class="card-title">
      <span class="card-icon">${icon}</span>
      ${escapeHtml(annonce.categorie)}
    </div>
    <div class="card-location">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 21s-8-5.686-8-12a8 8 0 1 1 16 0c0 6.314-8 12-8 12z"/>
        <circle cx="12" cy="9" r="2.5"/>
      </svg>
      ${escapeHtml(annonce.localisation)}
    </div>
    <p class="card-description">${escapeHtml(annonce.description)}</p>
    <div class="card-action">
      <button class="card-btn" onclick="handleCardAction(${annonce.id}, '${annonce.type}')">
        ${btnLabel}
      </button>
    </div>
  `;

  return card;
}

/* ──────────────────────────────────────────
   Action sur le bouton de la carte
   → À connecter à votre logique Flask (redirect, modal, etc.)
────────────────────────────────────────── */
function handleCardAction(annonceId, type) {
  // Exemple : redirection vers une page de contact / détail
  // window.location.href = `/annonce/${annonceId}/contact`;

  console.log(`Action sur annonce #${annonceId} (${type})`);
  alert(`Action enregistrée pour l'annonce #${annonceId}`);
}

/* ──────────────────────────────────────────
   Utilitaires
────────────────────────────────────────── */
function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ──────────────────────────────────────────
   Données de démonstration (utilisées si
   window.ANNONCES n'est pas défini)
────────────────────────────────────────── */
function getDemoData() {
  return [
    {
      id: 1, type: "perdu", categorie: "Clés", localisation: "Hexagone",
      description: "J'ai perdu mes clés vers 13h le dimanche 20 mars à la BU."
    },
    {
      id: 2, type: "perdu", categorie: "Clés", localisation: "Hexagone",
      description: "J'ai perdu mes clés vers 13h le dimanche 20 mars à la BU."
    },
    {
      id: 3, type: "perdu", categorie: "Clés", localisation: "Hexagone",
      description: "J'ai perdu mes clés vers 13h le dimanche 20 mars à la BU."
    },
    {
      id: 4, type: "perdu", categorie: "Clés", localisation: "Hexagone",
      description: "J'ai perdu mes clés vers 13h le dimanche 20 mars à la BU."
    },
    {
      id: 5, type: "trouve", categorie: "Clés", localisation: "Hexagone",
      description: "J'ai trouvé des clés vers 13h le dimanche 20 mars à la BU."
    },
    {
      id: 6, type: "trouve", categorie: "Clés", localisation: "Hexagone",
      description: "J'ai trouvé des clés vers 13h le dimanche 20 mars à la BU."
    },
    {
      id: 7, type: "trouve", categorie: "Clés", localisation: "Hexagone",
      description: "J'ai trouvé des clés vers 13h le dimanche 20 mars à la BU."
    },
    {
      id: 8, type: "trouve", categorie: "Clés", localisation: "Hexagone",
      description: "J'ai trouvé des clés vers 13h le dimanche 20 mars à la BU."
    },
    {
      id: 9, type: "perdu", categorie: "Phone", localisation: "RU",
      description: "Téléphone Samsung Galaxy noir oublié à la cafétéria le lundi matin."
    },
    {
      id: 10, type: "perdu", categorie: "Carte", localisation: "TPR1",
      description: "Carte étudiante perdue dans l'amphithéâtre TPR1 après le cours de 10h."
    },
    {
      id: 11, type: "trouve", categorie: "Sac", localisation: "BAT A",
      description: "Petit sac à dos bleu marine trouvé devant le bâtiment A."
    },
    {
      id: 12, type: "trouve", categorie: "Habit", localisation: "Technoforme",
      description: "Veste grise trouvée à la salle de sport Technoforme."
    },
  ];
}
