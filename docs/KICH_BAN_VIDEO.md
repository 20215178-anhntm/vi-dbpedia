# Kịch bản video demo ViDBpedia (≈ 3 phút 10 giây, giới hạn 3–5 phút)

Video là **bản quay màn hình demo trên web**, một người quay và thuyết minh, **không mở slide**. Mỗi cảnh ghi theo thứ tự:
**Thao tác** (làm gì trên màn hình) → **Tiếng Việt** (lời nói) → **English** (lời nói nếu quay bằng tiếng Anh).
Chọn một ngôn ngữ cho cả video.

Cả video đi theo một mạch: mở trang vua Trần Nhân Tông → chỉ ra dữ kiện Wikipedia không viết → dữ liệu nối ra ngoài →
ontology tạo ra suy diễn → hỏi bằng SPARQL.

| # | Thời gian | Trang | Nội dung |
|---|---|---|---|
| 1 | 0:00–0:20 | Trang chủ | Giới thiệu, bốn graph |
| 2 | 0:20–1:10 | Tìm kiếm → trang Trần Nhân Tông | Dữ kiện suy diễn: lớp, ông nội, cuộc chiến |
| 3 | 1:10–1:35 | `owl:sameAs` → dbpedia.org, link Turtle | Liên kết DBpedia, Linked Data |
| 4 | 1:35–1:55 | Ontology → lớp Monarch | Lớp định nghĩa |
| 5 | 1:55–2:55 | SPARQL: CQ2, CQ8 | Hỏi điều Wikipedia không ghi |
| 6 | 2:55–3:10 | Trang chủ | Kết |

Nếu còn thời gian (video ngắn hơn 3 phút khi quay thật), thêm **cảnh 5b — CQ13** (khoảng 25 giây).

---

## Chạy web trước khi quay

1. Mở terminal ở thư mục `vi-dbpedia`, chạy:
   ```bash
   python src/serve.py
   ```
2. Chờ đến khi hiện hai dòng (khoảng 10–20 giây):
   ```
   Fuseki:  http://localhost:3030/...
   Web UI:  http://127.0.0.1:5000/
   ```
   **Để nguyên cửa sổ terminal này** trong lúc quay; đóng nó là web tắt. Muốn tắt: bấm `Ctrl+C` trong cửa sổ đó.
3. Mở trình duyệt vào **`http://127.0.0.1:5000/`**. Dùng `127.0.0.1`, không dùng `localhost`: trên Windows localhost chậm
   thêm khoảng 2 giây mỗi trang, sẽ lộ trên video.
4. Mở trước từng trang một lần (trang chủ, Trần Nhân Tông, Ontology, SPARQL) để lần quay thật tải nhanh.

Lỗi thường gặp:
* *Trang chủ báo “Chưa kết nối được SPARQL endpoint”*: Fuseki chưa khởi động xong, chờ thêm vài giây rồi tải lại.
* *Address already in use / port 3030 hoặc 5000*: web đang chạy ở một cửa sổ khác; dùng luôn cửa sổ đó, hoặc tắt nó rồi chạy lại.
* *'java' is not recognized*: cần cài Java 17 trở lên (Fuseki chạy bằng Java).

## Chuẩn bị quay

* Trình duyệt toàn màn hình (F11), zoom 125%, ẩn thanh bookmark; bật *Focus assist* để không hiện thông báo.
* Ghi bằng **Clipchamp** (*Record & create → Screen*) hoặc OBS Studio, độ phân giải 1920×1080, dùng tai nghe có mic.
* Quay **từng cảnh** một rồi ghép lại; nói vấp chỉ cần quay lại cảnh đó. Di chuột chậm, dừng 1–2 giây ở chỗ đang nói.

---

## Cảnh 1 — Trang chủ (0:00–0:20)

**Thao tác**
* Mở `http://127.0.0.1:5000/`.
* Rê chuột qua bốn ô số triple của các graph *data*, *inferred*, *links*, *ontology*.

**Tiếng Việt**
> Đây là ViDBpedia, DBpedia tiếng Việt của nhóm em, xây dựng từ 44 nghìn bài Wikipedia về lịch sử, địa lý và danh nhân
> Việt Nam. Dữ liệu chia thành bốn graph: *data* là trích từ Wikipedia, *inferred* là máy tự suy ra từ ontology, *links* là
> liên kết sang DBpedia và Wikidata. Graph suy diễn còn lớn hơn graph dữ liệu gốc.

**English**
> This is ViDBpedia, our Vietnamese DBpedia, built from 44 thousand Wikipedia articles on Vietnamese history, geography
> and notable people. The data lives in four graphs: *data* is extracted from Wikipedia, *inferred* is derived by the
> machine from our ontology, and *links* points to DBpedia and Wikidata. The inferred graph is even larger than the
> extracted one.

## Cảnh 2 — Trang Trần Nhân Tông (0:20–1:10)

**Thao tác**
* Gõ “Trần Nhân Tông” vào ô tìm kiếm góc trên, Enter, bấm kết quả đầu tiên (kết quả thứ hai là phường Trần Nhân Tông,
  một đơn vị hành chính mang tên ông).
* Dừng ở dòng chú thích nhãn màu (*data*, *inferred*, *links*).
* Cuộn tới khối `rdf:type`, rê chuột qua các dòng nhãn **inferred** (`Monarch`, `VietnameseMonarch`, `MonarchWarrior`, `RoyalChild`).
* Cuộn tới `hasPaternalGrandfather` (Trần Thái Tông), rồi `participatedIn` (cuộc kháng chiến chống Nguyên Mông).

**Tiếng Việt**
> Em mở trang vua Trần Nhân Tông. Mỗi dòng có nhãn cho biết nó từ đâu ra: *data* là từ infobox Wikipedia, *inferred* là do
> máy suy ra. Infobox chỉ ghi ông là một người, cha là Trần Thánh Tông, và hai thời kỳ: làm hoàng đế rồi làm thái thượng
> hoàng. Nhưng máy đã xếp ông vào
> lớp vua, vua Việt Nam, vua cầm quân và con của vua. Dòng này: ông nội là Trần Thái Tông, vì ông nội là cha của cha.
> Dòng này: ông tham gia kháng chiến chống Nguyên Mông, vì ông chỉ huy trận Bạch Đằng, mà trận đó thuộc cuộc kháng chiến.
> Wikipedia cho 53 dữ kiện về ông, máy suy ra thêm 158.

**English**
> Here is Emperor Trần Nhân Tông. Each line carries a badge: *data* comes from the Wikipedia infobox, *inferred* was
> derived by the machine. The infobox only says he is a person, his father is Trần Thánh Tông, and he held two tenures:
> emperor, then retired emperor. Yet he
> is classified as a monarch, a Vietnamese monarch, a warrior monarch and a royal child. This line: his paternal
> grandfather is Trần Thái Tông, because a grandfather is a father's father. This line: he took part in the Mongol–Đại
> Việt war, because he commanded the Battle of Bạch Đằng, which is part of that war. Wikipedia gives 53 facts about him;
> the machine adds 158.

## Cảnh 3 — Liên kết ra ngoài (1:10–1:35)

**Thao tác**
* Cuộn tới dòng `owl:sameAs`, bấm link `dbr:Trần_Nhân_Tông` → trang dbpedia.org mở ra, dừng 2 giây, bấm Back.
* Bấm link **Turtle** ở đầu trang để hiện dữ liệu dạng RDF, dừng 2 giây, bấm Back.

**Tiếng Việt**
> Dòng owl:sameAs nối ông với DBpedia tiếng Anh và Wikidata; bấm vào là sang đúng trang của ông trên dbpedia.org. Toàn bộ
> có hơn 32 nghìn liên kết như vậy. Còn đây là cùng dữ liệu dạng Turtle: cùng một URI, người xem nhận trang web, chương
> trình nhận RDF. Đó là Linked Data.

**English**
> owl:sameAs links him to English DBpedia and Wikidata; one click opens his page on dbpedia.org. There are more than
> 32 thousand such links. And this is the same data as Turtle: the same URI gives a web page to people and RDF to
> programs. That is Linked Data.

## Cảnh 4 — Ontology (1:35–1:55)

**Thao tác**
* Bấm **Ontology** trên thanh menu, cuộn danh sách lớp, bấm `Monarch`.
* Chỉ vào dòng **`owl:equivalentClass`**: `Person ⊓ ∃hasReign.Reign` (dòng đầu bảng).
* Chỉ vào chữ “dùng trong 3981 triple” ở đầu trang.

**Tiếng Việt**
> Những suy diễn đó đến từ ontology. Đây là lớp Monarch. Dòng equivalentClass là định nghĩa: Person giao với “có ít nhất
> một hasReign là Reign”, nghĩa là vua là người có ít nhất một thời kỳ trị vì. Nhóm em không gán tay ai là vua; máy tự xếp
> gần bốn nghìn người vào lớp này.

**English**
> Those inferences come from the ontology. This is the class Monarch. The equivalentClass line is its definition: a
> person with at least one reign. We never state who is a monarch; the machine places almost four thousand people in
> this class.

## Cảnh 5 — SPARQL (1:55–2:55)

**Thao tác**
* Bấm **SPARQL** trên menu.
* Chọn **CQ2** trong ô *Câu hỏi mẫu* → bấm **Chạy** → chỉ vào kết quả Trần Thái Tông và cột `?g`.
* Chọn **CQ8** → bấm **Chạy** → chỉ vào dòng “264 kết quả”.

**Tiếng Việt**
> Cuối cùng là hỏi bằng SPARQL. Câu thứ nhất: ông nội của Trần Nhân Tông là ai? Trần Thái Tông, và cột graph cho thấy câu
> trả lời nằm trong graph *inferred*: không bài viết nào ghi điều này.
> Câu thứ hai: những ai sinh ra trên đất Nghệ An ngày nay? Wikipedia thường chỉ ghi nơi sinh là một huyện hay một xã, nhưng
> máy biết xã nằm trong huyện, huyện nằm trong tỉnh, nên chỉ cần hỏi theo tỉnh: được 264 người.

**English**
> Finally, SPARQL. First question: who is Trần Nhân Tông's paternal grandfather? Trần Thái Tông, and the graph column
> shows the answer is in the *inferred* graph: no article states it.
> Second question: who was born in today's Nghệ An province? Wikipedia usually names only a district or a commune, but
> the machine knows which province contains it, so we simply ask by province: 264 people.

### Cảnh 5b — CQ13 (tùy chọn, thêm khoảng 25 giây)

**Thao tác**
* Chọn **CQ13** → bấm **Chạy** → chỉ vào cột mô tả tiếng Anh. Cần Internet; chạy thử một lần trước khi quay.

**Tiếng Việt**
> Câu này chạy trên hai bộ dữ liệu cùng lúc: lấy các vua nhà Lý trong ViDBpedia, rồi nhờ owl:sameAs lấy mô tả tiếng Anh
> của họ trực tiếp từ DBpedia.

**English**
> This query runs over two datasets at once: our Lý-dynasty monarchs, and through owl:sameAs, their English descriptions
> fetched live from DBpedia.

## Cảnh 6 — Kết (2:55–3:10)

**Thao tác**
* Bấm logo **ViDBpedia** về trang chủ, dừng ở các ô số liệu.

**Tiếng Việt**
> Tóm lại, từ 44 nghìn bài Wikipedia, ViDBpedia trích xuất 1,5 triệu triple, ontology suy ra thêm 2,6 triệu triple, dữ liệu
> liên kết với DBpedia và trả lời được những câu hỏi Wikipedia không viết sẵn. Cảm ơn thầy và các bạn đã theo dõi.

**English**
> To sum up: from 44 thousand Wikipedia articles, ViDBpedia extracts 1.5 million triples, its ontology infers 2.6 million
> more, the data is linked to DBpedia, and it answers questions that Wikipedia never states. Thank you for watching.

---

## Biên tập

1. Ghép 6 đoạn trong Clipchamp, chuyển cảnh *Cross fade* 0,3 giây; cắt bỏ lúc chờ trang tải và chờ truy vấn chạy.
2. **Zoom vào** đúng chỗ đang nói: nhãn *inferred* (cảnh 2), dòng `hasPaternalGrandfather` (cảnh 2), cột `?g` và số
   “264 kết quả” (cảnh 5). Chữ trên web nhỏ, không zoom thì người xem không đọc được.
3. *Captions → Auto captions* để có phụ đề.
4. Xuất **1080p MP4**; kiểm tra tổng thời lượng nằm trong 3:00–5:00. Nếu dưới 3 phút, thêm cảnh 5b.
