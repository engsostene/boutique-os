// The physical layout of the shop: areas, and the compartments (cells) inside each.
// Later this will come from the backend (ShopArea and Compartment models).
export const shopAreas = [
  { id: "left", name: "Left Shelf", icon: "▤", cells: ["A01", "A02", "A03", "A04"] },
  { id: "right", name: "Right Shelf", icon: "▤", cells: ["B01", "B02", "B03", "B04"] },
  { id: "counter", name: "Counter", icon: "▣", cells: ["C01", "C02"] },
  { id: "cupboard", name: "Cupboard", icon: "▥", cells: ["D01", "D02"] },
  { id: "storage", name: "Storage", icon: "▦", cells: ["E01", "E02"] },
];
