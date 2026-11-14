const statusElement = document.getElementById("app-status");
statusElement.textContent = "Planner ready.";

const generateButton = document.getElementById("generate-plan");
generateButton.addEventListener("click", () => {
  statusElement.textContent = "Generate Plan clicked.";
});
