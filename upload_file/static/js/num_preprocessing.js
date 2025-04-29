document.addEventListener('DOMContentLoaded', function() {
    toggleOptions('process_missing', 'missing_strategy');
    toggleOptions('process_outliers', 'outlier_strategy');
    // toggleOptions('process_categorical', 'categorical_strategy');
    toggleOptions('process_normalization', 'normalization_strategy');
    // toggleOptions('process_text', ['text_lowercase', 'text_remove_punct', 'text_remove_stopwords', 'text_stemming']);

    // Динамическое отображение поля для константного значения
    const missingStrategy = document.querySelector('select[name="missing_strategy"]');
    const missingConstant = document.querySelector('input[name="missing_constant"]');
    
    missingStrategy.addEventListener('change', function() {
        if (this.value === 'constant') {
            missingConstant.style.display = 'block';
            missingConstant.setAttribute('required', 'required');
        } else {
            missingConstant.style.display = 'none';
            missingConstant.removeAttribute('required');
        }
    });

    const columnCheckboxes = document.querySelectorAll('.column-checkbox input');
    const selectAllBtn = document.createElement('button');
    selectAllBtn.type = 'button';
    selectAllBtn.className = 'btn btn-select-all';
    selectAllBtn.textContent = 'Select All';
    
    const columnsSelector = document.querySelector('.columns-selector');
    columnsSelector.parentNode.insertBefore(selectAllBtn, columnsSelector);
    
    let allSelected = true;
    selectAllBtn.addEventListener('click', function() {
        columnCheckboxes.forEach(checkbox => {
            checkbox.checked = !allSelected;
        });
        allSelected = !allSelected;
        this.textContent = allSelected ? 'Deselect All' : 'Select All';
    });

    const form = document.querySelector('.processing-form');
    form.addEventListener('submit', function(e) {
        const selectedColumns = Array.from(columnCheckboxes).filter(cb => cb.checked);
        if (selectedColumns.length === 0) {
            e.preventDefault();
            alert('Please select at least one column to process.');
            return;
        }
        
    });

    // Функция для включения/выключения опций при переключении метода
    function toggleOptions(checkboxName, targetElements) {
        const checkbox = document.querySelector(`input[name="${checkboxName}"]`);
        const targets = Array.isArray(targetElements) ? 
            targetElements.map(name => document.querySelector(`input[name="${name}"]`)) :
            [document.querySelector(`select[name="${targetElements}"]`)];
        
        // Инициализация состояния
        targets.forEach(target => {
            if (target) {
                target.disabled = !checkbox.checked;
                if (target.tagName === 'SELECT') {
                    target.parentNode.style.opacity = checkbox.checked ? '1' : '0.5';
                }
            }
        });
        
        // Обработчик изменений
        checkbox.addEventListener('change', function() {
            targets.forEach(target => {
                if (target) {
                    target.disabled = !this.checked;
                    if (target.tagName === 'SELECT') {
                        target.parentNode.style.opacity = this.checked ? '1' : '0.5';
                    }
                }
            });
        });
    }
});