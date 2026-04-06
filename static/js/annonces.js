"use strict";

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("filters-form");
  const searchInput = document.getElementById("search-input");
  const tags = document.querySelectorAll(".tag");
  const modalOverlay = document.getElementById("modal-overlay");
  const modalClose = document.getElementById("modal-close");

  if (!form) return;

  // Clic sur un tag => toggle + submit immédiat
  tags.forEach(tag => {
    tag.addEventListener("click", function (e) {
      e.preventDefault();

      const checkbox = this.querySelector("input[type='checkbox']");
      if (!checkbox) return;

      checkbox.checked = !checkbox.checked;
      this.classList.toggle("active", checkbox.checked);

      form.submit();
    });
  });

  // Recherche texte : submit sur Entrée
  if (searchInput) {
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        form.submit();
      }
    });
  }

  // Modale
  if (modalClose && modalOverlay) {
    modalClose.addEventListener("click", closeModal);

    modalOverlay.addEventListener("click", function (e) {
      if (e.target === modalOverlay) {
        closeModal();
      }
    });
  }
});

function setMode(mode) {
  const modeInput = document.getElementById("mode-input");
  const form = document.getElementById("filters-form");

  if (!modeInput || !form) return;

  modeInput.value = mode;
  form.submit();
}

function clearFilters() {
  const form = document.getElementById("filters-form");
  const searchInput = document.getElementById("search-input");

  if (!form) return;

  document.querySelectorAll('input[name="objet"]').forEach(input => {
    input.checked = false;
  });

  document.querySelectorAll('input[name="location"]').forEach(input => {
    input.checked = false;
  });

  document.querySelectorAll(".tag").forEach(tag => {
    tag.classList.remove("active");
  });

  if (searchInput) {
    searchInput.value = "";
  }

  form.submit();
}

function openModal(button) {
  const overlay = document.getElementById("modal-overlay");
  const contactValue = document.getElementById("modal-contact-value");
  const dateValue = document.getElementById("modal-date-value");
  const form = document.getElementById("modal-form");
  const desc = document.getElementById("modal-desc");
  const confirmBtn = document.getElementById("modal-confirm-btn");

  if (!overlay || !contactValue || !form || !button) return;

  const id = button.dataset.id;
  const contact = button.dataset.contact;
  const type = button.dataset.type;
  const createdAt = button.dataset.createdAt;

  contactValue.textContent = contact || "—";

  if (dateValue) {
    dateValue.textContent = createdAt || "—";
  }

  form.action = `/annonces/${id}/confirm`;

  if (type === "perdu") {
    if (desc) {
      desc.textContent = "Retrouvez ci-dessous les coordonnées du propriétaire et confirmez pour marquer ceci comme récupéré.";
    }
    if (confirmBtn) {
      confirmBtn.textContent = "Confirmer";
    }
  } else {
    if (desc) {
      desc.textContent = "Retrouvez ci-dessous les coordonnées de la personne ayant trouvé l'objet et confirmez pour marquer ceci comme récupéré.";
    }
    if (confirmBtn) {
      confirmBtn.textContent = "Confirmer";
    }
  }

  overlay.classList.add("is-open");
}

function closeModal() {
  const overlay = document.getElementById("modal-overlay");
  if (overlay) {
    overlay.classList.remove("is-open");
  }
}