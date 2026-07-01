import { img } from "@/lib/data";

export default function Hero() {
  return (
    <section id="top" className="relative min-h-[100svh] flex items-end overflow-hidden">
      {/* 背景图 */}
      <div className="absolute inset-0">
        <img
          src={img(
            "A tranquil modern Chinese courtyard garden at dawn, wooden planter boxes with lush greenery, stone path, soft mist, bamboo silhouette in background, cinematic natural light, wabi-sabi aesthetic, muted earthy palette, architectural photography",
            "landscape_16_9"
          )}
          alt="森呼吸庭院设计 — 自然光下的庭院景观"
          className="w-full h-full object-cover"
        />
        {/* 暗色蒙层：从左下渐深 */}
        <div className="absolute inset-0 bg-gradient-to-t from-ink-900/85 via-ink-900/30 to-ink-900/20" />
        <div className="absolute inset-0 bg-gradient-to-r from-ink-900/50 to-transparent" />
      </div>

      {/* 内容 */}
      <div className="relative w-full container max-w-content pb-20 md:pb-28 pt-32">
        <div className="max-w-3xl">
          <p className="text-paper-100/70 text-xs md:text-sm tracking-widest2 uppercase mb-6 md:mb-8 font-display animate-fade-up">
            Forest Breath · Garden Design
          </p>
          <h1 className="font-serif text-paper-100 text-display-xl animate-fade-up" style={{ animationDelay: "0.15s" }}>
            森呼吸
          </h1>
          <p
            className="font-serif text-paper-100/95 text-2xl md:text-4xl mt-4 md:mt-6 leading-snug animate-fade-up"
            style={{ animationDelay: "0.3s" }}
          >
            庭院设计
          </p>
          <p
            className="text-paper-100/80 text-base md:text-lg mt-8 md:mt-10 max-w-prose leading-relaxed animate-fade-up"
            style={{ animationDelay: "0.45s" }}
          >
            让每一寸户外，都有呼吸的节奏。
            <br className="hidden md:block" />
            花箱定制 · 精品绿植 · 现场搭建 · 庭院整装，一站式落地。
          </p>

          <div
            className="flex flex-col sm:flex-row gap-4 mt-10 md:mt-12 animate-fade-up"
            style={{ animationDelay: "0.6s" }}
          >
            <a
              href="#cases"
              className="px-8 py-4 text-sm tracking-wider text-ink-900 bg-paper-100 hover:bg-bamboo hover:text-paper-100 transition-all duration-300 text-center"
            >
              查看案例作品
            </a>
            <a
              href="tel:13520553153"
              className="px-8 py-4 text-sm tracking-wider text-paper-100 border border-paper-100/60 hover:bg-paper-100 hover:text-ink-900 transition-all duration-300 text-center"
            >
              电话咨询 · 13520553153
            </a>
          </div>
        </div>
      </div>

      {/* 滚动指引 */}
      <a
        href="#services"
        aria-label="向下滚动"
        className="absolute bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-paper-100/60 hover:text-paper-100 transition-colors"
      >
        <span className="text-[10px] tracking-widest2 uppercase font-display">Scroll</span>
        <svg width="14" height="22" viewBox="0 0 14 22" fill="none" className="animate-breath">
          <rect x="0.5" y="0.5" width="13" height="21" rx="6.5" stroke="currentColor" />
          <rect x="6" y="5" width="2" height="5" rx="1" fill="currentColor" />
        </svg>
      </a>
    </section>
  );
}
