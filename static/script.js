document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");

    form.addEventListener("submit", function(event) {
        const name = document.querySelector('input[name="name"]').value.trim();
        const email = document.querySelector('input[name="email"]').value.trim();
        const phone = document.querySelector('input[name="phone"]').value.trim();
        const message = document.querySelector('textarea[name="message"]').value.trim();

        if (name === "" || email === "" || phone === "" || message === "") {
            alert("All fields are required!");
            event.preventDefault();
        } else if (!/^\d{10}$/.test(phone)) {
            alert("Please enter a valid 10-digit phone number.");
            event.preventDefault();
        }
    });
});
