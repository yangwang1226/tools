import { navLinks } from "@/lib/data";

export default function Footer() {
  return (
    <footer className="bg-ink-900 text-paper-100/70">
      <div className="container max-w-content py-16 md:py-20">
        <div className="grid md:grid-cols-12 gap-10">
          {/* 公司信息 */}
          <div className="md:col-span-5">
            <div className="flex items-center gap-3 mb-6">
              <svg width="24" height="24" viewBox="0 0 32 32" fill="none" className="text-bamboo">
                <path
                  d="M16 4C10 8 8 13 8 18a8 8 0 0016 0c0-5-2-10-8-14z"
                  stroke="currentColor"
                  strokeWidth="1.4"
                  strokeLinejoin="round"
                />
                <path d="M16 10v18M12 16h8M13 20h6" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
              </svg>
              <span className="font-serif text-paper-100 text-lg tracking-wider">森呼吸庭院设计</span>
            </div>
            <p className="text-sm leading-relaxed max-w-sm">
              专注花箱定制、精品绿植、现场搭建与庭院整装，
              用东方造园审美与标准化施工落地能力，
              打造有呼吸节奏的户外庭院空间。
            </p>
          </div>

          {/* 快速导航 */}
          <div className="md:col-span-3">
            <h4 className="text-paper-100 text-xs tracking-widest2 uppercase mb-5 font-display">Navigate</h4>
            <ul className="space-y-3 text-sm">
              {navLinks.map((l) => (
                <li key={l.href}>
                  <a href={l.href} className="hover:text-bamboo transition-colors">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* 联系方式 */}
          <div className="md:col-span-4">
            <h4 className="text-paper-100 text-xs tracking-widest2 uppercase mb-5 font-display">Contact</h4>
            <ul className="space-y-3 text-sm">
              <li>电话：13520553153</li>
              <li>微信：13520553153</li>
              <li>服务区域：全国</li>
            </ul>
          </div>
        </div>

        <div className="hairline my-10 opacity-30" />

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 text-xs text-paper-100/50">
          <p>© {new Date().getFullYear()} 森呼吸庭院设计. 保留所有权利.</p>
          <p className="tracking-wider">沪ICP备 0000000 号 · 沪公网安备 0000000000 号</p>
        </div>
      </div>
    </footer>
  );
}
