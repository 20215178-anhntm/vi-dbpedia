# Kịch bản demo ViDBpedia (8–10 phút)

Thông điệp xuyên suốt cần để lại cho thầy: **ontology không chỉ để mô tả dữ liệu, mà để máy tự suy ra tri thức mới
và tự phát hiện lỗi.** Mỗi bước demo đều quay về thông điệp này.

---

## 0. Chuẩn bị (làm trước giờ demo 15 phút)

| Việc | Lệnh / thao tác | Kiểm tra |
|---|---|---|
| Bật endpoint + web | `cd vi-dbpedia` rồi `python src/serve.py` (để cửa sổ này chạy) | Hiện dòng `Web UI: http://127.0.0.1:5000/` |
| Mở sẵn 4 tab trình duyệt | ① `http://127.0.0.1:5000/` ② `http://127.0.0.1:5000/page/Trần_Nhân_Tông` ③ `http://127.0.0.1:5000/sparql` ④ `http://127.0.0.1:5000/ontology` | Cả 4 tab load được (dùng **127.0.0.1**, không dùng `localhost` vì trên Windows chậm 2 giây) |
| Mở Protégé | File → Open → `ontology/examples/protege_demo_tran.ttl` (file đã gộp ontology + dữ liệu mẫu nhà Trần, **không cần** import) | Thấy tab *Entities* có cây lớp |
| Mở 1 cửa sổ terminal thứ hai | `cd vi-dbpedia` | Gõ thử `python src/query.py --list` ra 18 câu hỏi |
| Mở file báo cáo | `docs/BAO_CAO.md` (preview Markdown trong VS Code để thấy sơ đồ pipeline) | |
| Kiểm tra Internet | Bước 4c (truy vấn liên hợp DBpedia) cần mạng | Nếu DBpedia sập → dùng phương án dự phòng ở cuối tài liệu |

---

## 1. Mở đầu — bài toán (1 phút)

**Màn hình:** `docs/BAO_CAO.md`, phần sơ đồ pipeline (mục 1).

**Nói:**
> “Đề bài yêu cầu xây DBpedia tiếng Việt. Wikipedia viết cho người đọc: hộp thông tin của Trần Nhân Tông ghi *cha là Trần Thánh Tông*,
> nhưng máy không hiểu. Nhóm em chuyển 44 nghìn bài Wikipedia tiếng Việt về lịch sử – địa lý – danh nhân thành RDF theo một ontology
> do nhóm em thiết kế, cho máy suy diễn, liên kết sang DBpedia tiếng Anh và cung cấp SPARQL endpoint.
> Pipeline đi đúng 5 bước của đề: ontology → thu thập → chuyển đổi 4 sao → liên kết 5 sao → endpoint.”

**Nêu 3 con số:** 44.003 bài · 1,5 triệu triple trích xuất · **2,6 triệu triple do suy diễn sinh ra**.

---

## 2. Ontology trong Protégé — trọng tâm (3 phút)

### 2a. Cây lớp (30 giây)
**Thao tác:** tab *Entities → Classes*, mở rộng `Agent → Person`.

**Nói:**
> “Ontology có 48 lớp, 115 thuộc tính, căn chỉnh với DBpedia, FOAF, schema.org.
> Điểm đặc biệt: các lớp như *Monarch*, *RoyalChild*, *MilitaryCommander* **không được gán tay** — chúng là lớp định nghĩa.”

### 2b. Một lớp định nghĩa (45 giây)
**Thao tác:** bấm vào `Monarch` → khung *Description* hiện *Equivalent To*: `Person and (hasReign some Reign)`.

**Nói:**
> “Vua là người có ít nhất một thời kỳ trị vì. Nhóm em không mô hình *vua* là lớp con cố định của *người* vì theo OntoClean,
> *vua* là vai trò không cứng — một người không phải lúc nào cũng là vua. Thời kỳ trị vì là một **quan hệ n-ngôi**
> (người, tước hiệu, triều đại, năm bắt đầu, năm kết thúc) nên được tách thành nút `Reign`.”

Bấm tiếp `MonarchWarrior` → *Equivalent To*: `Monarch and MilitaryCommander`.
> “Vua trực tiếp cầm quân là giao của hai lớp định nghĩa.”

### 2c. Property chain (30 giây)
**Thao tác:** tab *Object properties* → `hasPaternalGrandfather` → *SuperProperty Of (Chain)*: `hasFather o hasFather`.
Bấm tiếp `memberOfDynasty` → chain `hasFather o memberOfDynasty`.
> “Ông nội là cha của cha. Thuộc hoàng tộc theo dòng cha: con của một thành viên nhà Trần (qua người cha) cũng thuộc nhà Trần.”

### 2d. Chạy reasoner — khoảnh khắc quan trọng nhất (1 phút 15 giây)
**Thao tác:** menu *Reasoner → HermiT* → *Start reasoner*. Vào tab *Individuals*, chọn `Trần_Nhân_Tông`.

**Chỉ vào màn hình** — phần chữ vàng (inferred) trong *Types* và *Object property assertions*:

| Khai báo trong file (chỉ có) | HermiT suy ra |
|---|---|
| là `Person`, có cha Trần Thánh Tông, có một `Reign`, sinh ở Thăng Long, chỉ huy trận Bạch Đằng 1288 | `VietnameseMonarch`, `MonarchWarrior`, `RoyalChild` |
| | `hasPaternalGrandfather` Trần Thái Tông |
| | `memberOfDynasty` Nhà Trần |
| | `participatedIn` Kháng chiến chống Nguyên lần 3 (vì trận Bạch Đằng là một phần của cuộc chiến) |
| | `bornWithin` Đại Việt |

**Nói:**
> “File mẫu chỉ ghi dữ kiện gốc. Toàn bộ phần màu vàng là reasoner suy ra từ tiên đề. Không có lớp nào bị rỗng (unsatisfiable),
> nghĩa là ontology nhất quán.”

*(Nếu Protégé có vấn đề: chạy `python tests/test_hermit.py` trong terminal — cùng nội dung, in ra `ALL PASSED`.)*

---

## 3. Dữ liệu thật trên web (1 phút 30 giây)

**Màn hình:** tab ② `page/Trần_Nhân_Tông`.

**Nói & chỉ:**
1. Dòng chú thích nhãn màu: *data* (xanh) = trích từ Wikipedia, *inferred* (vàng) = suy diễn, *links* (xanh lá) = liên kết ngoài.
   > “Trên dữ liệu thật, Trần Nhân Tông có **53 triple trích xuất nhưng 158 triple do suy diễn** — gấp 3 lần.”
2. Kéo xuống `rdf:type`: các lớp `VietnameseMonarch`, `MonarchWarrior`… đều nhãn **inferred**.
3. Dòng `owl:sameAs` → `dbr:Trần_Nhân_Tông` (DBpedia tiếng Anh) và `wd:Q72083` (Wikidata) — **5 sao**.
4. Dòng `vidbo:hasReign` → bấm vào nút `Reign_0`: tước hiệu *Hoàng đế Đại Việt*, 1278–1293, `durationYears` 15 (luật suy ra).

**Chứng minh URI dereference được (4 sao)** — trong terminal:
```bash
python -c "import requests;r=requests.get('http://127.0.0.1:5000/resource/Trần_Nhân_Tông',headers={'Accept':'text/turtle'});print(r.status_code);print(r.text[:700])"
```
> “Cùng một URI: trình duyệt nhận HTML, máy nhận Turtle — đó là nguyên tắc Linked Data (content negotiation, 303 redirect).”

---

## 4. SPARQL — trả lời câu hỏi mà Wikipedia không ghi (2 phút 30 giây)

Dùng tab ③ (chọn trong ô *Câu hỏi mẫu* rồi bấm *Chạy*) hoặc terminal `python src/query.py --cq N`.

### 4a. CQ2 — ông nội (20 giây)
`python src/query.py --cq 2` → Trần Thái Tông, cột `?g` = `.../graph/inferred`.
> “Cột graph cho thấy câu trả lời nằm trong graph suy diễn — Wikipedia không có câu ‘ông nội của Trần Nhân Tông là…’.”

### 4b. CQ5 — ai tham gia kháng chiến chống Nguyên Mông (40 giây)
`python src/query.py --cq 5` → Trần Hưng Đạo, Trần Quang Khải, Trần Nhật Duật, Trần Nhân Tông, Thoát Hoan, Toa Đô…
> “Infobox chỉ ghi *ai chỉ huy trận nào*. Chuỗi `participatedIn ∘ partOfConflict` cộng tính bắc cầu của `partOfConflict`
> đưa người chỉ huy một trận lên thành người tham gia cả cuộc chiến bao ngoài.”

### 4c. CQ9 — các tỉnh sau sáp nhập 2025 (30 giây)
`python src/query.py --cq 9` → Thanh Hóa 166 xã/phường, Ninh Bình mật độ 1.119 người/km²…
> “Cấp hành chính được định nghĩa bằng `hasValue` trên `adminLevel`, mật độ dân số do luật R5 tính.
> Ontology cũng mô hình cải cách 2025: cấp huyện là `HistoricalAdministrativeUnit` (CQ16 liệt kê 65 tỉnh/thành có huyện bị giải thể).”

### 4d. CQ13 — truy vấn liên hợp sang DBpedia tiếng Anh (40 giây, cần Internet)
`python src/query.py --cq 13` → 9 vua nhà Lý kèm mô tả tiếng Anh lấy trực tiếp từ dbpedia.org.
> “Một câu SPARQL chạy trên cả hai bộ dữ liệu nhờ `owl:sameAs` — đó là giá trị của sao thứ năm.”

---

## 5. Ontology phát hiện lỗi (1 phút)

```bash
python src/query.py "SELECT ?label ?b ?d WHERE { vidbr:Anna_Freud rdfs:label ?label ; vidbo:birthYear ?b ; vidbo:deathYear ?d }"
```
→ sinh **1985**, mất 1982.
> “Wikipedia tiếng Việt ghi sai năm sinh của Anna Freud (đúng là 1895). Ràng buộc SHACL phát hiện ra.
> Tiên đề rời nhau `Person ⊥ Place` phát hiện 145 thực thể mâu thuẫn, ví dụ trường *cha* trỏ tới một quốc gia.
> Thậm chí trong lúc làm, tiên đề `Person ⊥ Tenure` đã phát hiện **lỗi trong chính chương trình của nhóm em** (17.841 vi phạm) —
> nhờ vậy nhóm em tìm ra một lỗi đọc file cấu hình.”

Có thể mở `data/rdf/consistency_report.json` để thầy xem.

---

## 6. Liên kết và kết luận (1 phút)

**Màn hình:** `linking/evaluation.json` hoặc mục 6 trong báo cáo.

> “Liên kết sang DBpedia có hai cách: 32.136 link từ interlanguage link, đã xác minh từng URI trên DBpedia;
> và một bộ so khớp giống Silk cho thực thể không có link, đánh giá trên 1.500 thực thể có đáp án: **precision 96,4%**.
> Nhóm em ưu tiên độ chính xác vì một `owl:sameAs` sai sẽ kéo toàn bộ thuộc tính của thực thể khác về.”

**Câu kết:**
> “Tóm lại: 5 yêu cầu của đề đều đáp ứng, và điểm nhóm em tập trung là ontology — 13 lớp định nghĩa, 10 property chain,
> giúp máy sinh ra 2,6 triệu triple mới và phát hiện lỗi dữ liệu. 18 câu hỏi năng lực đều trả lời được.”

---

## Phương án dự phòng

| Sự cố | Xử lý |
|---|---|
| Web/Fuseki không chạy | `python src/serve.py`. Nếu báo lỗi khoá TDB: tắt hết `java.exe` rồi chạy lại |
| Trang web chậm 2 giây | Đang dùng `localhost` → đổi sang `127.0.0.1` |
| DBpedia sập (CQ13 rỗng / lỗi) | Nói: “endpoint công cộng của DBpedia hay quá tải — nhóm em đã gặp khi làm, nên bộ liên kết có cache”; mở `docs/cq_results.md` mục CQ13 (kết quả đã lưu) |
| Protégé lỗi | `python tests/test_hermit.py` (HermiT chạy qua owlready2) |
| Không có Internet | Toàn bộ demo trừ CQ13 chạy offline |

---

## Câu hỏi thầy có thể hỏi — trả lời gợi ý

| Câu hỏi | Trả lời |
|---|---|
| Ontology có gì “phức tạp” so với RDFS? | RDFS chỉ có subClass, subProperty, domain, range. Nhóm em dùng OWL 2: lớp định nghĩa bằng restriction, giao/hợp, property chain, transitive, inverse, symmetric, functional, disjoint, hasKey, ràng buộc số lượng có điều kiện. RDFS không suy ra được *ông nội* hay *vua trực tiếp cầm quân*. |
| Vì sao không dùng owlrl hay reasoner của Jena trên dữ liệu thật? | owlrl thuần Python quá chậm với 1,5 triệu triple. Nhóm em viết bộ suy diễn tiến theo đúng các luật OWL 2 RL, đọc tiên đề trực tiếp từ ontology — 15 phút ra 2,6 triệu triple. Phần tableau (HermiT) dùng để kiểm tra tính nhất quán trên tập mẫu. |
| Open World Assumption ảnh hưởng thế nào? | Ràng buộc `MilitaryConflict ⊑ ≥2 combatant` không bao giờ sinh lỗi khi thiếu bên tham chiến — thiếu thông tin ≠ sai. Vì vậy nhóm em dùng thêm SHACL (giả định thế giới đóng) để kiểm tra dữ liệu. |
| Vì sao “anh chị em” phải dùng luật? | Chain `hasParent ∘ hasChild` sẽ làm mỗi người là anh chị em của chính mình; OWL không biểu diễn được x ≠ y. Luật SPARQL R1 có `FILTER(?x != ?y)`; kết quả sau đó lại được OWL dùng trong chain `uncleOrAunt = hasParent ∘ sibling`. |
| Làm sao biết hai URI là cùng một thực thể? | Interlanguage link (do cộng đồng Wikipedia nối) + bộ so khớp nhãn/kiểu/năm như Silk; có đánh giá precision/recall trên tập có đáp án. |
| Vì sao không khai báo `predecessor` là bắc cầu? | Nhóm em đã thử: sinh thêm 3,8 triệu triple vô nghĩa vì một người giữ nhiều chức vụ, tiền nhiệm của các chức khác nhau bị nối thành một chuỗi. Đây là bài học: tiên đề sai ngữ nghĩa → suy diễn sai hàng loạt. |
| Vì sao `xsd:date` không là `rdfs:range`? | `xsd:date`, `xsd:gYear` không thuộc OWL 2 datatype map, HermiT từ chối ontology. Nhóm em giữ kiểu dữ liệu giống DBpedia và kiểm tra bằng SHACL. |
