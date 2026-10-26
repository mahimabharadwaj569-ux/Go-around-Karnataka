document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("menuToggle");
  const nav = document.getElementById("mainNav");
  if (toggle && nav) toggle.addEventListener("click", () => nav.classList.toggle("nav-open"));

  document.querySelectorAll('input[type="date"][name="check_in"]').forEach(input => {
    const form = input.closest("form");
    const out = form && form.querySelector('input[name="check_out"]');
    if (out) {
      input.addEventListener("change", () => {
        out.min = input.value;
        if (out.value && out.value < input.value) out.value = input.value;
      });
    }
  });

  document.querySelectorAll(".flash").forEach(flash => {
    const close = flash.querySelector("button");
    if (close) close.addEventListener("click", () => flash.remove());
  });
});
