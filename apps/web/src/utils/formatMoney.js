// Shows an amount the way the shop displays money, for example 1,800 RWF.
export function formatMoney(amount) {
  return `${new Intl.NumberFormat("en-US").format(amount)} RWF`;
}
