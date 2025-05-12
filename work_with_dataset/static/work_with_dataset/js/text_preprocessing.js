document.addEventListener('DOMContentLoaded', function() {
    function toggleOptions(checkboxName, targetNames) {
        const checkbox = document.querySelector(`input[name="${checkboxName}"]`);
        if (!checkbox) return;
        
        const targets = Array.isArray(targetNames) 
            ? targetNames.map(name => document.querySelector(`[name="${name}"]`))
            : [document.querySelector(`[name="${targetNames}"]`)];
        
        function updateState() {
            targets.forEach(el => {
                if (el) {
                    if (el.tagName === 'SELECT') {
                        el.disabled = !checkbox.checked;
                        el.closest('.method-options').style.opacity = checkbox.checked ? 1 : 0.6;
                    } else {
                        el.disabled = !checkbox.checked;
                    }
                }
            });
        }
        
        checkbox.addEventListener('change', updateState);
        updateState(); 
    }

        function setupMissingStrategy() {
        const missingStrategy = document.querySelector('select[name="missing_strategy"]');
        const missingConstant = document.querySelector('input[name="missing_constant"]');
        
        if (missingStrategy && missingConstant) {
            function updateConstantVisibility() {
                const isConstant = missingStrategy.value === 'constant';
                missingConstant.style.display = isConstant ? 'block' : 'none';
                if (isConstant) {
                    missingConstant.setAttribute('required', 'required');
                } else {
                    missingConstant.removeAttribute('required');
                }
            }
            
            missingStrategy.addEventListener('change', updateConstantVisibility);
            updateConstantVisibility();
        }
    }

    function setupSelectAllButton() {
        const columnCheckboxes = document.querySelectorAll('.column-checkbox input');
        const selectAllBtn = document.createElement('button');
        selectAllBtn.type = 'button';
        selectAllBtn.className = 'btn btn-select-all';
        selectAllBtn.textContent = 'Deselect All';
        
        const columnsSelector = document.querySelector('.columns-selector');
        if (columnsSelector && columnCheckboxes.length > 0) {
            columnsSelector.parentNode.insertBefore(selectAllBtn, columnsSelector);
            
            let allSelected = true;
            selectAllBtn.addEventListener('click', function() {
                allSelected = !allSelected;
                columnCheckboxes.forEach(checkbox => {
                    checkbox.checked = allSelected;
                });
                this.textContent = allSelected ? 'Deselect All' : 'Select All';
            });
        }
    }

    function setupFormValidation() {
        const form = document.querySelector('.processing-form');
        if (!form) return;
        
        form.addEventListener('submit', function(e) {
            const selectedColumns = Array.from(document.querySelectorAll('.column-checkbox input:checked'));
            if (selectedColumns.length === 0) {
                e.preventDefault();
                alert('Please select at least one column to process.');
                return;
            }
            
        });
    }

    function setupDependentOptions() {
        toggleOptions('process_categorical', 'categorical_strategy');
        
        toggleOptions('process_text', [
            'text_lowercase',
            'text_remove_punct',
            'text_remove_stopwords',
            'text_stemming'
        ]);
    }

    setupSelectAllButton();
    setupFormValidation();
    setupMissingStrategy();
    setupDependentOptions();
});
