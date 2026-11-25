// The left navigation. It only changes which page is shown.
// Customers, Products, Inventory and Reports are placeholders for now.
export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">B</div>
        <div>
          <h1>Boutique OS</h1>
          <span>RETAIL MANAGEMENT</span>
        </div>
      </div>

      <div className="sidebar-label">WORKSPACE</div>

      <button
        className={`nav-item ${activePage === "digital-shop" ? "active" : ""}`}
        onClick={() => onNavigate("digital-shop")}
      >
        <span>▦</span> Digital Shop
      </button>

      <button
        className={`nav-item ${activePage === "sales" ? "active" : ""}`}
        onClick={() => onNavigate("sales")}
      >
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
  );
}
