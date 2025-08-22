const API_BASE = "http://localhost:8000";

const $ = (sel) => document.querySelector(sel);
const input = $("#inputText");
const btn = $("#btnConvert");
const base64Out = $("#base64Out");
const ctxLabel = $("#ctx");

btn.addEventListener("click", async () => {
  base64Out.textContent = "";
  const text = input.value.trim();
  if (!text) return alert("Please enter some text.");

  try {
    const res = await fetch(`${API_BASE}/api/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed: ${res.status}`);
    }
    const data = await res.json();
    const { audio_base64, used_provider } = data;

    // Print to browser console (requirement)
    console.log("Base64 Audio (", used_provider, ") →", audio_base64);

    // Show on page for screenshot
    base64Out.textContent = audio_base64;
    ctxLabel.textContent = `provider: ${used_provider}`;

    // (Optional) Play audio in page
    try {
      const src = `data:audio/wav;base64,${audio_base64}`;
      const audio = new Audio(src);
      await audio.play();
    } catch (_) {}
  } catch (e) {
    console.error(e);
    alert(e.message || "Something went wrong.");
  }
});
