// Extraits éditoriaux du CSV : aucune requête vers un modèle sur cette page.
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
const ids = Object.keys(scenarios);
function selectScenario(id) {
  const scenario = scenarios[id];
  if (!scenario) return;
  document.querySelector('#question-title').textContent = scenario.question;
  document.querySelector('#answer-text').textContent = scenario.answer;
  document.querySelector('#answer-detail').textContent = scenario.detail;
  document.querySelector('#topic').textContent = scenario.topic;
  document.querySelector('#source-title').textContent = '« ' + scenario.source + ' »';
  document.querySelector('#source-ref').textContent = 'Entrée ' + scenario.id + ' · data_pretraitee.csv';
  document.querySelector('#folio').textContent = 'FICHE ' + String(ids.indexOf(id) + 1).padStart(2, '0');
  document.querySelectorAll('.scenario').forEach(button => {
    const active = button.dataset.scenario === id;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
}
document.querySelectorAll('.scenario').forEach(button => {
  button.addEventListener('click', () => selectScenario(button.dataset.scenario));
});
selectScenario('absence');
