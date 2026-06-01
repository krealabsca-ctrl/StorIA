/* Componente de chat compartido entre cliente y admin. */
(function () {
  "use strict";

  const root = document.getElementById("chat");
  if (!root) return;

  const endpoint = root.dataset.endpoint;
  const title = root.dataset.title || "Asistente StorAI";
  const subtitle = root.dataset.subtitle || "En línea";
  const greeting = root.dataset.greeting || "¡Hola! ¿En qué puedo ayudarte?";
  const mode = root.dataset.mode || "customer";

  const initialSuggestions = (root.dataset.suggestions || "")
    .split("|")
    .map((s) => s.trim())
    .filter(Boolean);

  // SVG icons
  const ICONS = {
    bot: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
    package: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
    location: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
  };

  root.innerHTML = `
    <div class="chat">
      <header class="chat-head">
        <div class="avatar">${ICONS.bot}</div>
        <div style="flex:1;">
          <div class="title">${escapeHTML(title)}</div>
          <div class="subtitle"><span class="pulse"></span> ${escapeHTML(subtitle)}</div>
        </div>
      </header>
      <div class="messages" id="chat-messages"></div>
      <form id="chat-form" autocomplete="off">
        <input id="chat-input" type="text"
               placeholder="Escribe tu mensaje..."
               maxlength="500" required />
        <button type="submit" aria-label="Enviar">${ICONS.send}</button>
      </form>
    </div>
  `;

  const messagesEl = root.querySelector("#chat-messages");
  const form = root.querySelector("#chat-form");
  const input = root.querySelector("#chat-input");
  const submitBtn = form.querySelector("button[type='submit']");

  appendBotMessage({ reply: greeting, suggestions: initialSuggestions });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    appendUserMessage(text);
    input.value = "";
    await sendToBot(text);
  });

  async function sendToBot(text) {
    submitBtn.disabled = true;
    const typingId = appendTypingIndicator();
    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      removeMessage(typingId);
      if (!res.ok) {
        appendBotMessage({
          reply: "Tuve un problema procesando tu mensaje. Intenta de nuevo.",
        });
        return;
      }
      const data = await res.json();
      appendBotMessage(data);
    } catch (err) {
      removeMessage(typingId);
      appendBotMessage({
        reply: "No pude conectarme al servidor. Verifica tu conexión.",
      });
    } finally {
      submitBtn.disabled = false;
      input.focus();
    }
  }

  function appendUserMessage(text) {
    const node = document.createElement("div");
    node.className = "msg user";
    node.innerHTML = `
      <div class="bubble">${escapeHTML(text)}</div>
      <div class="time">${timeNow()}</div>
    `;
    messagesEl.appendChild(node);
    scrollToBottom();
  }

  function appendBotMessage(data) {
    const node = document.createElement("div");
    node.className = "msg bot";
    let html = `<div class="bubble">${formatReply(data.reply || "")}`;

    if (data.products && data.products.length > 0) {
      html += '<div class="product-list">';
      for (const p of data.products) {
        html += renderProductCard(p);
      }
      html += "</div>";
    }
    html += "</div>";

    if (data.suggestions && data.suggestions.length > 0) {
      html += '<div class="suggestions">';
      for (const s of data.suggestions) {
        html += `<button type="button" data-suggestion="${escapeHTML(s)}">${escapeHTML(s)}</button>`;
      }
      html += "</div>";
    }
    html += `<div class="time">${timeNow()}</div>`;
    node.innerHTML = html;

    node.querySelectorAll("button[data-suggestion]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const text = btn.dataset.suggestion;
        appendUserMessage(text);
        sendToBot(text);
      });
    });

    messagesEl.appendChild(node);
    scrollToBottom();
  }

  function appendTypingIndicator() {
    const id = "typing-" + Math.random().toString(36).slice(2);
    const node = document.createElement("div");
    node.className = "msg bot";
    node.id = id;
    node.innerHTML = `<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>`;
    messagesEl.appendChild(node);
    scrollToBottom();
    return id;
  }

  function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function renderProductCard(p) {
    let extra = "";
    if (mode === "admin") {
      const stockClass =
        p.stock_current === 0 ? "stock-out" :
        p.stock_current != null && p.stock_current <= 10 ? "stock-low" : "";
      const stockLine = p.stock_current != null
        ? `<span class="stock-line ${stockClass}">${p.stock_current} uds</span>`
        : "";
      const locLine = p.location
        ? `<div class="loc">${ICONS.location}<span>${escapeHTML(p.location)}</span></div>`
        : `<div class="loc-empty">${ICONS.alert}<span>Sin ubicación asignada</span></div>`;
      extra = `
        <div class="meta">
          <span class="sku">${escapeHTML(p.sku)}</span>
          <span class="price">$${Number(p.price).toFixed(2)}</span>
          ${stockLine}
        </div>
        ${locLine}
      `;
    } else {
      const status = p.in_stock
        ? '<span class="tag ok"><span class="tag-dot"></span>Disponible</span>'
        : '<span class="tag out"><span class="tag-dot"></span>Sin stock</span>';
      extra = `
        <div class="meta">
          <span class="sku">${escapeHTML(p.sku)}</span>
          <span class="price">$${Number(p.price).toFixed(2)}</span>
          ${status}
        </div>
      `;
    }
    return `
      <div class="product-card">
        <div class="thumb">${ICONS.package}</div>
        <div class="info">
          <div class="name">${escapeHTML(p.name)}</div>
          ${extra}
        </div>
      </div>
    `;
  }

  function formatReply(text) {
    const safe = escapeHTML(text);
    return safe
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  function timeNow() {
    const d = new Date();
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function escapeHTML(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
})();
