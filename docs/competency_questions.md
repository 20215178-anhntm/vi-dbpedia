# Câu hỏi năng lực (Competency Questions)

Ontology `vidbo` được thiết kế theo phương pháp **Grüninger & Fox** (slide *07 – Knowledge Modeling*):

1. **Kịch bản sử dụng:** người dùng muốn hỏi về lịch sử, địa lý, danh nhân Việt Nam bằng SPARQL,
   kể cả những câu hỏi mà Wikipedia **không ghi trực tiếp** (ông nội của ai, ai sinh ra trong tỉnh nào theo địa giới mới…).
2. **Câu hỏi năng lực không hình thức** (bảng dưới).
3. **Thuật ngữ:** từ các câu hỏi rút ra lớp, thuộc tính.
4. **Câu hỏi năng lực hình thức:** mỗi câu hỏi là một truy vấn SPARQL trong [`queries/`](../queries/).
5. **Tiên đề:** thêm tiên đề OWL 2 / luật cho đến khi ontology trả lời được các câu hỏi đó.

Cột *Cơ chế* cho biết vì sao câu trả lời **không có sẵn** trong dữ liệu trích xuất mà phải do suy diễn mới có.

| # | Câu hỏi (không hình thức) | Thuật ngữ / tiên đề trả lời | Cơ chế |
|---|---|---|---|
| CQ1 | Các vua Việt Nam theo từng triều đại, năm lên ngôi? | `VietnameseMonarch ≡ Monarch ⊓ ∃memberOfDynasty.VietnameseDynasty`, `Monarch ≡ Person ⊓ ∃hasReign.Reign`, chuỗi `hasReign ∘ tenureDynasty ⊑ memberOfDynasty` | lớp định nghĩa + property chain |
| CQ2 | Ông nội của Trần Nhân Tông là ai? | `hasPaternalGrandfather ≡ hasFather ∘ hasFather` | property chain |
| CQ3 | Liệt kê hậu duệ của Trần Thái Tông có trong dữ liệu. | `hasParent ⊑ hasAncestor` (transitive), `hasDescendant ≡ hasAncestor⁻` | transitive + inverse |
| CQ4 | Vua nào trực tiếp cầm quân, trong trận nào? | `MonarchWarrior ≡ Monarch ⊓ MilitaryCommander`, `MilitaryCommander ≡ Person ⊓ ∃commanded.MilitaryConflict`, `commanded ≡ commander⁻` | inverse + giao hai lớp định nghĩa |
| CQ5 | Ai đã tham gia (trực tiếp hoặc qua một trận thành phần) một cuộc chiến tranh? | `commanded ⊑ participatedIn`, `participatedIn ∘ partOfConflict ⊑ participatedIn`, `partOfConflict` transitive | chain + transitive |
| CQ6 | Các vua nhà Trần theo thứ tự thời gian và số năm trị vì? | mẫu n-ary `Reign` (startYear, endYear), luật R4 `durationYears` | n-ary pattern + luật |
| CQ7 | Những trận đánh nào diễn ra trên lãnh thổ một tỉnh/quốc gia? | `conflictPlace ⊑ tookPlaceWithin`, `tookPlaceWithin ∘ locatedIn ⊑ tookPlaceWithin`, `locatedIn` transitive | chain + transitive |
| CQ8 | Danh nhân nào sinh ra trong địa bàn tỉnh Nghệ An (kể cả khi Wikipedia chỉ ghi tên huyện/xã)? | `birthPlace ⊑ bornWithin`, `bornWithin ∘ locatedIn ⊑ bornWithin`, `province ⊑ locatedIn` | chain + subproperty |
| CQ9 | Tỉnh/thành nào (sau sáp nhập 2025) có nhiều đơn vị cấp xã nhất, mật độ dân số bao nhiêu? | `ThirdLevelUnit ≡ AdministrativeUnit ⊓ ∋adminLevel.{3}`, `province ⊑ locatedIn`, luật R5 | hasValue + luật |
| CQ10 | Vua nào trị vì đúng lúc triều đại của mình tham chiến trong một cuộc xung đột? | luật thời gian R6 `reignedDuringConflict` | luật (so sánh năm) |
| CQ11 | Anh chị em và chú/bác/cô của Trần Nhân Tông? | luật R1 `sibling` (x ≠ y), `uncleOrAunt ≡ hasParent ∘ sibling` | luật + chain |
| CQ12 | Những nhân vật thọ từ 100 tuổi trở lên? | luật R2 `ageAtDeath`, R3 `CentenarianPerson` | luật số học |
| CQ13 | Lấy thêm tóm tắt tiếng Anh và dữ liệu DBpedia cho các vua Việt Nam. | `owl:sameAs` tới DBpedia + `SERVICE <https://dbpedia.org/sparql>` | liên kết 5★ + truy vấn liên hợp |
| CQ14 | Vị quân chủ nào có nhiều quan lại (đã phục vụ dưới triều) nhất? | mẫu n-ary `OfficeTenure` + `underMonarch`, chuỗi `holdsOffice ∘ underMonarch ⊑ servedUnder`, `RoyalCourtOfficial` | chain + lớp định nghĩa |
| CQ15 | Ai chịu ảnh hưởng (trực tiếp hoặc gián tiếp) của Nguyễn Du? | `influencedBy ⊑ intellectualLineage` (transitive), `influenced ≡ influencedBy⁻` | inverse + transitive |
| CQ16 | Các huyện đã bị giải thể (từ 1/7/2025) và số xã từng thuộc mỗi huyện? | `SecondLevelUnit ⊑ HistoricalAdministrativeUnit` (tri thức miền: cải cách 2025) | phân loại |
| CQ17 | Dữ liệu có mâu thuẫn không (năm mất trước năm sinh, một thực thể vừa là Người vừa là Địa điểm)? | `Person ⊥ Place`, `hasParent` irreflexive/asymmetric, SHACL `sh:lessThanOrEquals` | kiểm tra nhất quán |
| CQ18 | Bao nhiêu phần trăm thực thể mỗi lớp đã liên kết tới DBpedia? | `owl:sameAs` | thống kê liên kết |
