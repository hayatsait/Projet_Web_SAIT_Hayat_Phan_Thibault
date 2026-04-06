"use strict";

function toggleEdit(field) {
  const input = document.getElementById(`input-${field}`);
  const button = document.getElementById(`btn-${field}`);
  const hiddenInput = document.getElementById(`hidden-${field}`);
  const form = document.getElementById(`form-${field}`);

  if (!input || !button || !hiddenInput || !form) return;

  if (input.disabled) {
    input.disabled = false;
    input.focus();
    button.textContent = "Enregistrer";
  } else {
    const value = input.value.trim();

    if (!value) {
      alert("Ce champ ne peut pas être vide.");
      return;
    }

    hiddenInput.value = value;
    form.submit();
  }
}

function openPasswordForm() {
  const defaultBlock = document.getElementById("security-default");
  const formBlock = document.getElementById("security-form");

  if (defaultBlock) defaultBlock.style.display = "none";
  if (formBlock) formBlock.style.display = "block";
}

function confirmDelete() {
  const ok = confirm("Voulez-vous vraiment supprimer votre compte ?");
  if (ok) {
    const form = document.getElementById("form-delete");
    if (form) {
      form.submit();
    }
  }
}