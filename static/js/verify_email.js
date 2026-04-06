"use strict";

/* ============================================================
   OTP INPUT — Vérification AmuFound
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {
  const boxes     = Array.from(document.querySelectorAll(".otp-box"));
  const form      = document.getElementById("otp-form");
  const hidden    = document.getElementById("otp-hidden");
  const errorMsg  = document.getElementById("otp-error");
  const btnVerify = document.getElementById("btn-verify");

  /* ---------- Focus automatique sur la 1ère case ---------- */
  boxes[0].focus();

  /* ---------- Helpers ---------- */
  function isDigit(char) {
    return /^\d$/.test(char);
  }

  function markFilled(box) {
    box.classList.toggle("filled", box.value !== "");
  }

  function clearError() {
    errorMsg.style.display = "none";
    errorMsg.textContent   = "";
    boxes.forEach(b => b.classList.remove("error"));
  }

  function showError(msg) {
    errorMsg.textContent   = msg;
    errorMsg.style.display = "block";
    boxes.forEach(b => b.classList.add("error"));
  }

  /* ---------- Saisie dans une case ---------- */
  boxes.forEach((box, idx) => {

    /* Keydown : gestion Backspace et navigation flèches */
    box.addEventListener("keydown", (e) => {
      if (e.key === "Backspace") {
        e.preventDefault();
        if (box.value !== "") {
          box.value = "";
          markFilled(box);
        } else if (idx > 0) {
          // Case vide → reculer
          boxes[idx - 1].value = "";
          markFilled(boxes[idx - 1]);
          boxes[idx - 1].focus();
        }
        clearError();
      }

      if (e.key === "ArrowLeft" && idx > 0) {
        boxes[idx - 1].focus();
      }

      if (e.key === "ArrowRight" && idx < boxes.length - 1) {
        boxes[idx + 1].focus();
      }
    });

    /* Input : saisie d'un chiffre */
    box.addEventListener("input", (e) => {
      const val = e.target.value;

      // Garder uniquement le dernier caractère saisi (au cas où)
      if (val.length > 1) {
        box.value = val.slice(-1);
      }

      if (!isDigit(box.value)) {
        box.value = "";
        markFilled(box);
        return;
      }

      markFilled(box);
      clearError();

      // Avancer automatiquement
      if (idx < boxes.length - 1) {
        boxes[idx + 1].focus();
      }
    });

    /* Paste : coller un code complet depuis le presse-papier */
    box.addEventListener("paste", (e) => {
      e.preventDefault();
      const pasted = (e.clipboardData || window.clipboardData)
        .getData("text")
        .replace(/\D/g, "") // ne garder que les chiffres
        .slice(0, boxes.length);

      if (!pasted) return;

      pasted.split("").forEach((char, i) => {
        if (boxes[i]) {
          boxes[i].value = char;
          markFilled(boxes[i]);
        }
      });

      // Focus sur la case suivant le dernier chiffre collé
      const nextIdx = Math.min(pasted.length, boxes.length - 1);
      boxes[nextIdx].focus();
      clearError();
    });

    /* Click : sélectionner la case entière pour écraser facilement */
    box.addEventListener("click", () => {
      box.select();
    });
  });

  /* ---------- Soumission du formulaire ---------- */
  form.addEventListener("submit", (e) => {
    const code = boxes.map(b => b.value).join("");

    if (code.length < boxes.length) {
      e.preventDefault();
      showError("Veuillez entrer les 6 chiffres du code.");
      // Focus sur la première case vide
      const firstEmpty = boxes.find(b => b.value === "");
      if (firstEmpty) firstEmpty.focus();
      return;
    }

    // Injecter le code complet dans le champ caché
    hidden.value = code;

    // Désactiver le bouton pendant la soumission (anti double-clic)
    btnVerify.disabled = true;
    btnVerify.textContent = "Vérification…";
  });
});
