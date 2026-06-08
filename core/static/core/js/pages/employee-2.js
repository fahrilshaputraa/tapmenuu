// --- DATA ---
        let employees = [
            { id: 1, name: "Siti Aminah", role: "Kasir", pin: "112233", active: true, avatar: "https://i.pravatar.cc/150?img=1" },
            { id: 2, name: "Joko Susilo", role: "Dapur", pin: "556677", active: true, avatar: "https://i.pravatar.cc/150?img=11" },
            { id: 3, name: "Rini Wati", role: "Pelayan", pin: "889900", active: true, avatar: "https://i.pravatar.cc/150?img=5" },
            { id: 4, name: "Andi Setiawan", role: "Pelayan", pin: "000000", active: false, avatar: "https://i.pravatar.cc/150?img=3" },
        ];

        let editingId = null;

        // --- INIT ---
        window.onload = () => {
            renderEmployees();
        };

        // --- FUNCTIONS ---
        function renderEmployees() {
            const tbody = document.getElementById('employee-table-body');
            const searchVal = document.getElementById('search-input').value.toLowerCase();

            tbody.innerHTML = '';

            const filtered = employees.filter(emp =>
                emp.name.toLowerCase().includes(searchVal) ||
                emp.role.toLowerCase().includes(searchVal)
            );

            if (filtered.length === 0) {
                document.getElementById('empty-state').classList.remove('hidden');
            } else {
                document.getElementById('empty-state').classList.add('hidden');
            }

            // Update Stats
            document.getElementById('total-count').innerText = employees.length;
            document.getElementById('active-count').innerText = employees.filter(e => e.active).length;

            filtered.forEach(emp => {
                const roleBadge = getRoleBadge(emp.role);
                const opacity = emp.active ? '' : 'opacity-50 grayscale';
                const checked = emp.active ? 'checked' : '';
                const statusText = emp.active ? '<span class="text-green-600 font-bold text-xs">Aktif</span>' : '<span class="text-gray-400 font-bold text-xs">Nonaktif</span>';

                const row = `
                <tr class="hover:bg-gray-50/80 transition-colors group ${opacity}">
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-3">
                            <img src="${emp.avatar}" class="w-10 h-10 rounded-full object-cover border border-gray-200">
                            <div>
                                <div class="font-bold text-dark text-sm">${emp.name}</div>
                                <div class="text-xs text-gray-400">ID: EMP-${emp.id}</div>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        ${roleBadge}
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-2">
                            <span class="font-mono font-bold text-gray-500 tracking-widest text-xs">******</span>
                            <button onclick="alert('PIN: ${emp.pin}')" class="text-gray-300 hover:text-primary transition-colors" title="Lihat PIN">
                                <i class="fa-regular fa-eye text-xs"></i>
                            </button>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <div class="flex items-center gap-3">
                            <div class="relative inline-block w-9 align-middle select-none">
                                <input type="checkbox" onchange="toggleStatus(${emp.id})" class="toggle-checkbox absolute block w-4 h-4 rounded-full bg-white border-4 appearance-none cursor-pointer transition-all duration-300 left-0 border-gray-300" ${checked}/>
                                <label class="toggle-label block overflow-hidden h-4 rounded-full bg-gray-300 cursor-pointer transition-colors duration-300"></label>
                            </div>
                            ${statusText}
                        </div>
                    </td>
                    <td class="px-6 py-4 text-right">
                        <div class="flex justify-end gap-2">
                            <button onclick="editEmployee(${emp.id})" class="w-8 h-8 rounded-lg border border-gray-200 text-gray-500 hover:text-primary hover:border-primary hover:bg-white transition-all flex items-center justify-center">
                                <i class="fa-solid fa-pen text-xs"></i>
                            </button>
                            <button onclick="deleteEmployee(${emp.id})" class="w-8 h-8 rounded-lg border border-gray-200 text-gray-500 hover:text-red-500 hover:border-red-200 hover:bg-red-50 transition-all flex items-center justify-center">
                                <i class="fa-solid fa-trash text-xs"></i>
                            </button>
                        </div>
                    </td>
                </tr>
                `;
                tbody.innerHTML += row;
            });
        }

        function getRoleBadge(role) {
            let classes = "px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wide inline-flex items-center gap-1.5";
            switch (role) {
                case 'Kasir': return `<span class="${classes} bg-blue-50 text-blue-600 border border-blue-100"><i class="fa-solid fa-cash-register"></i> Kasir</span>`;
                case 'Dapur': return `<span class="${classes} bg-orange-50 text-orange-600 border border-orange-100"><i class="fa-solid fa-fire-burner"></i> Dapur</span>`;
                case 'Pelayan': return `<span class="${classes} bg-purple-50 text-purple-600 border border-purple-100"><i class="fa-solid fa-bell-concierge"></i> Pelayan</span>`;
                case 'Manajer': return `<span class="${classes} bg-primary/10 text-primary border border-primary/20"><i class="fa-solid fa-user-tie"></i> Manajer</span>`;
                default: return `<span class="${classes} bg-gray-100 text-gray-600">Staff</span>`;
            }
        }

        function toggleStatus(id) {
            const emp = employees.find(e => e.id === id);
            if (emp) {
                emp.active = !emp.active;
                renderEmployees();
            }
        }

        // --- MODAL LOGIC ---
        function openAddModal() {
            editingId = null;
            document.getElementById('modal-title').innerText = 'Tambah Karyawan';
            document.getElementById('input-name').value = '';
            document.getElementById('input-role').value = 'Kasir';
            document.getElementById('input-pin').value = '';
            document.getElementById('preview-avatar').src = 'https://cdn-icons-png.flaticon.com/512/847/847969.png';

            document.getElementById('employee-modal').classList.remove('hidden');
        }

        function editEmployee(id) {
            const emp = employees.find(e => e.id === id);
            if (!emp) return;

            editingId = id;
            document.getElementById('modal-title').innerText = 'Edit Karyawan';
            document.getElementById('input-name').value = emp.name;
            document.getElementById('input-role').value = emp.role;
            document.getElementById('input-pin').value = emp.pin;
            document.getElementById('preview-avatar').src = emp.avatar;

            document.getElementById('employee-modal').classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('employee-modal').classList.add('hidden');
        }

        function togglePinVisibility() {
            const input = document.getElementById('input-pin');
            const icon = document.getElementById('pin-icon');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }

        function handleAvatarUpload(input) {
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    document.getElementById('preview-avatar').src = e.target.result;
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function saveEmployee() {
            const name = document.getElementById('input-name').value;
            const role = document.getElementById('input-role').value;
            const pin = document.getElementById('input-pin').value;
            const avatar = document.getElementById('preview-avatar').src;

            if (!name || pin.length < 4) return alert("Nama dan PIN (min 4 digit) wajib diisi!");

            if (editingId) {
                const idx = employees.findIndex(e => e.id === editingId);
                if (idx !== -1) {
                    employees[idx] = { ...employees[idx], name, role, pin, avatar };
                }
            } else {
                const newId = employees.length > 0 ? Math.max(...employees.map(e => e.id)) + 1 : 1;
                employees.push({ id: newId, name, role, pin, active: true, avatar });
            }

            closeModal();
            renderEmployees();
        }

        function deleteEmployee(id) {
            if (confirm("Hapus karyawan ini?")) {
                employees = employees.filter(e => e.id !== id);
                renderEmployees();
            }
        }
