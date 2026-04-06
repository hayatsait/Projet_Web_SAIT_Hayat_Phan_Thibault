"use strict";

function toggleNav() {
  const navbar = document.getElementById("navbar");
  if (navbar) {
    navbar.classList.toggle("open");
  }
}

function toggleProfileMenu() {
  const menu = document.getElementById("profileMenu");
  if (menu) {
    menu.classList.toggle("show");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".nav-links a").forEach(link => {
    link.addEventListener("click", () => {
      const navbar = document.getElementById("navbar");
      if (navbar) {
        navbar.classList.remove("open");
      }
    });
  });

  document.addEventListener("click", (event) => {
    const dropdown = document.querySelector(".profile-dropdown");
    const menu = document.getElementById("profileMenu");

    if (!dropdown || !menu) return;

    if (!dropdown.contains(event.target)) {
      menu.classList.remove("show");
    }
  });
});