document.addEventListener('DOMContentLoaded', function() {
    // Анимация элементов при скролле
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.dashboard-card, .report-card, .stat-card');
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.2;

            if (elementPosition < screenPosition) {
                const delay = element.getAttribute('data-delay') || '0';
                element.style.animationDelay = `${delay}ms`;
                element.classList.add('animate__animated', 'animate__fadeInUp');
            }
        });
    };

    // Обновление времени
    function updateTime() {
        const now = new Date();
        const timeElement = document.getElementById('current-time');
        const dateElement = document.getElementById('current-date');
        if (!timeElement || !dateElement) return;

        const options = {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        };

        const dateOptions = {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        };

        timeElement.textContent = now.toLocaleTimeString('ru-RU', options);
        dateElement.textContent = now.toLocaleDateString('ru-RU', dateOptions);
    }

    // Переключение бокового меню на мобильных устройствах
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }

    // Обработка форм отчетов
    document.querySelectorAll('.report-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Анимация загрузки
            const button = this.querySelector('button[type="submit"]');
            const originalText = button.innerHTML;

            button.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Формирование...';
            button.disabled = true;


            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;

                const toast = document.createElement('div');
                toast.className = 'position-fixed bottom-0 end-0 p-3';
                toast.style.zIndex = '1100';
                toast.innerHTML = `
                    <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                        <div class="toast-header bg-danger text-white">
                            <strong class="me-auto">Успешно</strong>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                        </div>
                        <div class="toast-body">
                            Отчет успешно сформирован и готов к скачиванию.
                        </div>
                    </div>
                `;

                document.body.appendChild(toast);

                // Удаление уведомления через 5 секунд
                setTimeout(() => {
                    toast.remove();
                }, 5000);
            }, 1500);
        });
    });


    updateTime();
    setInterval(updateTime, 1000); // Обновление каждую секунду, чтобы минута менялась вовремя

    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Запуск при загрузке


    const sections = document.querySelectorAll('section');
    const menuItems = document.querySelectorAll('.sidebar-menu li');

    window.addEventListener('scroll', function() {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;

            if (pageYOffset >= (sectionTop - 300)) {
                current = section.getAttribute('id');
            }
        });

        menuItems.forEach(item => {
            item.classList.remove('active');
            const link = item.querySelector('a');
            if (link.getAttribute('href') === `#${current}`) {
                item.classList.add('active');
            }
        });
    });
});