document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-confirm]").forEach((button) => {
        button.addEventListener("click", (event) => {
            const message = button.getAttribute("data-confirm") || "Are you sure?";
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll(".toast").forEach((toastEl) => {
        const toast = new bootstrap.Toast(toastEl, { delay: 4200 });
        toast.show();
    });

    document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", () => {
            const submitter = form.querySelector("button[type='submit'], button:not([type])");
            if (submitter && !submitter.dataset.confirm) {
                submitter.classList.add("disabled");
            }
        });
    });
});
