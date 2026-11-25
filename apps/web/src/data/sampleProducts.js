// Demo products used until the screen is connected to the Django API
// (GET /api/businesses/<id>/products/ and the shop stock endpoint).
// "area" and "cell" say where the product sits in the shop.
export const sampleProducts = [
  { id: 1, name: "Rice", detail: "1 kg · Long grain", price: 1800, emoji: "🍚", area: "left", cell: "A01", stock: 24 },
  { id: 2, name: "Wheat Flour", detail: "1 kg · Regular", price: 1400, emoji: "🌾", area: "left", cell: "A01", stock: 18 },
  { id: 3, name: "Sugar", detail: "1 kg · White", price: 1600, emoji: "🧂", area: "left", cell: "A02", stock: 32 },
  { id: 4, name: "Cooking Oil", detail: "1 litre", price: 3200, emoji: "🫗", area: "left", cell: "A02", stock: 12 },
  { id: 5, name: "Bathing Soap", detail: "Single bar", price: 1000, emoji: "🧼", area: "right", cell: "B01", stock: 40 },
  { id: 6, name: "Laundry Soap", detail: "Large bar", price: 1500, emoji: "🧽", area: "right", cell: "B01", stock: 15 },
  { id: 7, name: "Toothpaste", detail: "Small tube", price: 2200, emoji: "🪥", area: "right", cell: "B02", stock: 9 },
  { id: 8, name: "Matches", detail: "One box", price: 200, emoji: "🔥", area: "counter", cell: "C01", stock: 60 },
  { id: 9, name: "Biscuits", detail: "Small packet", price: 500, emoji: "🍪", area: "counter", cell: "C01", stock: 25 },
  { id: 10, name: "Tea Leaves", detail: "250 g packet", price: 1200, emoji: "🍵", area: "cupboard", cell: "D01", stock: 14 },
  { id: 11, name: "Maize Flour", detail: "2 kg packet", price: 2500, emoji: "🌽", area: "storage", cell: "E01", stock: 20 },
];
