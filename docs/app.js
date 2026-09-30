const scenarios = {
  absence: {
    question: "Quel est le quota d'absences autorisées par semestre ?",
    answer: "Le jeu de données indique un quota de 18 absences autorisées par semestre. Au-delà, des conséquences progressives sont prévues par le règlement."
  },
  justificatif: {
    question: "Comment déposer un justificatif d'absence ?",
    answer: "Depuis votre plateforme, ouvrez « Scolarité », puis « Absences » et choisissez « Ajouter un justificatif d'absence »."
  },
  isic: {
    question: "Qu'est-ce que la carte ISIC ?",
    answer: "La carte étudiante internationale ISIC est dématérialisée et permet de bénéficier de réductions en France et à l'étranger."
  }
};

const question = document.querySelector('#question-bubble');
const answer = document.querySelector('#answer-bubble');
const caption = document.querySelector('.experience-caption span:last-child');
const ids = Object.keys(scenarios);
function selectScenario(id) {
  if (!scenarios[id]) return;
  question.textContent = scenarios[id].question;
  answer.textContent = scenarios[id].answer;
  question.classList.remove('animate');
  answer.classList.remove('animate');
  void question.offsetWidth;
  question.classList.add('animate');
  answer.classList.add('animate');
  caption.textContent = `${String(ids.indexOf(id) + 1).padStart(2, '0')} / 03`;
  document.querySelectorAll('.scenario').forEach(button => {
    const active = button.dataset.scenario === id;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
}
document.querySelectorAll('.scenario').forEach(button => button.addEventListener('click', () => selectScenario(button.dataset.scenario)));
selectScenario('absence');

const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: .1, rootMargin: '0px 0px -20px 0px' });
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

const navObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      document.querySelectorAll('[data-nav]').forEach(link => link.classList.toggle('active', link.dataset.nav === entry.target.id));
    }
  });
}, { rootMargin: '-35% 0px -55% 0px' });
document.querySelectorAll('#experience,#mecanique,#prototype,#equipe').forEach(section => navObserver.observe(section));

const count = document.querySelector('[data-count]');
const countObserver = new IntersectionObserver(entries => {
  if (!entries[0].isIntersecting) return;
  countObserver.disconnect();
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { count.textContent = '504'; return; }
  const start = performance.now();
  function frame(now) {
    const t = Math.min((now - start) / 1400, 1);
    count.textContent = Math.round(504 * (1 - Math.pow(1 - t, 3)));
    if (t < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}, { threshold: .5 });
countObserver.observe(count);

const progress = document.querySelector('.scroll-line');
let ticking = false;
function updateScroll() {
  const max = document.documentElement.scrollHeight - innerHeight;
  progress.style.width = `${max > 0 ? (scrollY / max) * 100 : 0}%`;
  ticking = false;
}
addEventListener('scroll', () => {
  if (!ticking) { requestAnimationFrame(updateScroll); ticking = true; }
}, { passive: true });
updateScroll();
