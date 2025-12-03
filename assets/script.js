const searchInput = document.getElementById('searchInput');
searchInput.addEventListener('input', function() {
  const term = this.value.toLowerCase();
  document.querySelectorAll('.row.file').forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(term) ? '' : 'none';
  });
  document.querySelectorAll('.folder-block').forEach(folder => {
    const text = folder.textContent.toLowerCase();
    folder.style.display = text.includes(term) ? '' : 'none';
  });
});

/* folder toggle functionality */ 
document.querySelectorAll('.folder-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!expanded));
    const panel = document.getElementById(btn.getAttribute('aria-controls'));
    if(panel) panel.hidden = expanded;
  });
});
