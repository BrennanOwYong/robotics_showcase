const filters = document.querySelectorAll(".filter");
const cards = document.querySelectorAll(".card-link[data-category]");

filters.forEach((filter) => {
  filter.addEventListener("click", () => {
    const selected = filter.dataset.filter;
    filters.forEach((button) => button.classList.toggle("is-active", button === filter));
    cards.forEach((card) => {
      const visible = selected === "all" || card.dataset.category === selected;
      card.hidden = !visible;
    });
  });
});

if (window.matchMedia("(prefers-reduced-motion: no-preference)").matches) {
  document.querySelectorAll(".card-link").forEach((card, index) => {
    card.style.animationDelay = `${index * 70}ms`;
    card.classList.add("reveal");
  });
}
