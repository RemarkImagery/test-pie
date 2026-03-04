"use client";

import React, { useRef, useCallback, Children } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Autoplay } from "swiper/modules";
import type { Swiper as SwiperType } from "swiper";
import "swiper/css";

interface ArcCarouselProps {
  children?: React.ReactNode;
  autoplayDelay?: number;
  rotationDeg?: number;
  dropPx?: number;
  cardWidth?: number;
  cardHeight?: number;
  showOverlay?: boolean;
}

export default function ArcCarousel({
  children,
  autoplayDelay = 3500,
  rotationDeg = 12,
  dropPx = 30,
  cardWidth = 280,
  cardHeight = 380,
  showOverlay = true,
}: ArcCarouselProps) {
  const swiperRef = useRef<SwiperType | null>(null);
  const childArray = Children.toArray(children);
  const count = childArray.length;

  const applyTransforms = useCallback(
    (swiper: SwiperType) => {
      swiper.slides.forEach((el: HTMLElement) => {
        const p = (el as any).progress ?? 0;
        const a = Math.abs(p);
        const z = 50 - Math.round(a) * 10;
        el.style.transform = `rotate(${p * -rotationDeg}deg) translateY(${a * a * dropPx}px) scale(${Math.max(0.75, 1 - a * 0.08)})`;
        el.style.opacity = a > 3 ? "0" : String(Math.max(0.25, 1 - a * 0.3));
        el.style.zIndex = String(z);
        el.style.position = "relative";
        el.style.transformOrigin = "center top";

        const ov = el.querySelector(".arc-card-ov") as HTMLElement | null;
        if (ov) {
          ov.style.opacity = a > 0 ? String(Math.min(0.85, a * 0.4)) : "0";
        }
      });
    },
    [rotationDeg, dropPx]
  );

  if (count === 0) return null;

  return (
    <div
      style={{
        width: "100%",
        overflow: "hidden",
        padding: "20px 0 0",
        position: "relative",
      }}
    >
      <style>{`
        .arc-swiper { overflow: visible !important; padding: 10px 0 50px; }
        .arc-swiper .swiper-slide { transform-origin: center top !important; width: ${cardWidth}px !important; }
        .arc-nav {
          position: absolute; top: 50%; transform: translateY(-50%);
          width: 48px; height: 48px; border-radius: 50%;
          border: 2px solid #1a1a2e; background: #fff;
          cursor: pointer; display: flex; align-items: center;
          justify-content: center; z-index: 100;
          font-size: 18px; color: #1a1a2e;
        }
        .arc-nav:hover { background: #f5f5f5; }
        .arc-prev { left: 40px; }
        .arc-next { right: 40px; }
        .arc-card-ov {
          position: absolute; top: 0; left: 0; width: 100%; height: 100%;
          background: rgba(255,255,255,0.6); border-radius: 12px;
          pointer-events: none; opacity: 0; transition: opacity 500ms ease;
        }
        @media (max-width: 767px) {
          .arc-swiper .swiper-slide { width: 60vw !important; }
          .arc-nav { width: 36px; height: 36px; font-size: 14px; top: 35%; }
          .arc-prev { left: 10px; }
          .arc-next { right: 10px; }
        }
      `}</style>

      <div style={{ position: "relative" }}>
        <Swiper
          className="arc-swiper"
          modules={[Navigation, Autoplay]}
          onSwiper={(s) => {
            swiperRef.current = s;
          }}
          onSetTranslate={(swiper) => applyTransforms(swiper)}
          onSetTransition={(swiper, duration) => {
            swiper.slides.forEach((el: HTMLElement) => {
              el.style.transition = `transform ${duration}ms ease, opacity ${duration}ms ease`;
              const ov = el.querySelector(".arc-card-ov") as HTMLElement | null;
              if (ov) ov.style.transition = `opacity ${duration}ms ease`;
            });
          }}
          initialSlide={Math.floor(count / 2)}
          centeredSlides
          slidesPerView="auto"
          spaceBetween={10}
          loop
          {...({ loopedSlides: count * 2 } as any)}
          speed={500}
          watchSlidesProgress
          slideToClickedSlide
          autoplay={{
            delay: autoplayDelay,
            disableOnInteraction: false,
            pauseOnMouseEnter: true,
          }}
          navigation={{
            nextEl: ".arc-next",
            prevEl: ".arc-prev",
          }}
        >
          {childArray.map((child, i) => (
            <SwiperSlide key={i}>
              <div
                style={{
                  position: "relative",
                  borderRadius: "12px",
                  overflow: "hidden",
                  minHeight: `${cardHeight}px`,
                }}
              >
                {child}
                {showOverlay && <div className="arc-card-ov" />}
              </div>
            </SwiperSlide>
          ))}
        </Swiper>

        <button className="arc-nav arc-prev" aria-label="Previous">
          &#8249;
        </button>
        <button className="arc-nav arc-next" aria-label="Next">
          &#8250;
        </button>
      </div>
    </div>
  );
}
