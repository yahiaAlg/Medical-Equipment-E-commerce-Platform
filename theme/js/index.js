function toggleMenu() {
  const mobileMenu = document.getElementById("mobileMenu");
  const mobileMenuOverlay = document.getElementById("mobileMenuOverlay");

  mobileMenu.classList.toggle("active");
  mobileMenuOverlay.classList.toggle("active");

  // Prevent body scroll when menu is open
  if (mobileMenu.classList.contains("active")) {
    document.body.style.overflow = "hidden";
  } else {
    document.body.style.overflow = "";
  }
}

function closeMenu() {
  const mobileMenu = document.getElementById("mobileMenu");
  const mobileMenuOverlay = document.getElementById("mobileMenuOverlay");

  mobileMenu.classList.remove("active");
  mobileMenuOverlay.classList.remove("active");
  document.body.style.overflow = "";
}
