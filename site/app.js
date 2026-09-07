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

const animation = document.querySelector("[data-animation]");
if (animation) {
  const scene = animation.querySelector("[data-scene]");
  const status = animation.querySelector("[data-status]");
  const caption = animation.querySelector("[data-caption]");
  const stepButtons = animation.querySelectorAll("[data-step]");
  const copy = [
    ["Ready to start", "Nothing is running yet."],
    ["Step 1 · startup", "The first client sees no usable hub and creates an atomic startup lock."],
    ["Step 2 · readiness", "The hub creates its ROS 2 services. The client waits for service discovery before registering."],
    ["Step 3 · identity", "The hub assigns each client a running user ID and colour, then publishes the active-user state."],
    ["Step 4 · routing", "The hub subscribes to one outbound topic per client. Each route has an explicit owner."],
    ["Step 5 · publish", "A client sends one record to its own topic. The hub identifies the sender and validates the record."],
    ["Step 6 · broadcast", "The hub publishes one shared record. DDS delivers it to every subscribed client."],
  ];
  let current = 0;
  let timer;

  const setStep = (step) => {
    current = Math.max(0, Math.min(copy.length - 1, step));
    scene.dataset.step = current;
    status.textContent = copy[current][0];
    caption.textContent = copy[current][1];
    caption.classList.remove("caption-pop");
    void caption.offsetWidth;
    caption.classList.add("caption-pop");
    stepButtons.forEach((button) => button.classList.toggle("is-current", Number(button.dataset.step) === current));
    const play = animation.querySelector('[data-action="play"]');
    play.textContent = current === copy.length - 1 ? "▶ Play again" : "▶ Play";
  };

  const stop = () => { window.clearInterval(timer); timer = undefined; };
  const play = () => {
    stop();
    if (current === copy.length - 1) setStep(0);
    timer = window.setInterval(() => {
      if (current === copy.length - 1) return stop();
      setStep(current + 1);
    }, 2200);
  };

  animation.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => {
    const action = button.dataset.action;
    if (action === "play") play();
    if (action === "next") { stop(); setStep(current + 1); }
    if (action === "previous") { stop(); setStep(current - 1); }
    if (action === "restart") { stop(); setStep(0); }
  }));
  stepButtons.forEach((button) => button.addEventListener("click", () => { stop(); setStep(Number(button.dataset.step)); }));
  setStep(0);
}
