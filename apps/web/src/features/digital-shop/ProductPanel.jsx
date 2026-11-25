import { formatMoney } from "../../utils/formatMoney";

// The left side of the shop workspace: compartments, search box and products.
export default function ProductPanel({ browser, onAddToBasket }) {
  const {
    currentArea,
    selectedCell,
    setSelectedCell,
    search,
    setSearch,
    visibleProducts,
  } = browser;

  return (
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

      {/* Compartments are hidden while searching. */}
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
                  onClick={() => onAddToBasket(product)}
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
  );
}
