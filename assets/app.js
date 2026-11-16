(() => {
  const search = document.querySelector('#search');
  if (!search) return;
  const cards = [...document.querySelectorAll('[data-note]')];
  const buttons = [...document.querySelectorAll('[data-category]')];
  const status = document.querySelector('#result-status');
  let category = '全部';
  function update() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      card.hidden = !(category === '全部' || card.dataset.note === category) ||
        !card.dataset.search.toLocaleLowerCase().includes(query);
      if (!card.hidden) visible++;
    }
    status.textContent = `顯示 ${visible} 篇筆記`;
    document.querySelector('.empty').hidden = visible !== 0;
  }
  for (const button of buttons) {
    button.addEventListener('click', () => {
      category = button.dataset.category;
      for (const item of buttons) {
        const active = item === button;
        item.classList.toggle('active', active);
        item.setAttribute('aria-pressed', String(active));
      }
      update();
    });
  }
  search.addEventListener('input', update);
  document.querySelector('.library-tools').hidden = false;
  status.hidden = false;
})();
