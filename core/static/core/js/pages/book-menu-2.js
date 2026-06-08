// --- DATA MENU ---
    const menuItems = [
        {
            id: 1,
            name: "Nasi Goreng Spesial",
            desc: "Dengan telur mata sapi, sate ayam, dan kerupuk udang.",
            price: 25000,
            image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80",
            category: "food"
        },
        {
            id: 2,
            name: "Ayam Bakar Madu",
            desc: "Ayam kampung bakar dengan olesan madu dan sambal terasi.",
            price: 28000,
            image: "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=400&q=80",
            category: "food"
        },
        {
            id: 3,
            name: "Sate Ayam Madura",
            desc: "10 tusuk sate ayam dengan bumbu kacang kental.",
            price: 30000,
            image: "https://images.unsplash.com/photo-1555126634-323283e090fa?auto=format&fit=crop&w=400&q=80",
            category: "food"
        },
        {
            id: 4,
            name: "Es Kopi Susu Gula Aren",
            desc: "Kopi arabika house blend dengan susu fresh milk.",
            price: 18000,
            image: "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&w=400&q=80",
            category: "drink"
        },
        {
            id: 5,
            name: "Es Teh Manis Jumbo",
            desc: "Teh tubruk wangi melati dengan gula asli.",
            price: 8000,
            image: "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=400&q=80",
            category: "drink"
        },
        {
            id: 6,
            name: "Pisang Goreng Keju",
            desc: "Pisang kepok kuning digoreng crispy topping keju.",
            price: 15000,
            image: "https://images.unsplash.com/photo-1519708227418-c8fd9a3a2b7b?auto=format&fit=crop&w=400&q=80",
            category: "snack"
        }
    ];

    // --- STATE MANAGEMENT ---
    let cart = {}; // { itemId: quantity }

    // --- FUNCTIONS ---


    renderMenu();

    function formatRupiah(number) {
        return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(number);
    }

    function renderMenu() {
        const container = document.getElementById('menu-container');
        container.innerHTML = menuItems.map(item => `
                <div class="bg-white p-4 rounded-2xl shadow-card flex gap-4 items-center md:items-start group">
                    <div class="w-24 h-24 md:w-32 md:h-32 bg-gray-100 rounded-xl overflow-hidden shrink-0 relative">
                        <img src="${item.image}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" alt="${item.name}">
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="font-bold text-dark text-lg leading-tight mb-1 truncate">${item.name}</h3>
                        <p class="text-xs text-gray-500 line-clamp-2 mb-3 leading-relaxed">${item.desc}</p>
                        <div class="flex justify-between items-end">
                            <span class="font-bold text-accent text-lg">${formatRupiah(item.price)}</span>
                            
                            <div class="flex items-center" id="btn-group-${item.id}">
                                ${getButtonState(item.id)}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
    }

    function getButtonState(id) {
        const qty = cart[id] || 0;
        if (qty === 0) {
            return `
                <button onclick="addToCart(${id})" class="w-9 h-9 bg-secondary text-primary rounded-lg flex items-center justify-center hover:bg-primary hover:text-white transition-colors shadow-sm">
                    <i class="fa-solid fa-plus"></i>
                </button>`;
        } else {
            return `
                <div class="flex items-center gap-3 bg-[#F7F5F2] rounded-lg p-1 border border-gray-200 pop">
                    <button onclick="updateQty(${id}, -1)" class="w-7 h-7 bg-white text-primary rounded flex items-center justify-center shadow-sm"><i class="fa-solid fa-minus text-xs"></i></button>
                    <span class="font-bold text-dark text-sm w-2 text-center">${qty}</span>
                    <button onclick="updateQty(${id}, 1)" class="w-7 h-7 bg-primary text-white rounded flex items-center justify-center shadow-sm"><i class="fa-solid fa-plus text-xs"></i></button>
                </div>`;
        }
    }

    function addToCart(id) {
        cart[id] = 1;
        updateUI(id);
    }

    function updateQty(id, change) {
        if (cart[id] + change <= 0) {
            delete cart[id];
        } else {
            cart[id] += change;
        }
        updateUI(id);
    }

    function updateUI(id) {
        // Re-render button for specific item (Optimization: could replace innerHTML directly)
        const btnGroup = document.getElementById(`btn-group-${id}`);
        if (btnGroup) btnGroup.innerHTML = getButtonState(id);

        // Update Floating Bar
        updateCartBar();
        // Update Cart Modal Content if open
        renderCartItems();
    }

    function updateCartBar() {
        const totalQty = Object.values(cart).reduce((a, b) => a + b, 0);
        const bar = document.getElementById('cart-bar');

        if (totalQty > 0) {
            bar.classList.remove('hidden');
            // Calculate Total Price
            let total = 0;
            for (const [id, qty] of Object.entries(cart)) {
                const item = menuItems.find(i => i.id == id);
                total += item.price * qty;
            }

            document.getElementById('total-items-badge').innerText = totalQty;
            document.getElementById('total-price-bar').innerText = formatRupiah(total);
        } else {
            bar.classList.add('hidden');
            closeCartModal(); // Close modal if empty
        }
    }

    function openCartModal() {
        document.getElementById('cart-modal').classList.remove('hidden');
        renderCartItems();
    }

    function closeCartModal() {
        document.getElementById('cart-modal').classList.add('hidden');
    }

    function renderCartItems() {
        const container = document.getElementById('cart-items-container');
        let html = '';
        let subtotal = 0;

        if (Object.keys(cart).length === 0) {
            container.innerHTML = '<div class="text-center text-gray-400 py-10">Keranjang kosong</div>';
            return;
        }

        for (const [id, qty] of Object.entries(cart)) {
            const item = menuItems.find(i => i.id == id);
            const itemTotal = item.price * qty;
            subtotal += itemTotal;

            html += `
                <div class="flex gap-4 items-center border-b border-gray-100 pb-4 last:border-0">
                    <div class="w-16 h-16 bg-gray-100 rounded-xl overflow-hidden shrink-0">
                        <img src="${item.image}" class="w-full h-full object-cover">
                    </div>
                    <div class="flex-1">
                        <h4 class="font-bold text-dark text-sm">${item.name}</h4>
                        <p class="text-xs text-gray-500 mb-2">${formatRupiah(item.price)} / porsi</p>
                        <div class="flex justify-between items-center">
                             <div class="flex items-center gap-3 bg-[#F7F5F2] rounded-lg p-1">
                                <button onclick="updateQty(${id}, -1)" class="w-6 h-6 bg-white text-gray-500 rounded flex items-center justify-center shadow-sm hover:text-primary"><i class="fa-solid fa-minus text-[10px]"></i></button>
                                <span class="font-bold text-dark text-xs w-4 text-center">${qty}</span>
                                <button onclick="updateQty(${id}, 1)" class="w-6 h-6 bg-primary text-white rounded flex items-center justify-center shadow-sm"><i class="fa-solid fa-plus text-[10px]"></i></button>
                            </div>
                            <span class="font-bold text-primary text-sm">${formatRupiah(itemTotal)}</span>
                        </div>
                    </div>
                </div>
                `;
        }

        container.innerHTML = html;

        // Bill Calculation
        const tax = subtotal * 0.1;
        const total = subtotal + tax;

        document.getElementById('bill-subtotal').innerText = formatRupiah(subtotal);
        document.getElementById('bill-tax').innerText = formatRupiah(tax);
        document.getElementById('bill-total').innerText = formatRupiah(total);
    }

    function processCheckout() {
        closeCartModal();
        // Simulasi Loading
        setTimeout(() => {
            document.getElementById('success-view').classList.remove('hidden');
        }, 300);
    }
