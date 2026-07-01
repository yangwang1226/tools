// 森呼吸庭院设计 — 站点静态数据

export const img = (prompt: string, size = "landscape_16_9") =>
  `https://console.enterprise.trae.cn/api/ide/v1/text_to_image?prompt=${encodeURIComponent(
    prompt
  )}&image_size=${size}`;

export type ServiceItem = {
  no: string;
  name: string;
  en: string;
  tagline: string;
  desc: string;
  points: string[];
  image: string;
};

export const services: ServiceItem[] = [
  {
    no: "壹",
    name: "花箱定制设计",
    en: "Bespoke Planter",
    tagline: "按需专属定制，告别千篇一律",
    desc: "支持全风格、全尺寸、全材质专属定制，贴合建筑风格与场地尺寸，让花箱成为景观点睛之笔，而非突兀摆设。可融入云纹、格栅、镂空、灯光等特色设计，适配别墅庭院、小区绿化、商业街、门店外摆、道路景观等场景。",
    points: [
      "定制风格全覆盖：新中式、现代极简、欧式轻奢、复古田园、市政简约",
      "主流优质材质：防腐木、铝合金、铁艺、304不锈钢、仿石材质",
      "防腐防锈防晒防水工艺，户外露天不开裂、不变形、不褪色",
      "支持异形、弧形、组合式、坐凳一体式、收纳式花箱定制",
      "免费上门勘测，结合采光与喜好出专属效果图，零误差落地",
    ],
    image: img(
      "A bespoke wooden planter box with lattice details in a modern Chinese courtyard, soft morning light, low saturation, natural materials, architectural photography, muted tones",
      "landscape_4_3"
    ),
  },
  {
    no: "贰",
    name: "精品绿植售卖",
    en: "Curated Greenery",
    tagline: "易活好养，景观适配",
    desc: "配套供应全品类庭院、花箱专用绿植，拒绝劣质滞销苗木，精选易存活、长势好、观赏性强、适配本地气候的花草灌木、四季绿植、造型景观树，解决客户买花难、养不活、搭配丑的痛点。",
    points: [
      "品类丰富：四季常青、开花花卉、多年生灌木、草坪、造型苗木、爬藤",
      "根据花箱尺寸、光照、干湿、季节专业搭配高低层次组合",
      "春夏秋冬皆有景致，四季轮转不空档",
      "苗木现选现发、根系完整、成活率高",
      "附带基础养护指导，新手也能轻松打理",
    ],
    image: img(
      "Lush green plants and flowers arranged in a wooden planter, morning dew, soft natural light, botanical photography, muted earthy palette, shallow depth of field",
      "landscape_4_3"
    ),
  },
  {
    no: "叁",
    name: "花箱现场搭建安装",
    en: "On-site Installation",
    tagline: "标准化落地，一站式完工",
    desc: "提供花箱全流程落地搭建服务，从成品运输、场地找平、定位安装、组合拼接、固定加固到绿植栽种、整体收尾一站式完成，客户无需自己找工人、无需费心对接。",
    points: [
      "团队拥有多年户外景观施工经验，标准化工艺施工",
      "安装稳固平整、拼接缝隙均匀、造型规整",
      "杜绝松动、倾斜、漏水等问题",
      "单组家用、庭院组合、商业街组团均可高效完工",
      "现场整洁、工期可控、售后有保障",
    ],
    image: img(
      "Workers installing wooden planter boxes along a commercial street, professional construction scene, overcast soft light, documentary photography style, earthy tones",
      "landscape_4_3"
    ),
  },
  {
    no: "肆",
    name: "庭院整体设计",
    en: "Garden Design",
    tagline: "专属私院，量身造景",
    desc: "针对别墅庭院、私家小院、露台、楼顶花园、厂区庭院、门店户外空间，提供一对一整体庭院景观设计服务。摒弃模板化设计，结合户型格局、生活习惯、审美风格、预算标准，打造兼具颜值、实用性、私密性的专属庭院方案。",
    points: [
      "全场景涵盖：动线规划、花箱布局、绿植层次、休闲区、造景小品",
      "灯光氛围设计、防水排水系统规划",
      "提供全套设计效果图 + 施工图",
      "方案清晰、细节完善，落地效果1:1还原",
      "适配新中式禅意、现代简约、轻奢精致、自然田园、极简工业风",
    ],
    image: img(
      "A serene modern Chinese courtyard garden design with wooden deck, stone pathway, bamboo and moss, soft evening light, architectural visualization, wabi-sabi aesthetic, muted palette",
      "landscape_4_3"
    ),
  },
  {
    no: "伍",
    name: "庭院整装搭建施工",
    en: "Turnkey Build",
    tagline: "全案落地，拎包式庭院",
    desc: "承接全品类庭院整装搭建工程，从设计、材料采购、场地改造、基础施工、景观搭建、绿植栽种到整体验收，全程一站式落地，真正实现设计—施工—落地—养护闭环服务。",
    points: [
      "施工范围：地面铺装、花箱景观、绿植造景、休闲区、旧庭院翻新",
      "施工团队专业靠谱，工艺精细、用料扎实",
      "严格把控施工细节与工程质量",
      "完工即成型、无需二次整改",
      "小院微改造到全屋庭院整装均可定制，高性价比落地",
    ],
    image: img(
      "A completed residential courtyard renovation with wooden planters, stone paving, greenery and ambient lighting, golden hour, real estate photography, warm muted tones",
      "landscape_4_3"
    ),
  },
];

export type CaseItem = {
  name: string;
  type: string;
  material: string;
  style: string;
  image: string;
  tall?: boolean;
};

export const cases: CaseItem[] = [
  {
    name: "云栖·和庄私院",
    type: "别墅庭院整装",
    material: "防腐木 / 青石",
    style: "新中式禅意",
    tall: true,
    image: img(
      "A private villa courtyard with wooden planter boxes, stone pathway, bamboo grove, moss garden, soft diffused light, tranquil zen atmosphere, architectural photography, muted earthy palette",
      "portrait_4_3"
    ),
  },
  {
    name: "外滩源门店外摆",
    type: "商业花箱组团",
    material: "304不锈钢",
    style: "现代极简",
    image: img(
      "Modern stainless steel planter boxes with greenery outside a boutique storefront on a European style street, overcast soft light, urban landscape photography, cool muted tones",
      "landscape_4_3"
    ),
  },
  {
    name: "临港市政花箱组团",
    type: "道路景观",
    material: "铝合金",
    style: "市政简约",
    image: img(
      "Aluminum alloy planter boxes with seasonal flowers along a city road, clean municipal landscape, soft daylight, urban documentary photography, neutral tones",
      "landscape_4_3"
    ),
  },
  {
    name: "莫干山露台花园",
    type: "露台整装",
    material: "仿石 / 铁艺",
    style: "自然田园",
    tall: true,
    image: img(
      "A mountain villa terrace garden with stone-look planters, wrought iron railing, lavender and olive trees, golden hour light, travel photography, warm muted tones",
      "portrait_4_3"
    ),
  },
  {
    name: "徐汇·梧桐里庭院",
    type: "私院微改造",
    material: "防腐木",
    style: "复古田园",
    image: img(
      "A cozy backyard garden renovation with wooden barrel planters, climbing roses, vintage bench, dappled afternoon light, cottage garden style, warm earthy palette",
      "landscape_4_3"
    ),
  },
  {
    name: "前海·壹方汇外摆",
    type: "商业景观",
    material: "铝合金 / 灯光",
    style: "欧式轻奢",
    image: img(
      "Luxury commercial plaza outdoor seating with aluminum planters integrated with warm lighting, manicured topiary, evening ambiance, architectural photography, refined muted tones",
      "landscape_4_3"
    ),
  },
];

export type ProcessStep = {
  no: string;
  title: string;
  desc: string;
};

export const processSteps: ProcessStep[] = [
  { no: "01", title: "上门勘测", desc: "实地测量尺寸、记录采光与场地条件" },
  { no: "02", title: "需求沟通", desc: "了解生活习惯、审美偏好与预算标准" },
  { no: "03", title: "方案设计", desc: "结合户型与风格出具专属设计方案" },
  { no: "04", title: "效果图预览", desc: "提前预览落地效果，按需调整至满意" },
  { no: "05", title: "施工落地", desc: "标准化工艺施工，工期可控现场整洁" },
  { no: "06", title: "养护指导", desc: "交付后提供养护指引，售后有保障" },
];

export const stats = [
  { num: "10+", label: "年景观设计与施工经验" },
  { num: "300+", label: "庭院与花箱落地案例" },
  { num: "5", label: "类主流材质全工艺处理" },
  { num: "全国", label: "上门勘测与施工服务区域" },
];

export const navLinks = [
  { href: "#services", label: "业务总览" },
  { href: "#detail", label: "服务详述" },
  { href: "#cases", label: "案例作品" },
  { href: "#process", label: "设计流程" },
  { href: "#about", label: "关于我们" },
];
