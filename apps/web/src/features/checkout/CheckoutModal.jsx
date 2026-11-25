import PaymentStep from "./PaymentStep";
import ReceiptStep from "./ReceiptStep";

// The checkout window. It shows the payment form until the sale is
// confirmed, then switches to the receipt.
export default function CheckoutModal({ checkout, totalPrice }) {
  if (!checkout.isOpen) return null;

  return (
    <div className="checkout-overlay">
      <div className="checkout-modal">
        {checkout.completedSale ? (
          <ReceiptStep sale={checkout.completedSale} onClose={checkout.close} />
        ) : (
          <PaymentStep checkout={checkout} totalPrice={totalPrice} />
        )}
      </div>
    </div>
  );
}
