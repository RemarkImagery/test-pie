import ArcCarousel from "../components/ArcCarousel";

const demoCards = [
  { image: "https://picsum.photos/seed/a/600/800", title: "Symmetrical Export Tariffs" },
  { image: "https://picsum.photos/seed/b/600/800", title: "Ratepayers Assistance Scheme" },
  { image: "https://picsum.photos/seed/c/600/800", title: "Community Energy" },
  { image: "https://picsum.photos/seed/d/600/800", title: "Electric Vehicle Policy" },
  { image: "https://picsum.photos/seed/e/600/800", title: "Heat Pump Rollout" },
  { image: "https://picsum.photos/seed/f/600/800", title: "Grid Modernisation" },
  { image: "https://picsum.photos/seed/g/600/800", title: "Solar Schools" },
  { image: "https://picsum.photos/seed/h/600/800", title: "Battery Storage" },
];

export default function Home() {
  return (
    <main style={{ fontFamily: "system-ui, sans-serif" }}>
      <div style={{ padding: "40px 0 0", textAlign: "center" }}>
        <h1 style={{ fontSize: "32px", fontWeight: 700 }}>Reports</h1>
      </div>
      <ArcCarousel>
        {demoCards.map((card, i) => (
          <div key={i}>
            <img
              src={card.image}
              alt={card.title}
              style={{
                width: "100%",
                height: "380px",
                objectFit: "cover",
                display: "block",
              }}
            />
            <div style={{ padding: "16px", textAlign: "center" }}>
              <h4 style={{ fontSize: "18px", fontWeight: 700, margin: "0 0 8px" }}>
                {card.title}
              </h4>
            </div>
          </div>
        ))}
      </ArcCarousel>
    </main>
  );
}
