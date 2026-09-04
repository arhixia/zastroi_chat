(function () {
  var script = document.currentScript;
  var siteId = script.getAttribute("data-site-id");
  var apiBase = new URL(script.src).origin;

  var sessionKey = "zastroi_session_" + siteId;
  var visitorKey = "zastroi_visitor_" + siteId;

  var sessionId = localStorage.getItem(sessionKey);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(sessionKey, sessionId);
  }

  var visitorId = localStorage.getItem(visitorKey);
  if (!visitorId) {
    visitorId = crypto.randomUUID();
    localStorage.setItem(visitorKey, visitorId);
  }

  // ===================== СТИЛИ =====================
  var style = document.createElement("style");
  style.textContent =
    ".zw-root, .zw-root * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }" +
    ".zw-launcher { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; border-radius: 50%;" +
    " background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border: none; cursor: pointer; z-index: 999999;" +
    " box-shadow: 0 4px 14px rgba(37,99,235,0.4); display: flex; align-items: center; justify-content: center;" +
    " transition: transform 0.2s ease, box-shadow 0.2s ease; }" +
    ".zw-launcher:hover { transform: scale(1.06); box-shadow: 0 6px 20px rgba(37,99,235,0.5); }" +
    ".zw-launcher svg { width: 26px; height: 26px; transition: transform 0.25s ease, opacity 0.25s ease; }" +
    ".zw-launcher .zw-icon-close { position: absolute; opacity: 0; transform: rotate(-90deg); }" +
    ".zw-launcher.zw-open .zw-icon-chat { opacity: 0; transform: rotate(90deg); }" +
    ".zw-launcher.zw-open .zw-icon-close { opacity: 1; transform: rotate(0deg); }" +
    ".zw-window { position: fixed; bottom: 92px; right: 20px; width: 340px; height: 460px; max-height: 70vh;" +
    " background: #fff; border-radius: 16px; box-shadow: 0 12px 36px rgba(0,0,0,0.18); display: flex; flex-direction: column;" +
    " overflow: hidden; z-index: 999999; opacity: 0; transform: translateY(16px) scale(0.98); pointer-events: none;" +
    " transition: opacity 0.18s ease, transform 0.18s ease; }" +
    ".zw-window.zw-visible { opacity: 1; transform: translateY(0) scale(1); pointer-events: auto; }" +
    ".zw-header { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; padding: 14px 16px;" +
    " display: flex; align-items: center; gap: 10px; flex-shrink: 0; }" +
    ".zw-header-avatar { width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,0.2);" +
    " display: flex; align-items: center; justify-content: center; flex-shrink: 0; }" +
    ".zw-header-avatar svg { width: 18px; height: 18px; }" +
    ".zw-header-text { flex: 1; min-width: 0; }" +
    ".zw-header-title { font-size: 14px; font-weight: 600; line-height: 1.3; }" +
    ".zw-header-status { font-size: 11px; opacity: 0.85; display: flex; align-items: center; gap: 5px; }" +
    ".zw-header-status::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #4ade80; display: inline-block; }" +
    ".zw-header-close { background: none; border: none; color: #fff; cursor: pointer; opacity: 0.85; padding: 4px;" +
    " display: flex; border-radius: 6px; transition: background 0.15s, opacity 0.15s; }" +
    ".zw-header-close:hover { background: rgba(255,255,255,0.15); opacity: 1; }" +
    ".zw-log { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; background: #f8fafc; }" +
    ".zw-log::-webkit-scrollbar { width: 6px; }" +
    ".zw-log::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }" +
    ".zw-bubble { max-width: 82%; padding: 9px 13px; border-radius: 14px; font-size: 13.5px; line-height: 1.45;" +
    " word-wrap: break-word; animation: zw-fade-in 0.2s ease; }" +
    "@keyframes zw-fade-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }" +
    ".zw-bubble.zw-user { align-self: flex-end; background: #2563eb; color: #fff; border-bottom-right-radius: 4px; }" +
    ".zw-bubble.zw-bot { align-self: flex-start; background: #fff; color: #1e293b; border: 1px solid #e2e8f0;" +
    " border-bottom-left-radius: 4px; }" +
    ".zw-typing { align-self: flex-start; display: flex; gap: 4px; padding: 12px 14px; background: #fff;" +
    " border: 1px solid #e2e8f0; border-radius: 14px; border-bottom-left-radius: 4px; }" +
    ".zw-typing span { width: 6px; height: 6px; border-radius: 50%; background: #94a3b8; animation: zw-bounce 1.2s infinite; }" +
    ".zw-typing span:nth-child(2) { animation-delay: 0.15s; }" +
    ".zw-typing span:nth-child(3) { animation-delay: 0.3s; }" +
    "@keyframes zw-bounce { 0%, 60%, 100% { transform: translateY(0); opacity: 0.5; } 30% { transform: translateY(-4px); opacity: 1; } }" +
    ".zw-input-row { display: flex; align-items: center; gap: 8px; padding: 10px; border-top: 1px solid #e2e8f0;" +
    " background: #fff; flex-shrink: 0; }" +
    ".zw-input { flex: 1; border: 1px solid #e2e8f0; border-radius: 20px; padding: 9px 14px; font-size: 13.5px;" +
    " outline: none; transition: border-color 0.15s; min-width: 0; }" +
    ".zw-input:focus { border-color: #2563eb; }" +
    ".zw-input:disabled { background: #f1f5f9; color: #94a3b8; }" +
    ".zw-send { border: none; background: #2563eb; color: #fff; width: 34px; height: 34px; border-radius: 50%; cursor: pointer;" +
    " display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background 0.15s, opacity 0.15s; }" +
    ".zw-send:hover:not(:disabled) { background: #1d4ed8; }" +
    ".zw-send:disabled { opacity: 0.5; cursor: default; }" +
    ".zw-send svg { width: 15px; height: 15px; }" +
    "@media (max-width: 480px) {" +
    "  .zw-window { top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; max-height: 100%;" +
    "    border-radius: 0; bottom: 0; }" +
    "  .zw-launcher { bottom: 16px; right: 16px; }" +
    "  .zw-input-row { padding-bottom: max(10px, env(safe-area-inset-bottom)); }" +
    "}";
  document.head.appendChild(style);

  // ===================== РАЗМЕТКА =====================
  var root = document.createElement("div");
  root.className = "zw-root";

  var ICON_CHAT =
    '<svg class="zw-icon-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>';
  var ICON_CLOSE =
    '<svg class="zw-icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
  var ICON_SEND =
    '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>';
  var ICON_BOT =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>';

  var button = document.createElement("button");
  button.className = "zw-launcher";
  button.setAttribute("aria-label", "Открыть чат");
  button.innerHTML = ICON_CHAT + ICON_CLOSE;

  var windowEl = document.createElement("div");
  windowEl.className = "zw-window";

  var header = document.createElement("div");
  header.className = "zw-header";
  header.innerHTML =
    '<div class="zw-header-avatar">' + ICON_BOT + "</div>" +
    '<div class="zw-header-text">' +
    '<div class="zw-header-title">Чат с застройщиком</div>' +
    '<div class="zw-header-status">Онлайн</div>' +
    "</div>" +
    '<button class="zw-header-close" aria-label="Закрыть чат">' + ICON_CLOSE.replace('zw-icon-close', '') + "</button>";

  var log = document.createElement("div");
  log.className = "zw-log";

  var inputRow = document.createElement("div");
  inputRow.className = "zw-input-row";

  var input = document.createElement("input");
  input.className = "zw-input";
  input.placeholder = "Напишите сообщение...";

  var sendBtn = document.createElement("button");
  sendBtn.className = "zw-send";
  sendBtn.innerHTML = ICON_SEND;
  sendBtn.setAttribute("aria-label", "Отправить");

  inputRow.appendChild(input);
  inputRow.appendChild(sendBtn);
  windowEl.appendChild(header);
  windowEl.appendChild(log);
  windowEl.appendChild(inputRow);
  root.appendChild(button);
  root.appendChild(windowEl);
  document.body.appendChild(root);

  // ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ОТОБРАЖЕНИЯ =====================
  function addMessage(role, text) {
    var bubble = document.createElement("div");
    var isUser = role === "user";
    bubble.className = "zw-bubble " + (isUser ? "zw-user" : "zw-bot");
    if (isUser) {
      // сообщение пользователя — только текст, без интерпретации как HTML (иначе XSS)
      bubble.textContent = text;
    } else {
      // сообщения бота формируются нашим же кодом/бэкендом, поэтому HTML (переносы, <b>) safe
      bubble.innerHTML = text.replace(/\n/g, "<br>");
    }
    log.appendChild(bubble);
    log.scrollTop = log.scrollHeight;
  }

  var typingEl = null;
  function showTyping() {
    if (typingEl) return;
    typingEl = document.createElement("div");
    typingEl.className = "zw-typing";
    typingEl.innerHTML = "<span></span><span></span><span></span>";
    log.appendChild(typingEl);
    log.scrollTop = log.scrollHeight;
  }
  function hideTyping() {
    if (typingEl) {
      typingEl.remove();
      typingEl = null;
    }
  }

  function setInputEnabled(enabled) {
    input.disabled = !enabled;
    sendBtn.disabled = !enabled;
  }

  function openChat() {
    windowEl.classList.add("zw-visible");
    button.classList.add("zw-open");
    input.focus();
  }
  function closeChat() {
    windowEl.classList.remove("zw-visible");
    button.classList.remove("zw-open");
  }

  button.addEventListener("click", function () {
    windowEl.classList.contains("zw-visible") ? closeChat() : openChat();
  });
  header.querySelector(".zw-header-close").addEventListener("click", closeChat);

  // ===================== СОСТОЯНИЕ СБОРА ЛИДА (логика без изменений) =====================
  var leadState = {
    step: "none", // none, name, phone, confirm
    tempName: "",
    tempPhone: ""
  };

  function processRegularMessage(text) {
    showTyping();
    setInputEnabled(false);
    fetch(apiBase + "/api/v1/widget/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        site_id: siteId,
        session_id: sessionId,
        visitor_id: visitorId,
        message: text,
        current_page_url: window.location.href,
        referrer: document.referrer || null,
      }),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        hideTyping();
        addMessage("assistant", data.answer);
        if (data.ask_lead) {
          leadState.step = "name";
          addMessage("assistant", "Чтобы дать точный ответ, позвольте узнать ваше имя?");
        }
      })
      .catch(function () {
        hideTyping();
        addMessage("assistant", "Не удалось получить ответ.");
      })
      .finally(function () {
        setInputEnabled(true);
        input.focus();
      });
  }

  function sendMessage() {
    var text = input.value.trim();
    if (!text) return;

    addMessage("user", text);
    input.value = "";

    // --- УМНАЯ ЛОГИКА СБОРА ЛИДА С ИИ-КЛАССИФИКАЦИЕЙ ---
    if (leadState.step === "name" || leadState.step === "phone") {
      showTyping();
      setInputEnabled(false);
      fetch(apiBase + "/api/v1/widget/classify-lead-response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        hideTyping();
        var category = data.category;

        if (leadState.step === "name") {
          if (category === "NAME") {
            leadState.tempName = text;
            leadState.step = "phone";
            addMessage("assistant", "Приятно познакомиться! Напишите ваш номер телефона для связи.");
          } else if (category === "REFUSAL") {
            leadState.step = "none";
            addMessage("assistant", "Хорошо, если передумаете — я всегда здесь. Чем еще могу помочь по ЖК?");
          } else {
            // QUESTION или PHONE — прерываем сбор и отвечаем на вопрос
            leadState.step = "none";
            setInputEnabled(true);
            processRegularMessage(text);
            return;
          }
        }
        else if (leadState.step === "phone") {
          if (category === "PHONE") {
            leadState.tempPhone = text;
            leadState.step = "confirm";
            addMessage("assistant", "Проверяем данные:<br><b>Имя:</b> " + leadState.tempName + "<br><b>Телефон:</b> " + text + "<br><br>Напишите <b>\"Да\"</b>, чтобы подтвердить согласие на обработку персональных данных.");
          } else if (category === "REFUSAL") {
            leadState.step = "none";
            addMessage("assistant", "Понял вас. Если будут вопросы по объектам — обращайтесь!");
          } else {
            // NAME или QUESTION — прерываем сбор и отвечаем на вопрос
            leadState.step = "none";
            setInputEnabled(true);
            processRegularMessage(text);
            return;
          }
        }
        setInputEnabled(true);
        input.focus();
      })
      .catch(function() {
        hideTyping();
        leadState.step = "none";
        setInputEnabled(true);
        processRegularMessage(text);
      });
      return;
    }

    // --- ПОДТВЕРЖДЕНИЕ ---
    if (leadState.step === "confirm") {
      if (text.toLowerCase().includes("да")) {
        showTyping();
        setInputEnabled(false);
        fetch(apiBase + "/api/v1/widget/lead", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            site_id: siteId,
            session_id: sessionId,
            last_message: text,
            name: leadState.tempName,
            phone: leadState.tempPhone
          })
        }).then(() => {
          hideTyping();
          addMessage("assistant", "✅ Спасибо! Заявка успешно отправлена. Менеджер свяжется с вами.");
          leadState.step = "none";
        }).catch(() => {
          hideTyping();
          addMessage("assistant", "Ошибка отправки. Попробуйте позже.");
          leadState.step = "none";
        }).finally(function () {
          setInputEnabled(true);
          input.focus();
        });
      } else {
        addMessage("assistant", "Хорошо, давайте начнем сначала. Как к вам обращаться?");
        leadState.step = "name";
      }
      return;
    }

    // --- ОБЫЧНЫЙ ЗАПРОС К RAG ---
    processRegularMessage(text);
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") sendMessage();
  });
})();