import { processSteps } from "@/lib/data";

export default function Process() {
  return (
    <section id="process" className="py-24 md:py-36 bg-ink-900 text-paper-100">
      <div className="container max-w-content">
        <div className="reveal mb-16 md:mb-24">
          <p className="text-clay text-xs tracking-widest2 uppercase font-display mb-4">How We Work</p>
          <h2 className="font-serif text-display-md">设计流程</h2>
          <p className="text-paper-100/70 max-w-xl mt-6 text-sm md:text-base leading-relaxed">
            从上门勘测到养护指导，六个环节构成森呼吸的标准服务路径，
            每一步都有明确交付，让改造有据可依。
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-px bg-paper-100/10">
          {processSteps.map((s, i) => (
            <div
              key={s.no}
              className="reveal bg-ink-900 p-6 md:p-8 relative group hover:bg-ink-800 transition-colors duration-500"
              style={{ transitionDelay: `${i * 70}ms` }}
            >
              <span className="font-display text-clay text-3xl md:text-4xl block mb-6">{s.no}</span>
              <h3 className="font-serif text-lg md:text-xl mb-3">{s.title}</h3>
              <p className="text-paper-100/60 text-xs md:text-sm leading-relaxed">{s.desc}</p>
              {/* 连接箭头（桌面） */}
              {i < processSteps.length - 1 && (
                <span className="hidden lg:block absolute top-1/2 -right-3 -translate-y-1/2 text-paper-100/30">
                  →
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
