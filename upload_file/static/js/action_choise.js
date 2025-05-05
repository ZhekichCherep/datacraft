document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.action-card-form .action-card').forEach(card => {
        card.addEventListener('click', function() {
            const fileInput = this.querySelector('input[type="file"]');
            fileInput.click();
        });
    });

    document.querySelectorAll('.action-card-form input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });
});