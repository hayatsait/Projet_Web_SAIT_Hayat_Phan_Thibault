"use strict";

/* ============================================================
   NOUVELLE ANNONCE — Validation front-end
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {

  const form    = document.getElementById("annonce-form");
  const btnSend = document.getElementById("btn-submit");

  /* ---- Mapping champ → message d'erreur ---- */
  const fields = [
    {
      el:      document.getElementById("type"),
      errEl:   document.getElementById("err-type"),
      validate: v => v !== "",
      msg:     "Veuillez choisir un type d'annonce.",
    },
    {
      el:      document.getElementById("objet"),
      errEl:   document.getElementById("err-objet"),
      validate: v => v !== "",
      msg:     "Veuillez choisir une catégorie.",
    },
    {
      el:      document.getElementById("location"),
      errEl:   document.getElementById("err-location"),
      validate: v => v !== "",
      msg:     "Veuillez choisir une localisation.",
    },
    {
      el:      document.getElementById("email"),
      errEl:   document.getElementById("err-email"),
      validate: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()),
      msg:     "Veuillez entrer une adresse email valide.",
    },
    {
      el:      document.getElementById("description"),
      errEl:   document.getElementById("err-description"),
      validate: v => v.trim().length >= 5,
      msg:     "La description doit contenir au moins 5 caractères.",
    },
  ];

  /* ---- Affiche / masque l'erreur d'un champ ---- */
  function setError(field, hasError) {
    field.el.classList.toggle("is-invalid", hasError);
    field.errEl.textContent = hasError ? field.msg : "";
  }

  /* ---- Valide tous les champs, retourne true si tout est ok ---- */
  function validateAll() {
    let valid = true;
    fields.forEach(f => {
      const ok = f.validate(f.el.value);
      setError(f, !ok);
      if (!ok) valid = false;
    });
    return valid;
  }

  /* ---- Validation à la perte du focus (retour immédiat) ---- */
  fields.forEach(f => {
    f.el.addEventListener("blur", () => {
      setError(f, !f.validate(f.el.value));
    });

    f.el.addEventListener("input", () => {
      // Efface l'erreur dès que l'utilisateur corrige
      if (f.validate(f.el.value)) setError(f, false);
    });
  });

  /* ---- Soumission ---- */
  form.addEventListener("submit", (e) => {
    if (!validateAll()) {
      e.preventDefault();

      // Focus sur le premier champ en erreur
      const first = fields.find(f => f.el.classList.contains("is-invalid"));
      if (first) first.el.focus();
      return;
    }

    // Désactive le bouton (anti double-clic)
    btnSend.disabled     = true;
    btnSend.textContent  = "Envoi en cours…";
  });

});
