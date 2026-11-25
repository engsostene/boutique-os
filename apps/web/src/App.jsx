import { useState } from "react";
import Sidebar from "./layouts/Sidebar";
import DigitalShopPage from "./features/digital-shop/DigitalShopPage";
import SalesHistoryPage from "./features/sales/SalesHistoryPage";
import { useBasket } from "./features/basket/useBasket";
import { useCheckout } from "./features/checkout/useCheckout";

// The root of the app. It owns only what must be shared between pages:
// which page is open, the basket, the checkout, and the sales history.
// Everything else lives inside the feature folders.
function App() {
  const [activePage, setActivePage] = useState("digital-shop");

  // Completed sales kept for this session only.
  // Later, this history will come from the database.
  const [salesHistory, setSalesHistory] = useState([]);

  const basket = useBasket();

  const checkout = useCheckout({
    items: basket.basket,
    totalPrice: basket.totalPrice,
    onSaleConfirmed: (sale) => {
      basket.clearBasket();
      // Newest sale goes first.
      setSalesHistory((previousSales) => [sale, ...previousSales]);
    },
  });

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

      <main className="main-content">
        {activePage === "sales" ? (
          <SalesHistoryPage
            salesHistory={salesHistory}
            onReturnToShop={() => setActivePage("digital-shop")}
          />
        ) : (
          <DigitalShopPage basket={basket} checkout={checkout} />
        )}
      </main>
    </div>
  );
}

export default App;
