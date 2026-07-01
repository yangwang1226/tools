import { stats, img } from "@/lib/data";

export default function About() {
  return (
    <section id="about" className="py-24 md:py-36 paper-texture">
      <div className="container max-w-content">
        <div className="grid md:grid-cols-12 gap-10 md:gap-16 items-start">
          {/* 左侧：理念长文 */}
          <div className="reveal md:col-span-7">
            <p className="text-ochre text-xs tracking-widest2 uppercase font-display mb-4">About Us</p>
            <h2 className="font-serif text-ink-900 text-display-md mb-10">造一处能呼吸的庭院</h2>

            <div className="space-y-5 text-ink-700 text-sm md:text-base leading-loose max-w-prose">
              <p>
                森呼吸庭院设计深耕户外景观十年，我们相信一方好的庭院不在于堆砌昂贵材料，
                而在于让花箱、绿植、光线与生活动线在场地里自然生长。
              </p>
              <p>
                我们不做模板化的复制。每一个方案都从上门勘测开始，
                结合建筑风格、采光条件、家庭习惯与预算标准量身出图，
                让效果图与落地效果一比一还原。
              </p>
              <p>
                从一只定制的防腐木花箱，到一整座别墅庭院的全案施工，
                我们用标准化的工艺保证质量，用东方造园的审美保证质感，
                让户外的每一寸都有呼吸的节奏。
              </p>
            </div>

            <div className="hairline mt-12 mb-8" />

            {/* 服务保障 */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {[
                { t: "实地勘测", d: "上门量尺、记录采光与场地条件" },
                { t: "效果图预览", d: "提前预览落地效果，按需调整" },
                { t: "售后保障", d: "交付后养护指导，问题随时响应" },
              ].map((g) => (
                <div key={g.t}>
                  <h4 className="font-serif text-ink-900 text-base mb-2">{g.t}</h4>
                  <p className="text-ink-600 text-xs leading-relaxed">{g.d}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 右侧：数据 + 图 */}
          <div className="reveal md:col-span-5">
            <div className="relative overflow-hidden mb-10">
              <img
                src={img(
                  "Detail shot of a wooden planter box with moss, ferns and small flowers in a zen courtyard, soft morning light, shallow depth of field, botanical still life, muted earthy tones",
                  "portrait_4_3"
                )}
                alt="森呼吸庭院设计 — 花箱与绿植细节"
                loading="lazy"
                className="w-full aspect-[4/5] object-cover"
              />
            </div>

            <div className="grid grid-cols-2 gap-px bg-ink-900/10">
              {stats.map((s) => (
                <div key={s.label} className="bg-paper-100 p-5 md:p-6">
                  <p className="font-serif text-moss text-3xl md:text-4xl mb-2">{s.num}</p>
                  <p className="text-ink-600 text-xs leading-relaxed">{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
