// ── Toggle helper ──────────────────────────────────────────────
function setupToggle(id, labelId) {
  const toggle = document.getElementById(id);
  const label  = document.getElementById(labelId);
  toggle.addEventListener("click", () => {
    const isOn = toggle.dataset.on === "true";
    toggle.dataset.on = String(!isOn);
    toggle.classList.toggle("on", !isOn);
    label.textContent = !isOn ? "Enabled" : "Disabled";
  });
}

function isToggleOn(id) {
  return document.getElementById(id).dataset.on === "true";
}

function setToggle(id, labelId, value) {
  const toggle = document.getElementById(id);
  toggle.dataset.on = String(value);
  toggle.classList.toggle("on", value);
  document.getElementById(labelId).textContent = value ? "Enabled" : "Disabled";
}

function showToast(id) {
  const t = document.getElementById(id);
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2500);
}

// ── Load existing settings ──────────────────────────────────────
async function loadSettings() {
  try {
    const res  = await fetch("/api/integrations/");
    if (res.status === 401) { location.href = "/"; return; }
    const data = await res.json();

    if (data.whatsapp) {
      document.getElementById("wa-number").value = data.whatsapp.number || "";
      setToggle("wa-toggle", "wa-toggle-label", data.whatsapp.enabled);
    }
    if (data.ecommerce) {
      document.getElementById("ec-type").value = data.ecommerce.store_type || "custom";
      document.getElementById("ec-url").value  = data.ecommerce.store_url  || "";
      setToggle("ec-toggle", "ec-toggle-label", data.ecommerce.enabled);
    }
  } catch (e) {
    console.error("Failed to load settings", e);
  }
}

// ── Save WhatsApp ───────────────────────────────────────────────
async function saveWhatsApp() {
  const body = {
    number:  document.getElementById("wa-number").value.trim(),
    api_key: document.getElementById("wa-api-key").value.trim(),
    enabled: isToggleOn("wa-toggle"),
  };
  const res = await fetch("/api/integrations/whatsapp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.ok) {
    document.getElementById("wa-api-key").value = "";
    showToast("wa-toast");
  } else {
    alert("Failed to save WhatsApp settings.");
  }
}

// ── Save E-commerce ─────────────────────────────────────────────
async function saveEcommerce() {
  const body = {
    store_type: document.getElementById("ec-type").value,
    store_url:  document.getElementById("ec-url").value.trim(),
    api_key:    document.getElementById("ec-api-key").value.trim(),
    enabled:    isToggleOn("ec-toggle"),
  };
  const res = await fetch("/api/integrations/ecommerce", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.ok) {
    document.getElementById("ec-api-key").value = "";
    showToast("ec-toast");
  } else {
    alert("Failed to save e-commerce settings.");
  }
}

// ── Init ────────────────────────────────────────────────────────
setupToggle("wa-toggle", "wa-toggle-label");
setupToggle("ec-toggle", "ec-toggle-label");
loadSettings();