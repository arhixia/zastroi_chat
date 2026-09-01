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

  var button = document.createElement("button");
  button.textContent = "Чат";
  button.style.cssText =
    "position:fixed;bottom:20px;right:20px;width:56px;height:56px;border-radius:50%;" +
    "background:#2563eb;color:#fff;border:none;font-size:13px;cursor:pointer;z-index:99999;" +
    "box-shadow:0 2px 8px rgba(0,0,0,0.2)";

  var windowEl = document.createElement("div");
  windowEl.style.cssText =
    "position:fixed;bottom:88px;right:20px;width:320px;height:420px;background:#fff;" +
    "border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.2);display:none;flex-direction:column;" +
    "z-index:99999;overflow:hidden;font-family:sans-serif";

  var header = document.createElement("div");
  header.textContent = "Чат с застройщиком";
  header.style.cssText = "background:#2563eb;color:#fff;padding:12px;font-size:14px";

  var log = document.createElement("div");
  log.style.cssText =
    "flex:1;overflow-y:auto;padding:12px;font-size:14px;display:flex;flex-direction:column;gap:8px";

  var inputRow = document.createElement("div");
  inputRow.style.cssText = "display:flex;border-top:1px solid #eee";

  var input = document.createElement("input");
  input.placeholder = "Напишите сообщение...";
  input.style.cssText = "flex:1;border:none;padding:10px;font-size:14px;outline:none";

  var sendBtn = document.createElement("button");
  sendBtn.textContent = "Отправить";
  sendBtn.style.cssText = "border:none;background:#2563eb;color:#fff;padding:10px 14px;cursor:pointer;font-size:13px";

  inputRow.appendChild(input);
  inputRow.appendChild(sendBtn);
  windowEl.appendChild(header);
  windowEl.appendChild(log);
  windowEl.appendChild(inputRow);
  document.body.appendChild(button);
  document.body.appendChild(windowEl);

  function addMessage(role, text) {
    var bubble = document.createElement("div");
    bubble.textContent = text;
    var isUser = role === "user";
    bubble.style.cssText =
      "max-width:80%;padding:8px 12px;border-radius:10px;font-size:13px;" +
      (isUser
        ? "align-self:flex-end;background:#2563eb;color:#fff"
        : "align-self:flex-start;background:#f1f1f1;color:#111");
    log.appendChild(bubble);
    log.scrollTop = log.scrollHeight;
  }

  button.addEventListener("click", function () {
    windowEl.style.display = windowEl.style.display === "flex" ? "none" : "flex";
  });

  function sendMessage() {
    var text = input.value.trim();
    if (!text) return;

    addMessage("user", text);
    input.value = "";

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
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        addMessage("assistant", data.answer);
      })
      .catch(function () {
        addMessage("assistant", "Не удалось получить ответ, попробуйте позже.");
      });
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") sendMessage();
  });
})();