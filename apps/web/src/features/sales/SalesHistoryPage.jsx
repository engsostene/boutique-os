import { formatMoney } from "../../utils/formatMoney";

// Lists the sales completed during this session.
// Later this will load saved sales from the backend instead.
export default function SalesHistoryPage({ salesHistory, onReturnToShop }) {
  return (
    <div className="sales-page">
      <header className="topbar">
        <div>
          <div className="breadcrumb">Selling Mode / Sales</div>
          <h2>Sales History</h2>
          <p>Review your completed transactions.</p>
        </div>
      </header>

      <section className="shop-heading">
        <div>
          <span className="eyebrow">TRANSACTION RECORDS</span>
          <h3>Recent sales</h3>
          <p>Your completed sales during this session.</p>
        </div>
      </section>

      <section className="sales-list">
        {salesHistory.length === 0 ? (
          <div className="empty-products">
            <span>📋</span>
            <strong>No sales recorded yet</strong>
            <p>Completed sales will appear here.</p>
          </div>
        ) : (
          salesHistory.map((sale) => (
            <article className="sale-card" key={sale.reference}>
              <div>
                <strong>{sale.reference}</strong>
                <p>{sale.customer || "Walk-in customer"}</p>
                <span>{sale.createdAt}</span>
              </div>

              <div>
                <strong>{formatMoney(sale.total)}</strong>
                <p>
                  {sale.balance > 0
                    ? `Outstanding: ${formatMoney(sale.balance)}`
                    : "Fully paid"}
                </p>
              </div>
            </article>
          ))
        )}
      </section>

      <button className="checkout-button" onClick={onReturnToShop}>
        Return to Digital Shop
      </button>
    </div>
  );
}
