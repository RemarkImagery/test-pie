import ArcCarousel from "../../components/ArcCarousel";

const accommodations = [
  {
    image: "https://picsum.photos/seed/palmcove1/600/800",
    name: "Peppers Beach Club & Spa",
    description:
      "Lagoon-style pool, direct beach access, and spacious suites with kitchenettes. Cots and highchairs available on request.",
    highlights: ["Lagoon pool", "Beach access", "Kids welcome"],
  },
  {
    image: "https://picsum.photos/seed/palmcove2/600/800",
    name: "Alamanda Palm Cove by Lancemore",
    description:
      "Spacious one- to three-bedroom apartments with full kitchens, laundry facilities, and a fenced resort pool ideal for toddlers.",
    highlights: ["Full kitchen", "Laundry", "Fenced pool"],
  },
  {
    image: "https://picsum.photos/seed/palmcove3/600/800",
    name: "Mantra Amphora",
    description:
      "Family-friendly resort with a large lagoon pool, BBQ area, and self-contained apartments with separate bedrooms for little ones.",
    highlights: ["Lagoon pool", "BBQ area", "Self-contained"],
  },
  {
    image: "https://picsum.photos/seed/palmcove4/600/800",
    name: "Sarayi Palm Cove",
    description:
      "Boutique resort with heated pool, tropical gardens, and one-bedroom suites. Walking distance to the beach and village shops.",
    highlights: ["Heated pool", "Gardens", "Village location"],
  },
  {
    image: "https://picsum.photos/seed/palmcove5/600/800",
    name: "The Reef House Palm Cove",
    description:
      "Heritage-listed boutique hotel with Brigadier Suite family rooms, three pools, and complimentary afternoon drinks for parents.",
    highlights: ["Three pools", "Family rooms", "Heritage charm"],
  },
  {
    image: "https://picsum.photos/seed/palmcove6/600/800",
    name: "Novotel Cairns Oasis Resort",
    description:
      "Just 20 minutes from Palm Cove with a massive lagoon pool, kids club, and family rooms. Great base for reef and rainforest day trips.",
    highlights: ["Kids club", "Lagoon pool", "Day trip base"],
  },
  {
    image: "https://picsum.photos/seed/palmcove7/600/800",
    name: "Elysium The Drift",
    description:
      "Beachfront apartments with ocean views, full kitchens, and an elevated pool deck. Quiet end of Palm Cove perfect for nap schedules.",
    highlights: ["Beachfront", "Ocean views", "Quiet location"],
  },
  {
    image: "https://picsum.photos/seed/palmcove8/600/800",
    name: "Melaleuca Resort",
    description:
      "Affordable self-contained studios and apartments surrounded by tropical gardens with a saltwater pool and shaded play area.",
    highlights: ["Budget-friendly", "Saltwater pool", "Play area"],
  },
];

const tips = [
  {
    title: "Best Time to Visit",
    text: "May to October (dry season) offers warm days, low humidity, and minimal stinger risk in the ocean. Perfect for toddlers at the beach.",
  },
  {
    title: "Beach Safety",
    text: "Palm Cove beach has a stinger net during October\u2013May. Outside stinger season, the calm waters and gentle slope make it ideal for toddlers to paddle.",
  },
  {
    title: "Getting Around",
    text: "The village is compact and pram-friendly. A car is handy for day trips to Cairns Aquarium, Hartley\u2019s Crocodile Adventures, or the Kuranda Scenic Railway.",
  },
  {
    title: "Dining with Toddlers",
    text: "Most Palm Cove restaurants are relaxed and welcoming. NuNu, Chill Cafe, and the Surf Club all have highchairs and kid-friendly menus.",
  },
  {
    title: "What to Pack",
    text: "Reef-safe sunscreen, a UV swim suit, a portable travel cot if your accommodation doesn\u2019t supply one, and insect repellent for evenings.",
  },
  {
    title: "Nearby Activities",
    text: "Wildlife Habitat Port Douglas (45 min), Cairns Esplanade Lagoon (free, 25 min), Mossman Gorge (1 hr), and glass-bottom boat reef tours from Palm Cove jetty.",
  },
];

export default function PalmCoveToddlerAccommodation() {
  return (
    <main style={{ fontFamily: "system-ui, sans-serif", color: "#1a1a2e" }}>
      <section
        style={{
          padding: "60px 20px 20px",
          textAlign: "center",
          maxWidth: "800px",
          margin: "0 auto",
        }}
      >
        <h1 style={{ fontSize: "36px", fontWeight: 800, margin: "0 0 12px" }}>
          Palm Cove Toddler-Friendly Accommodation
        </h1>
        <p
          style={{
            fontSize: "18px",
            lineHeight: 1.6,
            color: "#555",
            margin: "0 0 8px",
          }}
        >
          Palm Cove is a palm-lined beachside village 25 minutes north of
          Cairns in Tropical North Queensland. Its calm waters, compact village
          layout, and family-friendly resorts make it one of Australia&apos;s
          best destinations for a holiday with toddlers.
        </p>
      </section>

      <section>
        <h2
          style={{
            textAlign: "center",
            fontSize: "24px",
            fontWeight: 700,
            margin: "0 0 4px",
          }}
        >
          Top Accommodation Picks
        </h2>
        <ArcCarousel cardWidth={300} cardHeight={420} autoplayDelay={4000}>
          {accommodations.map((place, i) => (
            <div key={i} style={{ background: "#fff" }}>
              <img
                src={place.image}
                alt={place.name}
                style={{
                  width: "100%",
                  height: "260px",
                  objectFit: "cover",
                  display: "block",
                }}
              />
              <div style={{ padding: "16px" }}>
                <h3
                  style={{
                    fontSize: "17px",
                    fontWeight: 700,
                    margin: "0 0 6px",
                  }}
                >
                  {place.name}
                </h3>
                <p
                  style={{
                    fontSize: "13px",
                    lineHeight: 1.5,
                    color: "#555",
                    margin: "0 0 10px",
                  }}
                >
                  {place.description}
                </p>
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                  {place.highlights.map((h) => (
                    <span
                      key={h}
                      style={{
                        fontSize: "11px",
                        fontWeight: 600,
                        background: "#e8f5e9",
                        color: "#2e7d32",
                        padding: "3px 8px",
                        borderRadius: "12px",
                      }}
                    >
                      {h}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </ArcCarousel>
      </section>

      <section
        style={{
          maxWidth: "900px",
          margin: "40px auto",
          padding: "0 20px 60px",
        }}
      >
        <h2
          style={{
            fontSize: "24px",
            fontWeight: 700,
            textAlign: "center",
            margin: "0 0 24px",
          }}
        >
          Tips for Visiting Palm Cove with Toddlers
        </h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
            gap: "20px",
          }}
        >
          {tips.map((tip) => (
            <div
              key={tip.title}
              style={{
                background: "#f9fafb",
                borderRadius: "12px",
                padding: "20px",
                border: "1px solid #e5e7eb",
              }}
            >
              <h3
                style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 8px" }}
              >
                {tip.title}
              </h3>
              <p
                style={{
                  fontSize: "14px",
                  lineHeight: 1.6,
                  color: "#555",
                  margin: 0,
                }}
              >
                {tip.text}
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
