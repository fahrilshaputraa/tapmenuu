// --- DATA DUMMY ---
        const reportData = {
            today: {
                revenue: 1250000,
                transactions: 45,
                average: 27777,
                chartLabels: ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"],
                chartData: [150000, 300000, 550000, 200000, 400000, 600000, 350000],
                employees: [
                    { name: "Siti Aminah", transactions: 20, total: 600000, avatar: "https://i.pravatar.cc/150?img=1" },
                    { name: "Andi Setiawan", transactions: 15, total: 450000, avatar: "https://i.pravatar.cc/150?img=3" },
                    { name: "Rini Wati", transactions: 10, total: 200000, avatar: "https://i.pravatar.cc/150?img=5" }
                ]
            },
            week: {
                revenue: 8450000,
                transactions: 320,
                average: 26406,
                chartLabels: ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
                chartData: [1100000, 1250000, 900000, 1400000, 1800000, 2100000, 1600000],
                employees: [
                    { name: "Siti Aminah", transactions: 120, total: 3500000, avatar: "https://i.pravatar.cc/150?img=1" },
                    { name: "Andi Setiawan", transactions: 110, total: 3000000, avatar: "https://i.pravatar.cc/150?img=3" },
                    { name: "Rini Wati", transactions: 90, total: 1950000, avatar: "https://i.pravatar.cc/150?img=5" }
                ]
            },
            month: {
                revenue: 35600000,
                transactions: 1450,
                average: 24551,
                chartLabels: ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"],
                chartData: [8500000, 9200000, 8100000, 9800000],
                employees: [
                    { name: "Siti Aminah", transactions: 500, total: 14000000, avatar: "https://i.pravatar.cc/150?img=1" },
                    { name: "Andi Setiawan", transactions: 480, total: 12500000, avatar: "https://i.pravatar.cc/150?img=3" },
                    { name: "Rini Wati", transactions: 470, total: 9100000, avatar: "https://i.pravatar.cc/150?img=5" }
                ]
            }
        };

        const transactions = [
            { id: "ORD-0094", time: "14:30", cashier: "Siti Aminah", method: "Tunai", total: 45000 },
            { id: "ORD-0093", time: "14:15", cashier: "Andi Setiawan", method: "QRIS", total: 120000 },
            { id: "ORD-0092", time: "13:45", cashier: "Siti Aminah", method: "Tunai", total: 25000 },
            { id: "ORD-0091", time: "13:30", cashier: "Rini Wati", method: "QRIS", total: 78000 },
            { id: "ORD-0090", time: "13:10", cashier: "Siti Aminah", method: "Tunai", total: 33000 },
        ];

        let salesChart = null;

        // --- FUNCTIONS ---

        function formatRupiah(num) {
            return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(num);
        }

        function setFilter(period) {
            // Update Buttons UI
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.className = "px-3 py-1.5 text-xs font-medium text-gray-500 hover:bg-gray-50 rounded-md filter-btn transition-colors";
            });
            const activeBtn = document.getElementById(`btn-${period}`);
            activeBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md bg-gray-100 text-dark shadow-sm filter-btn transition-colors";

            // Update Data
            const data = reportData[period];

            // 1. Update Summary Cards
            animateValue("summary-revenue", data.revenue, true);
            animateValue("summary-transactions", data.transactions, false);
            animateValue("summary-average", data.average, true);

            // 2. Update Chart
            updateChart(data.chartLabels, data.chartData);

            // 3. Update Employee List
            renderEmployeeStats(data.employees);
        }

        function renderEmployeeStats(list) {
            const container = document.getElementById('employee-stats-container');
            container.innerHTML = '';

            // Sort by total revenue desc
            list.sort((a, b) => b.total - a.total);

            list.forEach((emp, index) => {
                const rankColor = index === 0 ? 'text-yellow-500' : index === 1 ? 'text-gray-400' : index === 2 ? 'text-orange-700' : 'text-gray-300';
                const percent = Math.round((emp.total / list[0].total) * 100);

                const html = `
                <div class="flex items-center gap-3 group">
                    <div class="w-6 text-center font-bold text-sm ${rankColor}">#${index + 1}</div>
                    <div class="relative">
                        <img src="${emp.avatar}" class="w-10 h-10 rounded-full object-cover border border-gray-100">
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex justify-between mb-1">
                            <h4 class="font-bold text-sm text-dark truncate">${emp.name}</h4>
                            <span class="font-bold text-xs text-primary">${formatRupiah(emp.total)}</span>
                        </div>
                        <div class="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                            <div class="bg-primary h-1.5 rounded-full" style="width: ${percent}%"></div>
                        </div>
                        <p class="text-[10px] text-gray-400 mt-1">${emp.transactions} Transaksi</p>
                    </div>
                </div>
                `;
                container.innerHTML += html;
            });
        }

        function renderTransactions() {
            const tbody = document.getElementById('transaction-table');
            tbody.innerHTML = '';
            transactions.forEach(trx => {
                const badgeColor = trx.method === 'QRIS' ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600';
                const html = `
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 font-mono text-xs font-bold text-primary">${trx.id}</td>
                    <td class="px-6 py-4 text-gray-500">${trx.time}</td>
                    <td class="px-6 py-4 font-bold text-dark">${trx.cashier}</td>
                    <td class="px-6 py-4">
                        <span class="px-2 py-1 rounded text-[10px] font-bold uppercase ${badgeColor}">${trx.method}</span>
                    </td>
                    <td class="px-6 py-4 text-right font-bold text-dark">${formatRupiah(trx.total)}</td>
                </tr>
                `;
                tbody.innerHTML += html;
            });
        }

        function initChart() {
            const ctx = document.getElementById('salesChart').getContext('2d');

            // Gradient Fill
            let gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(27, 67, 50, 0.2)'); // Primary Color low opacity
            gradient.addColorStop(1, 'rgba(27, 67, 50, 0)');

            salesChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Pemasukan (Rp)',
                        data: [],
                        borderColor: '#1B4332',
                        backgroundColor: gradient,
                        borderWidth: 2,
                        pointBackgroundColor: '#ffffff',
                        pointBorderColor: '#1B4332',
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#1B4332',
                            titleFont: { family: 'Plus Jakarta Sans' },
                            bodyFont: { family: 'Plus Jakarta Sans' },
                            padding: 10,
                            cornerRadius: 8,
                            callbacks: {
                                label: function (context) {
                                    return formatRupiah(context.raw);
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { borderDash: [5, 5], color: '#f3f4f6' },
                            ticks: {
                                callback: function (value) {
                                    if (value >= 1000000) return (value / 1000000) + 'jt';
                                    if (value >= 1000) return (value / 1000) + 'rb';
                                    return value;
                                },
                                font: { family: 'Plus Jakarta Sans', size: 10 },
                                color: '#9ca3af'
                            }
                        },
                        x: {
                            grid: { display: false },
                            ticks: {
                                font: { family: 'Plus Jakarta Sans', size: 10 },
                                color: '#9ca3af'
                            }
                        }
                    }
                }
            });
        }

        function updateChart(labels, data) {
            if (salesChart) {
                salesChart.data.labels = labels;
                salesChart.data.datasets[0].data = data;
                salesChart.update();
            }
        }

        function animateValue(id, end, isCurrency) {
            const obj = document.getElementById(id);
            const start = 0;
            const duration = 500;
            let startTimestamp = null;

            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                const value = Math.floor(progress * (end - start) + start);

                obj.innerHTML = isCurrency ? formatRupiah(value) : value;

                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        }

        // --- INIT ON LOAD ---
        window.onload = () => {
            initChart();
            setFilter('today'); // Load default data
            renderTransactions();
        };
