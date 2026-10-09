// ViDBpedia slide deck, in the form of the SoICT/HUST course-project template
// (Group5_Heterophily-Aware ... .pptx): white content slides with the red dot accent,
// a small red "Part n" line above a 29pt Arial title, red section dividers, SoICT logo and page number.
// Content slides show real artefacts of the project (wiki-text, Turtle, reasoner output, queries, errors)
// rather than decorative cards.
//   node build_deck.js   ->  ViDBpedia_slides.pptx
const pptxgen = require("pptxgenjs");
const path = require("path");
const { applyTheme } = require("./apply_theme.js");

const THEME = {
  name: "ViDBpedia HUST",
  headFontFace: "Arial",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "222222", lt1: "FFFFFF", dk2: "6B6B6B", lt2: "F7F8FA",
    accent1: "C02034", accent2: "8E1626", accent3: "FBE9EC", accent4: "E4E7EB", accent5: "9A9A9A", accent6: "2E7D46",
    hlink: "C02034", folHlink: "8E1626",
  },
};
const HEX = { red: "C02034", deep: "8E1626", dark: "222222", grey: "6B6B6B", card: "F7F8FA", border: "E4E7EB",
  rowAlt: "F4F4F4", sectionLabel: "F4C3CB", lightPink: "FCE4E8", term: "1F1F1F", termText: "E8E8E8", termOk: "9BD49B" };

const TITLE_DOTS = 45;
const A = (f) => path.join(__dirname, "assets", f);
const F = (f) => path.join(__dirname, "figs", f);
const HEAD = "+mj-lt";   // theme heading font (Arial)
const MONO = "Consolas";
const MATH = "Cambria Math";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 like the template
pres.title = "ViDBpedia: an inference-rich Vietnamese DBpedia";
pres.author = "Le Phu Tai, Nguyen Thi Mai Anh, Duong Hoang Hai, Le Van Luan";
pres.company = "SoICT, HUST";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

// speaker of each slide (docs/KICH_BAN_THUYET_TRINH.md); prefixed to the notes so Presenter View shows whose turn it is
const SPEAKERS = [[1, 5, "Hải"], [6, 12, "Mai Anh"], [13, 17, "Hải"], [18, 21, "Tài"], [22, 27, "Luận"]];
let slideNo = 0;
const addSlideRaw = pres.addSlide.bind(pres);
pres.addSlide = (opts) => {
  const s = addSlideRaw(opts), n = ++slideNo;
  const who = (SPEAKERS.find(([a, b]) => n >= a && n <= b) || [0, 0, "?"])[2];
  const addNotesRaw = s.addNotes.bind(s);
  s.addNotes = (t) => addNotesRaw(`[${who}]  ${t}`);
  return s;
};
const C = pres.SchemeColor;
const RED = C.accent1, DEEP = C.accent2, BORDER = C.accent4;
const DARK = C.text1, GREY = C.text2, CARD = C.background2, WHITE = C.background1;

// ------------------------------------------------------------------ layouts
const footer = [
  { image: { x: 0.55, y: 7.0, w: 1.0, h: 0.41, path: A("soict_logo.png"), altText: "SoICT logo" } },
];
const slideNumber = { x: 12.35, y: 7.02, w: 0.5, h: 0.32, fontFace: "Calibri", fontSize: 11, color: "9A9A9A", align: "right" };

pres.defineSlideMaster({
  title: "VIDB_TITLE",
  background: { color: "FFFFFF" },
  objects: [
    { image: { x: 10.7, y: -0.5, w: 3.2, h: 2.84, path: A("accent_dots.png"), altText: "decorative dots", transparency: TITLE_DOTS } },
    { image: { x: 0.6, y: 0.5, w: 3.5, h: 1.27, path: A("hust_logo.png"), altText: "Hanoi University of Science and Technology logo" } },
    { image: { x: 11.2, y: 6.55, w: 1.55, h: 0.63, path: A("soict_logo.png"), altText: "SoICT logo" } },
    ...footer,
  ],
  slideNumber,
});

pres.defineSlideMaster({
  title: "VIDB_CONTENT",
  background: { color: "FFFFFF" },
  objects: [
    { image: { x: 11.5, y: -0.42, w: 2.3, h: 2.04, path: A("accent_dots.png"), altText: "decorative dots", transparency: 62 } },
    ...footer,
    { placeholder: { options: { name: "kicker", type: "body", x: 0.62, y: 0.42, w: 11.0, h: 0.3, fontFace: "Calibri",
      fontSize: 13, bold: false, color: HEX.red, margin: 0, valign: "middle", align: "left" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.72, w: 11.2, h: 0.85, fontFace: "Arial",
      fontSize: 29, bold: true, color: HEX.dark, margin: 0, valign: "middle", align: "left" }, text: "" } },
  ],
  slideNumber,
});

pres.defineSlideMaster({
  title: "VIDB_SECTION",
  background: { path: A("section_bg.png") },
  objects: [
    { placeholder: { options: { name: "part", type: "body", x: 1.2, y: 2.5, w: 6.0, h: 0.5, fontFace: "Calibri",
      fontSize: 18, bold: true, color: HEX.sectionLabel, charSpacing: 3, margin: 0, valign: "middle", align: "left" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 1.2, y: 3.0, w: 9.4, h: 1.6, fontFace: "Arial",
      fontSize: 34, bold: true, color: "FFFFFF", margin: 0, valign: "top", align: "left" }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "VIDB_THANKS",
  background: { path: A("section_bg.png") },
  objects: [...footer],
  slideNumber,
});

// ------------------------------------------------------------------ helpers
let section = "", part = "";
function contentSlide(title, notes) {
  const s = pres.addSlide({ masterName: "VIDB_CONTENT", sectionTitle: section });
  s.addText(part, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function sectionSlide(label, title, kicker, notes) {
  section = title.replace("\n", " ");
  part = kicker;
  pres.addSection({ title: section });
  const s = pres.addSlide({ masterName: "VIDB_SECTION", sectionTitle: section });
  s.addText(label, { placeholder: "part" });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function box(s, x, y, w, h, opts = {}) {
  s.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: opts.fill || CARD }, line: { color: opts.line || BORDER, width: 0.75 }, objectName: opts.name || "box",
  });
}
function text(s, t, o) {
  s.addText(t, Object.assign({ isTextBox: true, margin: 0, valign: "top", fontSize: 15, color: DARK }, o));
}
function bullets(s, items, o) {
  const runs = items.map((it, i) => {
    const parts = Array.isArray(it) ? it : [{ text: it }];
    return parts.map((p, j) => ({
      text: p.text,
      options: Object.assign({ bullet: j === 0 ? { indent: 18 } : undefined, breakLine: j === parts.length - 1 && i < items.length - 1,
        paraSpaceAfter: 9 }, p.options || {}),
    }));
  }).flat();
  s.addText(runs, Object.assign({ isTextBox: true, margin: 0, valign: "top", fontSize: 16, color: DARK }, o));
}
// small grey label above a code block or table
function label(s, t, x, y, w) {
  text(s, t, { x, y, w, h: 0.32, fontSize: 13, color: GREY, valign: "middle" });
}
// source code / data, light background
function code(s, lines, x, y, w, h, size = 12) {
  box(s, x, y, w, h, { name: "code" });
  text(s, lines.join("\n"), { x: x + 0.18, y: y + 0.14, w: w - 0.3, h: h - 0.25, fontFace: MONO, fontSize: size, color: DARK });
}
// terminal output, dark background; lines starting with "$" are commands
function terminal(s, lines, x, y, w, h, size = 11.5) {
  box(s, x, y, w, h, { fill: HEX.term, line: HEX.term, name: "terminal" });
  const runs = lines.map((l, i) => ({ text: l, options: { color: l.startsWith("$") ? HEX.termText : HEX.termOk, breakLine: i < lines.length - 1 } }));
  text(s, runs, { x: x + 0.2, y: y + 0.14, w: w - 0.35, h: h - 0.25, fontFace: MONO, fontSize: size });
}
function table(s, header, rows, o) {
  const head = header.map((h) => ({ text: h, options: { bold: true, color: WHITE, fill: { color: HEX.red }, fontSize: o.fontSize || 13.5 } }));
  const body = rows.map((r, i) => r.map((c, j) => {
    const cell = typeof c === "object" ? c : { text: String(c) };
    return { text: cell.text, options: Object.assign({ fill: { color: i % 2 ? HEX.rowAlt : "FFFFFF" }, fontSize: o.fontSize || 13,
      color: j === 0 && o.firstRed !== false ? HEX.red : HEX.dark, bold: j === 0 && o.firstRed !== false }, cell.options || {}) };
  }));
  const rowH = o.rowH || 0.48;
  const opts = Object.assign({ fontFace: "Calibri", valign: "middle", margin: [0.04, 0.12, 0.04, 0.12],
    border: { type: "none" } }, o, { rowH: [Math.min(rowH, 0.52), ...rows.map(() => rowH)] });
  delete opts.firstRed;
  s.addTable([head, ...body], opts);
}
const math = (t) => ({ text: t, options: { fontFace: MATH, bold: false, color: HEX.dark } });

// ================================================================== 1. title
{
  const s = pres.addSlide({ masterName: "VIDB_TITLE" });
  text(s, "Semantic Web course project, topic 2", { x: 0.62, y: 2.35, w: 11.0, h: 0.35, fontSize: 15, color: RED, valign: "middle" });
  text(s, "ViDBpedia: An Inference-Rich\nVietnamese DBpedia", { x: 0.6, y: 2.75, w: 11.8, h: 1.7, fontFace: HEAD, fontSize: 42, bold: true, valign: "middle" });
  text(s, "from Wikipedia infoboxes to 5-star Linked Data", { x: 0.62, y: 4.4, w: 11.8, h: 0.7, fontFace: HEAD, fontSize: 26, bold: true, color: RED, valign: "middle" });
  text(s, "Le Phu Tai (20252268M)   ·   Nguyen Thi Mai Anh (20252265M)\nDuong Hoang Hai (20252273M)   ·   Le Van Luan (20252572M)",
    { x: 0.62, y: 5.25, w: 9.5, h: 0.8, fontSize: 15, lineSpacingMultiple: 1.15 });
  text(s, "School of Information and Communication Technology  ·  HUST", { x: 0.62, y: 6.45, w: 10.0, h: 0.35, fontSize: 12.5, italic: true, color: GREY });
  s.addNotes("Chào thầy và các bạn. Nhóm em gồm Hải, Mai Anh, Tài và Luận, trình bày đề tài 2: xây dựng DBpedia tiếng Việt. Phần nhóm em đầu tư nhiều nhất là ontology, để máy tự suy ra được những điều Wikipedia không viết.");
}

// ================================================================== 2. outline
{
  const s = contentSlide("Outline", "Bài gồm 5 phần, đi theo đúng 5 yêu cầu của đề.");
  const parts = [
    ["Introduction", "motivation and requirements"],
    ["Ontology design", "competency questions, classes, property axioms"],
    ["Extraction and reasoning", "pipeline, infobox extraction, reasoning, data quality"],
    ["Linking and endpoint", "links to DBpedia, SPARQL endpoint, 5-star data"],
    ["Evaluation and conclusion", "competency questions, lessons learned, future work"],
  ];
  parts.forEach(([t, sub], i) => {
    const y = 1.75 + i * 0.98;
    text(s, String(i + 1).padStart(2, "0"), { x: 0.9, y, w: 1.0, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: RED, valign: "middle" });
    text(s, t, { x: 2.05, y: y + 0.02, w: 8.2, h: 0.44, fontFace: HEAD, fontSize: 18, bold: true, valign: "middle" });
    text(s, sub, { x: 2.05, y: y + 0.44, w: 8.2, h: 0.3, fontSize: 13.5, color: GREY });
  });
}

// ================================================================== PART 01
sectionSlide("PART 01", "Introduction", "Part 1 · Introduction", "Phần 1: bài toán.");

{
  const s = contentSlide("Motivation",
    "Wikipedia tiếng Việt có 1,6 triệu bài nhưng dữ kiện nằm trong infobox dạng wiki-text, máy không hỏi được. DBpedia tiếng Anh lại có rất ít về triều đại, quan lại, trận đánh của Việt Nam, và không có gì về đợt sáp nhập tỉnh 2025. Bảng bên phải là ba câu hỏi mà không bài nào trả lời trực tiếp: muốn trả lời phải ghép thông tin từ nhiều bài. Mục tiêu của nhóm là để máy tự ghép được.");
  bullets(s, [
    "Vietnamese Wikipedia has 1.6 million articles. Its facts sit in infoboxes written as wiki-text, so a program cannot query them.",
    "English DBpedia covers few Vietnamese dynasties, mandarins and battles, and nothing about the 2025 merger of provinces.",
    "Many answers are not written in any article. They have to be put together from several pages.",
  ], { x: 0.7, y: 1.85, w: 5.3, h: 3.6, fontSize: 16.5 });
  table(s, ["Question", "Where the answer is"], [
    ["Who is Trần Nhân Tông’s paternal grandfather?", "his father’s article, then that article’s “cha” field"],
    ["Who was born in today’s Nghệ An?", "birthplaces are communes or districts, many renamed or merged in 2025"],
    ["Who took part in the Mongol–Đại Việt war?", "each battle’s infobox lists its own commanders"],
  ], { x: 6.35, y: 1.85, w: 6.3, colW: [3.0, 3.3], fontSize: 14, rowH: 0.9, firstRed: false });
  text(s, "Our goal: an ontology that lets the machine answer such questions by itself.",
    { x: 0.7, y: 5.75, w: 11.95, h: 0.45, fontSize: 17, bold: true, valign: "middle" });
}

{
  const s = contentSlide("Requirements",
    "Đây là cách nhóm đáp ứng từng yêu cầu của đề, kèm quy mô. Thầy nhấn mạnh yêu cầu 1: ontology phải suy diễn ra được nhiều hơn những gì trích xuất. Con số cuối cùng trả lời điều đó: 1,51 triệu triple trích xuất, suy diễn thêm 2,64 triệu.");
  table(s, ["Requirement", "What we built", "Size"], [
    ["1. Define an ontology", "vidbo in OWL 2 DL, SHACL shapes, 6 SPARQL rules", "48 classes, 115 properties"],
    ["2. Collect Vietnamese Wikipedia articles", "read the official dump; keep articles by infobox and category", "44,003 articles"],
    ["3. Transform into 4-star data", "YAML infobox mappings, Vietnamese value parsers, resolvable URIs", "1.51M triples"],
    ["4. Link to English DBpedia", "interlanguage links checked on dbpedia.org, plus a Silk-style matcher", "32,465 links"],
    ["5. SPARQL endpoint / terminal", "Apache Jena Fuseki, web pages, command-line client", "18 test queries"],
  ], { x: 0.7, y: 1.8, w: 11.95, colW: [3.75, 5.6, 2.6], fontSize: 14.5, rowH: 0.62 });
  text(s, "The lecturer asked for an ontology that infers more than was extracted: reasoning adds 2.64M triples to the 1.51M extracted ones.",
    { x: 0.7, y: 5.75, w: 11.95, h: 0.6, fontSize: 15, color: GREY });
}

// ================================================================== PART 02
sectionSlide("PART 02", "Ontology\ndesign", "Part 2 · Ontology design",
  "(Hải chuyển lượt: “Phần quan trọng nhất là ontology, xin mời Mai Anh.”) Phần 2: thiết kế ontology vidbo.");

{
  const s = contentSlide("Competency questions",
    "Nhóm làm theo Grüninger & Fox như trên lớp: viết 18 câu hỏi năng lực trước, mỗi câu thành một truy vấn SPARQL, rồi thêm tiên đề đến khi cả 18 câu đều có kết quả. Bảng là bốn ví dụ: mỗi câu hỏi kéo theo một loại tiên đề khác nhau.");
  text(s, "We wrote 18 competency questions first. Each became a SPARQL query, and we added axioms until all 18 returned answers. Four examples:",
    { x: 0.7, y: 1.75, w: 11.95, h: 0.7, fontSize: 16 });
  table(s, ["Competency question", "What the ontology needs", "Axiom"], [
    ["CQ2  Paternal grandfather of Trần Nhân Tông", "a two-step family relation", math("hasPaternalGrandfather ≡ hasFather ∘ hasFather")],
    ["CQ4  Monarchs who commanded battles", "“monarch” and “commander” as classes the reasoner fills", math("MonarchWarrior ≡ Monarch ⊓ MilitaryCommander")],
    ["CQ8  People born in today’s Nghệ An", "a birthplace rolled up to its province", math("bornWithin ∘ locatedIn ⊑ bornWithin")],
    ["CQ9  Provinces after the 2025 merger", "the administrative level as a value", math("FirstLevelUnit ≡ AdminUnit ⊓ ∋adminLevel.{1}")],
  ], { x: 0.7, y: 2.6, w: 11.95, colW: [3.85, 3.3, 4.8], fontSize: 14, rowH: 0.72 });
}

{
  const s = contentSlide("Class hierarchy",
    "Năm lớp gốc Agent, Place, Event, Work, Tenure, ánh xạ sang DBpedia, FOAF, schema.org. Lớp chữ đỏ là lớp định nghĩa: không ai gán tay, reasoner tự xếp thực thể vào. Dòng dưới cùng là các tiên đề rời nhau, dùng để phát hiện lỗi dữ liệu.");
  s.addImage({ path: F("fig_hierarchy.png"), x: 1.6, y: 1.6, w: 10.1, h: 4.74, altText: "Class hierarchy of the vidbo ontology" });
  text(s, "48 classes under five roots; the 13 in red are defined classes, filled by the reasoner.",
    { x: 0.7, y: 6.42, w: 11.95, h: 0.4, fontSize: 15, color: GREY, align: "center" });
}

{
  const s = contentSlide("Defined classes",
    "Theo OntoClean, vua, tướng, quan là vai trò một người giữ trong một thời gian, không phải bản chất. Vì vậy nhóm không gán lớp Monarch, mà định nghĩa: người có ít nhất một thời kỳ trị vì. Cột phải là số thực thể reasoner tự xếp vào lớp trên dữ liệu thật.");
  text(s, "Monarch, general and mandarin are roles a person holds for a time (OntoClean), so we define them instead of asserting them.",
    { x: 0.7, y: 1.72, w: 11.95, h: 0.5, fontSize: 16 });
  const dl = { fontFace: MATH, color: HEX.dark, bold: false };
  table(s, ["Class", "Definition", "Members found"], [
    ["Monarch", { text: "Person ⊓ ∃hasReign.Reign", options: dl }, "3,981"],
    ["VietnameseMonarch", { text: "Monarch ⊓ ∃memberOfDynasty.VietnameseDynasty", options: dl }, "169"],
    ["RoyalChild", { text: "Person ⊓ ∃hasParent.Monarch", options: dl }, "6,160"],
    ["MilitaryCommander", { text: "Person ⊓ ∃commanded.MilitaryConflict", options: dl }, "10,257"],
    ["MonarchWarrior", { text: "Monarch ⊓ MilitaryCommander", options: dl }, "755"],
    ["RoyalCourtOfficial", { text: "OfficeHolder ⊓ ∃servedUnder.Monarch", options: dl }, "204"],
    ["ThirdLevelUnit", { text: "AdministrativeUnit ⊓ ∋adminLevel.{3}", options: dl }, "3,328"],
  ], { x: 0.7, y: 2.4, w: 11.95, colW: [3.0, 6.75, 2.2], fontSize: 14, rowH: 0.5 });
}

{
  const s = contentSlide("Property axioms",
    "Các tiên đề thuộc tính tạo ra quan hệ mới. Cột giữa là ví dụ thật trên dữ liệu. Ví dụ dòng 4: infobox trận Bạch Đằng 1288 chỉ ghi Trần Nhân Tông chỉ huy trận đó; nhờ chain, máy suy ra ông tham gia cả cuộc kháng chiến chống Nguyên Mông. Dòng dưới là quy mô trên toàn bộ dữ liệu.");
  table(s, ["Axiom", "Example on our data"], [
    [math("hasPaternalGrandfather ≡ hasFather ∘ hasFather"), "Trần Nhân Tông → Trần Thái Tông"],
    [math("memberOfDynasty ⊒ hasFather ∘ memberOfDynasty"), "Trần Anh Tông → Nhà Trần (his father is a Trần)"],
    [math("bornWithin ∘ locatedIn ⊑ bornWithin,  locatedIn transitive"), "born in a commune → born within its district and province"],
    [math("participatedIn ∘ partOfConflict ⊑ participatedIn"), "commanded Bạch Đằng 1288 → took part in the Mongol–Đại Việt war"],
    [math("uncleOrAunt ≡ hasParent ∘ sibling"), "Trần Nhân Tông → Trần Quang Khải (sibling comes from rule R1)"],
    [math("hasAncestor transitive,  hasParent ⊑ hasAncestor"), "whole royal family trees"],
  ], { x: 0.7, y: 1.8, w: 11.95, colW: [6.2, 5.75], fontSize: 14, rowH: 0.56 });
  text(s, "On the full data: 618k ancestor links, 69k bornWithin links, 36.7k participations in enclosing wars.",
    { x: 0.7, y: 5.95, w: 11.95, h: 0.45, fontSize: 15, color: GREY });
}

{
  const s = contentSlide("Reigns and the 2025 reform",
    "Bên trái: một lần trị vì có nhiều thành phần (người, tước hiệu, triều đại, ngày bắt đầu, ngày kết thúc) nên nhóm tách thành một nút Reign, theo mẫu quan hệ n-ngôi của W3C. Đoạn Turtle là dữ liệu thật. Bên phải: tri thức về cải cách hành chính 2025, cấp huyện bị bỏ nên thành đơn vị lịch sử.");
  text(s, "A reign is an n-ary relation", { x: 0.7, y: 1.75, w: 5.9, h: 0.45, fontFace: HEAD, fontSize: 18, bold: true, color: RED, valign: "middle" });
  text(s, "“Trần Nhân Tông reigned as Emperor of Đại Việt for the Trần dynasty from 1278 to 1293” links five things, so each reign is a node of its own:",
    { x: 0.7, y: 2.25, w: 5.9, h: 0.9, fontSize: 14.5, color: GREY });
  code(s, [
    "vidbr:Trần_Nhân_Tông__Reign_0 a vidbo:Reign ;",
    "    vidbo:title \"Hoàng đế Đại Việt\"@vi ;",
    "    vidbo:tenureDynasty vidbr:Nhà_Trần ;",
    "    vidbo:startDate \"1278-11-08\"^^xsd:date ;",
    "    vidbo:endDate   \"1293-04-16\"^^xsd:date .",
  ], 0.7, 3.25, 5.9, 1.55, 12.5);
  text(s, "Queens and crown princes get a RoyalTitleTenure instead. Before we separated the two, 925 queens were inferred to be monarchs.",
    { x: 0.7, y: 5.0, w: 5.9, h: 0.9, fontSize: 14.5 });
  text(s, "The 2025 reform", { x: 7.05, y: 1.75, w: 5.6, h: 0.45, fontFace: HEAD, fontSize: 18, bold: true, color: RED, valign: "middle" });
  bullets(s, [
    [{ text: "The level is a value: " }, { text: "FirstLevelUnit ≡ AdministrativeUnit ⊓ ∋adminLevel.{1}", options: { fontFace: MATH } }],
    "34 provinces after the merger; communes, wards and special zones are level 3.",
    [{ text: "Districts were abolished on 1 July 2025: " }, { text: "SecondLevelUnit ⊑ HistoricalAdministrativeUnit", options: { fontFace: MATH } }],
    "hasKey(adminCode) found 19 new communes that reuse an old commune’s code.",
  ], { x: 7.05, y: 2.3, w: 5.6, h: 3.8, fontSize: 14.5 });
}

{
  const s = contentSlide("Example: Trần Nhân Tông",
    "Màu xám là dữ kiện có trong infobox, màu đỏ là do ontology suy ra: ông nội, thuộc nhà Trần, tham gia cả cuộc kháng chiến, và bốn lớp. Khung đen là output thật khi chạy HermiT trên tập mẫu nhà Trần: đúng các suy diễn đó, không có lớp nào rỗng. Trên dữ liệu thật, ông có 53 triple trích xuất và 158 triple suy diễn.");
  s.addImage({ path: F("fig_inference.png"), x: 0.7, y: 1.6, w: 8.6, h: 3.7, altText: "Asserted and inferred facts about Trần Nhân Tông" });
  text(s, [
    { text: "Grey: from the infobox.", options: { breakLine: true } },
    { text: "Red dashed: inferred.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "On the full data he has 53 extracted triples and 158 inferred ones.", options: {} },
  ], { x: 9.7, y: 1.9, w: 2.95, h: 3.0, fontSize: 15 });
  terminal(s, [
    "$ python tests/test_hermit.py      # HermiT on a sample of the Trần dynasty",
    "OK  Tran_Nhan_Tong: ['MonarchWarrior', 'Person', 'RoyalChild', 'VietnameseMonarch']",
    "OK  Tran_Nhan_Tong hasPaternalGrandfather -> ['Tran_Thai_Tong']",
    "OK  Tran_Nhan_Tong participatedIn -> ['Chien_tranh_Nguyen_Mong-Dai_Viet_lan_3']",
    "unsatisfiable classes: []",
    "ALL PASSED",
  ], 0.7, 5.4, 11.95, 1.45, 11.5);
}

// ================================================================== PART 03
sectionSlide("PART 03", "Extraction &\nreasoning", "Part 3 · Extraction and reasoning",
  "(Mai Anh chuyển lượt: “Ontology cần dữ liệu, mời Hải trình bày cách nhóm lấy dữ liệu và suy diễn.”) Phần 3: trích xuất và suy diễn.");

{
  const s = contentSlide("System pipeline",
    "Pipeline đi giống DBpedia Extraction Framework: dump, lọc bài, ánh xạ infobox, suy diễn, liên kết, nạp vào Fuseki. Ontology được dùng ở hai chỗ: khi trích xuất (kiểm tra kiểu của đối tượng) và khi suy diễn. Cả pipeline chạy lại bằng một lệnh, khoảng 1,5 giờ trên laptop.");
  s.addImage({ path: F("fig_pipeline.png"), x: 0.75, y: 1.8, w: 11.8, h: 4.3, altText: "Pipeline architecture" });
  text(s, "One command rebuilds everything: python run_pipeline.py (about 1.5 hours on a laptop).",
    { x: 0.7, y: 6.35, w: 11.95, h: 0.4, fontSize: 14, color: GREY, align: "center" });
}

{
  const s = contentSlide("Infobox extraction",
    "Bên trái là wiki-text thật của infobox Trần Nhân Tông trong bản dump, bên phải là Turtle mà extract.py sinh ra (rút gọn). Chú ý: ngày “8 tháng 11 năm 1278” thành xsd:date, trường “tại vị” thành một nút Reign. Nhóm dùng dump chứ không gọi API vì API chỉ cho khoảng 50 trang mỗi phút.");
  label(s, "Wiki-text in the dump (excerpt)", 0.7, 1.7, 5.6);
  code(s, [
    "{{Thông tin nhân vật hoàng gia",
    "| tên        = Trần Nhân Tông",
    "| chức vị    = [[Nhà Trần|Hoàng đế Đại Việt]]",
    "| tại vị     = [[8 tháng 11]] năm [[1278]] –",
    "               [[16 tháng 4]] năm [[1293]]",
    "| tiền nhiệm = [[Trần Thánh Tông]]",
    "| cha        = [[Trần Thánh Tông]]",
    "| sinh       = {{birth date|1258|12|7|df=y}}",
    "| nơi sinh   = [[Thăng Long]]",
    "  ...",
  ], 0.7, 2.05, 5.6, 2.8, 13);
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 6.45, y: 3.2, w: 0.45, h: 0.5, fill: { color: RED }, line: { color: RED }, objectName: "arrow" });
  label(s, "Turtle written by extract.py (excerpt)", 7.05, 1.7, 5.6);
  code(s, [
    "vidbr:Trần_Nhân_Tông",
    "  vidbo:hasFather   vidbr:Trần_Thánh_Tông ;",
    "  vidbo:predecessor vidbr:Trần_Thánh_Tông ;",
    "  vidbo:birthDate   \"1258-12-07\"^^xsd:date ;",
    "  vidbo:birthPlace  vidbr:Thăng_Long ;",
    "  vidbo:hasReign    vidbr:Trần_Nhân_Tông__Reign_0 .",
    "",
    "vidbr:Trần_Nhân_Tông__Reign_0 a vidbo:Reign ;",
    "  vidbo:title \"Hoàng đế Đại Việt\"@vi ;",
    "  vidbo:startDate \"1278-11-08\"^^xsd:date .",
  ], 7.05, 2.05, 5.6, 2.8, 13);
  text(s, "The mappings are one YAML file (11 infobox groups, 100+ name variants). Parsers read Vietnamese dates, BCE years (“257 TCN”) and numbers (“4.412.264”), with 16 unit tests. In total: 44,003 articles, 1.51M triples.",
    { x: 0.7, y: 5.2, w: 11.95, h: 0.8, fontSize: 15.5 });
}

{
  const s = contentSlide("Reasoning",
    "Các reasoner Python có sẵn quá chậm với 1,5 triệu triple, nên nhóm viết bộ suy diễn tiến theo luật OWL 2 RL. Nó đọc tiên đề từ file ontology, nên sửa ontology là kết quả đổi theo, không phải sửa code. Biểu đồ: phần lớn là bắc cầu, nhưng phần có giá trị nhất là xếp lớp và property chain.");
  bullets(s, [
    "We wrote a forward-chaining reasoner for the OWL 2 RL rules. It reads the axioms from vidbo.ttl, so changing the ontology changes the result without touching the code.",
    "It reaches a fix-point after 26 rounds (about 15 minutes) with 2.64M inferred triples.",
    "Six SPARQL rules add what OWL cannot express: siblings (x ≠ y), age at death, reign length, population density, reigns that overlap a war.",
    "HermiT checks the ontology itself for consistency.",
  ], { x: 0.7, y: 1.8, w: 5.6, h: 4.6, fontSize: 15.5 });
  const m = require("./facts.json").inferred_by_mechanism;
  const order = [["inverse_subproperty", "Inverse / sub-property"], ["rule", "SPARQL rules"], ["chain", "Property chains"],
    ["class", "Class membership"], ["alignment", "Alignment (dbo, FOAF)"], ["transitive", "Transitive closure"]];
  s.addChart(pres.charts.BAR, [{ name: "inferred (k)", labels: order.map((o) => o[1]), values: order.map((o) => Math.round(m[o[0]] / 1000)) }], {
    x: 6.55, y: 1.7, w: 6.15, h: 4.7, barDir: "bar", chartColors: [HEX.red],
    showTitle: true, title: "Inferred triples by mechanism (thousands)", titleFontSize: 13, titleColor: HEX.dark, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: HEX.dark, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "#,##0",
    catAxisLabelColor: HEX.grey, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 45,
  });
}

{
  const s = contentSlide("Data quality",
    "Tiên đề không chỉ suy diễn mà còn bắt lỗi. Các dòng là lỗi thật trong Wikipedia tiếng Việt, ví dụ Anna Freud ghi sinh 1985, mất 1982. Dòng cuối là lỗi của chính nhóm: tiên đề Person rời Tenure báo 17.841 vi phạm, lần ra thì do YAML đọc khóa “on:” thành giá trị true.");
  table(s, ["Check", "Found", "Example"], [
    ["Range check at extraction", "536", "predecessor of Lý Thái Tổ = Nhà Đinh (a dynasty, not a person)"],
    ["Disjoint classes", "145", "a “father” field linking to a country (Person ⊥ Place)"],
    ["Cycles of transitive properties", "857", "Shakespeare and Henry James influencing each other"],
    ["Asymmetric hasParent", "6", "father and son swapped (Jesse Root Grant, Ulysses S. Grant)"],
    ["Functional birthDate", "6", "two birth years for Alexandre de Rhodes (1591, 1593)"],
    ["hasKey(adminCode)", "19", "2025 communes reusing a dissolved commune’s code"],
    ["SHACL (closed world)", "104", "Anna Freud: born 1985, died 1982 (should be 1895)"],
    ["Person ⊥ Tenure", "17,841", { text: "our own bug: YAML read the mapping key on: as true", options: { bold: true } }],
  ], { x: 0.7, y: 1.75, w: 11.95, colW: [3.4, 1.15, 7.4], fontSize: 14, rowH: 0.52 });
}

// ================================================================== PART 04
sectionSlide("PART 04", "Linking &\nendpoint", "Part 4 · Linking and endpoint",
  "(Hải chuyển lượt: “Dữ liệu đã có và đã suy diễn; bước tiếp theo là nối nó với DBpedia tiếng Anh, mời Tài.”) Phần 4: liên kết và endpoint.");

{
  const s = contentSlide("Linking to DBpedia",
    "Giai đoạn 1 dùng liên kết liên ngôn ngữ của Wikipedia, nhưng nhóm kiểm tra từng URI trên DBpedia vì có bài tiếng Anh mới hơn bản DBpedia. Giai đoạn 2 cho thực thể không có liên kết: so khớp nhãn, kiểu và năm giống Silk. Đánh giá trên 1.500 cặp đã biết đáp án: độ chính xác 96,4%, độ phủ 48,5%. Bảng dưới là hai lỗi thật của bộ so khớp; nhóm cố ý ưu tiên độ chính xác vì một owl:sameAs sai sẽ kéo theo mọi dữ kiện của thực thể khác.");
  s.addChart(pres.charts.BAR, [{ name: "linked (%)", labels: ["Person", "Admin. unit", "Conflict", "Monarch", "Writer", "State"], values: [38, 35, 53, 84, 69, 88] }], {
    x: 0.6, y: 1.65, w: 6.4, h: 3.55, barDir: "col", chartColors: [HEX.red],
    showTitle: true, title: "Entities linked to DBpedia, by class (%)", titleFontSize: 13, titleColor: HEX.dark, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: HEX.dark, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.grey, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
    valAxisHidden: true, valAxisMaxVal: 100, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 55,
  });
  bullets(s, [
    "Stage 1: 33,278 interlanguage links, each checked on dbpedia.org; 32,136 kept.",
    "Stage 2: a Silk-style matcher (label, type, year) for 10,930 entities without a link; 329 accepted.",
  ], { x: 0.7, y: 5.35, w: 6.3, h: 1.3, fontSize: 14.5 });
  label(s, "Matcher on 1,500 pairs with a known answer", 7.4, 1.75, 5.25);
  table(s, ["Precision", "Recall", "F1"], [["96.4%", "48.5%", "0.65"]],
    { x: 7.4, y: 2.1, w: 5.25, colW: [1.75, 1.75, 1.75], fontSize: 15, rowH: 0.48, firstRed: false });
  label(s, "Two of its 27 wrong matches", 7.4, 3.4, 5.25);
  table(s, ["Our entity", "Matched", "Correct"], [
    ["Trà Cú (huyện)", "dbr:Trà_Cú", "dbr:Trà_Cú_district"],
    ["Mannert L. Abele", "dbr:Mannert_L._Abele", "dbr:USS_Mannert_L._Abele"],
  ], { x: 7.4, y: 3.75, w: 5.25, colW: [1.4, 1.75, 2.1], fontSize: 11.5, rowH: 0.44, firstRed: false });
  text(s, "We keep precision high on purpose: a wrong owl:sameAs imports every fact of the other entity.",
    { x: 7.4, y: 5.35, w: 5.25, h: 0.9, fontSize: 14.5 });
}

{
  const s = contentSlide("Endpoint and interfaces",
    "Dữ liệu nằm trong Fuseki với bốn named graph: ontology, dữ liệu, suy diễn, liên kết. Trang tài nguyên gắn nhãn cho từng dòng: dữ liệu trích xuất, suy diễn hay liên kết. Cùng một URI, trình duyệt nhận HTML còn chương trình nhận Turtle: đó là nguyên tắc Linked Data. Ngoài web còn có công cụ dòng lệnh.");
  [["web_page_crop.png", "Resource page of Trần Nhân Tông, with data / inferred / links badges"], ["web_sparql_crop.png", "SPARQL editor answering CQ5 in 105 ms"]].forEach(([f, cap], i) => {
    const x = 0.7 + i * 6.1;
    box(s, x, 1.75, 5.85, 4.15);
    s.addImage({ path: F(f), x: x + 0.12, y: 1.87, w: 5.61, h: 3.75, altText: cap });
    text(s, cap, { x, y: 6.0, w: 5.85, h: 0.35, fontSize: 13, color: GREY, align: "center" });
  });
  text(s, "The same URI returns HTML to a browser and Turtle, RDF/XML or JSON-LD to a program (HTTP 303). Terminal: python src/query.py --cq 5",
    { x: 0.7, y: 6.45, w: 11.95, h: 0.4, fontSize: 13.5, align: "center" });
}

{
  const s = contentSlide("5-star Linked Data",
    "Đối chiếu thang 5 sao của Tim Berners-Lee. Đề yêu cầu 4 sao cho dữ liệu và liên kết DBpedia, tức sao thứ 5. Sao thứ 4 nằm ở chỗ URI tra được; sao thứ 5 là owl:sameAs sang DBpedia và Wikidata.");
  table(s, ["Stars", "Requirement", "ViDBpedia"], [
    ["★", "on the web, open licence", "CC BY-SA 4.0, the same as Wikipedia"],
    ["★★", "machine-readable", "RDF instead of wiki-text"],
    ["★★★", "non-proprietary format", "Turtle, N-Triples, RDF/XML, JSON-LD"],
    ["★★★★", "URIs and W3C standards", "every resource URI resolves; SPARQL 1.1 endpoint"],
    ["★★★★★", "linked to other data", "32,465 links to DBpedia, 43,145 to Wikidata; ontology aligned with dbo, FOAF, schema.org"],
  ], { x: 0.7, y: 1.8, w: 11.95, colW: [1.6, 3.5, 6.85], fontSize: 15, rowH: 0.7 });
}

// ================================================================== PART 05
sectionSlide("PART 05", "Evaluation &\nconclusion", "Part 5 · Evaluation and conclusion",
  "(Tài chuyển lượt: “Vậy hệ thống trả lời được những câu hỏi ban đầu không? Mời Luận.”) Phần 5: đánh giá và kết luận.");

{
  const s = contentSlide("Evaluation",
    "Cả 18 câu hỏi năng lực đều có kết quả, thời gian trung vị 44 ms. Cột cơ chế cho thấy câu nào cũng cần ít nhất một suy diễn. Bên phải là truy vấn CQ8 thật: câu truy vấn chỉ hỏi theo tỉnh, vì reasoner đã đưa nơi sinh cấp xã, huyện lên tỉnh qua bornWithin; kết quả 264 người.");
  table(s, ["CQ", "Question", "Answered by", "Rows"], [
    ["CQ2", "Trần Nhân Tông’s paternal grandfather", "property chain", "1"],
    ["CQ4", "Monarchs who commanded battles", "defined classes", "89"],
    ["CQ5", "Participants of the Mongol–Đại Việt war", "chain + transitivity", "12"],
    ["CQ8", "People born in today’s Nghệ An", "chain + transitivity", "264"],
    ["CQ9", "Provinces after the 2025 merger", "hasValue + rule", "28"],
    ["CQ10", "Monarchs reigning while their dynasty was at war", "temporal rule", "166"],
    ["CQ13", "English descriptions from DBpedia", "owl:sameAs + SERVICE", "9"],
  ], { x: 0.7, y: 1.8, w: 7.05, colW: [0.75, 3.55, 2.05, 0.7], fontSize: 13, rowH: 0.5 });
  label(s, "CQ8 as it runs on the endpoint", 8.05, 1.75, 4.6);
  code(s, [
    "SELECT ?person ?label ?birthYear",
    "WHERE {",
    "  ?person vidbo:bornWithin",
    "            vidbr:Nghệ_An ;",
    "          rdfs:label ?label .",
    "  OPTIONAL {",
    "    ?person vidbo:birthYear ?birthYear }",
    "}",
    "ORDER BY ?birthYear",
  ], 8.05, 2.1, 4.6, 2.3, 11.5);
  text(s, "264 rows in 116 ms. The query only names the province; the reasoner has already rolled communes and districts up to it.",
    { x: 8.05, y: 4.55, w: 4.6, h: 0.9, fontSize: 13.5, color: GREY });
  text(s, "All 18 competency questions return answers; median time 44 ms on the local Fuseki endpoint.",
    { x: 0.7, y: 5.95, w: 7.05, h: 0.4, fontSize: 14.5 });
}

{
  const s = contentSlide("Lessons learned",
    "Đây là những lỗi thật trong quá trình làm. Điểm chung: phần lớn chỉ lộ ra sau khi chạy suy diễn, vì một tiên đề sai sẽ bị nhân lên hàng triệu lần. Bài học của nhóm: domain, range và tính bắc cầu không chỉ là mô tả, mà là luật suy diễn.");
  table(s, ["What we did", "What happened", "Fix"], [
    ["Declared predecessor as transitive", "3.8M meaningless triples: predecessors from different offices were chained together", "removed transitivity"],
    ["Gave posthumousName the domain Monarch", "925 queens and princes were inferred to be monarchs", "domain changed to Person"],
    ["Used the key on: in the YAML mapping", "YAML read it as true; 17,841 Person ⊥ Tenure violations", "renamed the key to attach:"],
    ["Read the province list of region infoboxes as locatedIn", "cycles: a border campaign ended up in a dozen provinces", "read it as contains; check for cycles"],
  ], { x: 0.7, y: 1.8, w: 11.95, colW: [3.7, 5.35, 2.9], fontSize: 14, rowH: 0.85, firstRed: false });
  text(s, "Most of these only became visible after reasoning: a wrong axiom is multiplied over the whole graph.",
    { x: 0.7, y: 6.05, w: 11.95, h: 0.45, fontSize: 15, color: GREY });
}

{
  const s = contentSlide("Conclusion",
    "Tóm lại ba ý: dữ liệu, ontology và chuẩn Linked Data. Bên phải là những gì nhóm chưa làm được và hướng tiếp theo.");
  text(s, "What we built", { x: 0.7, y: 1.75, w: 5.7, h: 0.45, fontFace: HEAD, fontSize: 18, bold: true, valign: "middle" });
  bullets(s, [
    "A Vietnamese DBpedia for history, geography and notable people: 44,003 articles, 1.51M extracted triples.",
    "An OWL 2 ontology whose axioms add 2.64M triples and answer all 18 competency questions.",
    "Five-star data: 32,465 links to DBpedia at 96.4% precision, served by a SPARQL endpoint.",
  ], { x: 0.7, y: 2.35, w: 5.7, h: 3.9, fontSize: 17 });
  s.addShape(pres.shapes.LINE, { x: 6.68, y: 1.85, w: 0, h: 4.3, line: { color: BORDER, width: 1 }, objectName: "divider" });
  text(s, "Limitations and next steps", { x: 6.95, y: 1.75, w: 5.7, h: 0.45, fontFace: HEAD, fontSize: 18, bold: true, valign: "middle" });
  bullets(s, [
    "Only 44k of 1.6M articles: extend the mappings to the whole Vietnamese Wikipedia.",
    "Lunar dates and era names are kept as text.",
    "Matcher recall is 48.5%: learn the linkage rule from the 1,500 known pairs.",
    "The namespace vi.dbpedia.example.org is a placeholder.",
  ], { x: 6.95, y: 2.35, w: 5.7, h: 3.9, fontSize: 17 });
}

{
  const s = contentSlide("Team contributions",
    "Phân công trong nhóm: mỗi người làm phần code tương ứng và trình bày phần slide đó. Bốn thành viên đóng góp như nhau.");
  table(s, ["Member", "Code / module", "Presents"], [
    ["Duong Hoang Hai", "Dump collection, infobox mappings, Vietnamese value parsers, OWL 2 RL reasoner, SPARQL rules, SHACL", "Part 1: Introduction\nPart 3: Extraction and reasoning"],
    ["Nguyen Thi Mai Anh", "Ontology vidbo, competency questions, HermiT verification, Protégé and web demo", "Part 2: Ontology design\nLive demo"],
    ["Le Phu Tai", "DBpedia / Wikidata linking, Silk-style matcher and gold-set evaluation, Fuseki endpoint, web UI, CLI", "Part 4: Linking and endpoint"],
    ["Le Van Luan", "Competency-question runner, evaluation of results and data quality", "Part 5: Evaluation and conclusion"],
  ], { x: 0.7, y: 1.85, w: 11.95, colW: [2.75, 5.9, 3.3], fontSize: 14, rowH: 0.85 });
  text(s, "All four members contributed equally.", { x: 0.7, y: 6.2, w: 11.95, h: 0.4, fontSize: 14, color: GREY });
}

// ================================================================== thanks
{
  const s = pres.addSlide({ masterName: "VIDB_THANKS", sectionTitle: section });
  text(s, "Thank you", { x: 1.2, y: 2.35, w: 10.5, h: 1.2, fontFace: HEAD, fontSize: 54, bold: true, color: WHITE, valign: "middle" });
  text(s, "Questions?", { x: 1.22, y: 3.7, w: 10.0, h: 0.7, fontFace: HEAD, fontSize: 24, color: HEX.lightPink, valign: "middle" });
  text(s, "ViDBpedia: An Inference-Rich Vietnamese DBpedia", { x: 1.22, y: 4.6, w: 10.5, h: 0.5, fontSize: 14, italic: true, color: HEX.sectionLabel, valign: "middle" });
  text(s, "SoICT, HUST  ·  Semantic Web course project", { x: 1.22, y: 5.05, w: 10.5, h: 0.4, fontSize: 13, color: HEX.sectionLabel, valign: "middle" });
  s.addNotes("Cảm ơn thầy và các bạn đã lắng nghe. Nếu thầy cho phép, nhóm em xin demo nhanh 5 phút, Mai Anh trình bày: trang Trần Nhân Tông (infobox → RDF), Protégé + HermiT, SPARQL CQ2, CQ5, CQ13.");
}

(async () => {
  const out = process.argv[2] || path.join(__dirname, "ViDBpedia_slides.pptx");   // optional output path
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("written", out, `(${slideNo} slides)`);
})();
