// static/script.js
const form = document.getElementById("form");
const respuestaDiv = document.getElementById("respuesta");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  respuestaDiv.innerHTML = "Procesando...";

  const pregunta = document.getElementById("pregunta").value;
  const imagenInput = document.getElementById("imagen");
  const formData = new FormData();
  formData.append("pregunta", pregunta);

  if (imagenInput.files.length > 0) {
    formData.append("imagen", imagenInput.files[0]);
  }

  try {
    const res = await fetch("/preguntar", {
      method: "POST",
      body: formData
    });
    const json = await res.json();
    if (json.error) {
      respuestaDiv.innerHTML = `<b>Error:</b> ${json.detail || json.error}`;
    } else {
      respuestaDiv.innerHTML = json.respuesta.replace(/\n/g, "<br>");
    }
  } catch (err) {
    respuestaDiv.innerHTML = `<b>Error de conexión:</b> ${err.message}`;
  }
});