import { formatMoney } from "../../utils/formatMoney";
import { paymentMethods } from "./paymentMethods";

// Step 1 of checkout: choose how the customer pays and review the amounts.
export default function PaymentStep({ checkout, totalPrice }) {
  const {
    paymentMethod, setPaymentMethod,
    amountPaid, setAmountPaid,
    cashAmount, setCashAmount,
    mobileAmount, setMobileAmount,
    customerName, setCustomerName,
    mobileReference, setMobileReference,
    paidTotal, outstandingBalance, changeDue,
    requiresCustomer, requiresMobileReference,
    paymentErrors, invalidPayment,
  } = checkout;

  return (
    <>
      <div className="checkout-header">
        <div>
          <span className="eyebrow">SELLING MODE</span>
          <h2>Complete your sale</h2>
          <p>Review the payment before confirming.</p>
        </div>
        <button className="close-button" onClick={checkout.close}>
          ×
        </button>
      </div>

      <div className="checkout-total">
        <span>Total amount</span>
        <strong>{formatMoney(totalPrice)}</strong>
      </div>

      <h3>Choose payment method</h3>

      <div className="payment-options">
        {paymentMethods.map((method) => (
          <button
            key={method.id}
            className={`payment-option ${paymentMethod === method.id ? "selected" : ""}`}
            onClick={() => setPaymentMethod(method.id)}
          >
            <span>{method.icon}</span>
            <strong>{method.label}</strong>
          </button>
        ))}
      </div>

      {(paymentMethod === "cash" || paymentMethod === "mobile_money") && (
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

      {/* Each payment problem is listed separately. */}
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
        onClick={checkout.confirm}
      >
        Confirm sale
      </button>
    </>
  );
}
