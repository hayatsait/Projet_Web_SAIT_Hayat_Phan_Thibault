"use strict"
function toggleNav() {
    document.getElementById('navbar').classList.toggle('open');
  }
  // Close nav on link click (mobile)
  document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
      document.getElementById('navbar').classList.remove('open');
    });
  });