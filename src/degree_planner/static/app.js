const statusElement = document.getElementById("app-status");
const semesterPlan = document.getElementById("semester-plan");
const completedCourses = document.getElementById("completed-courses");
const catalogBody = document.getElementById("course-catalog-body");
const multiSemesterPlan = document.getElementById("multi-semester-plan");
const curriculumProgress = document.getElementById("curriculum-progress");
const graphValidation = document.getElementById("course-graph-validation");

function element(tag, text) {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}

function showMessage(container, message) {
  container.replaceChildren(element("p", message));
}

function showStatus(message, isError = false) {
  statusElement.textContent = message;
  statusElement.classList.toggle("error", isError);
}

async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let detail = `Request failed (${response.status}).`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // A plain-text or empty error response still has the status above.
    }
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}

function creditsFrom(inputId) {
  const value = Number(document.getElementById(inputId).value);
  if (!Number.isSafeInteger(value) || value < 1) {
    throw new Error("Enter a positive whole number of credits.");
  }
  return value;
}

function courseLine(course) {
  const unit = course.credits === 1 ? "credit" : "credits";
  return `${course.code} — ${course.title} (${course.credits} ${unit})`;
}

function renderCourseList(container, courses, emptyMessage) {
  if (courses.length === 0) {
    showMessage(container, emptyMessage);
    return;
  }
  const list = document.createElement("ul");
  for (const course of courses) list.append(element("li", courseLine(course)));
  container.replaceChildren(list);
}

function renderSemesters(container, semesters) {
  if (semesters.length === 0) {
    showMessage(container, "No remaining courses to plan.");
    return;
  }
  const sections = semesters.map((courses, index) => {
    const section = document.createElement("section");
    section.className = "semester";
    const credits = courses.reduce((total, course) => total + course.credits, 0);
    section.append(element("h3", `Semester ${index + 1} (${credits} credits)`));
    const list = document.createElement("ul");
    for (const course of courses) list.append(element("li", courseLine(course)));
    section.append(list);
    return section;
  });
  container.replaceChildren(...sections);
}

async function loadCatalog() {
  const courses = await request("/courses");
  if (courses.length === 0) {
    const row = document.createElement("tr");
    const cell = element("td", "No courses have been loaded yet.");
    cell.colSpan = 5;
    row.append(cell);
    catalogBody.replaceChildren(row);
    return;
  }
  const rows = courses.map((course) => {
    const row = document.createElement("tr");
    for (const value of [
      course.code, course.title, course.credits, course.category,
      course.prerequisites.join(", ") || "None",
    ]) row.append(element("td", String(value)));
    return row;
  });
  catalogBody.replaceChildren(...rows);
}

async function loadCompleted() {
  const codes = await request("/completed");
  if (codes.length === 0) {
    showMessage(completedCourses, "No completed courses have been recorded yet.");
    return;
  }
  const list = document.createElement("ul");
  for (const code of codes) list.append(element("li", code));
  completedCourses.replaceChildren(list);
}

function progressGroup(name, description) {
  const item = document.createElement("li");
  item.append(element("strong", name), document.createTextNode(`: ${description}`));
  return item;
}

async function loadProgress() {
  const progress = await request("/progress");
  const heading = element("h3", progress.name);
  const summary = element("p", progress.is_complete
    ? "All degree requirements are satisfied with distinct course allocations."
    : "Degree requirements are still incomplete.");
  const list = document.createElement("ul");
  for (const group of progress.required_groups) {
    const missing = group.missing_course_codes;
    list.append(progressGroup(group.name, missing.length === 0
      ? "Complete" : `Missing: ${missing.join(", ")}`));
  }
  for (const group of progress.choice_groups) {
    list.append(progressGroup(group.name,
      `${group.remaining_count} more required; choices: ${group.course_codes.join(", ")}`));
  }
  for (const group of progress.option_groups) {
    const options = group.options.map((option) => option.course_codes.join(" + "));
    list.append(progressGroup(group.name,
      `${group.remaining_count} more required; options: ${options.join("; ")}`));
  }
  const content = [heading, summary, list];
  if (progress.allocations !== null) {
    content.push(element("h4", "Course allocation"));
    const allocations = document.createElement("ul");
    for (const allocation of progress.allocations) {
      allocations.append(progressGroup(
        allocation.group_name, allocation.course_codes.join(" + ")));
    }
    content.push(allocations);
  }
  curriculumProgress.replaceChildren(...content);
}

async function loadValidation() {
  const result = await request("/validation");
  if (result.is_valid) {
    showMessage(graphValidation, "Prerequisite graph is valid.");
    return;
  }
  const content = [element("p", "Prerequisite graph needs attention.")];
  const issues = document.createElement("ul");
  for (const missing of result.missing_prerequisites) {
    issues.append(element("li",
      `${missing.course_code} requires missing course ${missing.prerequisite_code}.`));
  }
  if (result.cycle_path.length) {
    issues.append(element("li", `Cycle: ${result.cycle_path.join(" → ")}`));
  }
  content.push(issues);
  graphValidation.replaceChildren(...content);
}

async function run(action) {
  showStatus("Loading…");
  try {
    await action();
    showStatus("Planner ready.");
  } catch (error) {
    showStatus(error.message || "Something went wrong. Please try again.", true);
  }
}

document.getElementById("generate-plan").addEventListener("click", () => run(async () => {
  const maxCredits = creditsFrom("max-credits");
  const courses = await request(`/plan?max_credits=${encodeURIComponent(maxCredits)}`);
  renderCourseList(semesterPlan, courses, "No courses are available next semester.");
}));

document.getElementById("generate-all-plan").addEventListener("click", () => run(async () => {
  const maxCredits = creditsFrom("all-max-credits");
  const semesters = await request(`/plan/all?max_credits=${encodeURIComponent(maxCredits)}`);
  renderSemesters(multiSemesterPlan, semesters);
}));

document.getElementById("mark-completed").addEventListener("click", () => run(async () => {
  const input = document.getElementById("completed-course-code");
  const courseCode = input.value.trim().toUpperCase();
  if (!courseCode) throw new Error("Enter a course code first.");
  await request("/completed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ course_code: courseCode }),
  });
  input.value = "";
  showMessage(semesterPlan, "Generate a plan to include your new completion.");
  showMessage(multiSemesterPlan, "Generate a full plan to include your new completion.");
  await Promise.all([loadCompleted(), loadProgress()]);
}));

run(async () => {
  const results = await Promise.allSettled([
    loadCatalog(), loadCompleted(), loadProgress(), loadValidation(),
  ]);
  const failures = results.filter((result) => result.status === "rejected");
  if (failures.length) throw failures[0].reason;
});
