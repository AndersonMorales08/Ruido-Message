// ---------- Onda decorativa del encabezado ----------
(function dibujarOnda() {
  const canvas = document.getElementById("wave");
  const ctx = canvas.getContext("2d");
  const barras = 60;
  const anchoBarra = canvas.width / barras;
  const alturas = Array.from({ length: barras }, () => Math.random());

  function render(t) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < barras; i++) {
      const fase = t / 700 + i * 0.35;
      const h = (0.25 + 0.75 * Math.abs(Math.sin(fase) * alturas[i])) * canvas.height;
      const x = i * anchoBarra;
      const y = (canvas.height - h) / 2;
      ctx.fillStyle = i % 7 === 0 ? "#e0a935" : "#35e0b2";
      ctx.globalAlpha = 0.85;
      ctx.fillRect(x, y, anchoBarra - 2, h);
    }
    requestAnimationFrame(render);
  }
  requestAnimationFrame(render);
})();

// ---------- Tabs ----------
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`panel-${tab.dataset.tab}`).classList.add("active");
  });
});

// ---------- Dropzones ----------
function conectarDropzone(dzId, inputId, chipId) {
  const dz = document.getElementById(dzId);
  const input = document.getElementById(inputId);
  const chip = document.getElementById(chipId);

  const mostrarArchivo = (file) => {
    if (!file) return;
    chip.textContent = `🎵 ${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
    chip.style.display = "block";
  };

  dz.addEventListener("click", () => input.click());
  input.addEventListener("change", () => mostrarArchivo(input.files[0]));

  ["dragenter", "dragover"].forEach((evt) =>
    dz.addEventListener(evt, (e) => {
      e.preventDefault();
      dz.classList.add("drag");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dz.addEventListener(evt, (e) => {
      e.preventDefault();
      dz.classList.remove("drag");
    })
  );
  dz.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
      input.files = e.dataTransfer.files;
      mostrarArchivo(file);
    }
  });

  return () => input.files[0] || null;
}

const getAudioOcultar = conectarDropzone("dz-ocultar", "audio-ocultar", "chip-ocultar");
const getAudioRevelar = conectarDropzone("dz-revelar", "audio-revelar", "chip-revelar");

// ---------- Helpers ----------
function mostrarError(boxId, texto) {
  const box = document.getElementById(boxId);
  box.textContent = texto;
  box.classList.add("show");
}
function ocultarError(boxId) {
  document.getElementById(boxId).classList.remove("show");
}
function ponerCargando(boton, cargando) {
  boton.disabled = cargando;
  boton.classList.toggle("loading", cargando);
}
function base64ABlob(base64, mime) {
  const bytes = atob(base64);
  const arr = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
  return new Blob([arr], { type: mime });
}

// ---------- Ocultar mensaje ----------
document.getElementById("btn-ocultar").addEventListener("click", async () => {
  const mensaje = document.getElementById("mensaje").value.trim();
  const audio = getAudioOcultar();
  const btn = document.getElementById("btn-ocultar");
  const urlBase = document.getElementById("url-encriptar").value.replace(/\/$/, "");

  ocultarError("error-ocultar");
  document.getElementById("resultado-ocultar").classList.remove("show");

  if (!mensaje) return mostrarError("error-ocultar", "Escribe un mensaje para esconder.");
  if (!audio) return mostrarError("error-ocultar", "Selecciona un archivo .wav.");

  const form = new FormData();
  form.append("mensaje", mensaje);
  form.append("audio", audio);

  ponerCargando(btn, true);
  try {
    const resp = await fetch(`${urlBase}/api/ocultar_mensaje`, { method: "POST", body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "Error desconocido");

    const blob = base64ABlob(data.audio_base64, "audio/wav");
    const url = URL.createObjectURL(blob);

    document.getElementById("audio-preview").src = url;
    const link = document.getElementById("link-descarga");
    link.href = url;
    link.download = data.nombre_archivo || "stego.wav";

    document.getElementById("valor-llave").textContent = `d = ${data.llave_privada}   |   n = ${data.n}`;
    document.getElementById("aviso-llave").textContent = data.aviso || "";

    document.getElementById("resultado-ocultar").classList.add("show");
  } catch (err) {
    mostrarError("error-ocultar", err.message);
  } finally {
    ponerCargando(btn, false);
  }
});

// ---------- Revelar mensaje ----------
document.getElementById("btn-revelar").addEventListener("click", async () => {
  const audio = getAudioRevelar();
  const llave = document.getElementById("llave").value.trim();
  const btn = document.getElementById("btn-revelar");
  const urlBase = document.getElementById("url-descifrar").value.replace(/\/$/, "");

  ocultarError("error-revelar");
  document.getElementById("resultado-revelar").classList.remove("show");

  if (!audio) return mostrarError("error-revelar", "Selecciona el archivo .wav con el mensaje escondido.");
  if (!llave) return mostrarError("error-revelar", "Ingresa la llave privada.");

  const form = new FormData();
  form.append("audio", audio);
  form.append("llave_privada", llave);

  ponerCargando(btn, true);
  try {
    const resp = await fetch(`${urlBase}/api/revelar_mensaje`, { method: "POST", body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "Error desconocido");

    document.getElementById("mensaje-recuperado").textContent = data.mensaje;
    document.getElementById("resultado-revelar").classList.add("show");
  } catch (err) {
    mostrarError("error-revelar", err.message);
  } finally {
    ponerCargando(btn, false);
  }
});
