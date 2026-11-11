
import { useState } from "react";
import "./App.css";

const areas = [
  { id: "left", name: "Left Shelf", icon: "▤", cells: ["A01", "A02", "A03", "A04"] },
  { id: "right", name: "Right Shelf", icon: "▤", cells: ["B01", "B02", "B03", "B04"] },
  { id: "counter", name: "Counter", icon: "▣", cells: ["C01", "C02"] },
  { id: "cupboard", name: "Cupboard", icon: "▥", cells: ["D01", "D02"] },
  { id: "storage", name: "Storage", icon: "▦", cells: ["E01", "E02"] },
];

const products = [
  { id: 1, name: "Rice", detail: "1 kg · Long grain", price: 1800, emoji: "🍚", area: "left", cell: "A01", stock: 24 },
  { id: 2, name: "Wheat Flour", detail: "1 kg · Regular", price: 1400, emoji: "🌾", area: "left", cell: "A01", stock: 18 },
  { id: 3, name: "Sugar", detail: "1 kg · White", price: 1600, emoji: "🧂", area: "left", cell: "A02", stock: 32 },
  { id: 4, name: "Cooking Oil", detail: "1 litre", price: 3200, emoji: "🫗", area: "left", cell: "A02", stock: 12 },
  { id: 5, name: "Bathing Soap", detail: "Single bar", price: 1000, emoji: "🧼", area: "right", cell: "B01", stock: 40 },
  { id: 6, name: "Laundry Soap", detail: "Large bar", price: 1500, emoji: "🧽", area: "right", cell: "B01", stock: 15 },
  { id: 7, name: "Toothpaste", detail: "Small tube", price: 2200, emoji: "🪥", area: "right", cell: "B02", stock: 9 },
  { id: 8, name: "Matches", detail: "One box", price: 200, emoji: "🔥", area: "counter", cell: "C01", stock: 60 },
  { id: 9, name: "Biscuits", detail: "Small packet", price: 500, emoji: "🍪", area: "counter", cell: "C01", stock: 25 },
  { id: 10, name: "Tea Leaves", detail: "250 g packet", price: 1200, emoji: "🍵", area: "cupboard", cell: "D01", stock: 14 },
  { id: 11, name: "Maize Flour", detail: "2 kg packet", price: 2500, emoji: "🌽", area: "storage", cell: "E01", stock: 20 },
];

function formatMoney(amount) {
  return `${new Intl.NumberFormat("en-US").format(amount)} RWF`;
}

function App() {
  const [selectedArea, setSelectedArea] = useState("left");
  const [selectedCell, setSelectedCell] = useState("A01");
  const [search, setSearch] = useState("");
  const [basket, setBasket] = useState([]);

  const currentArea = areas.find((area) => area.id === selectedArea);

  const visibleProducts = products.filter((product) => {
    const matchesSearch =
      product.name.toLowerCase().includes(search.toLowerCase()) ||
      product.detail.toLowerCase().includes(search.toLowerCase());

    const matchesLocation =
      product.area === selectedArea && product.cell === selectedCell;

    return search.trim() ? matchesSearch : matchesLocation;
  });

  const totalItems = basket.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = basket.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  function chooseArea(area) {
    setSelectedArea(area.id);
    setSelectedCell(area.cells[0]);
    setSearch("");
  }

  function addToBasket(product) {
    setBasket((currentBasket) => {
      const existingItem = currentBasket.find((item) => item.id === product.id);

      if (existingItem) {
        return currentBasket.map((item) =>
          item.id === product.id
            ? { ...item, quantity: Math.min(item.quantity + 1, product.stock) }
            : item
        );
      }

      return [...currentBasket, { ...product, quantity: 1 }];
    });
  }

  function changeQuantity(productId, change) {
    setBasket((currentBasket) =>
      currentBasket
        .map((item) =>
          item.id === productId
            ? {
                ...item,
                quantity: Math.min(item.quantity + change, item.stock),
              }
            : item
        )
        .filter((item) => item.quantity > 0)
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">B</div>
          <div>
            <h1>Boutique OS</h1>
            <span>RETAIL MANAGEMENT</span>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <button className="nav-item active">
          <span>▦</span> Digital Shop
        </button>
        <button className="nav-item">
          <span>▤</span> Sales
        </button>
        <button className="nav-item">
          <span>♙</span> Customers
        </button>

        <div className="sidebar-label management-label">MANAGEMENT</div>

        <button className="nav-item">
          <span>▧</span> Products
        </button>
        <button className="nav-item">
          <span>▥</span> Inventory
        </button>
        <button className="nav-item">
          <span>▨</span> Reports
        </button>

        <div className="sidebar-bottom">
          <div className="shop-avatar">K</div>
          <div className="shop-user">
            <strong>Karibu Boutique</strong>
            <span>Owner account</span>
          </div>
          <span className="more-icon">•••</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="breadcrumb">Selling Mode / Digital Shop</div>
            <h2>Good morning, Seller <span>☀️</span></h2>
            <p>Let's make today's sales count.</p>
          </div>

          <div className="topbar-actions">
            <div className="connection-status">
              <span className="status-dot"></span>
              Online
            </div>
            <button className="icon-button" aria-label="Notifications">♧</button>
            <div className="user-avatar">S</div>
          </div>
        </header>

        <section className="shop-heading">
          <div>
            <span className="eyebrow">YOUR SHOP</span>
            <h3>Explore your shop</h3>
            <p>Select a shop area, find a compartment and add products to the basket.</p>
          </div>
          <button className="mode-button">Selling Mode <span>⌄</span></button>
        </section>

        <section className="area-section">
          <div className="section-heading">
            <div>
              <h3>Shop areas</h3>
              <span>Choose where you want to look</span>
            </div>
            <button className="text-button">View shop layout ↗</button>
          </div>

          <div className="area-list">
            {areas.map((area) => (
              <button
                key={area.id}
                className={`area-card ${selectedArea === area.id ? "selected" : ""}`}
                onClick={() => chooseArea(area)}
              >
                <span className="area-icon">{area.icon}</span>
                <span className="area-name">{area.name}</span>
                <span className="area-count">{area.cells.length} cells</span>
              </button>
            ))}
          </div>
        </section>

        <section className="shop-workspace">
          <div className="products-panel">
            <div className="section-heading">
              <div>
                <h3>{search ? "Search results" : currentArea.name}</h3>
                <span>
                  {search
                    ? "Products matching your search"
                    : "Choose a compartment to see its products"}
                </span>
              </div>
              <span className="location-tag">SHOP FLOOR</span>
            </div>

            {!search && (
              <div className="compartment-list">
                {currentArea.cells.map((cell) => (
                  <button
                    key={cell}
                    className={`compartment ${selectedCell === cell ? "selected" : ""}`}
                    onClick={() => setSelectedCell(cell)}
                  >
                    <span className="compartment-icon">▦</span>
                    <strong>{cell}</strong>
                    <span>Compartment</span>
                  </button>
                ))}
              </div>
            )}

            <div className="product-toolbar">
              <div>
                <h4>Products</h4>
                <span>{visibleProducts.length} products found</span>
              </div>
              <label className="search-box">
                <span>⌕</span>
                <input
                  type="search"
                  placeholder="Search products..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </label>
            </div>

            <div className="product-grid">
              {visibleProducts.map((product) => (
                <article className="product-card" key={product.id}>
                  <div className="product-visual">
                    <span>{product.emoji}</span>
                    <small>{product.stock} in stock</small>
                  </div>
                  <div className="product-information">
                    <h4>{product.name}</h4>
                    <p>{product.detail}</p>
                    <div className="product-card-bottom">
                      <strong>{formatMoney(product.price)}</strong>
                      <button
                        className="add-button"
                        onClick={() => addToBasket(product)}
                        disabled={product.stock === 0}
                        aria-label={`Add ${product.name} to basket`}
                      >
                        +
                      </button>
                    </div>
                  </div>
                </article>
              ))}

              {visibleProducts.length === 0 && (
                <div className="empty-products">
                  <span>🔎</span>
                  <strong>No products found</strong>
                  <p>Try another search or choose a different compartment.</p>
                  <button onClick={() => setSearch("")}>Clear search</button>
                </div>
              )}
            </div>
          </div>

          <aside className="basket-panel">
            <div className="basket-heading">
              <div>
                <h3>Current basket</h3>
                <span>Your selected products</span>
              </div>
              <span className="basket-count">{totalItems}</span>
            </div>

            {basket.length === 0 ? (
              <div className="empty-basket">
                <div className="basket-illustration">🛒</div>
                <strong>Your basket is empty</strong>
                <p>Select products from your shop to start a sale.</p>
              </div>
            ) : (
              <div className="basket-items">
                {basket.map((item) => (
                  <div className="basket-item" key={item.id}>
                    <div className="basket-product-icon">{item.emoji}</div>
                    <div className="basket-product-info">
                      <strong>{item.name}</strong>
                      <span>{formatMoney(item.price)}</span>
                      <div className="quantity-control">
                        <button onClick={() => changeQuantity(item.id, -1)}>−</button>
                        <span>{item.quantity}</span>
                        <button
                          onClick={() => changeQuantity(item.id, 1)}
                          disabled={item.quantity >= item.stock}
                        >
                          +
                        </button>
                      </div>
                    </div>
                    <strong className="basket-line-total">
                      {formatMoney(item.price * item.quantity)}
                    </strong>
                  </div>
                ))}
              </div>
            )}

            <div className="basket-summary">
              <div className="summary-row">
                <span>Items</span>
                <span>{totalItems}</span>
              </div>
              <div className="summary-row">
                <span>Subtotal</span>
                <span>{formatMoney(totalPrice)}</span>
              </div>
              <div className="summary-total">
                <span>Total</span>
                <strong>{formatMoney(totalPrice)}</strong>
              </div>
              <button className="checkout-button" disabled={basket.length === 0}>
                Continue to checkout <span>→</span>
              </button>
              <p className="basket-note">Prices are shown in Rwandan francs (RWF).</p>
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}

export default App;
