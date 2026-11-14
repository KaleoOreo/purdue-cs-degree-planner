const statusElement = document.getElementById("app-status");
statusElement.textContent = "Planner ready.";

const generateButton = document.getElementById("generate-plan");
const maxCreditsInput = document.getElementById("max-credits");
generateButton.addEventListener("click", () => {
  statusElement.textContent = "Maximum credits: " + maxCreditsInput.value;
});
