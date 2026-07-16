window.tailwind = window.tailwind || {};
tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#1B4332',    /* Deep Emerald */
                        secondary: '#D8F3DC',  /* Mint */
                        accent: '#E07A5F',     /* Terracotta */
                        bg: '#F7F5F2',         /* Bone White */
                        dark: '#2D3436',       /* Charcoal */
                    },
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                    },
                    boxShadow: {
                        'card': '0 2px 12px rgba(0,0,0,0.06)',
                        'floating': '0 -4px 20px rgba(0,0,0,0.1)',
                    }
                }
            }
        }
