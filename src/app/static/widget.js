(function () {
  var script = document.currentScript;
  var siteId = script.getAttribute("data-site-id");
  var privacyUrl = script.getAttribute("data-privacy-url") || "#";
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

    ".zw-window { position: fixed; bottom: 92px; right: 20px; width: 340px; height: 480px; max-height: 72vh;" +
    " background: #fff; border-radius: 16px; box-shadow: 0 12px 36px rgba(0,0,0,0.18); display: flex; flex-direction: column;" +
    " overflow: hidden; z-index: 999999; opacity: 0; transform: translateY(16px) scale(0.98); pointer-events: none;" +
    " transition: opacity 0.18s ease, transform 0.18s ease; }" +
    ".zw-window.zw-visible { opacity: 1; transform: translateY(0) scale(1); pointer-events: auto; }" +

    ".zw-header { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; padding: 14px 16px;" +
    " display: flex; align-items: center; gap: 10px; flex-shrink: 0; position: relative; }" +
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

    /* --- Значок заявки в углу шапки --- */
    ".zw-lead-trigger { position: absolute; top: -8px; right: -8px; width: 34px; height: 34px;" +
    " background: #f59e0b; border-radius: 50%; border: 2.5px solid #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.18);" +
    " display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 20;" +
    " transition: transform 0.2s ease; }" +
    ".zw-lead-trigger:hover { transform: scale(1.1); }" +
    ".zw-lead-trigger svg { width: 16px; height: 16px; color: #fff; }" +
    ".zw-lead-trigger.zw-pulse { animation: zw-pulse-anim 1.6s infinite; }" +
    "@keyframes zw-pulse-anim { 0% { box-shadow: 0 0 0 0 rgba(245,158,11,0.55); } 70% { box-shadow: 0 0 0 9px rgba(245,158,11,0); } 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0); } }" +

    ".zw-log { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; background: #f8fafc; }" +
    ".zw-log::-webkit-scrollbar { width: 6px; }" +
    ".zw-log::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }" +
    ".zw-bubble { max-width: 82%; padding: 9px 13px; border-radius: 14px; font-size: 13.5px; line-height: 1.45;" +
    " word-wrap: break-word; animation: zw-fade-in 0.2s ease; }" +
    "@keyframes zw-fade-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }" +
    ".zw-bubble.zw-user { align-self: flex-end; background: #2563eb; color: #fff; border-bottom-right-radius: 4px; }" +
    ".zw-bubble.zw-bot { align-self: flex-start; background: #fff; color: #1e293b; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; }" +

    ".zw-typing { align-self: flex-start; display: flex; gap: 4px; padding: 12px 14px; background: #fff;" +
    " border: 1px solid #e2e8f0; border-radius: 14px; border-bottom-left-radius: 4px; }" +
    ".zw-typing span { width: 6px; height: 6px; border-radius: 50%; background: #94a3b8; animation: zw-bounce 1.2s infinite; }" +
    ".zw-typing span:nth-child(2) { animation-delay: 0.15s; } .zw-typing span:nth-child(3) { animation-delay: 0.3s; }" +
    "@keyframes zw-bounce { 0%, 60%, 100% { transform: translateY(0); opacity: 0.5; } 30% { transform: translateY(-4px); opacity: 1; } }" +

    /* --- Выезжающая панель заявки --- */
    ".zw-lead-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15,23,42,0.35);" +
    " opacity: 0; pointer-events: none; transition: opacity 0.25s ease; z-index: 15; }" +
    ".zw-lead-overlay.zw-active { opacity: 1; pointer-events: auto; }" +

    ".zw-lead-panel { position: absolute; top: 66px; right: 12px; left: 12px; background: #fff;" +
    " border-radius: 14px; box-shadow: 0 14px 32px rgba(0,0,0,0.22); padding: 18px; z-index: 16;" +
    " opacity: 0; transform: translateX(24px) scale(0.97); pointer-events: none;" +
    " transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.4, 0, 0.2, 1); }" +
    ".zw-lead-panel.zw-active { opacity: 1; transform: translateX(0) scale(1); pointer-events: auto; }" +

    ".zw-lead-panel-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }" +
    ".zw-lead-title { font-size: 14px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 6px; }" +
    ".zw-lead-title svg { width: 16px; height: 16px; color: #f59e0b; }" +
    ".zw-lead-panel-close { background: none; border: none; cursor: pointer; color: #94a3b8; padding: 3px;" +
    " display: flex; border-radius: 5px; transition: background 0.15s, color 0.15s; }" +
    ".zw-lead-panel-close:hover { background: #f1f5f9; color: #475569; }" +
    ".zw-lead-panel-close svg { width: 15px; height: 15px; }" +

    ".zw-lead-inputs { display: flex; flex-direction: column; gap: 10px; }" +
    ".zw-lead-field-label { font-size: 11px; font-weight: 600; color: #64748b; margin-bottom: 3px; display: block; }" +
    ".zw-lead-input { width: 100%; padding: 9px 11px; border: 1.5px solid #e2e8f0; border-radius: 8px; font-size: 13px;" +
    " outline: none; transition: border-color 0.15s; }" +
    ".zw-lead-input:focus { border-color: #2563eb; }" +
    ".zw-lead-input.zw-error { border-color: #ef4444; }" +

    ".zw-lead-consent { display: flex; align-items: flex-start; gap: 7px; margin-top: 2px; }" +
    ".zw-lead-consent input { margin-top: 2px; flex-shrink: 0; accent-color: #2563eb; }" +
    ".zw-lead-consent label { font-size: 11px; line-height: 1.4; color: #64748b; }" +
    ".zw-lead-consent a { color: #2563eb; text-decoration: underline; }" +

    ".zw-lead-error-text { font-size: 11px; color: #ef4444; margin-top: -4px; display: none; }" +
    ".zw-lead-error-text.zw-visible { display: block; }" +

    ".zw-lead-btn { width: 100%; background: #10b981; color: #fff; border: none; padding: 10px; border-radius: 8px;" +
    " font-weight: 600; font-size: 13px; cursor: pointer; margin-top: 2px; transition: background 0.2s, opacity 0.2s;" +
    " display: flex; align-items: center; justify-content: center; gap: 6px; }" +
    ".zw-lead-btn:hover:not(:disabled) { background: #059669; }" +
    ".zw-lead-btn:disabled { opacity: 0.6; cursor: default; }" +

    ".zw-lead-success { text-align: center; color: #10b981; font-size: 13px; font-weight: 600; display: none;" +
    " padding: 18px 0; flex-direction: column; align-items: center; gap: 8px; }" +
    ".zw-lead-success svg { width: 30px; height: 30px; }" +

    ".zw-input-row { display: flex; align-items: center; gap: 8px; padding: 10px; border-top: 1px solid #e2e8f0;" +
    " background: #fff; flex-shrink: 0; position: relative; z-index: 5; }" +
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
    "  .zw-window { top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; max-height: 100%; border-radius: 0; }" +
    "  .zw-launcher { bottom: 16px; right: 16px; }" +
    "  .zw-input-row { padding-bottom: max(10px, env(safe-area-inset-bottom)); }" +
    "  .zw-lead-panel { left: 12px; right: 12px; }" +
    "}";
  document.head.appendChild(style);

  // ===================== РАЗМЕТКА =====================
  var root = document.createElement("div");
  root.className = "zw-root";

  var ICON_CHAT = '<svg class="zw-icon-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>';
  var ICON_CLOSE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
  var ICON_CLOSE_LAUNCHER = '<svg class="zw-icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
  var ICON_SEND = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>';
  var ICON_BOT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>';
  var ICON_LEAD = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>';
  var ICON_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';

  var button = document.createElement("button");
  button.className = "zw-launcher";
  button.setAttribute("aria-label", "Открыть чат");
  button.innerHTML = ICON_CHAT + ICON_CLOSE_LAUNCHER;

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
    '<button class="zw-header-close" aria-label="Закрыть чат">' + ICON_CLOSE + "</button>";

  var leadTrigger = document.createElement("div");
  leadTrigger.className = "zw-lead-trigger";
  leadTrigger.innerHTML = ICON_LEAD;
  leadTrigger.title = "Оставить заявку";
  header.appendChild(leadTrigger);

  var log = document.createElement("div");
  log.className = "zw-log";

  var leadOverlay = document.createElement("div");
  leadOverlay.className = "zw-lead-overlay";

  var leadPanel = document.createElement("div");
  leadPanel.className = "zw-lead-panel";
  leadPanel.innerHTML =
    '<div class="zw-lead-form">' +
      '<div class="zw-lead-panel-header">' +
        '<div class="zw-lead-title">' + ICON_LEAD + "Оставить заявку</div>" +
        '<button class="zw-lead-panel-close" aria-label="Закрыть">' + ICON_CLOSE + "</button>" +
      "</div>" +
      '<div class="zw-lead-inputs">' +
        '<div>' +
          '<label class="zw-lead-field-label" for="zw-name">Имя</label>' +
          '<input type="text" class="zw-lead-input" id="zw-name" placeholder="Как к вам обращаться">' +
        "</div>" +
        '<div>' +
          '<label class="zw-lead-field-label" for="zw-phone">Телефон</label>' +
          '<input type="tel" inputmode="tel" class="zw-lead-input" id="zw-phone" placeholder="+7 (___) ___-__-__">' +
        "</div>" +
        '<div class="zw-lead-error-text" id="zw-lead-error">Заполните имя и телефон</div>' +
        '<div class="zw-lead-consent">' +
          '<input type="checkbox" id="zw-consent">' +
          '<label for="zw-consent">Согласен(а) на обработку персональных данных согласно <a href="' + privacyUrl + '" target="_blank" rel="noopener">политике конфиденциальности</a></label>' +
        "</div>" +
        '<button class="zw-lead-btn" id="zw-submit">Отправить</button>' +
      "</div>" +
    "</div>" +
    '<div class="zw-lead-success">' + ICON_CHECK + "<span>Заявка принята!</span></div>";

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
  windowEl.appendChild(leadOverlay);
  windowEl.appendChild(leadPanel);
  windowEl.appendChild(inputRow);

  root.appendChild(button);
  root.appendChild(windowEl);
  document.body.appendChild(root);

  // ===================== СОСТОЯНИЕ =====================
  var messageCount = 0;
  var leadFormDismissed = false;
  var isLeadPanelOpen = false;

  function addMessage(role, text) {
    var bubble = document.createElement("div");
    var isUser = role === "user";
    if (isUser) messageCount++;
    bubble.className = "zw-bubble " + (isUser ? "zw-user" : "zw-bot");
    if (isUser) {
      bubble.textContent = text; // без интерпретации как HTML — защита от XSS
    } else {
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
    if (typingEl) { typingEl.remove(); typingEl = null; }
  }

  function openChat() { windowEl.classList.add("zw-visible"); button.classList.add("zw-open"); input.focus(); }
  function closeChat() { windowEl.classList.remove("zw-visible"); button.classList.remove("zw-open"); }
  button.addEventListener("click", function () {
    windowEl.classList.contains("zw-visible") ? closeChat() : openChat();
  });
  header.querySelector(".zw-header-close").addEventListener("click", closeChat);

  // ===================== ФОРМА ЗАЯВКИ =====================
  var leadForm = leadPanel.querySelector(".zw-lead-form");
  var leadSuccess = leadPanel.querySelector(".zw-lead-success");
  var nameInput = leadPanel.querySelector("#zw-name");
  var phoneInput = leadPanel.querySelector("#zw-phone");
  var consentInput = leadPanel.querySelector("#zw-consent");
  var submitBtn = leadPanel.querySelector("#zw-submit");
  var errorText = leadPanel.querySelector("#zw-lead-error");
  var panelCloseBtn = leadPanel.querySelector(".zw-lead-panel-close");

  function toggleLeadPanel(forceOpen) {
    if (leadFormDismissed && !forceOpen) return;

    isLeadPanelOpen = forceOpen !== undefined ? forceOpen : !isLeadPanelOpen;

    if (isLeadPanelOpen) {
      leadOverlay.classList.add("zw-active");
      leadPanel.classList.add("zw-active");
      leadTrigger.classList.remove("zw-pulse");
      setTimeout(function () { nameInput.focus(); }, 260);
    } else {
      leadOverlay.classList.remove("zw-active");
      leadPanel.classList.remove("zw-active");
    }
  }

  leadTrigger.addEventListener("click", function (e) {
    e.stopPropagation();
    leadFormDismissed = false;
    toggleLeadPanel(true);
  });

  function dismissLeadPanel() {
    toggleLeadPanel(false);
    leadFormDismissed = true;
}
  leadOverlay.addEventListener("click", dismissLeadPanel);
  panelCloseBtn.addEventListener("click", dismissLeadPanel);

  function showFieldError(message) {
    errorText.textContent = message;
    errorText.classList.add("zw-visible");
    nameInput.classList.toggle("zw-error", !nameInput.value.trim());
    phoneInput.classList.toggle("zw-error", !phoneInput.value.trim());
  }

  submitBtn.addEventListener("click", function () {
    var name = nameInput.value.trim();
    var phone = phoneInput.value.trim();

    if (!name || !phone) {
      showFieldError("Заполните имя и телефон");
      return;
    }
    if (!consentInput.checked) {
      showFieldError("Подтвердите согласие на обработку данных");
      return;
    }

    errorText.classList.remove("zw-visible");
    nameInput.classList.remove("zw-error");
    phoneInput.classList.remove("zw-error");

    submitBtn.disabled = true;
    submitBtn.textContent = "Отправка...";

    fetch(apiBase + "/api/v1/widget/lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site_id: siteId, session_id: sessionId, name: name, phone: phone }),
    })
      .then(function () {
        leadForm.style.display = "none";
        leadSuccess.style.display = "flex";
        setTimeout(function () {
          toggleLeadPanel(false);
          leadForm.style.display = "block";
          leadSuccess.style.display = "none";
          submitBtn.disabled = false;
          submitBtn.textContent = "Отправить";
          nameInput.value = "";
          phoneInput.value = "";
          consentInput.checked = false;
        }, 2200);
        addMessage("assistant", "Спасибо! Мы свяжемся с вами в ближайшее время.");
      })
      .catch(function () {
        showFieldError("Не удалось отправить, попробуйте ещё раз");
        submitBtn.disabled = false;
        submitBtn.textContent = "Отправить";
      });
  });

  // ===================== ОБЫЧНЫЙ ЧАТ =====================
  function processRegularMessage(text) {
    showTyping();
    input.disabled = true;
    sendBtn.disabled = true;

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

        // Бэкенд уже сам решает (LangChain + few-shot), когда стоит попросить
        // контакт — виджет больше не переспоривает это своей эвристикой.
        if (data.ask_lead === true) {
          if (!leadFormDismissed) {
            toggleLeadPanel(true);
          } else {
            // юзер уже один раз закрыл форму в этом диалоге — не навязываем,
            // просто мягко подсвечиваем иконку
            leadTrigger.classList.add("zw-pulse");
          }
        }
      })
      .catch(function () {
        hideTyping();
        addMessage("assistant", "Не удалось получить ответ. Попробуйте ещё раз.");
      })
      .finally(function () {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
      });
  }

  function sendMessage() {
    var text = input.value.trim();
    if (!text) return;
    addMessage("user", text);
    input.value = "";
    processRegularMessage(text);
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") sendMessage();
  });
})();