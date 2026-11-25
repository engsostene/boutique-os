import { formatMoney } from "../../utils/formatMoney";

// The basket shown on the right of the Digital Shop.
// It only displays data and reports clicks; the logic lives in useBasket.
export default function BasketPanel({ basket, totalItems, totalPrice, onChangeQuantity, onCheckout }) {
  return (
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
                  <button onClick={() => onChangeQuantity(item.id, -1)}>−</button>
                  <span>{item.quantity}</span>
                  <button
                    onClick={() => onChangeQuantity(item.id, 1)}
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
          onClick={onCheckout}
        >
          Continue to checkout <span>→</span>
        </button>
        <p className="basket-note">Prices are shown in Rwandan francs (RWF).</p>
      </div>
    </aside>
  );
}
