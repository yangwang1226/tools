import { services } from "@/lib/data";

export default function ServiceDetail() {
  return (
    <section id="detail" className="py-24 md:py-36 bg-paper-200">
      <div className="container max-w-content">
        <div className="reveal mb-20 md:mb-28">
          <p className="text-ochre text-xs tracking-widest2 uppercase font-display mb-4">In Detail</p>
          <h2 className="font-serif text-ink-900 text-display-md">服务详述</h2>
        </div>

        <div className="space-y-24 md:space-y-36">
          {services.map((s, i) => {
            const reverse = i % 2 === 1;
            return (
              <div
                key={s.no}
                className="grid md:grid-cols-12 gap-8 md:gap-12 items-center"
              >
                {/* 图片 */}
                <div
                  className={[
                    "reveal md:col-span-6 lg:col-span-7",
                    reverse ? "md:order-2" : "",
                  ].join(" ")}
                >
                  <div className="relative overflow-hidden">
                    <img
                      src={s.image}
                      alt={`${s.name} — 森呼吸庭院设计`}
                      loading="lazy"
                      className="w-full aspect-[4/3] object-cover transition-transform duration-[1.2s] hover:scale-105"
                    />
                    {/* 编号印章 */}
                    <div className="absolute top-4 left-4 md:top-6 md:left-6">
                      <span className="seal inline-block font-serif text-paper-100 text-base md:text-lg bg-ink-900/30 backdrop-blur-sm">
                        {s.no}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 文案 */}
                <div
                  className={[
                    "reveal md:col-span-6 lg:col-span-5",
                    reverse ? "md:order-1 md:pr-8" : "md:pl-8",
                  ].join(" ")}
                >
                  <p className="font-display text-ochre text-sm tracking-widest2 mb-3">
                    {s.no} · {s.en}
                  </p>
                  <h3 className="font-serif text-ink-900 text-2xl md:text-3xl mb-2">{s.name}</h3>
                  <p className="text-moss text-sm md:text-base tracking-wider mb-6">{s.tagline}</p>
                  <div className="hairline mb-6" />
                  <p className="text-ink-700 text-sm md:text-base leading-relaxed mb-6">{s.desc}</p>
                  <ul className="space-y-3">
                    {s.points.map((p, idx) => (
                      <li key={idx} className="flex gap-3 text-sm md:text-[15px] text-ink-700 leading-relaxed">
                        <span className="text-ochre mt-1 shrink-0">·</span>
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
