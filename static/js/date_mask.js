function formatDate(input) {
    let numbers = input.value.replace(/\D/g, '');
    if (numbers.length > 8) numbers = numbers.slice(0, 8);

    let formatted = '';

    if (numbers.length > 0) {
        let day = numbers.slice(0, 2);
        if (parseInt(day) > 31) day = '31';
        if (parseInt(day) === 0) day = '01';
        formatted = day;

        if (numbers.length >= 3) {
            let month = numbers.slice(2, 4);
            if (parseInt(month) > 12) month = '12';
            if (parseInt(month) === 0) month = '01';
            formatted += '.' + month;
        } else if (numbers.length > 2) {
            formatted += '.' + numbers.slice(2);
        }

        if (numbers.length >= 5) {
            let year = numbers.slice(4, 8);
            let currentYear = new Date().getFullYear();
            if (year.length === 4 && parseInt(year) > currentYear) {
                year = currentYear.toString();
            }
            formatted += '.' + year;
        } else if (numbers.length > 4) {
            formatted += '.' + numbers.slice(4);
        }
    }
    const cursorPos = input.selectionStart;
    const oldLength = input.value.length;
    input.value = formatted;

    const newLength = formatted.length;
    let newCursorPos = cursorPos + (newLength - oldLength);
    if (newCursorPos < 0) newCursorPos = 0;
    if (newCursorPos > newLength) newCursorPos = newLength;
    input.setSelectionRange(newCursorPos, newCursorPos);
}

function validateDate(dateStr) {
    if (!dateStr) return true;

    const parts = dateStr.split('.');
    if (parts.length !== 3) return true;

    const day = parseInt(parts[0]);
    const month = parseInt(parts[1]);
    const year = parseInt(parts[2]);

    if (isNaN(day) || isNaN(month) || isNaN(year)) return true;

    const date = new Date(year, month - 1, day);
    if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) {
        return false;
    }
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (date > today) return false;

    return true;
}

document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[id$="birthday"], input[name$="birthday"]');

    dateInputs.forEach(input => {
        input.removeEventListener('input', dateInputHandler);
        input.removeEventListener('blur', dateBlurHandler);
        input.addEventListener('input', dateInputHandler);
        input.addEventListener('blur', dateBlurHandler);
    });
});

function dateInputHandler(e) {
    formatDate(e.target);
}

function dateBlurHandler(e) {
    if (!validateDate(e.target.value) && e.target.value !== '') {
        e.target.classList.add('is-invalid');
        let errorDiv = e.target.parentElement.querySelector('.date-error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback date-error-message';
            errorDiv.style.display = 'block';
            errorDiv.textContent = 'Введите корректную дату (ДД.ММ.ГГГГ)';
            e.target.parentElement.appendChild(errorDiv);
        }
    } else {
        e.target.classList.remove('is-invalid');
        const errorDiv = e.target.parentElement.querySelector('.date-error-message');
        if (errorDiv) errorDiv.remove();
    }
}