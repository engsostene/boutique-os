import { useState } from "react";
import { shopAreas } from "../../data/shopAreas";
import { sampleProducts } from "../../data/sampleProducts";

// Decides which products the seller sees: either the products in the
// chosen compartment, or the results of a search across the whole shop.
export function useShopBrowser() {
  const [selectedArea, setSelectedArea] = useState("left");
  const [selectedCell, setSelectedCell] = useState("A01");
  const [search, setSearch] = useState("");

  const currentArea = shopAreas.find((area) => area.id === selectedArea);

  const visibleProducts = sampleProducts.filter((product) => {
    const matchesSearch =
      product.name.toLowerCase().includes(search.toLowerCase()) ||
      product.detail.toLowerCase().includes(search.toLowerCase());

    const matchesLocation =
      product.area === selectedArea && product.cell === selectedCell;

    // While searching, look everywhere; otherwise only the open compartment.
    return search.trim() ? matchesSearch : matchesLocation;
  });

  // Opening an area selects its first compartment and clears any search.
  function chooseArea(area) {
    setSelectedArea(area.id);
    setSelectedCell(area.cells[0]);
    setSearch("");
  }

  return {
    selectedArea,
    selectedCell,
    setSelectedCell,
    search,
    setSearch,
    currentArea,
    visibleProducts,
    chooseArea,
  };
}
