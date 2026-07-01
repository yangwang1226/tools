import { useEffect, useState } from "react";
import { navLinks } from "@/lib/data";
import { useNavScrolled } from "@/hooks/useNavScroll";

export default function Nav() {
  const scrolled = useNavScrolled(80);
  const [open, setOpen] = useState(false);

  // 点击锚点后关闭菜单
  useEffect(() => {
    if (!open) return;
    const close = () => setOpen(false);
    window.addEventListener("hashchange", close);
    return () => window.removeEventListener("hashchange", close);
  }, [open]);

  return (
    <header
      className={[
        "fixed inset-x-0 top-0 z-50 transition-all duration-500",
        scrolled
          ? "bg-paper-100/90 backdrop-blur-md shadow-[0_1px_0_rgba(44,53,48,0.08)]"
          : "bg-transparent",
      ].join(" ")}
    >
      <div className="container max-w-content flex items-center justify-between h-16 md:h-20">
        {/* Logo */}
        <a href="#top" className="flex items-center gap-3 group" aria-label="森呼吸庭院设计 首页">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none" className="text-moss">
            <path
              d="M16 4C10 8 8 13 8 18a8 8 0 0016 0c0-5-2-10-8-14z"
              stroke="currentColor"
              strokeWidth="1.4"
              strokeLinejoin="round"
            />
            <path d="M16 10v18M12 16h8M13 20h6" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
          </svg>
          <span
            className={[
              "font-serif text-lg md:text-xl tracking-wider transition-colors",
              scrolled ? "text-ink-900" : "text-paper-100",
            ].join(" ")}
          >
            森呼吸
          </span>
        </a>

        {/* 桌面导航 */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className={[
                "text-sm tracking-wider transition-colors hover:text-ochre",
                scrolled ? "text-ink-700" : "text-paper-100/90",
              ].join(" ")}
            >
              {l.label}
            </a>
          ))}
          <a
            href="tel:13520553153"
            className={[
              "text-sm tracking-wider px-4 py-2 border transition-all duration-300",
              scrolled
                ? "border-ink-800 text-ink-900 hover:bg-ink-900 hover:text-paper-100"
                : "border-paper-100/70 text-paper-100 hover:bg-paper-100 hover:text-ink-900",
            ].join(" ")}
          >
            13520553153
          </a>
        </nav>

        {/* 移动端汉堡 */}
        <button
          className="md:hidden flex flex-col gap-1.5 p-2"
          aria-label="展开菜单"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          <span
            className={[
              "block w-6 h-px transition-all duration-300",
              scrolled ? "bg-ink-900" : "bg-paper-100",
              open ? "translate-y-[7px] rotate-45" : "",
            ].join(" ")}
          />
          <span
            className={[
              "block w-6 h-px transition-all duration-300",
              scrolled ? "bg-ink-900" : "bg-paper-100",
              open ? "opacity-0" : "",
            ].join(" ")}
          />
          <span
            className={[
              "block w-6 h-px transition-all duration-300",
              scrolled ? "bg-ink-900" : "bg-paper-100",
              open ? "-translate-y-[7px] -rotate-45" : "",
            ].join(" ")}
          />
        </button>
      </div>

      {/* 移动端展开层 */}
      <div
        className={[
          "md:hidden overflow-hidden transition-all duration-500 bg-paper-100/98 backdrop-blur-md",
          open ? "max-h-[80vh] border-t border-ink-900/10" : "max-h-0",
        ].join(" ")}
      >
        <nav className="container max-w-content flex flex-col py-4">
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="py-3 text-base text-ink-800 border-b border-ink-900/5 tracking-wider"
            >
              {l.label}
            </a>
          ))}
          <a
            href="tel:13520553153"
            onClick={() => setOpen(false)}
            className="mt-4 py-3 text-center text-base text-paper-100 bg-ink-900 tracking-wider"
          >
            电话咨询 · 13520553153
          </a>
        </nav>
      </div>
    </header>
  );
}
