const mobile = matchMedia('(max-width: 760px)');
const menus = document.querySelectorAll('[data-menu]');
const sidebar = document.querySelector('#sidebar');
const scrim = document.querySelector('#nav-scrim');
let menuTrigger;
function toggleMenu(open) {
  if (open) menuTrigger = document.activeElement;
  document.body.classList.toggle('nav-open', open);
  menus.forEach(button => button.setAttribute('aria-expanded', String(open)));
  if (scrim) scrim.hidden = !open;
  if (sidebar) sidebar.toggleAttribute('inert', mobile.matches && !open);
  const workspace = document.querySelector('.workspace');
  if (workspace) workspace.toggleAttribute('inert', open);
  if (open) sidebar?.querySelector('.nav-list a')?.focus();
  else menuTrigger?.focus();
}
menus.forEach(button => button.addEventListener('click', () => toggleMenu(!document.body.classList.contains('nav-open'))));
scrim?.addEventListener('click', () => toggleMenu(false));
function setLayout() {
  toggleMenu(false);
  document.querySelectorAll('[data-mobile-collapse]').forEach(details => { details.open = !mobile.matches; });
}
mobile.addEventListener('change', setLayout);
setLayout();
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') toggleMenu(false);
  if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.target.matches('input,textarea,select')) {
    const search = document.querySelector('input[type="search"]');
    if (search) { event.preventDefault(); search.focus(); }
  }
});
document.querySelectorAll('form[data-confirm]').forEach(form => {
  form.addEventListener('submit', event => { if (!confirm(form.dataset.confirm)) event.preventDefault(); });
});
const type = document.querySelector('#question-type');
function updateType() {
  if (!type) return;
  document.querySelector('#editor-options').hidden = ['判断题', '填空题'].includes(type.value);
  document.querySelector('#answer-hint').textContent = {
    '单选题': '填写一个选项字母，例如 B。', '多选题': '填写全部正确选项，例如 ACD，顺序不限。',
    '判断题': '填写“正确”或“错误”。', '填空题': '填写完整答案，文字顺序需要一致。'
  }[type.value];
}
type?.addEventListener('change', updateType);
updateType();
const examMode = document.querySelector('#exam-mode');
function updateDuration() {
  if (examMode) document.querySelector('#exam-duration').hidden = examMode.value !== 'timed';
}
examMode?.addEventListener('change', updateDuration);
updateDuration();
const draftForm = document.querySelector('form[data-draft]');
const clear = document.querySelector('[data-clear-draft]');
try { if (clear) localStorage.removeItem(clear.dataset.clearDraft); } catch { /* Storage may be unavailable. */ }
if (draftForm) {
  const key = draftForm.dataset.draft;
  let draft = {};
  try { draft = JSON.parse(localStorage.getItem(key) || '{}'); } catch { /* Start with an empty draft. */ }
  for (const input of draftForm.querySelectorAll('[name^="answer"]')) {
    if (!draft?.[input.name]) continue;
    if (['checkbox', 'radio'].includes(input.type)) input.checked = draft[input.name].includes(input.value);
    else input.value = draft[input.name][0];
  }
  draftForm.addEventListener('input', () => {
    const answers = {};
    for (const [name, value] of new FormData(draftForm)) (answers[name] ??= []).push(value);
    try { localStorage.setItem(key, JSON.stringify(answers)); } catch { /* Answer submission still works. */ }
  });
}
const exam = document.querySelector('form[data-exam]');
if (exam) {
  const cards = [...exam.querySelectorAll('.question-card')];
  const sheet = document.querySelector('#exam-sheet');
  const previous = document.querySelector('[data-exam-step="-1"]');
  const next = document.querySelector('[data-exam-step="1"]');
  const hashIndex = () => Math.max(0, cards.findIndex(card => '#' + card.id === location.hash));
  let current = hashIndex();
  function showQuestion(index, navigate = false) {
    current = Math.max(0, Math.min(index, cards.length - 1));
    exam.classList.toggle('paged-exam', mobile.matches);
    cards.forEach((card, i) => { card.hidden = mobile.matches && i !== current; });
    previous.disabled = current === 0;
    next.textContent = current === cards.length - 1 ? '检查交卷' : '下一题';
    document.querySelector('#exam-position').textContent = `${current + 1} / ${cards.length}`;
    if (navigate) {
      history.replaceState(null, '', '#' + cards[current].id);
      if (mobile.matches) window.scrollTo(0, 0);
    }
  }
  function openSheet() {
    let answered = 0;
    cards.forEach((card, i) => {
      const done = [...card.querySelectorAll('input:checked,textarea')].some(input => input.value.trim());
      answered += Number(done);
      const link = sheet.querySelectorAll('.question-nav a')[i];
      link.classList.toggle('answered', done);
      link.setAttribute('aria-label', `第 ${i + 1} 题，${done ? '已答' : '未答'}`);
      if (i === current) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    document.querySelector('#exam-status').textContent = `已答 ${answered} / ${cards.length} 题 · 还有 ${cards.length - answered} 题未答`;
    sheet.showModal();
  }
  document.querySelector('[data-open-exam]').addEventListener('click', openSheet);
  document.querySelector('[data-close-exam]').addEventListener('click', () => sheet.close());
  document.querySelectorAll('[data-exam-step]').forEach(button => button.addEventListener('click', () => {
    if (button === next && current === cards.length - 1) openSheet();
    else showQuestion(current + Number(button.dataset.examStep), true);
  }));
  sheet.querySelectorAll('.question-nav a').forEach((link, i) => link.addEventListener('click', event => {
    event.preventDefault(); sheet.close(); showQuestion(i, true);
  }));
  window.addEventListener('hashchange', () => showQuestion(hashIndex(), mobile.matches));
  mobile.addEventListener('change', () => { sheet.close(); showQuestion(hashIndex(), mobile.matches); });
  showQuestion(current);
  const deadline = Number(exam.dataset.deadline);
  if (deadline) {
    let submitted = false;
    const tick = () => {
      const seconds = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
      document.querySelector('#countdown').textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
      if (!seconds && !submitted) { submitted = true; exam.requestSubmit(); }
    };
    exam.addEventListener('submit', () => { submitted = true; });
    tick();
    setInterval(tick, 1000);
  }
}
