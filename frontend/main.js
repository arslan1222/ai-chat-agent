const messagesEl  = document.getElementById("messages");
const inputEl     = document.getElementById("user-input");
const sendBtn     = document.getElementById("send-btn");
const usagePill   = document.getElementById("usage-pill");
const statusText  = document.getElementById("status-text");
const charCount   = document.getElementById("char-count");
const limitBanner = document.getElementById("limit-banner");
const clearBtn    = document.getElementById("clear-btn");
const userAvatar  = document.getElementById("user-avatar");

let isWaiting = false;
let msgLimit  = 100;
let msgCount  = 0;

// ── Bootstrap ──────────────────────────────────────────────────
async function init() {
  try {
    const res = await fetch("/auth/me");
    if (res.status === 401) { location.href = "/"; return; }
    const user = await res.json();

    msgCount = user.today_count;
    msgLimit = user.daily_limit;
    updateUsage();

    if (user.picture) {
      userAvatar.src = user.picture;
      userAvatar.style.display = "";
    }

    // Load history
    const hRes  = await fetch("/api/chat/history");
    const msgs  = await hRes.json();
    if (msgs.length > 0) {
      // Clear the default greeting
      messagesEl.innerHTML = "";
      msgs.forEach(m => appendMessage(m.role, m.content));
    }
  } catch (e) {
    console.error(e);
  }
}

// ── Render helpers ─────────────────────────────────────────────
function appendMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;

  const av = document.createElement("div");
  av.className = "msg-avatar";
  av.textContent = role === "user" ? "Me" : "AI";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.textContent = text;

  wrap.appendChild(av);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return wrap;
}

function showTyping() {
  const wrap   = document.createElement("div");
  wrap.className = "msg assistant typing";
  wrap.id = "typing-indicator";

  const av = document.createElement("div");
  av.className = "msg-avatar";
  av.textContent = "AI";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';

  wrap.appendChild(av);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function removeTyping() {
  const t = document.getElementById("typing-indicator");
  if (t) t.remove();
}

function updateUsage() {
  usagePill.textContent = `${msgCount} / ${msgLimit}`;
  usagePill.className = "usage-pill";
  if (msgCount >= msgLimit) {
    usagePill.classList.add("full");
    limitBanner.classList.remove("hidden");
    inputEl.disabled = true;
    sendBtn.disabled = true;
    statusText.textContent = "Daily limit reached";
  } else if (msgCount >= msgLimit * 0.8) {
    usagePill.classList.add("warn");
  }
}

// ── Send message ───────────────────────────────────────────────
async function sendMessage() {
  if (isWaiting) return;
  const text = inputEl.value.trim();
  if (!text) return;

  appendMessage("user", text);
  inputEl.value = "";
  charCount.textContent = "0 chars";
  isWaiting = true;
  statusText.textContent = "GPT-OSS-120B is thinking…";
  sendBtn.disabled = true;
  showTyping();

  try {
    const res  = await fetch("/api/chat/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();

    removeTyping();

    if (res.status === 429 || data.error === "limit_reached") {
      limitBanner.classList.remove("hidden");
      inputEl.disabled = true;
      sendBtn.disabled = true;
      statusText.textContent = "Daily limit reached";
      return;
    }
    if (!res.ok) {
      appendMessage("assistant", `⚠️ Error: ${data.error || "Unknown error"}`);
      return;
    }

    appendMessage("assistant", data.reply);
    msgCount = data.count;
    updateUsage();
    statusText.textContent = "GPT-OSS-120B ready";
  } catch (e) {
    removeTyping();
    appendMessage("assistant", "⚠️ Network error. Please try again.");
    statusText.textContent = "Error – retry?";
  } finally {
    isWaiting = false;
    if (!inputEl.disabled) sendBtn.disabled = false;
  }
}

// ── Event listeners ────────────────────────────────────────────
sendBtn.addEventListener("click", sendMessage);

inputEl.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

inputEl.addEventListener("input", () => {
  const len = inputEl.value.length;
  charCount.textContent = `${len} char${len !== 1 ? "s" : ""}`;
  // Auto-grow
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 140) + "px";
});

clearBtn.addEventListener("click", async (e) => {
  e.preventDefault();
  if (!confirm("Clear all conversation history?")) return;
  await fetch("/api/chat/clear", { method: "DELETE" });
  messagesEl.innerHTML = "";
  appendMessage("assistant", "Conversation cleared. How can I help you?");
});

// ── Start ──────────────────────────────────────────────────────
init();