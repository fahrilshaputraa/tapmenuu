// --- DATA ---
        let orders = [
            {
                id: "ORD-1024",
                table: "Meja 4 (Indoor)",
                time: "Baru Saja",
                timestamp: Date.now(),
                status: "new",
                total: 58000,
                items: [
                    { name: "Nasi Goreng Spesial", qty: 1, price: 25000, notes: "Pedas, Tanpa Acar" },
                    { name: "Sate Ayam Madura", qty: 1, price: 25000, notes: "" },
                    { name: "Es Teh Manis", qty: 1, price: 8000, notes: "Es Sedikit" }
                ]
            },
            {
                id: "ORD-1023",
                table: "Meja 2",
                time: "5 Menit lalu",
                timestamp: Date.now() - 300000,
                status: "new",
                total: 18000,
                items: [
                    { name: "Kopi Susu Gula Aren", qty: 1, price: 18000, notes: "Less Sugar" }
                ]
            },
            {
                id: "ORD-1022",
                table: "Meja 8 (Outdoor)",
                time: "10 Menit lalu",
                timestamp: Date.now() - 600000,
                status: "new",
                total: 45000,
                items: [
                    { name: "Pisang Keju", qty: 2, price: 15000, notes: "" },
                    { name: "Jus Alpukat", qty: 1, price: 15000, notes: "" }
                ]
            },
            {
                id: "ORD-1021",
                table: "Meja 1",
                time: "15 Menit lalu",
                timestamp: Date.now() - 900000,
                status: "processing",
                total: 120000,
                items: [
                    { name: "Ayam Bakar Madu", qty: 2, price: 30000, notes: "" },
                    { name: "Nasi Goreng Spesial", qty: 2, price: 25000, notes: "" },
                    { name: "Es Jeruk", qty: 2, price: 10000, notes: "" }
                ]
            },
            {
                id: "ORD-1020",
                table: "Bungkus - Rini",
                time: "20 Menit lalu",
                timestamp: Date.now() - 1200000,
                status: "ready",
                total: 30000,
                items: [
                    { name: "Ayam Geprek", qty: 2, price: 15000, notes: "Sambal Pisah" }
                ]
            },
            {
                id: "ORD-1019",
                table: "Meja 5",
                time: "30 Menit lalu",
                timestamp: Date.now() - 1800000,
                status: "completed",
                total: 55000,
                items: [
                    { name: "Mie Goreng Jawa", qty: 2, price: 20000, notes: "" },
                    { name: "Es Teh", qty: 3, price: 5000, notes: "" }
                ]
            }
        ];

        let currentFilter = 'all';

        // --- INIT ---
        window.onload = () => {
            updateTime();
            renderOrders();
            setInterval(updateTime, 60000);
        };

        // --- FUNCTIONS ---
        function formatRupiah(num) {
            return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(num);
        }

        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').innerText = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
            document.getElementById('current-date').innerText = now.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' });
        }

        function renderOrders() {
            const container = document.getElementById('orders-container');
            const searchVal = document.getElementById('search-order').value.toLowerCase();

            container.innerHTML = '';

            const filtered = orders.filter(o => {
                const matchStatus = currentFilter === 'all' || o.status === currentFilter;
                const matchSearch = o.id.toLowerCase().includes(searchVal) || o.table.toLowerCase().includes(searchVal);
                return matchStatus && matchSearch;
            });

            if (filtered.length === 0) {
                document.getElementById('empty-state').classList.remove('hidden');
            } else {
                document.getElementById('empty-state').classList.add('hidden');
            }

            filtered.forEach(order => {
                let statusBadge = '';
                let actionBtn = '';
                let cardClass = 'bg-white rounded-2xl p-5 shadow-card border border-gray-100 relative transition-all hover:shadow-md';

                if (order.status === 'new') {
                    statusBadge = `<span class="bg-yellow-100 text-yellow-700 text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wide flex items-center gap-1"><i class="fa-solid fa-circle text-[6px] animate-pulse"></i> Baru</span>`;
                    actionBtn = `<button onclick="updateStatus('${order.id}', 'processing')" class="w-full py-2.5 bg-primary text-white font-bold rounded-xl text-sm hover:bg-primaryLight transition-colors shadow-sm mt-4">Terima Pesanan</button>`;
                    cardClass += ' new-order-card'; // Blinking border
                } else if (order.status === 'processing') {
                    statusBadge = `<span class="bg-blue-100 text-blue-700 text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wide"><i class="fa-solid fa-fire-burner mr-1"></i> Dimasak</span>`;
                    actionBtn = `<button onclick="updateStatus('${order.id}', 'ready')" class="w-full py-2.5 bg-blue-600 text-white font-bold rounded-xl text-sm hover:bg-blue-700 transition-colors shadow-sm mt-4">Selesai Masak</button>`;
                } else if (order.status === 'ready') {
                    statusBadge = `<span class="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wide"><i class="fa-solid fa-bell-concierge mr-1"></i> Siap Saji</span>`;
                    actionBtn = `<button onclick="updateStatus('${order.id}', 'completed')" class="w-full py-2.5 bg-green-600 text-white font-bold rounded-xl text-sm hover:bg-green-700 transition-colors shadow-sm mt-4">Antar & Selesai</button>`;
                } else {
                    statusBadge = `<span class="bg-gray-100 text-gray-600 text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wide"><i class="fa-solid fa-check mr-1"></i> Selesai</span>`;
                    actionBtn = `<button class="w-full py-2.5 bg-gray-100 text-gray-400 font-bold rounded-xl text-sm cursor-not-allowed mt-4">Arsip</button>`;
                    cardClass += ' opacity-75';
                }

                // Items Preview (Max 2)
                let itemsHtml = '';
                order.items.slice(0, 2).forEach(item => {
                    itemsHtml += `
                        <div class="flex justify-between text-sm mb-1">
                            <span class="text-gray-600"><span class="font-bold text-dark">${item.qty}x</span> ${item.name}</span>
                        </div>
                    `;
                });
                if (order.items.length > 2) {
                    itemsHtml += `<div class="text-xs text-gray-400 italic mt-1">+${order.items.length - 2} item lainnya...</div>`;
                }

                const html = `
                <div class="${cardClass}">
                    <div class="flex justify-between items-start mb-3 border-b border-gray-100 pb-3">
                        <div>
                            <h4 class="font-extrabold text-lg text-dark leading-tight">${order.table}</h4>
                            <p class="text-xs text-gray-400 font-mono mt-0.5">${order.id}</p>
                        </div>
                        <div class="text-right flex flex-col items-end gap-1">
                            ${statusBadge}
                            <span class="text-[10px] text-gray-400 flex items-center gap-1"><i class="fa-regular fa-clock"></i> ${order.time}</span>
                        </div>
                    </div>
                    
                    <div class="mb-4 min-h-[60px] cursor-pointer hover:bg-gray-50 p-2 -mx-2 rounded-lg transition-colors" onclick="openDetail('${order.id}')">
                        ${itemsHtml}
                    </div>

                    <div class="flex justify-between items-center border-t border-gray-100 pt-3">
                        <span class="text-xs font-bold text-gray-400 uppercase">Total</span>
                        <span class="font-extrabold text-lg text-primary">${formatRupiah(order.total)}</span>
                    </div>

                    ${actionBtn}
                </div>
                `;
                container.innerHTML += html;
            });

            updateTabs();
        }

        function updateTabs() {
            const tabs = ['all', 'new', 'processing', 'ready', 'completed'];
            tabs.forEach(t => {
                const btn = document.getElementById(`tab-${t}`);
                if (t === currentFilter) {
                    btn.classList.add('bg-primary', 'text-white', 'shadow-sm');
                    btn.classList.remove('bg-white', 'text-gray-500', 'border-gray-200', 'hover:bg-gray-50', 'hover:text-gray-700');
                    // Remove specific hover colors for active tab to keep it consistent
                    btn.classList.remove('hover:text-new-order', 'hover:text-processing', 'hover:text-ready');
                } else {
                    btn.classList.remove('bg-primary', 'text-white', 'shadow-sm');
                    btn.classList.add('bg-white', 'text-gray-500', 'border-gray-200');
                }
            });
        }

        function filterOrders(status) {
            currentFilter = status;
            renderOrders();
        }

        function updateStatus(id, newStatus) {
            const order = orders.find(o => o.id === id);
            if (order) {
                order.status = newStatus;
                // Move timestamp to simulate real-time
                if (newStatus === 'processing') order.time = 'Sedang Dimasak';
                if (newStatus === 'ready') order.time = 'Baru Saja';
                renderOrders();
            }
        }

        // --- MODAL LOGIC ---
        function openDetail(id) {
            const order = orders.find(o => o.id === id);
            if (!order) return;

            document.getElementById('modal-order-id').innerText = order.id;
            document.getElementById('modal-table').innerText = order.table;
            document.getElementById('modal-time').innerText = order.time; // Should be real time in app
            document.getElementById('modal-total').innerText = formatRupiah(order.total);

            // Status Badge in Modal
            const statusEl = document.getElementById('modal-status');
            if (order.status === 'new') { statusEl.className = "text-xs font-bold px-2 py-1 rounded bg-yellow-100 text-yellow-700"; statusEl.innerText = "Baru"; }
            else if (order.status === 'processing') { statusEl.className = "text-xs font-bold px-2 py-1 rounded bg-blue-100 text-blue-700"; statusEl.innerText = "Diproses"; }
            else if (order.status === 'ready') { statusEl.className = "text-xs font-bold px-2 py-1 rounded bg-green-100 text-green-700"; statusEl.innerText = "Siap Saji"; }
            else { statusEl.className = "text-xs font-bold px-2 py-1 rounded bg-gray-100 text-gray-600"; statusEl.innerText = "Selesai"; }

            // Items List
            const itemsContainer = document.getElementById('modal-items');
            itemsContainer.innerHTML = '';
            order.items.forEach(item => {
                itemsContainer.innerHTML += `
                    <div class="bg-white border border-gray-100 p-3 rounded-lg flex justify-between items-start">
                        <div>
                            <p class="font-bold text-dark"><span class="text-primary mr-1">${item.qty}x</span> ${item.name}</p>
                            ${item.notes ? `<p class="text-xs text-gray-500 italic mt-1 bg-gray-50 inline-block px-2 py-0.5 rounded"><i class="fa-regular fa-note-sticky mr-1"></i>${item.notes}</p>` : ''}
                        </div>
                        <span class="font-bold text-sm text-gray-700">${formatRupiah(item.price * item.qty)}</span>
                    </div>
                `;
            });

            // Action Button Logic
            const btn = document.getElementById('modal-action-btn');
            btn.onclick = () => { updateStatus(id, getNextStatus(order.status)); closeModal(); };

            if (order.status === 'new') { btn.innerText = "Terima Pesanan"; btn.className = "py-3 bg-primary text-white font-bold rounded-xl shadow hover:bg-primaryLight transition-colors"; btn.disabled = false; }
            else if (order.status === 'processing') { btn.innerText = "Selesai Masak"; btn.className = "py-3 bg-blue-600 text-white font-bold rounded-xl shadow hover:bg-blue-700 transition-colors"; btn.disabled = false; }
            else if (order.status === 'ready') { btn.innerText = "Antar & Selesai"; btn.className = "py-3 bg-green-600 text-white font-bold rounded-xl shadow hover:bg-green-700 transition-colors"; btn.disabled = false; }
            else { btn.innerText = "Pesanan Selesai"; btn.className = "py-3 bg-gray-200 text-gray-400 font-bold rounded-xl cursor-not-allowed"; btn.disabled = true; }

            document.getElementById('order-modal').classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('order-modal').classList.add('hidden');
        }

        function getNextStatus(current) {
            if (current === 'new') return 'processing';
            if (current === 'processing') return 'ready';
            if (current === 'ready') return 'completed';
            return 'completed';
        }
