import { shopAreas } from "../../data/shopAreas";

// The row of shop areas (Left Shelf, Counter, ...).
export default function AreaPicker({ selectedArea, onChooseArea }) {
  return (
    <section className="area-section">
      <div className="section-heading">
        <div>
          <h3>Shop areas</h3>
          <span>Choose where you want to look</span>
        </div>
        <button className="text-button">View shop layout ↗</button>
      </div>

      <div className="area-list">
        {shopAreas.map((area) => (
          <button
            key={area.id}
            className={`area-card ${selectedArea === area.id ? "selected" : ""}`}
            onClick={() => onChooseArea(area)}
          >
            <span className="area-icon">{area.icon}</span>
            <span className="area-name">{area.name}</span>
            <span className="area-count">{area.cells.length} cells</span>
          </button>
        ))}
      </div>
    </section>
  );
}
