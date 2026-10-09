document.addEventListener("DOMContentLoaded", () => {
  const dateInput = document.querySelector("#booking-date");
  if (dateInput) {
    const today = new Date();
    const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    dateInput.min = localToday;
  }

  document.querySelectorAll("form[data-submit-kind]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;

      const submitButton = form.querySelector("[type='submit']");
      const status = form.querySelector(".form-status");
      const endpoint = form.dataset.submitKind === "reservations" ? "/api/reservations" : "/api/messages";
      const payload = Object.fromEntries(new FormData(form).entries());
      submitButton.disabled = true;
      status.classList.remove("is-error");
      status.textContent = "Sending your note...";

      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Please try again in a moment.");
        status.textContent = form.dataset.submitKind === "reservations"
          ? "Thanks! Your table request is in. We'll be in touch to confirm."
          : "Thanks for reaching out. Your message is with our team.";
        form.reset();
      } catch (error) {
        status.classList.add("is-error");
        status.textContent = error.message === "Failed to fetch"
          ? "We couldn't reach the server. Please try again shortly."
          : error.message;
      } finally {
        submitButton.disabled = false;
      }
    });
  });
});