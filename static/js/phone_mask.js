function formatPhoneNumber(input) {
    let numbers = input.value.replace(/\D/g, '');
    if (numbers.length > 11) numbers = numbers.slice(0, 11);

    let formatted = '';

    if (numbers.length > 0) {
        formatted = '+7';

        if (numbers.length > 1) {
            if (numbers.length >= 4) {
                formatted += ' ' + numbers.slice(1, 4);
            } else {
                formatted += ' ' + numbers.slice(1);
            }

            if (numbers.length >= 7) {
                formatted += ' ' + numbers.slice(4, 7);
            } else if (numbers.length > 4) {
                formatted += ' ' + numbers.slice(4);
            }

            if (numbers.length >= 9) {
                formatted += '-' + numbers.slice(7, 9);
            } else if (numbers.length > 7) {
                formatted += '-' + numbers.slice(7);
            }

            if (numbers.length >= 11) {
                formatted += '-' + numbers.slice(9, 11);
            } else if (numbers.length > 9) {
                formatted += '-' + numbers.slice(9);
            }
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

document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[id$="phone"], input[name$="phone"]');

    phoneInputs.forEach(input => {
        input.removeEventListener('input', phoneInputHandler);
        input.addEventListener('input', phoneInputHandler);
    });
});

function phoneInputHandler(e) {
    formatPhoneNumber(e.target);
}