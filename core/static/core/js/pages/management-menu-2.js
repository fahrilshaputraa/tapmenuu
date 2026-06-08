// --- DATA ---
        let menuList = [
            {
                id: 1,
                name: "Nasi Goreng Spesial",
                category: "food",
                price: 25000,
                discount: 0,
                tax: 10,
                desc: "Lengkap dengan telur dan sate.",
                image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=300&q=80",
                active: true,
                labels: ['favorite'],
                variants: [
                    {
                        name: "Level Pedas",
                        type: "radio",
                        options: [
                            { name: "Tidak Pedas", price: 0 },
                            { name: "Sedang", price: 0 },
                            { name: "Pedas", price: 0 }
                        ]
                    }
                ]
            },
            { id: 2, name: "Es Teh Manis", category: "drink", price: 5000, discount: 0, tax: 10, desc: "Teh asli menyegarkan.", image: "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=300&q=80", active: true, labels: [], variants: [] },
            { id: 3, name: "Ayam Bakar Madu", category: "food", price: 35000, discount: 15, tax: 10, desc: "Ayam kampung bumbu madu.", image: "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=300&q=80", active: true, labels: ['new'], variants: [] },
            { id: 4, name: "Pisang Keju", category: "snack", price: 15000, discount: 0, tax: 10, desc: "Pisang kepok pilihan.", image: "https://images.unsplash.com/photo-1519708227418-c8fd9a3a2b7b?auto=format&fit=crop&w=300&q=80", active: true, labels: [], variants: [] },
        ];

        let currentFilter = 'all';
        let editingId = null;

        // --- INIT ---
        window.onload = () => {
            renderMenu();
        };

        // --- FUNCTIONS ---
        function formatRupiah(num) {
            return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(num);
        }

        function renderMenu() {
            const container = document.getElementById('menu-container');
            const searchVal = document.getElementById('search-input').value.toLowerCase();

            container.innerHTML = '';

            const filtered = menuList.filter(item => {
                const matchCat = currentFilter === 'all' || item.category === currentFilter;
                const matchSearch = item.name.toLowerCase().includes(searchVal);
                return matchCat && matchSearch;
            });

            if (filtered.length === 0) {
                document.getElementById('empty-state').classList.remove('hidden');
            } else {
                document.getElementById('empty-state').classList.add('hidden');
            }

            filtered.forEach(item => {
                const statusColor = item.active ? 'text-primary' : 'text-danger';
                const statusText = item.active ? 'Tersedia' : 'Habis';
                const opacity = item.active ? '' : 'opacity-75 grayscale-[0.5]';
                const checked = item.active ? 'checked' : '';
                const hasDiscount = item.discount && item.discount > 0;
                const finalPrice = hasDiscount ? item.price * ((100 - item.discount) / 100) : item.price;

                let labelsHtml = '';
                if (item.labels.includes('favorite')) labelsHtml += `<span class="bg-[#FFF0EB] text-accent text-[10px] font-bold px-2 py-0.5 rounded-full border border-accent/20 mr-1">Favorit</span>`;
                if (item.labels.includes('new')) labelsHtml += `<span class="bg-secondary text-primary text-[10px] font-bold px-2 py-0.5 rounded-full border border-primary/20 mr-1">Baru</span>`;

                // Variant Badge
                const variantBadge = item.variants && item.variants.length > 0
                    ? `<span class="bg-gray-100 text-gray-500 text-[10px] font-bold px-2 py-0.5 rounded-full border border-gray-200 mr-1">${item.variants.length} Varian</span>`
                    : '';

                const card = `
                <div class="bg-white rounded-2xl border border-gray-100 shadow-card hover:shadow-lg transition-all duration-300 group overflow-hidden flex flex-col h-full ${opacity}">
                    <div class="h-40 bg-gray-100 relative overflow-hidden">
                        <img src="${item.image}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
                        <div class="absolute top-2 right-2">
                            <button onclick="deleteItem(${item.id})" class="w-8 h-8 bg-white/90 backdrop-blur rounded-lg text-red-400 hover:text-red-600 flex items-center justify-center shadow-sm transition-colors"><i class="fa-solid fa-trash"></i></button>
                        </div>
                        <div class="absolute bottom-2 left-2 flex gap-1">
                            <span class="bg-black/60 backdrop-blur text-white px-2 py-1 rounded text-xs font-bold">
                                ${item.category === 'food' ? 'Makanan' : item.category === 'drink' ? 'Minuman' : 'Cemilan'}
                            </span>
                            ${hasDiscount ? `<span class="bg-red-500 text-white px-2 py-1 rounded text-xs font-bold">-${item.discount}%</span>` : ''}
                        </div>
                    </div>
                    
                    <div class="p-4 flex flex-col flex-1">
                        <div class="flex justify-between items-start mb-1">
                            <h3 class="font-bold text-dark text-lg leading-tight line-clamp-1">${item.name}</h3>
                        </div>
                        <div class="mb-2 flex flex-wrap gap-1 items-center">
                            ${labelsHtml}
                            ${variantBadge}
                        </div>
                        <p class="text-xs text-gray-500 mb-3 line-clamp-2 flex-1">${item.desc}</p>
                        
                        <div class="mb-4">
                             ${hasDiscount ? `<span class="text-gray-400 text-xs line-through mr-1">${formatRupiah(item.price)}</span>` : ''}
                             <span class="text-accent font-extrabold text-lg">${formatRupiah(finalPrice)}</span>
                        </div>

                        <div class="flex items-center justify-between pt-3 border-t border-gray-50">
                            <div class="flex items-center gap-2">
                                <div class="relative inline-block w-10 mr-2 align-middle select-none">
                                    <input type="checkbox" onchange="toggleStatus(${item.id})" class="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer transition-all duration-300 left-0 border-gray-300" ${checked}/>
                                    <label class="toggle-label block overflow-hidden h-5 rounded-full bg-gray-300 cursor-pointer transition-colors duration-300"></label>
                                </div>
                                <span class="text-xs font-bold ${statusColor}">${statusText}</span>
                            </div>
                            
                            <button onclick="editItem(${item.id})" class="text-primary hover:bg-secondary/30 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors">
                                Edit <i class="fa-solid fa-pen ml-1"></i>
                            </button>
                        </div>
                    </div>
                </div>
                `;
                container.innerHTML += card;
            });

            updateTabs();
        }

        function updateTabs() {
            const tabs = ['all', 'food', 'drink', 'snack'];
            tabs.forEach(t => {
                const btn = document.getElementById(`tab-${t}`);
                if (t === currentFilter) {
                    btn.classList.add('bg-primary', 'text-white', 'shadow-sm');
                    btn.classList.remove('bg-white', 'text-gray-500', 'border-gray-200');
                } else {
                    btn.classList.remove('bg-primary', 'text-white', 'shadow-sm');
                    btn.classList.add('bg-white', 'text-gray-500', 'border-gray-200');
                }
            });
        }

        function filterMenu(category) {
            currentFilter = category;
            renderMenu();
        }

        function searchMenu() {
            renderMenu();
        }

        function toggleStatus(id) {
            const item = menuList.find(i => i.id === id);
            if (item) {
                item.active = !item.active;
                renderMenu();
            }
        }

        // --- MODAL & TABS LOGIC ---
        function switchTab(tabName) {
            ['basic', 'pricing', 'variants', 'others'].forEach(t => {
                document.getElementById(`tab-content-${t}`).classList.add('hidden');
                document.getElementById(`tab-btn-${t}`).classList.remove('border-primary', 'text-primary');
                document.getElementById(`tab-btn-${t}`).classList.add('border-transparent', 'text-gray-500');
            });
            document.getElementById(`tab-content-${tabName}`).classList.remove('hidden');
            document.getElementById(`tab-btn-${tabName}`).classList.add('border-primary', 'text-primary');
            document.getElementById(`tab-btn-${tabName}`).classList.remove('border-transparent', 'text-gray-500');
        }

        function openAddModal() {
            editingId = null;
            document.getElementById('modal-title').innerText = 'Tambah Menu Baru';

            // Reset inputs
            document.getElementById('input-name').value = '';
            document.getElementById('input-category').value = 'food';
            document.getElementById('input-desc').value = '';
            document.getElementById('input-price').value = '';
            document.getElementById('input-discount').value = '';
            document.getElementById('input-tax').value = '10';
            document.getElementById('input-stock').value = '';
            document.getElementById('toggle-stock').checked = false;
            toggleStockInput();
            document.getElementById('label-favorite').checked = false;
            document.getElementById('label-new').checked = false;
            document.getElementById('toggle-active').checked = true;

            document.getElementById('preview-image').src = '';
            document.getElementById('preview-image').classList.add('hidden');

            // Clear variants
            document.getElementById('variants-container').innerHTML = '';

            switchTab('basic'); // Default tab
            calculateFinalPrice();
            document.getElementById('menu-modal').classList.remove('hidden');
        }

        function editItem(id) {
            const item = menuList.find(i => i.id === id);
            if (!item) return;

            editingId = id;
            document.getElementById('modal-title').innerText = 'Edit Menu';

            // Populate fields
            document.getElementById('input-name').value = item.name;
            document.getElementById('input-category').value = item.category;
            document.getElementById('input-desc').value = item.desc;
            document.getElementById('input-price').value = item.price;
            document.getElementById('input-discount').value = item.discount || '';
            document.getElementById('input-tax').value = item.tax || 10;

            // Stock
            if (item.stockQty) {
                document.getElementById('toggle-stock').checked = true;
                document.getElementById('input-stock').value = item.stockQty;
            } else {
                document.getElementById('toggle-stock').checked = false;
                document.getElementById('input-stock').value = '';
            }
            toggleStockInput();

            // Labels & Active
            document.getElementById('label-favorite').checked = item.labels.includes('favorite');
            document.getElementById('label-new').checked = item.labels.includes('new');
            document.getElementById('toggle-active').checked = item.active;

            if (item.image) {
                document.getElementById('preview-image').src = item.image;
                document.getElementById('preview-image').classList.remove('hidden');
            }

            // Populate Variants
            const vContainer = document.getElementById('variants-container');
            vContainer.innerHTML = '';
            if (item.variants) {
                item.variants.forEach(group => addVariantGroup(group));
            }

            switchTab('basic');
            calculateFinalPrice();
            document.getElementById('menu-modal').classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('menu-modal').classList.add('hidden');
        }

        function toggleStockInput() {
            const isChecked = document.getElementById('toggle-stock').checked;
            const container = document.getElementById('stock-input-container');
            if (isChecked) {
                container.classList.remove('hidden');
            } else {
                container.classList.add('hidden');
            }
        }

        function calculateFinalPrice() {
            const price = parseFloat(document.getElementById('input-price').value) || 0;
            const discount = parseFloat(document.getElementById('input-discount').value) || 0;

            document.getElementById('preview-original').innerText = formatRupiah(price);

            let final = price;
            if (discount > 0) {
                final = price * ((100 - discount) / 100);
                document.getElementById('preview-discount-label').innerText = `Hemat ${discount}%`;
                document.getElementById('preview-original-container').classList.remove('hidden');
            } else {
                document.getElementById('preview-discount-label').innerText = '';
                document.getElementById('preview-original-container').classList.add('hidden');
            }

            document.getElementById('preview-final').innerText = formatRupiah(final);
        }

        function handleImageUpload(input) {
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    document.getElementById('preview-image').src = e.target.result;
                    document.getElementById('preview-image').classList.remove('hidden');
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        // --- VARIANT LOGIC ---
        function addVariantGroup(data = null) {
            const container = document.getElementById('variants-container');
            const groupId = Date.now() + Math.random().toString(36).substr(2, 5);

            const groupName = data ? data.name : '';
            const groupType = data ? data.type : 'radio';

            const groupHtml = document.createElement('div');
            groupHtml.className = 'variant-group bg-gray-50 rounded-xl p-4 border border-gray-200 relative';
            groupHtml.id = `v-group-${groupId}`;
            groupHtml.innerHTML = `
                <div class="flex justify-between items-start mb-3">
                    <div class="flex-1 grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Nama Grup</label>
                            <input type="text" class="group-name-input w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary" placeholder="Cth: Level Pedas" value="${groupName}">
                        </div>
                        <div>
                            <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Tipe Pilihan</label>
                            <select class="group-type-input w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary">
                                <option value="radio" ${groupType === 'radio' ? 'selected' : ''}>Pilih Satu (Wajib)</option>
                                <option value="checkbox" ${groupType === 'checkbox' ? 'selected' : ''}>Pilih Banyak (Opsional)</option>
                            </select>
                        </div>
                    </div>
                    <button onclick="removeVariantGroup('${groupId}')" class="ml-3 text-gray-400 hover:text-red-500"><i class="fa-solid fa-trash"></i></button>
                </div>
                
                <div class="space-y-2" id="v-options-${groupId}">
                    <!-- Options go here -->
                </div>
                
                <button onclick="addVariantOption('${groupId}')" class="mt-3 text-xs font-bold text-primary hover:underline">+ Tambah Opsi</button>
            `;
            container.appendChild(groupHtml);

            // Add Options
            if (data && data.options) {
                data.options.forEach(opt => addVariantOption(groupId, opt));
            } else {
                addVariantOption(groupId); // Add one default option
            }
        }

        function addVariantOption(groupId, data = null) {
            const optionsContainer = document.getElementById(`v-options-${groupId}`);
            const optId = Date.now() + Math.random().toString(36).substr(2, 5);

            const optName = data ? data.name : '';
            const optPrice = data ? data.price : '';

            const optDiv = document.createElement('div');
            optDiv.className = 'flex gap-2 items-center option-row';
            optDiv.id = `v-opt-${optId}`;
            optDiv.innerHTML = `
                <input type="text" class="opt-name-input flex-1 bg-white border border-gray-200 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-primary" placeholder="Nama Opsi (Cth: Sedang)" value="${optName}">
                <div class="relative w-24">
                     <span class="absolute left-2 top-1/2 -translate-y-1/2 text-gray-400 text-[10px] font-bold">+Rp</span>
                    <input type="number" class="opt-price-input w-full bg-white border border-gray-200 rounded-lg pl-8 pr-2 py-2 text-xs focus:outline-none focus:border-primary" placeholder="0" value="${optPrice}">
                </div>
                <button onclick="removeVariantOption('${optId}')" class="text-gray-300 hover:text-red-500"><i class="fa-solid fa-xmark"></i></button>
            `;
            optionsContainer.appendChild(optDiv);
        }

        function removeVariantGroup(groupId) {
            const el = document.getElementById(`v-group-${groupId}`);
            if (el) el.remove();
        }

        function removeVariantOption(optId) {
            const el = document.getElementById(`v-opt-${optId}`);
            if (el) el.remove();
        }

        function collectVariantData() {
            const variants = [];
            const groups = document.querySelectorAll('.variant-group');

            groups.forEach(group => {
                const name = group.querySelector('.group-name-input').value;
                const type = group.querySelector('.group-type-input').value;
                const options = [];

                group.querySelectorAll('.option-row').forEach(opt => {
                    const optName = opt.querySelector('.opt-name-input').value;
                    const optPrice = parseInt(opt.querySelector('.opt-price-input').value) || 0;
                    if (optName) {
                        options.push({ name: optName, price: optPrice });
                    }
                });

                if (name && options.length > 0) {
                    variants.push({ name, type, options });
                }
            });
            return variants;
        }

        // --- SAVE LOGIC ---
        function saveMenu() {
            // Gather Data
            const name = document.getElementById('input-name').value;
            const category = document.getElementById('input-category').value;
            const desc = document.getElementById('input-desc').value;
            const price = parseInt(document.getElementById('input-price').value);
            const discount = parseInt(document.getElementById('input-discount').value) || 0;
            const tax = parseInt(document.getElementById('input-tax').value) || 10;

            // Stock Logic
            let stockQty = null;
            if (document.getElementById('toggle-stock').checked) {
                stockQty = parseInt(document.getElementById('input-stock').value) || 0;
            }

            // Labels Logic
            let labels = [];
            if (document.getElementById('label-favorite').checked) labels.push('favorite');
            if (document.getElementById('label-new').checked) labels.push('new');

            const active = document.getElementById('toggle-active').checked;

            // Image Logic
            let image = document.getElementById('preview-image').src;
            if (!image || image.includes(window.location.href)) {
                image = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=300&q=80";
            }

            // Collect Variants
            const variants = collectVariantData();

            // Validation
            if (!name || isNaN(price)) return alert("Nama dan Harga dasar wajib diisi!");

            const newData = {
                name, category, desc, price, discount, tax, stockQty, labels, active, image, variants
            };

            if (editingId) {
                const idx = menuList.findIndex(i => i.id === editingId);
                if (idx !== -1) {
                    menuList[idx] = { ...menuList[idx], ...newData };
                }
            } else {
                const newId = menuList.length > 0 ? Math.max(...menuList.map(i => i.id)) + 1 : 1;
                menuList.push({ id: newId, ...newData });
            }

            closeModal();
            renderMenu();
        }

        function deleteItem(id) {
            if (confirm("Hapus menu ini secara permanen?")) {
                menuList = menuList.filter(i => i.id !== id);
                renderMenu();
            }
        }
