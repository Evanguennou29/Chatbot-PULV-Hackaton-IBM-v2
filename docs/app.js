// Exemples archivés du CSV ; aucun appel au modèle sur la présentation.
const scenarios = {
  absence: {
    topic: 'Scolarité · Absences',
    question: 'Quel est le quota d’absences autorisées par semestre ?',
    answer: 'Le jeu de données prévoit 18 absences autorisées par semestre. Au-delà, un avertissement est envoyé. À la 29e absence, la compensation entre modules est perdue ; à la 39e, une convocation en conseil de discipline est prévue.',
    detail: 'Un régime différent est indiqué pour Executive Education : 10 demi-journées pour l’année académique.',
    source: "Quel est le quota d'absence autorisée par semestre?", id: '2135'
  },
  justificatif: {
    topic: 'Scolarité · Justificatifs',
    question: 'Comment déposer un justificatif d’absence ?',
    answer: 'Depuis votre plateforme, ouvrez « Scolarité », puis « Absences ». Sélectionnez « Ajouter un justificatif d’absence » pour transmettre votre document.',
    detail: 'Le dépôt d’un document ne garantit pas que l’absence sera excusée. Référez-vous aux conditions du règlement et à votre scolarité.',
    source: 'Quelle est la procédure pour déposer un justificatif?', id: '2141'
  },
  isic: {
    topic: 'Vie étudiante · Carte ISIC',
    question: 'À quoi sert la carte ISIC ?',
    answer: 'La carte étudiante internationale ISIC donne accès à des réductions en France et à l’étranger. Le jeu de données la présente sous une forme dématérialisée.',
    detail: 'Cet exemple reprend les informations archivées dans le projet. Pour les modalités actuelles, consultez les services de votre école.',
    source: "Qu'est ce que la carte ISIC ?", id: '2147'
  }
};

const sources = {
  "2135": "Vous disposez d'un quota de 18 absences autorisées par semestre. Au-delà, vous recevez un mail d'avertissement et un commentaire est inscrit sur votre bulletin. A la 29ème absence vous perdez la compensation entre les modules. A la 39ème absence, vous êtes convoqué en conseil de discipline. Pour Executive Education : Vous disposez d'un quota de 10 demi-journées d'absences autorisées pour l'année académique. Au-delà, vous recevrez un mail demandant de justifier vos absences et une convocation administrative vous sera transmise.",
  "2141": "Lorsque vous êtes connecté à votre plateforme, vous devez allez dans l'onglet \"scolarité\" et sélectionner \"absences\" puis \"ajouter un justificatif d'abence\".",
  "2147": "La carte d'identité étudiant internationale appelée ISIC vous permet de bénéficier de réductions en France et à l'étranger. Elle est dématérialisée."
};

const ids = Object.keys(scenarios);
const labels = { absence: 'Les absences', justificatif: 'Déposer un justificatif', isic: 'La carte ISIC' };
const views = ['conversation', 'demo', 'projet', 'equipe'];
let selectedScenario = 'absence';

function showView(id, focus = false) {
  const current = views.includes(id) ? id : 'conversation';
  document.querySelectorAll('.view').forEach(view => { view.hidden = view.id !== current; });
  document.querySelectorAll('[data-view]').forEach(link => {
    const active = link.dataset.view === current;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  // A hidden video must stop playing when the visitor leaves its view.
  if (current !== 'demo') document.querySelector('video').pause();
  if (focus) {
    const heading = document.querySelector('#' + current + ' h2');
    heading.setAttribute('tabindex', '-1');
    heading.focus({ preventScroll: true });
  }
}

function selectScenario(id) {
  const scenario = scenarios[id];
  if (!scenario) return;
  selectedScenario = id;
  document.querySelector('#question-text').textContent = scenario.question;
  document.querySelector('#answer-text').textContent = scenario.answer;
  document.querySelector('#answer-detail').textContent = scenario.detail;
  document.querySelector('#topic').textContent = scenario.topic;
  document.querySelector('#source-title').textContent = scenario.source;
  document.querySelector('#source-id').textContent = scenario.id;
  document.querySelector('#source-content').textContent = sources[scenario.id];
  document.querySelector('#answer-reference').textContent = 'Reformulation de l’entrée ' + scenario.id;
  document.querySelector('#example-label').textContent = labels[id];
  document.querySelectorAll('.scenario').forEach(button => {
    const active = button.dataset.scenario === id;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
}

function moveExample(direction) {
  const index = (ids.indexOf(selectedScenario) + direction + ids.length) % ids.length;
  selectScenario(ids[index]);
}

document.querySelectorAll('.scenario').forEach(button => {
  button.addEventListener('click', () => {
    selectScenario(button.dataset.scenario);
    showView('conversation');
    if (location.hash !== '#conversation') location.hash = 'conversation';
  });
});
document.querySelector('#previous-example').addEventListener('click', () => moveExample(-1));
document.querySelector('#next-example').addEventListener('click', () => moveExample(1));
document.querySelectorAll('[data-view]').forEach(link => {
  link.addEventListener('click', () => showView(link.dataset.view, true));
});
window.addEventListener('hashchange', () => {
  const view = location.hash.slice(1);
  if (views.includes(view)) showView(view, true);
});

const compactLayout = matchMedia('(max-width: 960px)');
function setSourceLayout() { document.querySelector('.inspector details').open = !compactLayout.matches; }
compactLayout.addEventListener('change', setSourceLayout);
setSourceLayout();
selectScenario('absence');
showView(location.hash.slice(1));
