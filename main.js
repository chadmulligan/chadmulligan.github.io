const HEADER_H = 80 + 16;
const SECTIONS = ['about', 'projects'];

function setActive(id, pushHash = true) {
  document.querySelectorAll('.side-nav-item').forEach(item => item.classList.remove('active'));
  const navItem = document.querySelector(`.side-nav-item[onclick="scrollToSection('${id}')"]`);
  if (navItem) navItem.classList.add('active');
  if (pushHash) history.replaceState(null, '', '#' + id);
}

let lockedId = null;
let lockTimer = null;

function scrollToSection(id) {
  const el = document.getElementById(id);
  lockedId = id;
  setActive(id);
  const top = el.getBoundingClientRect().top + window.scrollY - HEADER_H;
  window.scrollTo({ top, behavior: 'smooth' });
  clearTimeout(lockTimer);
  lockTimer = setTimeout(() => { lockedId = null; }, 2500);
}

window.addEventListener('scrollend', () => {
  clearTimeout(lockTimer);
  lockedId = null;
});

const hash = location.hash.slice(1);
if (SECTIONS.includes(hash)) {
  window.addEventListener('load', () => scrollToSection(hash));
}

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !lockedId) setActive(entry.target.id);
  });
}, { rootMargin: '-20% 0px -70% 0px' });

SECTIONS.forEach(id => {
  const el = document.getElementById(id);
  if (el) observer.observe(el);
});
