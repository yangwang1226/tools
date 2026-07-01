import { services } from "@/lib/data";

// 五个手绘风线稿图标
const icons = [
  // 花箱
  <svg key="1" viewBox="0 0 48 48" fill="none" className="w-full h-full">
    <path d="M10 18h28l-3 20H13L10 18z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    <path d="M14 18c0-4 3-7 5-7M24 18c0-5 3-8 5-8M34 18c0-4 2-7 4-7" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    <path d="M10 18h28" stroke="currentColor" strokeWidth="1.4" />
  </svg>,
  // 绿植
  <svg key="2" viewBox="0 0 48 48" fill="none" className="w-full h-full">
    <path d="M24 42V20" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    <path d="M24 22c-8 0-12-5-12-12 8 0 12 5 12 12z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    <path d="M24 26c8 0 12-5 12-12-8 0-12 5-12 12z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
  </svg>,
  // 搭建
  <svg key="3" viewBox="0 0 48 48" fill="none" className="w-full h-full">
    <path d="M8 38h32" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    <path d="M12 38V20l12-8 12 8v18" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    <path d="M20 38v-8h8v8" stroke="currentColor" strokeWidth="1.4" />
  </svg>,
  // 设计
  <svg key="4" viewBox="0 0 48 48" fill="none" className="w-full h-full">
    <path d="M10 38l10-28 18 8-10 28-18-8z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    <path d="M20 10l18 8" stroke="currentColor" strokeWidth="1.4" />
    <path d="M16 24c4-2 8-1 10 2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
  </svg>,
  // 整装
  <svg key="5" viewBox="0 0 48 48" fill="none" className="w-full h-full">
    <path d="M6 42h36" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    <path d="M10 42V18l14-10 14 10v24" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    <path d="M20 42v-10h8v10" stroke="currentColor" strokeWidth="1.4" />
    <path d="M14 22h6M28 22h6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
  </svg>,
];

export default function ServicesOverview() {
  return (
    <section id="services" className="py-24 md:py-36 paper-texture">
      <div className="container max-w-content">
        {/* 标题 */}
        <div className="reveal flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-16 md:mb-24">
          <div>
            <p className="text-ochre text-xs tracking-widest2 uppercase font-display mb-4">What We Do</p>
            <h2 className="font-serif text-ink-900 text-display-md">五项核心业务</h2>
          </div>
          <p className="text-ink-600 max-w-md text-sm md:text-base leading-relaxed">
            从一只花箱到一方庭院，从绿植搭配到全案施工，
            <br className="hidden md:block" />
            森呼吸提供完整闭环的户外景观服务。
          </p>
        </div>

        {/* 五列概览 */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-px bg-ink-900/10">
          {services.map((s, i) => (
            <a
              key={s.no}
              href="#detail"
              className="reveal group bg-paper-100 hover:bg-paper-50 transition-colors duration-500 p-6 md:p-8 flex flex-col"
              style={{ transitionDelay: `${i * 60}ms` }}
            >
              <div className="text-moss mb-6 w-12 h-12 md:w-14 md:h-14">{icons[i]}</div>
              <p className="font-display text-ochre text-sm tracking-widest2">{s.no}</p>
              <h3 className="font-serif text-ink-900 text-lg md:text-xl mt-2 mb-3">{s.name}</h3>
              <p className="text-ink-600 text-xs md:text-sm leading-relaxed">{s.tagline}</p>
              <span className="mt-6 text-ink-600 text-xs tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                查看详情 →
              </span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
