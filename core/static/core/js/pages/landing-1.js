window.tailwind = window.tailwind || {};
tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#1B4332',    /* Deep Emerald: Warna utama yang mewah & natural */
                        secondary: '#D8F3DC',  /* Mint: Untuk aksen background */
                        accent: '#E07A5F',     /* Terracotta: Untuk tombol (CTA) agar kontras */
                        bg: '#F7F5F2',         /* Bone White: Warna latar hangat (bukan putih murni) */
                        dark: '#2D3436',       /* Charcoal: Warna teks */
                    },
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                    },
                    boxShadow: {
                        'soft': '0 10px 40px -10px rgba(0,0,0,0.08)',
                    }
                }
            }
        }
