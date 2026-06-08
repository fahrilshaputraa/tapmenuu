tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#1B4332',    /* Deep Emerald */
                        primaryLight: '#2D6A4F',
                        secondary: '#D8F3DC',  /* Mint */
                        accent: '#E07A5F',     /* Terracotta */
                        bg: '#F7F5F2',         /* Bone White */
                        dark: '#2D3436',       /* Charcoal */
                        pending: '#F59E0B',    /* Amber for New Orders */
                        processing: '#3B82F6', /* Blue for Cooking */
                        ready: '#10B981',      /* Green for Ready */
                    },
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                    },
                    boxShadow: {
                        'card': '0 2px 12px rgba(0,0,0,0.06)',
                        'soft': '0 4px 20px -2px rgba(0,0,0,0.05)',
                    }
                }
            }
        }
