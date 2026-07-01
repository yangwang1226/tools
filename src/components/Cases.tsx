import { cases } from "@/lib/data";

export default function Cases() {
  return (
    <section id="cases" className="py-24 md:py-36 paper-texture">
      <div className="container max-w-content">
        <div className="reveal flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-16 md:mb-20">
          <div>
            <p className="text-ochre text-xs tracking-widest2 uppercase font-display mb-4">Selected Works</p>
            <h2 className="font-serif text-ink-900 text-display-md">案例作品</h2>
          </div>
          <p className="text-ink-600 max-w-md text-sm md:text-base leading-relaxed">
            从私院到街区，从花箱组团到全案庭院，
            <br className="hidden md:block" />
            每一个落地项目都是一次与场地的对话。
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          {cases.map((c, i) => (
            <figure
              key={c.name}
              className={[
                "reveal group relative overflow-hidden",
                c.tall ? "lg:row-span-2" : "",
              ].join(" ")}
              style={{ transitionDelay: `${i * 80}ms` }}
            >
              <img
                src={c.image}
                alt={`${c.name} — ${c.type}`}
                loading="lazy"
                className={[
                  "w-full object-cover transition-transform duration-[1.2s] ease-soft group-hover:scale-105",
                  c.tall ? "aspect-[3/4] lg:h-full" : "aspect-[4/3]",
                ].join(" ")}
              />
              {/* 遮罩 */}
              <figcaption className="absolute inset-0 flex flex-col justify-end p-5 md:p-6 bg-gradient-to-t from-ink-900/90 via-ink-900/20 to-transparent opacity-0 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-500">
                <span className="font-display text-bamboo text-xs tracking-widest2 mb-2">
                  {c.style}
                </span>
                <h3 className="font-serif text-paper-100 text-lg md:text-xl mb-2">{c.name}</h3>
                <div className="flex flex-wrap gap-2 text-xs text-paper-100/80">
                  <span className="border border-paper-100/30 px-2 py-0.5">{c.type}</span>
                  <span className="border border-paper-100/30 px-2 py-0.5">{c.material}</span>
                </div>
              </figcaption>
              {/* 移动端常显标题 */}
              <div className="md:hidden absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-ink-900/80 to-transparent">
                <h3 className="font-serif text-paper-100 text-base">{c.name}</h3>
                <p className="text-paper-100/70 text-xs mt-1">{c.type} · {c.style}</p>
              </div>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
