import { useState } from "react";

// Everything about the basket in one place: what is in it, how to change it,
// and the totals. Stock limits are respected here for the demo; the real
// stock check is done again by the backend when the sale is confirmed.
export function useBasket() {
  const [basket, setBasket] = useState([]);

  const totalItems = basket.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = basket.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

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

  // change is +1 or -1. An item whose quantity reaches 0 is removed.
  function changeQuantity(productId, change) {
    setBasket((currentBasket) =>
      currentBasket
        .map((item) =>
          item.id === productId
            ? { ...item, quantity: Math.min(item.quantity + change, item.stock) }
            : item
        )
        .filter((item) => item.quantity > 0)
    );
  }

  function clearBasket() {
    setBasket([]);
  }

  return { basket, totalItems, totalPrice, addToBasket, changeQuantity, clearBasket };
}
