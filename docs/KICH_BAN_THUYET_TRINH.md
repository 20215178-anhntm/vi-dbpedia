# Kịch bản thuyết trình ViDBpedia — 4 thành viên (≈ 15 phút + 5 phút demo)

Dùng bộ [`presentation/ViDBpedia_slides.pptx`](../presentation/ViDBpedia_slides.pptx) (27 slide). Ghi chú của mỗi slide
đã có **tên người nói** ở đầu, nên khi bật *Presenter View* ai cũng biết đến lượt mình.

| Tài liệu | Dùng khi |
|---|---|
| File này | Thuyết trình trực tiếp trên lớp (4 người, slide + demo ngắn) |
| [`KICH_BAN_DEMO.md`](KICH_BAN_DEMO.md) | Thầy yêu cầu demo dài, chi tiết (8–10 phút); thao tác chi tiết từng bước |
| [`KICH_BAN_VIDEO.md`](KICH_BAN_VIDEO.md) | Quay video nộp bài (3–5 phút) |

## Cách nói cho tự nhiên

Mỗi slide có một thứ **thật** của dự án (wiki-text, Turtle, output của HermiT, câu SPARQL, lỗi đã gặp). Khi nói,
hãy **chỉ vào thứ đó** thay vì đọc chữ trên slide:

* Mỗi slide nói 1 ý chính; chữ trên slide là để người nghe nhìn, không phải để đọc to.
* Dùng ví dụ Trần Nhân Tông xuyên suốt: infobox (slide 15) → suy diễn (slide 12) → câu hỏi (slide 23).
* Kể lỗi của nhóm (slide 17, 24) bằng giọng kể chuyện: “lúc đầu nhóm em khai báo…, chạy xong thì thấy…, nên…”.

## Phân công (theo slide 26 *Team contributions*)

| Thành viên | Phần | Slide | Thời lượng |
|---|---|---|---|
| **Duong Hoang Hai** | Phần 1 Introduction + Phần 3 Extraction and reasoning | 1–5, 13–17 | ≈ 5:20 |
| **Nguyen Thi Mai Anh** | Phần 2 Ontology design + demo | 6–12, demo sau slide 27 | ≈ 4:40 + 5:00 demo |
| **Le Phu Tai** | Phần 4 Linking and endpoint | 18–21 | ≈ 2:30 |
| **Le Van Luan** | Phần 5 Evaluation and conclusion | 22–27 | ≈ 3:05 |

Thứ tự người nói: **Hải → Mai Anh → Hải → Tài → Luận → demo (Mai Anh) → hỏi đáp**.

**Nếu chỉ được 10–12 phút:** lướt qua slide 8, 11, 20, 21 (dừng 1–2 giây rồi chuyển) và bỏ demo; vẫn giữ nguyên người nói.

---

## Lời nói từng slide

Các câu dưới đây là gợi ý, không phải để học thuộc. Chỉ cần giữ **các con số in đậm** và **câu chuyển lượt**.

### Duong Hoang Hai — Phần 1: Introduction (slide 1–5, ≈ 2:15)

**Slide 1 — Tiêu đề (0:20).**
“Chào thầy và các bạn. Nhóm em gồm Hải, Mai Anh, Tài và Luận, trình bày đề tài 2: xây dựng DBpedia tiếng Việt.
Phần nhóm em đầu tư nhiều nhất là ontology, để máy tự suy ra được những điều Wikipedia không viết.”

**Slide 2 — Outline (0:15).** “Bài gồm 5 phần, đi theo đúng 5 yêu cầu của đề.”

**Slide 3 — Phần 1 (0:05).** Chuyển ngay.

**Slide 4 — Motivation (0:50).**
“Wikipedia tiếng Việt có **1,6 triệu** bài, nhưng dữ kiện nằm trong infobox dạng wiki-text nên máy không hỏi được.
DBpedia tiếng Anh thì có rất ít về triều đại, quan lại, trận đánh của Việt Nam. (Chỉ vào bảng.) Ba câu hỏi này không bài nào
trả lời trực tiếp. Ví dụ ông nội của Trần Nhân Tông: phải mở bài của cha ông, rồi xem trường ‘cha’ trong bài đó.
Mục tiêu của nhóm là để máy tự ghép được như vậy.”

**Slide 5 — Requirements (0:45).**
“Đây là năm yêu cầu của đề và nhóm làm gì cho từng yêu cầu. Cột phải là quy mô: **48** lớp, **44 nghìn** bài, **1,51 triệu**
triple, **32 nghìn** liên kết. Thầy nhấn mạnh ontology phải suy ra được nhiều hơn những gì trích xuất: phần suy diễn
thêm **2,64 triệu** triple.”

> **Chuyển lượt:** “Phần quan trọng nhất là ontology, xin mời Mai Anh.”

### Nguyen Thi Mai Anh — Phần 2: Ontology design (slide 6–12, ≈ 4:40)

**Slide 6 — Phần 2 (0:05).** Chuyển ngay.

**Slide 7 — Competency questions (0:45).**
“Nhóm em không bắt đầu bằng việc vẽ cây lớp, mà viết **18 câu hỏi năng lực** trước, như phương pháp Grüninger & Fox
trên lớp. Mỗi câu thành một truy vấn SPARQL, rồi thêm tiên đề cho đến khi cả 18 câu có kết quả. (Chỉ từng dòng.)
Câu ông nội cần một chain; câu vua cầm quân cần lớp định nghĩa; câu Nghệ An cần chain cộng bắc cầu; câu tỉnh sau
sáp nhập cần hasValue.”

**Slide 8 — Class hierarchy (0:40).**
“Kết quả là **48 lớp** dưới năm gốc, ánh xạ sang DBpedia, FOAF, schema.org. Các lớp chữ đỏ, **13 lớp**, là lớp định nghĩa:
không ai gán tay, reasoner tự xếp thực thể vào. Dòng dưới là các tiên đề rời nhau, lát nữa Hải sẽ cho thấy chúng bắt lỗi.”

**Slide 9 — Defined classes (0:45).**
“Theo OntoClean, làm vua hay làm tướng là vai trò một người giữ trong một thời gian. Nên nhóm em không gán ‘X là vua’,
mà định nghĩa: vua là người có ít nhất một thời kỳ trị vì. Cột phải là số thực thể reasoner tự tìm ra trên dữ liệu thật:
**3.981** vua, **755** vua trực tiếp cầm quân.”

**Slide 10 — Property axioms (0:50).**
“Đây là các tiên đề tạo ra quan hệ mới, cột phải là ví dụ thật. Em lấy dòng 4: infobox trận Bạch Đằng 1288 chỉ ghi
Trần Nhân Tông chỉ huy trận đó. Vì trận đó là một phần của cuộc kháng chiến, chain suy ra ông tham gia cả cuộc kháng chiến.
Trên toàn bộ dữ liệu được **618 nghìn** liên kết tổ tiên và **36,7 nghìn** lượt tham gia chiến tranh.”

**Slide 11 — Reigns and the 2025 reform (0:45).**
“Một lần trị vì gồm người, tước hiệu, triều đại, ngày bắt đầu và kết thúc, nên nhóm tách thành một nút Reign. Đây là
dữ liệu thật. Lúc đầu nhóm chưa tách hoàng hậu ra, kết quả **925** hoàng hậu bị suy ra là vua. Bên phải là cải cách 2025:
cấp huyện bị bỏ nên thành đơn vị lịch sử, và hasKey phát hiện **19** xã mới dùng lại mã của xã cũ.”

**Slide 12 — Example: Trần Nhân Tông (0:50).**
“Đây là toàn bộ câu chuyện trên một người. Màu xám là infobox ghi, màu đỏ là máy suy ra: ông nội Trần Thái Tông, thuộc
nhà Trần, tham gia cả cuộc kháng chiến, và bốn lớp. Khung đen là output thật khi chạy HermiT trên tập mẫu: đúng các
suy diễn đó, không có lớp nào rỗng. Trên dữ liệu thật ông có **53** triple trích xuất và **158** triple suy diễn.
Phần demo cuối bài em sẽ cho thầy xem trực tiếp.”

> **Chuyển lượt:** “Ontology cần dữ liệu, mời Hải trình bày cách nhóm lấy dữ liệu và suy diễn.”

### Duong Hoang Hai — Phần 3: Extraction and reasoning (slide 13–17, ≈ 3:05)

**Slide 13 — Phần 3 (0:05).** Chuyển ngay.

**Slide 14 — System pipeline (0:40).**
“Pipeline đi giống DBpedia: dump Wikipedia, lọc bài, ánh xạ infobox, suy diễn, liên kết, rồi nạp vào Fuseki. Ontology
được dùng hai lần: lúc trích xuất để kiểm tra kiểu, và lúc suy diễn. Cả pipeline chạy lại bằng một lệnh, khoảng 1,5 giờ.”

**Slide 15 — Infobox extraction (0:55).**
“Bên trái là wiki-text thật của infobox Trần Nhân Tông, bên phải là Turtle chương trình sinh ra. Ví dụ ‘8 tháng 11 năm 1278’
thành một ngày chuẩn xsd:date, còn trường ‘tại vị’ thành nút Reign mà Mai Anh vừa nói. Nhóm đọc bản dump chứ không gọi
API, vì API chỉ cho khoảng 50 trang mỗi phút. Ánh xạ viết trong một file YAML, có **16** unit test cho phần đọc ngày tháng
và số. Tổng cộng **44 nghìn** bài, **1,51 triệu** triple.”

**Slide 16 — Reasoning (0:45).**
“Từ 1,5 triệu triple này, reasoner sinh thêm bao nhiêu? Các reasoner Python có sẵn quá chậm, nên nhóm viết bộ suy diễn
theo luật OWL 2 RL. Nó đọc tiên đề từ file ontology, nên sửa ontology là kết quả đổi theo. Sau 26 vòng, khoảng 15 phút,
được **2,64 triệu** triple. Biểu đồ: nhiều nhất là bắc cầu, nhưng có giá trị nhất là xếp lớp và property chain.”

**Slide 17 — Data quality (0:40).**
“Tiên đề còn bắt lỗi. Đây là lỗi thật trong Wikipedia tiếng Việt, ví dụ Anna Freud ghi sinh 1985 mà mất 1982.
Dòng cuối là lỗi của chính nhóm em: tiên đề ‘người không thể là nhiệm kỳ’ báo **17.841** vi phạm, lần ra thì do YAML đọc
khóa ‘on:’ thành giá trị true.”

> **Chuyển lượt:** “Dữ liệu đã có và đã suy diễn; bước tiếp theo là nối nó với DBpedia tiếng Anh, mời Tài.”

### Le Phu Tai — Phần 4: Linking and endpoint (slide 18–21, ≈ 2:30)

**Slide 18 — Phần 4 (0:05).** Chuyển ngay.

**Slide 19 — Linking to DBpedia (1:00).**
“Giai đoạn 1 dùng liên kết liên ngôn ngữ của Wikipedia. Nhóm không tin ngay mà kiểm tra từng URI trên DBpedia, giữ lại
**32.136** liên kết. Giai đoạn 2 cho những thực thể không có liên kết: so khớp tên, kiểu và năm. Thử trên **1.500** cặp đã biết
đáp án: đúng **96,4%** nhưng chỉ tìm ra một nửa. (Chỉ bảng dưới.) Đây là hai lần nó sai: huyện Trà Cú bị nối sang trang
Trà Cú chứ không phải trang của huyện, và bài về con tàu USS Mannert L. Abele bị nối sang người cùng tên. Nhóm cố ý ưu
tiên độ chính xác, vì nối sai là kéo cả dữ liệu của thực thể khác về.”

**Slide 20 — Endpoint and interfaces (0:50).**
“Dữ liệu nằm trong Fuseki với bốn named graph. Trang tài nguyên gắn nhãn từng dòng: trích xuất, suy diễn hay liên kết.
Cùng một URI, trình duyệt nhận HTML còn chương trình nhận Turtle, đúng nguyên tắc Linked Data. Ngoài web còn có công cụ dòng lệnh.”

**Slide 21 — 5-star Linked Data (0:35).**
“Đối chiếu thang 5 sao: giấy phép mở, RDF, định dạng chuẩn, URI tra được, và liên kết sang DBpedia, Wikidata.
Đề yêu cầu 4 sao cho dữ liệu và liên kết DBpedia, nhóm đạt cả 5.”

> **Chuyển lượt:** “Vậy hệ thống trả lời được những câu hỏi ban đầu không? Mời Luận.”

### Le Van Luan — Phần 5: Evaluation and conclusion (slide 22–27, ≈ 3:05)

**Slide 22 — Phần 5 (0:05).** Chuyển ngay.

**Slide 23 — Evaluation (0:50).**
“Cả **18** câu hỏi năng lực đều có kết quả, trung vị **44 ms**. Cột giữa cho thấy câu nào cũng cần ít nhất một suy diễn.
(Chỉ khung code.) Đây là câu Nghệ An: truy vấn chỉ hỏi theo tỉnh, vì reasoner đã đưa nơi sinh cấp xã, huyện lên tỉnh.
Được **264** người trong 116 ms. Câu ông nội ở đầu bảng chính là câu hỏi ở slide 4.”

**Slide 24 — Lessons learned (0:55).**
“Đây là những lỗi nhóm em gặp thật. Khai báo ‘tiền nhiệm’ là bắc cầu thì sinh **3,8 triệu** triple vô nghĩa. Đặt domain
của thụy hiệu là vua thì **925** hoàng hậu thành vua. Một khóa YAML tên ‘on’ bị đọc thành true. Điểm chung: lỗi chỉ lộ ra
sau khi suy diễn, vì một tiên đề sai bị nhân lên trên cả đồ thị. Bài học: domain, range, bắc cầu là luật suy diễn,
không chỉ là mô tả.”

**Slide 25 — Conclusion (0:40).**
“Tóm lại, nhóm có một DBpedia tiếng Việt 44 nghìn bài, một ontology suy ra thêm 2,64 triệu triple và trả lời cả 18 câu hỏi,
và dữ liệu 5 sao. Chưa làm được: mới 44 nghìn trên 1,6 triệu bài, chưa chuẩn hóa âm lịch và niên hiệu, bộ so khớp mới
tìm được một nửa số liên kết.”

**Slide 26 — Team contributions (0:20).** “Đây là phân công của nhóm: mỗi người làm phần code và trình bày phần tương ứng.”

**Slide 27 — Thank you (0:15).**
“Nhóm em xin cảm ơn thầy và các bạn. Nếu thầy cho phép, Mai Anh xin demo nhanh hệ thống trong 5 phút.”

---

## Demo ngắn (5 phút, sau slide 27) — Mai Anh

Chuẩn bị trước như mục 0 của [`KICH_BAN_DEMO.md`](KICH_BAN_DEMO.md): `python src/serve.py`, các tab trình duyệt mở sẵn
(dùng `127.0.0.1`), Protégé đã mở `ontology/examples/protege_demo_tran.ttl`.

| Phần | Thao tác | Nói |
|---|---|---|
| D1 (1:00) | Mở bài Wikipedia *Trần Nhân Tông* (infobox) cạnh trang `127.0.0.1:5000/page/Trần_Nhân_Tông` | “Bên trái là infobox, bên phải là cùng dữ kiện đã thành RDF, nhãn *data*. Các dòng nhãn *inferred* thì infobox không hề ghi.” |
| D2 (1:30) | Protégé: *Reasoner → HermiT → Start*, chọn `Trần_Nhân_Tông`, chỉ phần tô vàng | “Phần vàng là HermiT suy ra từ tiên đề: vua Việt Nam, vua cầm quân, ông nội, cuộc chiến ông tham gia.” |
| D3 (2:30) | Tab SPARQL chạy **CQ2**, **CQ5**, rồi **CQ13** | “CQ2 trả về Trần Thái Tông từ graph *inferred*; CQ5 liệt kê 12 người tham gia kháng chiến chống Nguyên Mông; CQ13 lấy mô tả tiếng Anh trực tiếp từ DBpedia nhờ owl:sameAs.” |

Nếu DBpedia không phản hồi ở D3: chạy **CQ10** (luật thời gian R6) thay CQ13. Nếu Protégé lỗi ở D2: chạy `python tests/test_hermit.py`.

---

## Hỏi đáp — ai trả lời câu nào

Câu hỏi thuộc phần của ai thì người đó trả lời. Gợi ý trả lời chi tiết ở cuối [`KICH_BAN_DEMO.md`](KICH_BAN_DEMO.md).

| Chủ đề câu hỏi | Người trả lời |
|---|---|
| Ontology phức tạp hơn RDFS ở đâu; OntoClean; lớp định nghĩa, property chain; vì sao predecessor không bắc cầu; vì sao “anh chị em” cần luật; HermiT và xsd:date | **Mai Anh** |
| Vì sao dùng dump thay API; lọc bài; xử lý ngày tháng, năm TCN; YAML mapping; vì sao tự viết reasoner; SHACL và OWA; lỗi dữ liệu | **Hải** |
| Làm sao biết hai URI là một; precision/recall; DBpedia endpoint không ổn định; endpoint, named graph, content negotiation | **Tài** |
| 18 câu hỏi năng lực, cách đánh giá; hạn chế và hướng phát triển; câu SPARQL khó (viết trực tiếp trên editor) | **Luận** |

## Tập dượt

* Tập ít nhất **2 lần** với đồng hồ; mỗi người tự canh phần của mình, lệch quá 20 giây thì cắt bớt câu.
* Tập riêng **4 câu chuyển lượt** và lúc chuyển sang demo: đó là chỗ dễ ngập ngừng nhất.
* Người đang nói cầm bút trình chiếu; người kế tiếp đứng sẵn bên cạnh.
* Mai Anh kiểm tra máy demo trước giờ thuyết trình (Fuseki chạy, Protégé mở sẵn, cỡ chữ trình duyệt 125%).
