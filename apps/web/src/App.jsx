
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
  // -----------------------------------------
  // DIGITAL SHOP STATE
  // -----------------------------------------

  // Controls which shop area and compartment are currently open.
  const [selectedArea, setSelectedArea] = useState("left");
  const [selectedCell, setSelectedCell] = useState("A01");

  // Stores the product search query and current basket.
  const [search, setSearch] = useState("");
  const [basket, setBasket] = useState([]);

  // -----------------------------------------
  // CHECKOUT STATE
  // -----------------------------------------

  // Controls whether checkout or the receipt is displayed.
  const [checkoutOpen, setCheckoutOpen] = useState(false);

  // Stores the selected payment method.
  const [paymentMethod, setPaymentMethod] = useState("cash");

  // Cash or Mobile Money amount, depending on payment method.
  const [amountPaid, setAmountPaid] = useState("0");

  // Separate amounts for split payments.
  const [cashAmount, setCashAmount] = useState("0");
  const [mobileAmount, setMobileAmount] = useState("0");

  // Customer details for credit and Mobile Money reference.
  const [customerName, setCustomerName] = useState("");
  const [mobileReference, setMobileReference] = useState("");

  // Stores the completed demonstration sale for receipt display.
  const [completedSale, setCompletedSale] = useState(null);


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

const cashPaid =
  paymentMethod === "cash"
    ? Number(amountPaid) || 0
    : paymentMethod === "split"
      ? Number(cashAmount) || 0
      : 0;

const mobilePaid =
  paymentMethod === "mobile_money"
    ? Number(amountPaid) || 0
    : paymentMethod === "split"
      ? Number(mobileAmount) || 0
      : 0;

const paidTotal = paymentMethod === "credit" ? 0 : cashPaid + mobilePaid;

const outstandingBalance = Math.max(0, totalPrice - paidTotal);

const changeDue =
  paymentMethod === "cash"
    ? Math.max(0, paidTotal - totalPrice)
    : 0;

const requiresCustomer = outstandingBalance > 0;
const requiresMobileReference = mobilePaid > 0;

// Prevent invalid payments from being confirmed.
// Cash overpayment is allowed because the seller must return change.
// Other payment methods cannot exceed the sale total.
const invalidPayment =
  (paymentMethod !== "cash" && paidTotal > totalPrice) ||
  (requiresCustomer && !customerName.trim()) ||
  (requiresMobileReference && !mobileReference.trim());

// Build a list of specific problems so the seller knows
// exactly what needs to be corrected before confirming a sale.
const paymentErrors = [];

if (paymentMethod !== "cash" && paidTotal > totalPrice) {
  paymentErrors.push("The payment amount cannot exceed the sale total.");
}

if (requiresCustomer && !customerName.trim()) {
  paymentErrors.push("Enter the customer's name for the outstanding balance.");
}

if (requiresMobileReference && !mobileReference.trim()) {
  paymentErrors.push("Enter the Mobile Money transaction reference.");
}


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

function openCheckout() {
  setPaymentMethod("cash");
  setAmountPaid(String(totalPrice));
  setCashAmount("0");
  setMobileAmount("0");
  setCustomerName("");
  setMobileReference("");
  setCompletedSale(null);
  setCheckoutOpen(true);
}

function confirmSale() {
  if (basket.length === 0 || invalidPayment) return;

  const sale = {
    reference: `DEMO-${Date.now()}`,
    items: [...basket],
    total: totalPrice,
    cashPaid,
    mobilePaid,
    paid: paidTotal,
    balance: outstandingBalance,
    change: changeDue,
    method: paymentMethod,
    customer: customerName.trim(),
    mobileReference: mobileReference.trim(),
    createdAt: new Date().toLocaleString(),
  };

  setCompletedSale(sale);
  setBasket([]);
}

// Open the browser's print dialogue for the completed receipt.
function printReceipt() {
  window.print();
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
              <button
                className="checkout-button"
                disabled={basket.length === 0}
                onClick={openCheckout}
   >
                 Continue to checkout <span>→</span>
              </button>
              <p className="basket-note">Prices are shown in Rwandan francs (RWF).</p>
            </div>
          </aside>
        </section>

        {checkoutOpen && (
  <div className="checkout-overlay">
    <div className="checkout-modal">
      {!completedSale ? (
        <>
          <div className="checkout-header">
            <div>
              <span className="eyebrow">SELLING MODE</span>
              <h2>Complete your sale</h2>
              <p>Review the payment before confirming.</p>
            </div>
            <button
              className="close-button"
              onClick={() => setCheckoutOpen(false)}
            >
              ×
            </button>
          </div>

          <div className="checkout-total">
            <span>Total amount</span>
            <strong>{formatMoney(totalPrice)}</strong>
          </div>

          <h3>Choose payment method</h3>

          <div className="payment-options">
            {[
              { id: "cash", label: "Cash", icon: "💵" },
              { id: "mobile_money", label: "Mobile Money", icon: "📱" },
              { id: "credit", label: "Credit", icon: "📝" },
              { id: "split", label: "Split payment", icon: "⇄" },
            ].map((method) => (
              <button
                key={method.id}
                className={`payment-option ${
                  paymentMethod === method.id ? "selected" : ""
                }`}
                onClick={() => setPaymentMethod(method.id)}
              >
                <span>{method.icon}</span>
                <strong>{method.label}</strong>
              </button>
            ))}
          </div>

          {(paymentMethod === "cash" ||
            paymentMethod === "mobile_money") && (
            <label className="checkout-field">
              {paymentMethod === "cash"
                ? "Cash received (RWF)"
                : "Mobile Money received (RWF)"}
              <input
                type="number"
                min="0"
                value={amountPaid}
                onChange={(event) => setAmountPaid(event.target.value)}
              />
            </label>
          )}

          {paymentMethod === "split" && (
            <div className="split-fields">
              <label className="checkout-field">
                Cash amount (RWF)
                <input
                  type="number"
                  min="0"
                  value={cashAmount}
                  onChange={(event) => setCashAmount(event.target.value)}
                />
              </label>

              <label className="checkout-field">
                Mobile Money amount (RWF)
                <input
                  type="number"
                  min="0"
                  value={mobileAmount}
                  onChange={(event) => setMobileAmount(event.target.value)}
                />
              </label>
            </div>
          )}

          {requiresMobileReference && (
            <label className="checkout-field">
              Mobile Money transaction reference
              <input
                type="text"
                placeholder="Enter payment reference"
                value={mobileReference}
                onChange={(event) => setMobileReference(event.target.value)}
              />
            </label>
          )}

          {requiresCustomer && (
            <label className="checkout-field">
              Customer name or familiar nickname
              <input
                type="text"
                placeholder="Enter customer name"
                value={customerName}
                onChange={(event) => setCustomerName(event.target.value)}
              />
            </label>
          )}

          <div className="payment-summary">
            <div>
              <span>Amount paid</span>
              <strong>{formatMoney(paidTotal)}</strong>
            </div>
            <div>
              <span>Outstanding balance</span>
              <strong>{formatMoney(outstandingBalance)}</strong>
            </div>
            {changeDue > 0 && (
              <div>
                <span>Change to return</span>
                <strong>{formatMoney(changeDue)}</strong>
              </div>
            )}
          </div>

          {/* Display each payment problem separately. */}
{paymentErrors.length > 0 && (
  <div className="payment-error" role="alert">
    <strong>Please check the following:</strong>

    <ul>
      {paymentErrors.map((error, index) => (
        <li key={index}>{error}</li>
      ))}
    </ul>
  </div>
)}

          <button
            className="checkout-button confirm-button"
            disabled={invalidPayment}
            onClick={confirmSale}
          >
            Confirm sale
          </button>
        </>
      ) : (
        <>
          <div className="receipt-success">
            <div>✓</div>
            <h2>Sale completed!</h2>
            <p>Your demonstration receipt is ready.</p>
          </div>

          <div className="receipt">
            <h3>Karibu Boutique</h3>
            <p>SALES RECEIPT</p>
            <div className="receipt-divider" />

            <div className="receipt-row">
              <span>Reference</span>
              <strong>{completedSale.reference}</strong>
            </div>
            <div className="receipt-row">
              <span>Date</span>
              <strong>{completedSale.createdAt}</strong>
            </div>
            {completedSale.customer && (
              <div className="receipt-row">
                <span>Customer</span>
                <strong>{completedSale.customer}</strong>
              </div>
            )}

            <div className="receipt-divider" />

            {completedSale.items.map((item) => (
              <div className="receipt-row" key={item.id}>
                <span>
                  {item.name} × {item.quantity}
                </span>
                <strong>
                  {formatMoney(item.price * item.quantity)}
                </strong>
              </div>
            ))}

            <div className="receipt-divider" />

            <div className="receipt-row">
              <span>Total</span>
              <strong>{formatMoney(completedSale.total)}</strong>
            </div>
            <div className="receipt-row">
              <span>Cash received</span>
              <strong>{formatMoney(completedSale.cashPaid)}</strong>
            </div>
            <div className="receipt-row">
              <span>Mobile Money received</span>
              <strong>{formatMoney(completedSale.mobilePaid)}</strong>
            </div>
            <div className="receipt-row">
              <span>Outstanding credit</span>
              <strong>{formatMoney(completedSale.balance)}</strong>
            </div>
            {completedSale.change > 0 && (
              <div className="receipt-row">
                <span>Change returned</span>
                <strong>{formatMoney(completedSale.change)}</strong>
              </div>
            )}
          </div>

          {/* Print the receipt without closing the checkout window. */}
          <button
            type="button"
            className="checkout-button print-button"
            onClick={printReceipt}
          >
            Print receipt
          </button>
          
          {/* Close the receipt and return to the Digital Shop. */}
          <button
            className="checkout-button"
            onClick={() => setCheckoutOpen(false)}
          >
            Finish and return to shop
          </button>
        </>
      )}
    </div>
  </div>
)}

        
      </main>
    </div>
  );
}

export default App;
