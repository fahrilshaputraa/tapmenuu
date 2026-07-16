window.tailwind = window.tailwind || {};
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#1B4332',
                primaryLight: '#2D6A4F',
                secondary: '#D8F3DC',
                accent: '#E07A5F',
                bg: '#F7F5F2',
                dark: '#2D3436',
                success: '#10B981',
                warning: '#F59E0B',
                danger: '#EF4444',
            },
            fontFamily: {
                sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            },
            boxShadow: {
                card: '0 2px 12px rgba(0,0,0,0.06)',
                soft: '0 8px 32px -12px rgba(27,67,50,0.12)',
            }
        }
    }
}
