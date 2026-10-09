# Giải thích chi tiết ontology `vidbo`

File: [`ontology/vidbo.ttl`](../ontology/vidbo.ttl) — 4 phần: (0) phần đầu, (1) lớp, (2) object property, (3) datatype property, (4) vài cá thể.
Tài liệu này đi theo đúng thứ tự file; số dòng ghi dạng `L100` để mở song song.

---

## Phần 0. Cách đọc file

### 0.1 Cú pháp Turtle trong 1 phút

```turtle
vidbo:Monarch a owl:Class ;                      # chủ ngữ  vị ngữ  tân ngữ ;   ("a" = rdf:type)
    rdfs:label "Monarch"@en , "Quân chủ / vua"@vi ;   # dấu "," = cùng chủ ngữ + vị ngữ, nhiều tân ngữ
    rdfs:subClassOf dbo:Monarch .                # dấu ";" = cùng chủ ngữ, vị ngữ khác; dấu "." = hết câu
```

* `[ ... ]` là **nút rỗng** (blank node) — một đối tượng không tên, dùng để viết biểu thức lớp như “những người có ít nhất một thời kỳ trị vì”.
* `( a b c )` là **danh sách** RDF — dùng cho giao, hợp, chuỗi thuộc tính.
* `[] a owl:AllDisjointClasses ; owl:members (...)` — một tiên đề không cần tên.

### 0.2 Ký hiệu logic mô tả (Description Logic) dùng trong tài liệu

| Ký hiệu | Đọc là | Trong Turtle |
|---|---|---|
| `A ⊑ B` | mọi A đều là B | `A rdfs:subClassOf B` |
| `A ≡ B` | A và B có cùng thành viên | `A owl:equivalentClass B` |
| `A ⊓ B` | vừa là A vừa là B | `owl:intersectionOf (A B)` |
| `A ⊔ B` | là A hoặc là B | `owl:unionOf (A B)` |
| `∃p.C` | có ít nhất một giá trị p thuộc C | `[ owl:onProperty p ; owl:someValuesFrom C ]` |
| `∋p.{v}` | có giá trị p bằng v | `[ owl:onProperty p ; owl:hasValue v ]` |
| `≥n p.C` | có ít nhất n giá trị p thuộc C | `owl:minQualifiedCardinality n ; owl:onClass C` |
| `A ⊥ B` | không gì vừa là A vừa là B | `owl:AllDisjointClasses` / `owl:disjointWith` |
| `p ∘ q ⊑ r` | nếu x p y và y q z thì x r z | `r owl:propertyChainAxiom (p q)` |
| `p⁻` | nghịch đảo của p | `owl:inverseOf` |

### 0.3 Hai loại câu trong ontology

* **Câu mô tả** (`⊑`, domain, range): cho biết điều kiện **cần**. “Mọi tỉnh đều là đơn vị hành chính.”
* **Câu định nghĩa** (`≡` với một biểu thức): cho biết điều kiện **cần và đủ**. “Vua ≡ người có thời kỳ trị vì” → hễ ai có thời kỳ trị vì là reasoner **tự xếp** vào lớp Vua.
  **Đây là nguồn chính của suy diễn** — ontology này có 13 câu định nghĩa như vậy.

---

## Phần 0'. Phần đầu file (L1–L36)

* `@prefix` (L1–13): rút gọn IRI. `vidbo:` = ontology của mình, `vidbr:` = tài nguyên (người, địa danh…), còn lại là từ vựng chuẩn tái sử dụng:
  `dbo:` (DBpedia), `foaf:`, `schema:`, `geo:` (toạ độ WGS84), `dct:` (Dublin Core), `skos:`, `vann:`.
* Khối `owl:Ontology` (L24–36): siêu dữ liệu — tên, phiên bản, prefix khuyến nghị, mô tả. Đây là “bìa sách” để công cụ (Protégé, LOV) nhận diện ontology.
* Chú thích L15–22 nói rõ hai chế độ dùng ontology:
  **OWL 2 RL** (phần lớn tiên đề) → chạy được bằng luật trên 1,5 triệu triple (`src/reason.py`);
  **OWL 2 DL đầy đủ** (thêm tiên đề tồn tại, ràng buộc số lượng) → kiểm tra bằng reasoner tableau HermiT trong Protégé.

---

## Phần 1. Phân cấp lớp (L38–L293)

### 1.1 Năm lớp gốc và tiên đề rời nhau (L42–L73)

```turtle
vidbo:Agent ≡ dbo:Agent      vidbo:Place ≡ dbo:Place ≡ schema:Place
vidbo:Event ≡ dbo:Event      vidbo:Work  ≡ dbo:Work  ≡ schema:CreativeWork
vidbo:Tenure                 # nhiệm kỳ / thời gian tại vị
[] a owl:AllDisjointClasses ; owl:members ( Person Place Event Work Tenure ) .
[] a owl:AllDisjointClasses ; owl:members ( Group Event Work Tenure ) .
```

* **Ý nghĩa:** thế giới được chia thành *tác nhân* (người, nhóm), *địa điểm*, *sự kiện*, *tác phẩm*, *nhiệm kỳ*.
* **`owl:equivalentClass dbo:…`:** căn chỉnh với DBpedia — mọi `vidbo:Person` tự động cũng là `dbo:Person`, `foaf:Person`, `schema:Person`
  (trên dữ liệu thật: 58.242 người có đủ 3 kiểu này) → truy vấn viết cho DBpedia chạy được trên ViDBpedia.
* **Tiên đề rời nhau:** một người không thể là địa điểm. Không giúp suy ra thêm, nhưng giúp **phát hiện mâu thuẫn**:
  nếu infobox ghi “cha = [[Phổ (quốc gia)]]” thì Phổ vừa bị suy ra là Person (range của `hasParent`) vừa là Place → reasoner báo lỗi.
  Trên dữ liệu thật phát hiện 145 trường hợp, và từng phát hiện một lỗi trong chính code trích xuất (17.841 vi phạm `Person ⊥ Tenure`).
* **Quyết định có chủ ý (L70–71):** `Group` (triều đại) **không** rời nhau với `Place`, vì Wikipedia dùng cùng một bài “Nhà Nguyên” cho cả dòng họ cai trị lẫn quốc gia.
  Nếu khai báo rời nhau, mọi triều đại có hộp thông tin quốc gia sẽ thành mâu thuẫn giả.

### 1.2 Tác nhân: Person, Group, Dynasty (L75–L96)

```
Person ⊑ Agent          Group ⊑ Agent          Dynasty ⊑ Group ⊑ dbo:Family
VietnameseDynasty ⊑ Dynasty                    Person ⊥ Group
```
* `VietnameseDynasty` được gán từ thể loại Wikipedia “Triều đại Việt Nam” (27 triều đại). Lớp này là “mỏ neo” cho định nghĩa `VietnameseMonarch` bên dưới.

### 1.3 Vai trò của con người — các lớp ĐỊNH NGHĨA (L98–L175) ⭐

Đây là phần quan trọng nhất. Không lớp nào trong số này được gán tay; reasoner xếp người vào dựa trên dữ liệu.

| Lớp (dòng) | Định nghĩa DL | Đọc thành lời | Trên dữ liệu thật |
|---|---|---|---|
| `Monarch` (L100) | `Monarch ≡ Person ⊓ ∃hasReign.Reign` | Vua là người có ít nhất một thời kỳ trị vì | 3.981 |
| `VietnameseMonarch` (L107) | `≡ Monarch ⊓ ∃memberOfDynasty.VietnameseDynasty` | Vua thuộc một triều đại Việt Nam | 169 |
| `RoyalChild` (L112) | `≡ Person ⊓ ∃hasParent.Monarch` | Hoàng tử/công chúa = người có cha hoặc mẹ là vua | 6.160 |
| `RoyalTitleHolder` (L125) | `≡ Person ⊓ ∃holdsRoyalTitle.RoyalTitleTenure` | Người giữ tước vị không trị vì (hậu phi, thái tử) | 1.409 |
| `RoyalFamilyMember` (L118–130) | `Monarch ⊔ RoyalChild ⊔ RoyalTitleHolder ⊔ ∃spouse.Monarch ⊑ RoyalFamilyMember` | Thành viên hoàng tộc | 10.255 |
| `OfficeHolder` (L132) | `≡ Person ⊓ ∃holdsOffice.OfficeTenure` | Người giữ chức vụ | 6.832 |
| `RoyalCourtOfficial` (L138) | `≡ OfficeHolder ⊓ ∃servedUnder.Monarch` | Quan lại = giữ chức dưới triều một vị vua | 204 |
| `MilitaryCommander` (L149) | `≡ Person ⊓ ∃commanded.MilitaryConflict` | Chỉ huy = người đã chỉ huy ít nhất một xung đột | 10.257 |
| `MonarchWarrior` (L156) | `≡ Monarch ⊓ MilitaryCommander` | Vua trực tiếp cầm quân | 755 |
| `Writer` (L161–166) | `∃notableWork.WrittenWork ⊑ Writer` | Ai có tác phẩm tiêu biểu là nhà văn | 1.442 |

**Vì sao thiết kế như vậy:**

* **OntoClean — tính cứng (rigidity):** *Người* là lớp cứng (đã là người thì luôn là người); *vua*, *quan*, *tướng* là **vai trò**
  (Trần Nhân Tông trước 1278 chưa là vua, sau 1293 là Thái thượng hoàng). Quy tắc OntoClean: lớp cứng không được nằm dưới lớp không cứng,
  và vai trò không nên là lớp con được gán sẵn. Vì vậy vai trò được **định nghĩa qua quan hệ** với một nút nhiệm kỳ.
* **Chuỗi suy diễn lồng nhau:** `MonarchWarrior` dựa trên `Monarch` và `MilitaryCommander`, hai lớp này lại dựa trên `hasReign` và `commanded`;
  `commanded` thì không có trong dữ liệu mà được suy ra từ nghịch đảo của `commander` (hộp thông tin trận đánh ghi “chỉ huy: …”).
  → Ghi “Trận Bạch Đằng có chỉ huy Trần Nhân Tông” là đủ để máy kết luận “Trần Nhân Tông là vua trực tiếp cầm quân”.
* **Hợp viết bằng nhiều câu `⊑` (L121–130):** `A ⊔ B ⊑ C` tương đương `A ⊑ C` và `B ⊑ C`; viết tách ra để nằm trong OWL 2 RL (luật xử lý được).
* `NationalHero` (L168) gán từ thể loại “Anh hùng dân tộc Việt Nam”; `CentenarianPerson` (L172) do **luật** R3 điền (OWL không tính được tuổi).

### 1.4 Địa điểm và đơn vị hành chính (L177–L245) ⭐

```
PopulatedPlace ⊑ Place      State ≡ dbo:Country ⊑ PopulatedPlace      Region ⊑ Place
State ⊓ ∃dissolutionYear.Literal ⊑ FormerState                       (L193)
AdministrativeUnit ≡ FirstLevelUnit ⊔ SecondLevelUnit ⊔ ThirdLevelUnit , hasKey(adminCode)   (L201)
FirstLevelUnit  ≡ AdministrativeUnit ⊓ ∋adminLevel.{1}               (L209)
SecondLevelUnit ≡ AdministrativeUnit ⊓ ∋adminLevel.{2}
ThirdLevelUnit  ≡ AdministrativeUnit ⊓ ∋adminLevel.{3}
Province, Municipality ⊑ FirstLevelUnit;  District ⊑ SecondLevelUnit;  Commune, Ward, Township, SpecialZone ⊑ ThirdLevelUnit
SecondLevelUnit ⊑ HistoricalAdministrativeUnit                      (L239)
∃mergedInto.AdministrativeUnit ⊑ HistoricalAdministrativeUnit       (L240)
ThirdLevelUnit ⊑ ∃locatedIn.FirstLevelUnit                          (L244)
```

* **`FormerState`:** quốc gia có năm giải thể là cựu quốc gia — điều kiện **đủ** (1.328 cựu quốc gia được suy ra).
* **`hasValue` (L209–220):** cấp hành chính được *định nghĩa* bằng một con số. Khi hộp thông tin không ghi loại đơn vị, chương trình
  suy cấp từ độ dài mã hành chính (2/3/5 chữ số) → reasoner tự xếp vào cấp tỉnh/huyện/xã.
* **Cải cách 2025 (L235–241):** Nghị quyết 202/2025/QH15 bãi bỏ cấp huyện từ 1/7/2025 → mọi đơn vị cấp 2 là *đơn vị đã giải thể*.
  Đây là **tri thức miền** đưa vào ontology (CQ16 dùng nó).
* **`hasKey(adminCode)`:** mã hành chính định danh duy nhất một đơn vị (tính năng OWL 2). Trên dữ liệu thật phát hiện 19 cặp trùng mã:
  xã mới (2025) kế thừa mã của xã cũ → reasoner chỉ **báo cáo** chứ không suy ra `owl:sameAs` (nếu không sẽ gộp nhầm hai thực thể).
* **Tiên đề tồn tại (L244):** “mọi xã đều nằm trong một tỉnh nào đó” — không thuộc OWL 2 RL, chỉ HermiT dùng; theo giả định thế giới mở,
  nó **không** báo lỗi khi thiếu tỉnh (thiếu thông tin ≠ sai). Kiểm tra “bắt buộc có” là việc của SHACL.

### 1.5 Sự kiện quân sự (L247–L266)

```
MilitaryConflict ≡ dbo:MilitaryConflict ⊑ Event
MilitaryConflict ⊑ ≥2 combatant.Belligerent        # ràng buộc số lượng có điều kiện (OWL 2)
Belligerent ≡ Agent ⊔ State
War, Campaign, Battle, Uprising ⊑ MilitaryConflict ;  War ⊥ Battle
```
* Một cuộc xung đột có ít nhất **hai** bên tham chiến; bên tham chiến có thể là triều đại (Agent) hoặc quốc gia (State) — dùng **hợp**.
* Loại xung đột (trận/chiến dịch/chiến tranh/khởi nghĩa) được gán từ tiêu đề bài (“Trận …”, “Chiến dịch …”).

### 1.6 Tác phẩm (L268–273) — `WrittenWork ≡ dbo:WrittenWork ⊑ Work`.

### 1.7 Nhiệm kỳ — mẫu quan hệ n-ngôi (L275–L293) ⭐

```
Reign ⊑ Tenure,   Reign ⊑ =1 reignOf.Person        # mỗi thời kỳ trị vì thuộc đúng một người
OfficeTenure ⊑ Tenure
RoyalTitleTenure ⊑ Tenure
Reign ⊥ OfficeTenure ⊥ RoyalTitleTenure
```

* **Vấn đề:** “Trần Nhân Tông trị vì Đại Việt với tước Hoàng đế, thuộc nhà Trần, từ 8/11/1278 đến 16/4/1293” có **5 thành phần** —
  không viết được bằng một triple. Giải pháp (W3C *Defining N-ary Relations*, mẫu thiết kế *Situation*): tạo một nút trung gian.

```
vidbr:Trần_Nhân_Tông  vidbo:hasReign  vidbr:Trần_Nhân_Tông__Reign_0 .
vidbr:Trần_Nhân_Tông__Reign_0  a vidbo:Reign ;
    vidbo:title "Hoàng đế Đại Việt" ; vidbo:tenureDynasty vidbr:Nhà_Trần ;
    vidbo:startDate "1278-11-08" ; vidbo:endDate "1293-04-16" .
```
* **`RoyalTitleTenure`:** hộp thông tin hoàng gia dùng chung cho vua, hậu, thái tử — ai cũng có trường “tại vị”. Nếu coi tất cả là `Reign`
  thì hoàng hậu bị suy ra là vua. Tước hậu phi/thái tử → `RoyalTitleTenure`; ba loại nhiệm kỳ rời nhau.

---

## Phần 2. Object property (L295–L586)

### 2.1 Gia đình (L299–L350) ⭐

| Thuộc tính | Tiên đề | Ý nghĩa / tác dụng |
|---|---|---|
| `hasParent` (L301) | Irreflexive, Asymmetric; domain/range Person; `⊑ hasAncestor`; `≡ hasChild⁻` | Không ai là cha/mẹ của chính mình; nếu A là cha B thì B không là cha A → phát hiện 6 cặp cha–con bị ghi hoán đổi |
| `hasChild` (L307) | `≡ dbo:child` | Nghịch đảo: ghi “con cái” ở hộp thông tin cha → suy ra `hasParent` ở người con |
| `hasFather`, `hasMother` (L311–319) | Functional; `⊑ hasParent` | Mỗi người tối đa một cha, một mẹ |
| `hasAncestor` / `hasDescendant` (L321–325) | Transitive, nghịch đảo nhau | Tổ tiên của tổ tiên cũng là tổ tiên → 618.339 cặp |
| `hasGrandparent` (L327) | `hasParent ∘ hasParent` | Ông bà |
| `hasPaternalGrandfather` (L333) | `hasFather ∘ hasFather` | Ông nội (CQ2) |
| `spouse` (L338) | Symmetric, Irreflexive | A là vợ/chồng B thì B là vợ/chồng A |
| `sibling` (L343) | Symmetric, Irreflexive — **điền bằng luật R1** | xem dưới |
| `uncleOrAunt` (L348) | `hasParent ∘ sibling` | Chú/bác/cô/dì |

**Vì sao `sibling` dùng luật:** chain `hasParent ∘ hasChild` cho ra “cùng cha mẹ” nhưng **bao gồm cả bản thân** — OWL không viết được
điều kiện x ≠ y. Luật SPARQL R1 (`rules/R1_sibling.rq`) có `FILTER(?x != ?y)`; kết quả của luật lại được OWL dùng trong chain `uncleOrAunt`
ở vòng suy diễn thứ hai → minh hoạ **phối hợp OWL + luật** (tầng *Rules* trong Semantic Web stack).

### 2.2 Triều đại (L352–L369)

```
memberOfDynasty: domain Person, range Dynasty, hasFather ∘ memberOfDynasty ⊑ memberOfDynasty   (phụ hệ)
servedDynasty:   Person → Dynasty      (quan lại PHỤC VỤ triều đại, không phải thành viên)
```
* Chain phụ hệ: chỉ cần biết vua đầu tiên thuộc nhà Trần, mọi con cháu theo dòng cha đều được suy ra thuộc nhà Trần.
* **Phân biệt ngữ nghĩa:** cùng là trường “triều đại” nhưng trong hộp thông tin vua nghĩa là *thuộc* hoàng tộc, trong hộp thông tin quan lại
  (“Thông tin nhân vật phong kiến”) nghĩa là *phục vụ* → hai thuộc tính khác nhau. Gộp chung thì Lý Thường Kiệt sẽ thành người họ Lý của hoàng tộc.

### 2.3 Nhiệm kỳ và chức vụ (L371–L423)

| Thuộc tính | Tiên đề | Ý nghĩa |
|---|---|---|
| `hasReign` (L373) | InverseFunctional, `≡ reignOf⁻`, domain Person, range Reign | Một nút Reign chỉ thuộc một người |
| `holdsOffice` (L379) | InverseFunctional, `≡ officeHolder⁻` | Tương tự cho chức vụ |
| `underMonarch` (L385) | OfficeTenure → Person | Nhiệm kỳ đó dưới triều vua nào |
| `servedUnder` (L389) | `holdsOffice ∘ underMonarch` | Người X làm quan dưới thời vua Y (dùng trong định nghĩa `RoyalCourtOfficial`) |
| `tenureDynasty` (L404) | Reign → Dynasty | Triều đại của thời kỳ trị vì |
| `ruledAsMemberOf` (L409) | `hasReign ∘ tenureDynasty`, `⊑ memberOfDynasty` | Ai trị vì dưới danh nghĩa nhà Trần thì thuộc nhà Trần |
| `predecessor` / `successor` (L413) | Irreflexive, nghịch đảo nhau | **Cố ý không bắc cầu** (L417–419) |

**Bài học về `predecessor`:** phiên bản đầu khai báo thuộc tính bắc cầu “những người tiền nhiệm”. Vì một người giữ nhiều chức vụ,
tiền nhiệm của các chức khác nhau bị nối thành một chuỗi → **3,8 triệu triple vô nghĩa**. Tiên đề sai ngữ nghĩa → suy diễn sai hàng loạt.

### 2.4 Địa lý (L425–L476) ⭐

```
locatedIn: Transitive, domain/range Place, ≡ contains⁻, ⊑ dbo:isPartOf
province, district, region ⊑ locatedIn          (range FirstLevelUnit / SecondLevelUnit / Region)
seatOf ⊑ capitalOf, seatOf ⊑ locatedIn ;  adminSeat ≡ seatOf⁻ ⊑ capital
mergedInto ≡ formedFrom⁻ ;  predecessorState ≡ successorState⁻
```
* **Thuộc tính con:** hộp thông tin xã ghi “tỉnh = Ninh Bình” → `province` → tự có `locatedIn Ninh Bình` → bắc cầu lên vùng, quốc gia.
* **`seatOf`:** tỉnh lỵ luôn nằm trong tỉnh → “tỉnh lỵ của Ninh Bình là phường Hoa Lư” cho ra “Hoa Lư nằm trong Ninh Bình”.
  Còn `capital` nói chung (kinh đô của một quốc gia cũ) thì **không** suy ra `locatedIn` — kinh đô xưa có thể nằm ngoài lãnh thổ ngày nay.
  HermiT còn tự suy ra ở mức lược đồ: `adminSeat ⊑ contains`.
* **Lưu ý OWL DL:** thuộc tính bắc cầu là *non-simple*, không được khai báo irreflexive → chu trình (A nằm trong B, B nằm trong A)
  được phát hiện bằng chương trình (`transitive_cycle` trong báo cáo nhất quán). Nhờ vậy đã tìm ra lỗi: trang “vùng” liệt kê các tỉnh
  bị hiểu ngược thành “vùng nằm trong tỉnh”.

### 2.5 Người – địa điểm (L478–L505) ⭐

```
birthPlace ⊑ bornWithin ;   bornWithin ∘ locatedIn ⊑ bornWithin        (L496)
deathPlace ⊑ diedWithin ;   diedWithin ∘ locatedIn ⊑ diedWithin
```
* **Mẹo chain đệ quy:** `bornWithin` = nơi sinh *hoặc bất kỳ nơi nào chứa nơi sinh*. Wikipedia chỉ ghi “Nam Đàn (huyện)”, nhưng vì Nam Đàn
  `locatedIn` Nghệ An nên người đó `bornWithin` Nghệ An (CQ8: 264 người). Dạng `p ∘ q ⊑ p` là chain *regular* hợp lệ trong OWL 2 DL.
* Tách riêng `bornWithin` thay vì làm `birthPlace` bắc cầu: giữ `birthPlace` đúng nghĩa (nơi được ghi), câu hỏi “sinh trong địa bàn” dùng `bornWithin`.

### 2.6 Quân sự (L507–L547) ⭐

```
commander: MilitaryConflict → Person, ≡ commanded⁻
commanded ⊑ participatedIn
partOfConflict: Transitive, ≡ hasSubConflict⁻
participatedIn ∘ partOfConflict ⊑ participatedIn        (L530)
conflictPlace ⊑ tookPlaceWithin ;  tookPlaceWithin ∘ locatedIn ⊑ tookPlaceWithin
reignedDuringConflict  (luật R6)
```
Chuỗi suy diễn đầy đủ cho Trần Hưng Đạo:
1. Hộp thông tin “Trận Bạch Đằng (1288)” ghi chỉ huy Trần Hưng Đạo → `commander`.
2. Nghịch đảo → Trần Hưng Đạo `commanded` Trận Bạch Đằng → là `MilitaryCommander`.
3. `commanded ⊑ participatedIn` → tham gia Trận Bạch Đằng.
4. Trận Bạch Đằng `partOfConflict` Kháng chiến lần 3, lần 3 `partOfConflict` Chiến tranh Nguyên Mông – Đại Việt (bắc cầu).
5. Chain → Trần Hưng Đạo `participatedIn` cả cuộc chiến (CQ5).

`reignedDuringConflict` cần so sánh năm (năm bắt đầu chiến tranh nằm trong khoảng trị vì) → làm bằng luật R6.

### 2.7 Tác phẩm và ảnh hưởng (L549–L568)

```
notableWork ≡ author⁻ ;  ∃notableWork.WrittenWork ⊑ Writer
influencedBy: Irreflexive, ≡ influenced⁻, ⊑ intellectualLineage (Transitive)
```
* Tản Đà chịu ảnh hưởng Nguyễn Du (trực tiếp); ai chịu ảnh hưởng Tản Đà thì gián tiếp chịu ảnh hưởng Nguyễn Du (CQ15).
* Chu trình ở `intellectualLineage` (ví dụ Shakespeare ↔ Henry James) cho thấy dữ liệu “ảnh hưởng” trên Wikipedia bị ghi ngược chiều.

### 2.8 Quốc gia và liên kết chung (L570–L590)
* `leader` (State → Person, `≡ leaderOf⁻`), `governmentType`.
* `wikiPageWikiLink`, `wikiPageRedirects`, `religion` — giữ tương thích với cấu trúc dữ liệu DBpedia.

---

## Phần 3. Datatype property (L591–L670)

### 3.1 Vấn đề kiểu ngày tháng (L594–L599)
`xsd:date` và `xsd:gYear` **không thuộc OWL 2 datatype map** → nếu viết `rdfs:range xsd:date`, HermiT/Protégé từ chối cả ontology.
Giải pháp: dữ liệu vẫn dùng `xsd:date`/`xsd:gYear` (giống DBpedia, liên kết tốt), ontology ghi kiểu mong đợi bằng chú thích
`vidbo:expectedDatatype`, còn việc **kiểm tra** giao cho SHACL (`ontology/shapes.ttl`). → Phân vai rõ: **OWL để suy luận, SHACL để kiểm tra**.

### 3.2 Các nhóm thuộc tính

| Nhóm | Thuộc tính | Ghi chú |
|---|---|---|
| Thời gian của người | `birthDate`, `deathDate`, `birthYear`, `deathYear` | **Functional**: hai ngày sinh khác nhau → phát hiện mâu thuẫn (Alexandre de Rhodes: 1591 và 1593) |
| Tên gọi | `birthName`, `penName`, `templeName` (miếu hiệu), `posthumousName` (thụy hiệu), `eraName` (niên hiệu), `courtesyName` (tên tự), `nativeName` (chữ Hán/Nôm) | Đặc thù văn hoá Việt Nam/Đông Á |
| Nhiệm kỳ | `startDate`, `endDate`, `startYear`, `endYear` (Functional) | Gắn vào nút Tenure |
| Do luật sinh ra | `durationYears` (R4), `ageAtDeath` (R2), `populationDensity` (R5) | OWL không làm phép tính |
| Hành chính | `adminLevel` (Functional, dùng trong `hasValue`), `adminCode` (khoá), `area`, `population`, `postalCode`, `areaCode`, `licensePlate`, `isoCode`, `foundingYear`, `dissolutionYear` | |
| Xung đột | `result`, `strength`, `casualties` | dạng văn bản |
| Siêu dữ liệu | `abstract`, `wikiPageID`, `wikiPageRevisionID`, `wikidataID`, `infoboxTemplate` | nguồn gốc dữ liệu (provenance) |

**Bài học về domain (L612–617):** ban đầu `posthumousName`, `templeName`, `eraName` có `rdfs:domain Monarch`. Nhưng hoàng hậu, vương hầu
cũng có thụy hiệu → reasoner suy ra **925 hoàng hậu và vương hầu là vua**. Domain trong OWL không phải ràng buộc kiểm tra mà là **luật suy diễn**
(“ai có thuộc tính này thì thuộc lớp domain”) — khai báo domain quá hẹp là lỗi phổ biến. Đã sửa thành `Person`.

---

## Phần 4. Cá thể (L672–) — `vidbr:Việt_Nam a vidbo:State` làm điểm neo.

---

## Tóm tắt: ontology này dùng những gì của OWL 2

| Đặc trưng | Số lượng | Ví dụ |
|---|---:|---|
| Lớp | 48 | |
| Lớp định nghĩa (`≡` biểu thức) | 13 | Monarch, RoyalChild, MonarchWarrior, FirstLevelUnit |
| Object / datatype property | 67 / 48 | |
| Property chain | 10 | hasPaternalGrandfather, bornWithin, participatedIn, servedUnder |
| Transitive | 7 | locatedIn, hasAncestor, partOfConflict, intellectualLineage |
| Cặp nghịch đảo | 18 | hasParent/hasChild, commander/commanded |
| Symmetric / Irreflexive / Asymmetric | 2 / 6 / 1 | spouse, sibling / hasParent |
| Functional / InverseFunctional | 15 / 3 | hasFather, birthDate / hasReign |
| Restriction (some/has-value/cardinality) | 17 | |
| Nhóm lớp rời nhau | 8 | Person ⊥ Place ⊥ Event ⊥ Work ⊥ Tenure |
| hasKey | 1 | AdministrativeUnit(adminCode) |
| Căn chỉnh với từ vựng ngoài | 53 | dbo, foaf, schema.org |

## Liên hệ với câu hỏi năng lực

| Phần ontology | Câu hỏi dùng đến |
|---|---|
| Lớp định nghĩa vai trò (1.3) | CQ1, CQ4, CQ14 |
| Hành chính + cải cách 2025 (1.4) | CQ9, CQ16 |
| Nhiệm kỳ n-ngôi (1.7, 2.3) | CQ6, CQ10, CQ14 |
| Gia đình (2.1) | CQ2, CQ3, CQ11 |
| Triều đại (2.2) | CQ1, CQ6, CQ13 |
| Địa lý + người–nơi (2.4, 2.5) | CQ7, CQ8 |
| Quân sự (2.6) | CQ4, CQ5, CQ7, CQ10 |
| Ảnh hưởng văn học (2.7) | CQ15 |
| Tiên đề rời nhau, functional, asymmetric, hasKey | CQ17 + báo cáo nhất quán |
