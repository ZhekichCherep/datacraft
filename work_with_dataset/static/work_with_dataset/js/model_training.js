document.addEventListener('DOMContentLoaded', function() {
    const modelCards = document.querySelectorAll('.model-card');
    
    modelCards.forEach(card => {
        card.addEventListener('click', function() {
            modelCards.forEach(c => c.classList.remove('active'));
            
            this.classList.add('active');
            
            document.querySelectorAll('.model-params').forEach(params => {
                params.style.display = 'none';
            });
            
            const params = this.querySelector('.model-params');
            if (params) params.style.display = 'block';
            
            document.getElementById('selected_model').value = this.dataset.model;
        });
    });
    
    document.querySelectorAll('.option-label input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const subOptions = this.closest('.option-label').nextElementSibling;
            if (subOptions) {
                subOptions.style.display = this.checked ? 'block' : 'none';
            }
        });
        
        if (checkbox.checked) {
            const subOptions = checkbox.closest('.option-label').nextElementSibling;
            if (subOptions) subOptions.style.display = 'block';
        }
    });
    
    if (modelCards.length > 0) {
        const firstCard = modelCards[0];
        const firstParams = firstCard.querySelector('.model-params');
        if (firstParams) firstParams.style.display = 'block';
    }
});