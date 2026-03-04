import ArcCarousel from "./ArcCarousel";
import { props } from "@webflow/data-types";
import { declareComponent } from "@webflow/react";

export default declareComponent(ArcCarousel, {
  name: "Arc Carousel",
  description: "Fan/arc card carousel with swipe support. Drop a Collection List inside the Cards slot.",
  group: "Sliders",
  props: {
    children: props.Slot({
      name: "Cards",
    }),
    rotationDeg: props.Number({
      name: "Rotation Angle",
      defaultValue: 12,
    }),
    dropPx: props.Number({
      name: "Drop Distance",
      defaultValue: 30,
    }),
    autoplayDelay: props.Number({
      name: "Autoplay Delay (ms)",
      defaultValue: 3500,
    }),
    cardWidth: props.Number({
      name: "Card Width (px)",
      defaultValue: 280,
    }),
    cardHeight: props.Number({
      name: "Card Height (px)",
      defaultValue: 380,
    }),
    showOverlay: props.Boolean({
      name: "Show Overlay",
      defaultValue: true,
    }),
  },
});
