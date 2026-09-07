const tabs = document.querySelectorAll(".view-tab");
const panels = document.querySelectorAll(".architecture-panel");
const events = {
  healthy: { code: "ROBOT_HEALTHY", text: "Robot operating normally" },
  lost: { code: "FORMATION_LOST", text: "Robot left formation" },
  rejoined: { code: "FORMATION_RESTORED", text: "Robot rejoined formation" },
};

tabs.forEach((tab) => tab.addEventListener("click", () => {
  const selected = tab.dataset.view;
  tabs.forEach((item) => {
    const active = item === tab;
    item.classList.toggle("is-active", active);
    item.setAttribute("aria-selected", active);
  });
  panels.forEach((panel) => panel.classList.toggle("is-active", panel.dataset.panel === selected));
}));

document.querySelectorAll("[data-event]").forEach((button) => button.addEventListener("click", () => {
  const event = events[button.dataset.event];
  const record = { kind: "telemetry", user_id: "user-2", code: event.code, text: event.text };
  document.querySelector("#telemetry-output").textContent = JSON.stringify(record, null, 2);
  document.querySelector("#telemetry-result").textContent = `Broadcast ${event.code} to every subscribed client`;
  document.querySelectorAll("[data-event]").forEach((item) => item.classList.toggle("is-selected", item === button));
}));
