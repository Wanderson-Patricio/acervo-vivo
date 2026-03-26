const email = localStorage.getItem("email");
const password = localStorage.getItem("password");

document.addEventListener("DOMContentLoaded", function () {
  const api_url = "http://localhost:3000";


  fetch(`${api_url}/authentication/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify({ email, password }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Erro ao autenticar usuário");
      }
      return response.json();
    })
    .then((data) => {
      alert("Autenticação bem-sucedida:", data);
      // Redirecionar ou realizar ações após autenticação
    })
    .catch((error) => {
      console.error("Erro na autenticação:", error);
      alert("Falha na autenticação. Verifique suas credenciais.");
    });
});