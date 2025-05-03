
document.addEventListener('DOMContentLoaded', function() {
    function toggleOptions(checkboxName, targetElements) {
        const checkbox = document.querySelector(`input[name="${checkboxName}"]`);
        if (!checkbox) return;
        
        const targets = Array.isArray(targetElements) 
            ? targetElements.map(name => document.querySelector(`[name="${name}"]`))
            : [document.querySelector(`[name="${targetElements}"]`)];
        
        checkbox.addEventListener('change', function() {
            targets.forEach(el => {
                if (el) el.disabled = !this.checked;
            });
        });
        
        // Инициализация состояния
        targets.forEach(el => {
            if (el) el.disabled = !checkbox.checked;
        });
    }

    toggleOptions('process_outliers', 'outlier_strategy');
    // toggleOptions('process_categorical', 'categorical_strategy');
    toggleOptions('process_normalization', 'normalization_strategy');
    // toggleOptions('process_text', ['text_lowercase', 'text_remove_punct', 'text_remove_stopwords', 'text_stemming']);

    const missingStrategy = document.querySelector('select[name="missing_strategy"]');
    const missingConstant = document.querySelector('input[name="missing_constant"]');
    
    if (missingStrategy && missingConstant) {
        missingStrategy.addEventListener('change', function() {
            if (this.value === 'constant') {
                missingConstant.style.display = 'block';
                missingConstant.setAttribute('required', 'required');
            } else {
                missingConstant.style.display = 'none';
                missingConstant.removeAttribute('required');
            }
        });
    }

    const columnCheckboxes = document.querySelectorAll('.column-checkbox input');
    const selectAllBtn = document.createElement('button');
    selectAllBtn.type = 'button';
    selectAllBtn.className = 'btn btn-select-all';
    selectAllBtn.textContent = 'Deselect All';
    
    const columnsSelector = document.querySelector('.columns-selector');
    if (columnsSelector) {
        columnsSelector.parentNode.insertBefore(selectAllBtn, columnsSelector);
    }
    
    let allSelected = true;
    selectAllBtn.addEventListener('click', function() {
        columnCheckboxes.forEach(checkbox => {
            checkbox.checked = !allSelected;
        });
        allSelected = !allSelected;
        this.textContent = allSelected ? 'Deselect All' : 'Select All';
    });

    form.addEventListener('submit', function(e) {
        const selectedColumns = Array.from(columnCheckboxes).filter(cb => cb.checked);
        if (selectedColumns.length === 0) {
            e.preventDefault();
            alert('Please select at least one column to process.');
            return;
        }
    });

    document.querySelectorAll('.switch input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const methodOptions = this.closest('.method-card').querySelector('.method-options');
            if (methodOptions) {
                methodOptions.querySelectorAll('select, input').forEach(el => {
                    el.disabled = !this.checked;
                });
            }
        });
    });
});