import AreaPicker from "./AreaPicker";
import ProductPanel from "./ProductPanel";
import { useShopBrowser } from "./useShopBrowser";
import BasketPanel from "../basket/BasketPanel";
import CheckoutModal from "../checkout/CheckoutModal";

// The main selling screen. It joins the pieces together:
// shop areas + products (left), basket (right), checkout window (on top).
// The basket and checkout come from App so they survive page changes.
export default function DigitalShopPage({ basket, checkout }) {
  const browser = useShopBrowser();

  return (
    <>
      <header className="topbar">
        <div>
          <div className="breadcrumb">Selling Mode / Digital Shop</div>
          <h2>
            Good morning, Seller <span>☀️</span>
          </h2>
          <p>Let's make today's sales count.</p>
        </div>

        <div className="topbar-actions">
          <div className="connection-status">
            <span className="status-dot"></span>
            Online
          </div>
          <button className="icon-button" aria-label="Notifications">
            ♧
          </button>
          <div className="user-avatar">S</div>
        </div>
      </header>

      <section className="shop-heading">
        <div>
          <span className="eyebrow">YOUR SHOP</span>
          <h3>Explore your shop</h3>
          <p>
            Select a shop area, find a compartment and add products to the
            basket.
          </p>
        </div>
        <button className="mode-button">
          Selling Mode <span>⌄</span>
        </button>
      </section>

      <AreaPicker
        selectedArea={browser.selectedArea}
        onChooseArea={browser.chooseArea}
      />

      <section className="shop-workspace">
        <ProductPanel browser={browser} onAddToBasket={basket.addToBasket} />
        <BasketPanel
          basket={basket.basket}
          totalItems={basket.totalItems}
          totalPrice={basket.totalPrice}
          onChangeQuantity={basket.changeQuantity}
          onCheckout={checkout.open}
        />
      </section>

      <CheckoutModal checkout={checkout} totalPrice={basket.totalPrice} />
    </>
  );
}
