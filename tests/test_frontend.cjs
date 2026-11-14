const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const script = fs.readFileSync(
  path.join(__dirname, "../src/degree_planner/static/app.js"), "utf8",
);

class FakeElement {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this.textContent = "";
    this.value = "";
    this.listeners = {};
    this.classList = { toggle() {} };
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  addEventListener(event, callback) { this.listeners[event] = callback; }
  click() { return this.listeners.click(); }
}

const course = (code) => ({
  code, title: `Title ${code}`, credits: 3, category: "CS", prerequisites: [],
});
const response = (body, status = 200) => ({
  ok: status < 400, status, json: async () => body,
});
const flush = () => new Promise((resolve) => setImmediate(resolve));

function setup() {
  const nodes = new Map();
  const calls = [];
  const completed = [];
  const document = {
    getElementById(id) {
      if (!nodes.has(id)) nodes.set(id, new FakeElement(id));
      return nodes.get(id);
    },
    createElement: (tag) => new FakeElement(tag),
    createTextNode: (text) => ({ textContent: text }),
  };
  document.getElementById("max-credits").value = "6";
  document.getElementById("all-max-credits").value = "6";
  const fetch = async (url, options) => {
    calls.push({ url, options });
    if (url === "/courses") return response([course("CS 18000")]);
    if (url === "/completed" && options?.method === "POST") {
      const code = JSON.parse(options.body).course_code;
      if (code !== "CS 18000") return response({ detail: "Course not found" }, 404);
      completed.push(code);
      return response(null, 204);
    }
    if (url === "/completed") return response(completed);
    if (url === "/progress") return response({
      name: "Software Engineering", is_complete: false,
      required_groups: [{ name: "Core", missing_course_codes: completed.length ? [] : ["CS 18000"] }],
      choice_groups: [], option_groups: [], allocations: null,
    });
    if (url === "/validation") return response({
      is_valid: true, missing_prerequisites: [], cycle_path: [],
    });
    if (url === "/plan?max_credits=6") return response([course("CS 18000")]);
    if (url === "/plan/all?max_credits=6") return response([[course("CS 18000")]]);
    throw new Error(`Unexpected request: ${url}`);
  };
  vm.runInNewContext(script, { document, fetch, Number, Error, String, Promise, encodeURIComponent });
  return { document, calls, completed };
}

test("loads the dashboard and renders both plan actions", async () => {
  const { document, calls } = setup();
  await flush();
  assert.deepEqual(calls.slice(0, 4).map((call) => call.url),
    ["/courses", "/completed", "/progress", "/validation"]);
  assert.equal(document.getElementById("course-catalog-body").children[0].children[0].textContent,
    "CS 18000");
  await document.getElementById("generate-plan").click();
  assert.equal(document.getElementById("semester-plan").children[0].children[0].textContent,
    "CS 18000 — Title CS 18000 (3 credits)");
  await document.getElementById("generate-all-plan").click();
  assert.equal(document.getElementById("multi-semester-plan").children[0].children[0].textContent,
    "Semester 1 (3 credits)");
});

test("rejects invalid credit input before requesting a plan", async () => {
  const { document, calls } = setup();
  await flush();
  document.getElementById("max-credits").value = "1.5";
  await document.getElementById("generate-plan").click();
  assert.equal(calls.length, 4);
  assert.equal(document.getElementById("app-status").textContent,
    "Enter a positive whole number of credits.");
});

test("completion updates progress and clears stale plans", async () => {
  const { document, calls, completed } = setup();
  await flush();
  await document.getElementById("generate-plan").click();
  document.getElementById("completed-course-code").value = " cs 18000 ";
  await document.getElementById("mark-completed").click();
  assert.deepEqual(completed, ["CS 18000"]);
  assert.equal(document.getElementById("completed-courses").children[0].children[0].textContent,
    "CS 18000");
  assert.equal(document.getElementById("semester-plan").children[0].textContent,
    "Generate a plan to include your new completion.");
  assert.equal(calls.at(-1).url, "/progress");
});

test("unknown course shows the API error without changing saved courses", async () => {
  const { document, completed } = setup();
  await flush();
  document.getElementById("completed-course-code").value = "CS 99999";
  await document.getElementById("mark-completed").click();
  assert.deepEqual(completed, []);
  assert.equal(document.getElementById("app-status").textContent, "Course not found");
  assert.equal(document.getElementById("completed-course-code").value, "CS 99999");
});
