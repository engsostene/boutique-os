import { useState } from "react";

// All checkout state and payment rules live here, away from the screen code.
//
// IMPORTANT: these rules are for the demo screen only. The backend
// (confirm_sale in services/api/core/services.py) is the real authority
// and must re-check every amount, stock level and credit limit.
//
// items       - the basket lines being sold
// totalPrice  - the basket total
// onSaleConfirmed(sale) - called once the seller confirms, so the app can
//                         clear the basket and save the sale in history
export function useCheckout({ items, totalPrice, onSaleConfirmed }) {
  const [isOpen, setIsOpen] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState("cash");

  // Cash or Mobile Money amount, depending on the payment method.
  const [amountPaid, setAmountPaid] = useState("0");

  // Separate amounts used only for split payments.
  const [cashAmount, setCashAmount] = useState("0");
  const [mobileAmount, setMobileAmount] = useState("0");

  // Customer name (for credit) and Mobile Money reference.
  const [customerName, setCustomerName] = useState("");
  const [mobileReference, setMobileReference] = useState("");

  // The finished sale, shown on the receipt. null while still paying.
  const [completedSale, setCompletedSale] = useState(null);

  // ---- Amounts worked out from what the seller typed ----
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
    paymentMethod === "cash" ? Math.max(0, paidTotal - totalPrice) : 0;

  const requiresCustomer = outstandingBalance > 0;
  const requiresMobileReference = mobilePaid > 0;

  // ---- Problems the seller must fix before confirming ----
  // Cash overpayment is allowed (the seller returns change).
  // Other methods cannot exceed the sale total.
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

  const invalidPayment =
    (paymentMethod !== "cash" && paidTotal > totalPrice) ||
    (requiresCustomer && !customerName.trim()) ||
    (requiresMobileReference && !mobileReference.trim());

  // ---- Actions ----
  function open() {
    setPaymentMethod("cash");
    setAmountPaid(String(totalPrice));
    setCashAmount("0");
    setMobileAmount("0");
    setCustomerName("");
    setMobileReference("");
    setCompletedSale(null);
    setIsOpen(true);
  }

  function close() {
    setIsOpen(false);
  }

  function confirm() {
    if (items.length === 0 || invalidPayment) return;

    const sale = {
      reference: `DEMO-${Date.now()}`,
      items: [...items],
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
    onSaleConfirmed(sale);
  }

  return {
    isOpen,
    completedSale,
    paymentMethod,
    setPaymentMethod,
    amountPaid,
    setAmountPaid,
    cashAmount,
    setCashAmount,
    mobileAmount,
    setMobileAmount,
    customerName,
    setCustomerName,
    mobileReference,
    setMobileReference,
    paidTotal,
    outstandingBalance,
    changeDue,
    requiresCustomer,
    requiresMobileReference,
    paymentErrors,
    invalidPayment,
    open,
    close,
    confirm,
  };
}
