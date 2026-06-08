function toggleMenu() {
            const menu = document.getElementById('mobile-menu');
            const navbar = document.getElementById('navbar');

            if (menu.classList.contains('hidden')) {
                menu.classList.remove('hidden');
                navbar.classList.add('bg-white'); // Solid background when menu opens
            } else {
                menu.classList.add('hidden');
                navbar.classList.remove('bg-white');
            }
        }
