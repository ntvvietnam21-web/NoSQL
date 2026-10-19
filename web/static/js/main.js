document.querySelectorAll('.alert').forEach((el) => {
  setTimeout(() => el.classList.add('fade-out'), 3500);
});
