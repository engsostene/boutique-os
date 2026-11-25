import { formatMoney } from "../../utils/formatMoney";

// Step 2 of checkout: the receipt shown after the sale is confirmed.
export default function ReceiptStep({ sale, onClose }) {
  // Opens the browser's print dialogue. The print rules are in
  // styles/07-small-screen-print.css and show only the receipt.
  function printReceipt() {
    window.print();
  }

  return (
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
          <strong>{sale.reference}</strong>
        </div>
        <div className="receipt-row">
          <span>Date</span>
          <strong>{sale.createdAt}</strong>
        </div>
        {sale.customer && (
          <div className="receipt-row">
            <span>Customer</span>
            <strong>{sale.customer}</strong>
          </div>
        )}

        <div className="receipt-divider" />

        {sale.items.map((item) => (
          <div className="receipt-row" key={item.id}>
            <span>
              {item.name} × {item.quantity}
            </span>
            <strong>{formatMoney(item.price * item.quantity)}</strong>
          </div>
        ))}

        <div className="receipt-divider" />

        <div className="receipt-row">
          <span>Total</span>
          <strong>{formatMoney(sale.total)}</strong>
        </div>
        <div className="receipt-row">
          <span>Cash received</span>
          <strong>{formatMoney(sale.cashPaid)}</strong>
        </div>
        <div className="receipt-row">
          <span>Mobile Money received</span>
          <strong>{formatMoney(sale.mobilePaid)}</strong>
        </div>
        <div className="receipt-row">
          <span>Outstanding credit</span>
          <strong>{formatMoney(sale.balance)}</strong>
        </div>
        {sale.change > 0 && (
          <div className="receipt-row">
            <span>Change returned</span>
            <strong>{formatMoney(sale.change)}</strong>
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
      <button className="checkout-button" onClick={onClose}>
        Finish and return to shop
      </button>
    </>
  );
}
