const loginButton = document.getElementById("login-button");

loginButton.addEventListener("click", function (event) {
  event.preventDefault(); // Evita o envio do formulário
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  localStorage.setItem("email", email);
  localStorage.setItem("password", password);

  window.location.href = '/authenticate'; // Redireciona para a página de autenticação
});
