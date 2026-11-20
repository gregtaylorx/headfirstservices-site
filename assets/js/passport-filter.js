document.getElementById('passport-filter').addEventListener('input', function(e) {
  var q = e.target.value.toLowerCase();
  document.querySelectorAll('#passport-table tbody tr').forEach(function(row) {
    row.style.display = row.dataset.name.indexOf(q) === -1 ? 'none' : '';
  });
});
