import { useState } from 'react'
import { useParams } from 'react-router-dom'

const DEFAULT_LOGO = 'https://cdn-icons-png.flaticon.com/512/2921/2921822.png'
const DEFAULT_BANNER = 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80'

const restaurantInfo = {
    name: 'Warung Bu Dewi',
    description: 'Warung makan dengan berbagai menu masakan Indonesia yang lezat dan terjangkau.',
    address: 'Jl. Merdeka No. 123, Jakarta Selatan',
    openTime: '08:00',
    closeTime: '22:00',
    logo: DEFAULT_LOGO,
    banner: DEFAULT_BANNER,
}

const categories = [
    { id: 'all', name: 'Semua' },
    { id: 'food', name: 'Makanan Berat' },
    { id: 'drink', name: 'Minuman' },
    { id: 'snack', name: 'Cemilan' },
]

const menuItems = [
    {
        id: 1,
        name: "Nasi Goreng Spesial",
        description: "Dengan telur mata sapi, sate ayam, dan kerupuk udang.",
        price: 25000,
        stock: true,
        image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80",
        category: "food"
    },
    {
        id: 2,
        name: "Ayam Bakar Madu",
        description: "Ayam kampung bakar dengan olesan madu dan sambal terasi.",
        price: 28000,
        stock: true,
        image: "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=400&q=80",
        category: "food"
    },
    {
        id: 3,
        name: "Sate Ayam Madura",
        description: "10 tusuk sate ayam dengan bumbu kacang kental.",
        price: 30000,
        stock: true,
        image: "https://images.unsplash.com/photo-1555126634-323283e090fa?auto=format&fit=crop&w=400&q=80",
        category: "food"
    },
    {
        id: 4,
        name: "Es Kopi Susu Gula Aren",
        description: "Kopi arabika house blend dengan susu fresh milk.",
        price: 18000,
        stock: true,
        image: "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&w=400&q=80",
        category: "drink"
    },
    {
        id: 5,
        name: "Es Teh Manis Jumbo",
        description: "Teh tubruk wangi melati dengan gula asli.",
        price: 8000,
        stock: true,
        image: "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=400&q=80",
        category: "drink"
    },
    {
        id: 6,
        name: "Pisang Goreng Keju",
        description: "Pisang kepok kuning digoreng crispy topping keju.",
        price: 15000,
        stock: true,
        image: "https://images.unsplash.com/photo-1519708227418-c8fd9a3a2b7b?auto=format&fit=crop&w=400&q=80",
        category: "snack"
    }
]

export function CustomerMenu() {
    const { tableId } = useParams()
    const [selectedCategory, setSelectedCategory] = useState('all')
    const [searchQuery, setSearchQuery] = useState('')
    const [showSearch, setShowSearch] = useState(false)
    const [cart, setCart] = useState([])
    const [showCart, setShowCart] = useState(false)
    const [showOrderSuccess, setShowOrderSuccess] = useState(false)

    const tableName = tableId ? `Meja ${tableId}` : 'Bawa Pulang'
    const bannerImage = restaurantInfo.banner || DEFAULT_BANNER
    const logoImage = restaurantInfo.logo || DEFAULT_LOGO

    const filteredItems = menuItems.filter(item => {
        if (selectedCategory !== 'all' && item.category !== selectedCategory) return false
        if (searchQuery && !item.name.toLowerCase().includes(searchQuery.toLowerCase())) return false
        return true
    })

    const getItemQuantity = (itemId) => {
        const cartItem = cart.find(item => item.id === itemId)
        return cartItem ? cartItem.quantity : 0
    }

    const addToCart = (item) => {
        if (!item.stock) return

        const existingItem = cart.find(cartItem => cartItem.id === item.id)
        if (existingItem) {
            setCart(cart.map(cartItem =>
                cartItem.id === item.id
                    ? { ...cartItem, quantity: cartItem.quantity + 1 }
                    : cartItem
            ))
        } else {
            setCart([...cart, { ...item, quantity: 1 }])
        }
    }

    const updateQuantity = (cartItemId, delta) => {
        setCart(cart.map(item => {
            const itemKey = item.cartItemId || item.id
            if (itemKey === cartItemId) {
                const newQuantity = item.quantity + delta
                return { ...item, quantity: newQuantity }
            }
            return item
        }).filter(item => item.quantity > 0))
    }

    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0)
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    const tax = Math.round(subtotal * 0.1) // 10% tax as per design
    const total = subtotal + tax

    const handleOrder = () => {
        if (cart.length === 0) return

        setShowCart(false)
        // Simulasi loading
        setTimeout(() => {
            setShowOrderSuccess(true)
        }, 300)
    }

    const resetOrder = () => {
        setCart([])
        setShowOrderSuccess(false)
        window.location.reload()
    }

    return (
        <div id="app-view" className="min-h-screen pb-0 md:pb-32 fade-in bg-[#F7F5F2] flex flex-col">
            <div className="flex-1 flex flex-col">
                {/* Store Hero */}
                <section className="bg-white pb-4">
                    <div className="relative h-40 bg-gray-200">
                        <img
                            src={bannerImage}
                            alt={`${restaurantInfo.name} banner`}
                            className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/10"></div>

                        <div className="absolute left-4 -bottom-6 md:-bottom-10 w-16 h-16 md:w-24 md:h-24 bg-white rounded-full p-1 shadow-md z-10">
                            <div className="w-full h-full bg-gray-100 rounded-full overflow-hidden">
                                <img
                                    src={logoImage}
                                    alt={`${restaurantInfo.name} logo`}
                                    className="w-full h-full object-cover"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="pt-8 md:pt-12 px-4">
                        <h1 className="text-xl md:text-2xl font-bold leading-tight text-dark">{restaurantInfo.name}</h1>
                        <p className="text-sm text-gray-600 mt-1">{restaurantInfo.description}</p>

                        <div className="flex flex-wrap gap-2 mt-3 text-xs text-gray-600">
                            <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-50 border border-gray-100">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                                <span className="font-bold text-dark">Buka {restaurantInfo.openTime} - {restaurantInfo.closeTime}</span>
                            </div>
                            <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-50 border border-gray-100">
                                <i className="fa-solid fa-location-dot text-primary text-xs"></i>
                                <span>{restaurantInfo.address}</span>
                            </div>
                            <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-50 border border-gray-100">
                                <i className="fa-solid fa-chair text-primary text-xs"></i>
                                <span>{tableName}</span>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Header Sticky */}
                <header className="sticky top-0 z-40 bg-[#F7F5F2]/95 backdrop-blur-md border-b border-gray-200/50">
                    {/* Category Filter (Horizontal Scroll) */}
                    <div className="px-4 pb-3 overflow-x-auto no-scrollbar flex gap-3 py-3">
                        {categories.map((category) => (
                            <button
                                key={category.id}
                                onClick={() => setSelectedCategory(category.id)}
                                className={`px-5 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${selectedCategory === category.id
                                    ? 'bg-primary text-white font-bold shadow-md'
                                    : 'bg-white text-gray-500 border border-gray-200 hover:border-primary hover:text-primary'
                                    }`}
                            >
                                {category.name}
                            </button>
                        ))}
                    </div>
                </header>

                {/* Menu List Grid */}
                <main className="px-4 pt-6 grid grid-cols-1 md:grid-cols-2 gap-6" id="menu-container">
                    {filteredItems.map((item) => {
                        const qty = getItemQuantity(item.id)
                        return (
                            <div key={item.id} className="bg-white p-4 rounded-2xl shadow-card flex gap-4 items-center md:items-start group">
                                <div className="w-24 h-24 md:w-32 md:h-32 bg-gray-100 rounded-xl overflow-hidden shrink-0 relative">
                                    <img src={item.image} alt={item.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="font-bold text-dark text-lg leading-tight mb-1 truncate">{item.name}</h3>
                                    <p className="text-xs text-gray-500 line-clamp-2 mb-3 leading-relaxed">{item.description}</p>
                                    <div className="flex justify-between items-end">
                                        <span className="font-bold text-accent text-lg">Rp {item.price.toLocaleString('id-ID')}</span>

                                        <div className="flex items-center">
                                            {qty === 0 ? (
                                                <button
                                                    onClick={() => addToCart(item)}
                                                    className="w-9 h-9 bg-secondary text-primary rounded-lg flex items-center justify-center hover:bg-primary hover:text-white transition-colors shadow-sm"
                                                >
                                                    <i className="fa-solid fa-plus"></i>
                                                </button>
                                            ) : (
                                                <div className="flex items-center gap-3 bg-[#F7F5F2] rounded-lg p-1 border border-gray-200">
                                                    <button
                                                        onClick={() => updateQuantity(item.id, -1)}
                                                        className="w-7 h-7 bg-white text-primary rounded flex items-center justify-center shadow-sm"
                                                    >
                                                        <i className="fa-solid fa-minus text-xs"></i>
                                                    </button>
                                                    <span className="font-bold text-dark text-sm w-2 text-center">{qty}</span>
                                                    <button
                                                        onClick={() => updateQuantity(item.id, 1)}
                                                        className="w-7 h-7 bg-primary text-white rounded flex items-center justify-center shadow-sm"
                                                    >
                                                        <i className="fa-solid fa-plus text-xs"></i>
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </main>
            </div>

            {/* Floating Cart Bar */}
            {totalItems > 0 && (
                <div
                    id="cart-bar"
                    className="sticky bottom-0 mt-auto z-30 px-4 pb-4 pt-4 md:fixed md:bottom-0 md:left-0 md:w-full"
                >
                    <div
                        className="bg-primary text-white rounded-2xl p-4 shadow-2xl flex justify-between items-center cursor-pointer"
                        onClick={() => setShowCart(true)}
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center font-bold text-lg" id="total-items-badge">
                                {totalItems}
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xs text-green-100">Total Pembayaran</span>
                                <span className="font-bold text-lg" id="total-price-bar">Rp {total.toLocaleString('id-ID')}</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 font-bold text-sm bg-accent px-4 py-2 rounded-xl hover:bg-[#d06a50] transition-colors">
                            Lihat Pesanan <i className="fa-solid fa-chevron-right"></i>
                        </div>
                    </div>
                </div>
            )}

            {/* Cart Modal */}
            {showCart && (
                <div id="cart-modal" className="fixed inset-0 z-50">
                    {/* Backdrop */}
                    <div
                        className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
                        onClick={() => setShowCart(false)}
                    ></div>

                    {/* Bottom Sheet */}
                    <div className="absolute bottom-0 w-full bg-[#F7F5F2] rounded-t-[2rem] shadow-2xl h-[85vh] flex flex-col slide-up">
                        {/* Handle bar */}
                        <div className="w-full flex justify-center pt-4 pb-2" onClick={() => setShowCart(false)}>
                            <div className="w-12 h-1.5 bg-gray-300 rounded-full"></div>
                        </div>

                        {/* Modal Header */}
                        <div className="px-6 pb-4 border-b border-gray-200 flex justify-between items-center">
                            <h2 className="text-xl font-bold text-primary">Pesanan Anda</h2>
                            <button
                                onClick={() => setShowCart(false)}
                                className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-500 hover:bg-gray-200"
                            >
                                <i className="fa-solid fa-xmark"></i>
                            </button>
                        </div>

                        {/* Cart Items (Scrollable) */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scroll" id="cart-items-container">
                            {cart.length === 0 ? (
                                <div className="text-center text-gray-400 py-10">Keranjang kosong</div>
                            ) : (
                                cart.map((item) => (
                                    <div key={item.id} className="flex gap-4 items-center border-b border-gray-100 pb-4 last:border-0">
                                        <div className="w-16 h-16 bg-gray-100 rounded-xl overflow-hidden shrink-0">
                                            <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                                        </div>
                                        <div className="flex-1">
                                            <h4 className="font-bold text-dark text-sm">{item.name}</h4>
                                            <p className="text-xs text-gray-500 mb-2">Rp {item.price.toLocaleString('id-ID')} / porsi</p>
                                            <div className="flex justify-between items-center">
                                                <div className="flex items-center gap-3 bg-[#F7F5F2] rounded-lg p-1">
                                                    <button
                                                        onClick={() => updateQuantity(item.id, -1)}
                                                        className="w-6 h-6 bg-white text-gray-500 rounded flex items-center justify-center shadow-sm hover:text-primary"
                                                    >
                                                        <i className="fa-solid fa-minus text-[10px]"></i>
                                                    </button>
                                                    <span className="font-bold text-dark text-xs w-4 text-center">{item.quantity}</span>
                                                    <button
                                                        onClick={() => updateQuantity(item.id, 1)}
                                                        className="w-6 h-6 bg-primary text-white rounded flex items-center justify-center shadow-sm"
                                                    >
                                                        <i className="fa-solid fa-plus text-[10px]"></i>
                                                    </button>
                                                </div>
                                                <span className="font-bold text-primary text-sm">Rp {(item.price * item.quantity).toLocaleString('id-ID')}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        {/* Bill Details & Checkout */}
                        <div className="bg-white p-6 rounded-t-[2rem] shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
                            <div className="space-y-3 mb-6 text-sm">
                                <div className="flex justify-between text-gray-500">
                                    <span>Subtotal</span>
                                    <span className="font-bold text-dark" id="bill-subtotal">Rp {subtotal.toLocaleString('id-ID')}</span>
                                </div>
                                <div className="flex justify-between text-gray-500">
                                    <span>Pajak & Layanan (10%)</span>
                                    <span className="font-bold text-dark" id="bill-tax">Rp {tax.toLocaleString('id-ID')}</span>
                                </div>
                                <div className="border-t border-dashed border-gray-300 my-2"></div>
                                <div className="flex justify-between text-lg">
                                    <span className="font-bold text-primary">Total</span>
                                    <span className="font-extrabold text-accent" id="bill-total">Rp {total.toLocaleString('id-ID')}</span>
                                </div>
                            </div>

                            <button
                                onClick={handleOrder}
                                className="w-full py-4 bg-primary text-white font-bold rounded-xl shadow-lg hover:bg-[#143326] transition-all flex justify-center items-center gap-2"
                            >
                                <i className="fa-solid fa-paper-plane"></i> Pesan Sekarang
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Success Overlay */}
            {showOrderSuccess && (
                <div id="success-view" className="fixed inset-0 z-[60] bg-primary flex flex-col items-center justify-center p-6 text-center text-white fade-in">
                    <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mb-6 animate-bounce">
                        <i className="fa-solid fa-check text-4xl text-white"></i>
                    </div>
                    <h2 className="text-3xl font-bold mb-2">Pesanan Diterima!</h2>
                    <p className="text-green-100 mb-8 max-w-xs mx-auto">Mohon tunggu sebentar, pesanan Anda sedang disiapkan oleh dapur.</p>

                    <div className="bg-white/10 backdrop-blur-md p-6 rounded-2xl w-full max-w-xs border border-white/10">
                        <p className="text-xs text-green-200 uppercase font-bold mb-1">Estimasi Waktu</p>
                        <p className="text-2xl font-bold">15 - 20 Menit</p>
                    </div>

                    <button
                        onClick={resetOrder}
                        className="mt-10 px-8 py-3 border border-white/30 rounded-xl text-sm font-bold hover:bg-white/10 transition-colors"
                    >
                        Kembali ke Menu
                    </button>
                </div>
            )}
        </div>
    )
}
