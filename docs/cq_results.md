# Kết quả các câu hỏi năng lực

Sinh tự động bởi `src/run_cqs.py` trên endpoint `http://localhost:3030/vidbpedia/sparql` (2026-10-08 11:53).
Mỗi bảng chỉ in tối đa 10 dòng đầu.

## CQ1: Các vua Việt Nam theo từng triều đại và năm lên ngôi (VietnameseMonarch là lớp ĐỊNH NGHĨA, được suy diễn)

`queries/cq01_vietnamese_monarchs_by_dynasty.rq` — **189 kết quả**, 246 ms

```sparql
# CQ1: Các vua Việt Nam theo từng triều đại và năm lên ngôi (VietnameseMonarch là lớp ĐỊNH NGHĨA, được suy diễn)
SELECT ?dynastyLabel ?monarchLabel (MIN(xsd:integer(STR(?start))) AS ?firstYear)
WHERE {
  ?m a vidbo:VietnameseMonarch ;
     rdfs:label ?monarchLabel ;
     vidbo:memberOfDynasty ?d ;
     vidbo:hasReign ?r .
  ?d a vidbo:VietnameseDynasty ; rdfs:label ?dynastyLabel .
  OPTIONAL { ?r vidbo:startYear ?start }
}
GROUP BY ?dynastyLabel ?monarchLabel
ORDER BY (!BOUND(?firstYear)) ?firstYear
```

| ?dynastyLabel | ?monarchLabel | ?firstYear |
|---|---|---|
| Hồng Bàng | Lạc Long Quân | -2792 |
| Hồng Bàng | Hùng Vương thứ VI | -1712 |
| Nhà Tiền Lý | Lý Nam Đế | 0544 |
| Nhà Tiền Lý | Lý Thiên Bảo | 0548 |
| Nhà Tiền Lý | Triệu Việt Vương | 0548 |
| Nhà Tiền Lý | Hậu Lý Nam Đế | 0555 |
| Nhà Tiền Lý | Lý Sư Lợi | 0602 |
| Nhà Ngô | Ngô Quyền | 0939 |
| Nhà Ngô | Dương Tam Kha | 0944 |
| Nhà Ngô | Hậu Ngô Vương | 0950 |

## CQ2: Ông nội của Trần Nhân Tông (property chain hasFather ∘ hasFather)

`queries/cq02_paternal_grandfather.rq` — **1 kết quả**, 11 ms

```sparql
# CQ2: Ông nội của Trần Nhân Tông (property chain hasFather ∘ hasFather)
SELECT ?grandfather ?label ?g
WHERE {
  GRAPH ?g { vidbr:Trần_Nhân_Tông vidbo:hasPaternalGrandfather ?grandfather }
  ?grandfather rdfs:label ?label .
}
```

| ?grandfather | ?label | ?g |
|---|---|---|
| vidbr:Trần_Thái_Tông | Trần Thái Tông | http://vi.dbpedia.example.org/graph/inferred |

## CQ3: Hậu duệ của Trần Thái Tông có trong dữ liệu (hasDescendant: nghịch đảo của hasAncestor, bắc cầu)

`queries/cq03_descendants.rq` — **62 kết quả**, 30 ms

```sparql
# CQ3: Hậu duệ của Trần Thái Tông có trong dữ liệu (hasDescendant: nghịch đảo của hasAncestor, bắc cầu)
SELECT ?d ?label ?birthYear
WHERE {
  vidbr:Trần_Thái_Tông vidbo:hasDescendant ?d .
  ?d rdfs:label ?label .
  OPTIONAL { ?d vidbo:birthYear ?birthYear }
}
ORDER BY ?birthYear ?label
```

| ?d | ?label | ?birthYear |
|---|---|---|
| vidbr:An_Tư_Công_chúa | An Tư Công chúa |  |
| vidbr:Bảo_Thánh_Hoàng_hậu | Bảo Thánh Hoàng hậu |  |
| vidbr:Bảo_Từ_Hoàng_hậu | Bảo Từ Hoàng hậu |  |
| vidbr:Huy_Ninh_công_chúa | Huy Ninh công chúa |  |
| vidbr:Huy_Tư_Hoàng_thái_phi | Huy Tư Hoàng thái phi |  |
| vidbr:Hồ_Hán_Thương | Hồ Hán Thương |  |
| vidbr:Khâm_Thánh_Hoàng_hậu | Khâm Thánh Hoàng hậu |  |
| vidbr:Ngô_Sĩ_Liên | Ngô Sĩ Liên |  |
| vidbr:Quang_Loan_Hoàng_hậu | Quang Loan Hoàng hậu |  |
| vidbr:Thiên_Chân_Công_chúa | Thiên Chân Công chúa |  |

## CQ4: Những vị vua Việt Nam trực tiếp cầm quân (MonarchWarrior = Monarch ⊓ MilitaryCommander) và trận đánh

`queries/cq04_monarch_warriors.rq` — **89 kết quả**, 47 ms

```sparql
# CQ4: Những vị vua Việt Nam trực tiếp cầm quân (MonarchWarrior = Monarch ⊓ MilitaryCommander) và trận đánh
SELECT ?monarchLabel (GROUP_CONCAT(DISTINCT ?battleLabel; separator=" | ") AS ?battles)
WHERE {
  ?m a vidbo:MonarchWarrior , vidbo:VietnameseMonarch ;
     rdfs:label ?monarchLabel ;
     vidbo:commanded ?b .
  ?b rdfs:label ?battleLabel .
}
GROUP BY ?monarchLabel
ORDER BY ?monarchLabel
```

| ?monarchLabel | ?battles |
|---|---|
| Bảo Đại | Cao trào kháng Nhật cứu nước / Chiến tranh Đông Dương / Cách mạng Tháng Tám / Phong trào g |
| Duy Tân | Phong trào giải phóng dân tộc Việt Nam (1885–1945) / Vụ mưu khởi nghĩa ở Huế (1916) |
| Dương Tam Kha | Trận Bạch Đằng (938) |
| Dục Đức | Chiến tranh Pháp – Đại Nam |
| Dực Thánh vương | Loạn ba vương |
| Gia Long | Chiến tranh Tây Sơn – Chúa Nguyễn / Chiến tranh Tây Sơn – Chúa Nguyễn (1771–1785) / Chiến  |
| Giản Định Đế | Chiến tranh Minh – Việt (1407–1414) / Trận Bô Cô |
| Hiệp Hòa | Chiến dịch Bắc Kỳ / Chiến tranh Pháp – Đại Nam |
| Hàm Nghi | Chiến dịch Bắc Kỳ / Phong trào Cần Vương / Phong trào giải phóng dân tộc Việt Nam (1885–19 |
| Hậu Lý Nam Đế | Chiến tranh Tiền Lý – Lương (545–550) / Chiến tranh Tùy–Vạn Xuân |

## CQ5: Ai đã tham gia Chiến tranh Nguyên Mông – Đại Việt? (participatedIn ∘ partOfConflict ⊑ participatedIn)

`queries/cq05_participants_of_war.rq` — **12 kết quả**, 37 ms

```sparql
# CQ5: Ai đã tham gia Chiến tranh Nguyên Mông – Đại Việt? (participatedIn ∘ partOfConflict ⊑ participatedIn)
SELECT ?person ?label (GROUP_CONCAT(DISTINCT ?viaLabel; separator=" | ") AS ?commandedIn)
WHERE {
  ?person vidbo:participatedIn <http://vi.dbpedia.example.org/resource/Chiến_tranh_Nguyên_Mông_–_Đại_Việt> ;
          rdfs:label ?label .
  OPTIONAL { ?person vidbo:commanded ?via . ?via rdfs:label ?viaLabel }
}
GROUP BY ?person ?label
ORDER BY ?label
```

| ?person | ?label | ?commandedIn |
|---|---|---|
| vidbr:Hốt_Tất_Liệt | Hốt Tất Liệt | Chiến tranh Mông Cổ – Khwarazm / Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên M |
| vidbr:Mông_Kha | Mông Kha | Chiến tranh Mông Cổ – Cao Ly / Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Môn |
| vidbr:Ngột_Lương_Hợp_Thai | Ngột Lương Hợp Thai | Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Mông – Đại Việt lần 1 / Chiến tran |
| vidbr:Thoát_Hoan | Thoát Hoan | Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Mông – Đại Việt lần 2 / Chiến tran |
| vidbr:Toa_Đô | Toa Đô | Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Mông – Đại Việt lần 2 / Chiến tran |
| vidbr:Trần_Hưng_Đạo | Trần Hưng Đạo | Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Mông – Đại Việt lần 1 / Chiến tran |
| vidbr:Trần_Nhân_Tông | Trần Nhân Tông | Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Mông – Đại Việt lần 2 / Chiến tran |
| vidbr:Trần_Nhật_Duật | Trần Nhật Duật | Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Mông – Đại Việt lần 2 / Chiến tran |
| vidbr:Trần_Quang_Khải | Trần Quang Khải | Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Mông – Đại Việt lần 2 / Chiến tran |
| vidbr:Trần_Thái_Tông | Trần Thái Tông | Chiến tranh Nguyên Mông – Đại Việt / Chiến tranh Nguyên Mông – Đại Việt lần 1 / Trận Bình  |

## CQ6: Các vua nhà Trần theo thứ tự thời gian và số năm trị vì (mẫu n-ary Reign + luật R4)

`queries/cq06_tran_dynasty_reigns.rq` — **29 kết quả**, 27 ms

```sparql
# CQ6: Các vua nhà Trần theo thứ tự thời gian và số năm trị vì (mẫu n-ary Reign + luật R4)
SELECT ?label ?title ?start ?end ?years
WHERE {
  ?m vidbo:memberOfDynasty vidbr:Nhà_Trần ; vidbo:hasReign ?r ; rdfs:label ?label .
  ?r a vidbo:Reign ; vidbo:startYear ?start .
  OPTIONAL { ?r vidbo:endYear ?end }
  OPTIONAL { ?r vidbo:durationYears ?years }
  OPTIONAL { ?r vidbo:title ?title }
}
ORDER BY ?start
```

| ?label | ?title | ?start | ?end | ?years |
|---|---|---|---|---|
| Trần Tự Khánh | Thái úy Đại Việt | 1216 | 1224 | 8.0 |
| Lý Chiêu Hoàng | Hoàng đế Đại Việt | 1224 | 1226 | 2.0 |
| Trần Thừa | Thái thượng hoàng nhà Trần | 1226 | 1234 | 8.0 |
| Trần Thái Tông | Hoàng đế Đại Việt | 1226 | 1258 | 32.0 |
| Trần Thái Tông | Thái thượng hoàng Đại Việt | 1258 | 1277 | 19.0 |
| Trần Thánh Tông | Hoàng đế Đại Việt | 1258 | 1278 | 20.0 |
| Trần Quang Khải | Thừa tướng Đại Việt | 1261 | 1294 | 33.0 |
| Trần Nhật Hiệu | Tể tướng nhà Trần | 1264 | 1268 | 4.0 |
| Trần Thánh Tông | Thái thượng hoàng Đại Việt | 1278 | 1290 | 12.0 |
| Trần Nhân Tông | Hoàng đế Đại Việt | 1278 | 1293 | 15.0 |

## CQ7: Số xung đột diễn ra trong địa bàn từng tỉnh/thành hiện nay (tookPlaceWithin ∘ locatedIn, locatedIn bắc cầu)

`queries/cq07_battles_by_province.rq` — **30 kết quả**, 117 ms

```sparql
# CQ7: Số xung đột diễn ra trong địa bàn từng tỉnh/thành hiện nay (tookPlaceWithin ∘ locatedIn, locatedIn bắc cầu)
SELECT ?provinceLabel (COUNT(DISTINCT ?c) AS ?conflicts) (SAMPLE(?cLabel) AS ?example)
WHERE {
  ?c a vidbo:MilitaryConflict ; vidbo:tookPlaceWithin ?p ; rdfs:label ?cLabel .
  ?p a vidbo:FirstLevelUnit ; rdfs:label ?provinceLabel .
}
GROUP BY ?provinceLabel
ORDER BY DESC(?conflicts)
LIMIT 30
```

| ?provinceLabel | ?conflicts | ?example |
|---|---|---|
| Hà Nội | 14 | Chiến dịch Linebacker II |
| Quảng Trị | 10 | Chiến dịch Kingfisher |
| Điện Biên | 9 | Chiến dịch Điện Biên Phủ |
| Lạng Sơn | 8 | Chiến dịch Biên giới |
| Đồng Nai | 8 | Chiến dịch Hump |
| Đà Nẵng | 7 | Biến động Miền Trung |
| Kon Tum (tỉnh) | 7 | Chiến dịch Bắc Tây Nguyên 1972 |
| Quảng Nam | 7 | Chiến dịch Union |
| Cao Bằng | 6 | Chiến dịch Biên giới |
| Bình Định (tỉnh) | 6 | Chiến dịch Masher |

## CQ8: Danh nhân sinh ra trong địa bàn tỉnh Nghệ An, kể cả khi Wikipedia chỉ ghi huyện/xã (bornWithin ∘ locatedIn)

`queries/cq08_people_born_in_province.rq` — **264 kết quả**, 116 ms

```sparql
# CQ8: Danh nhân sinh ra trong địa bàn tỉnh Nghệ An, kể cả khi Wikipedia chỉ ghi huyện/xã (bornWithin ∘ locatedIn)
SELECT ?person ?label ?birthYear (GROUP_CONCAT(DISTINCT ?placeLabel; separator=", ") AS ?statedBirthPlace)
WHERE {
  ?person vidbo:bornWithin vidbr:Nghệ_An ; rdfs:label ?label .
  OPTIONAL { ?person vidbo:birthYear ?birthYear }
  OPTIONAL { ?person vidbo:birthPlace ?bp . ?bp rdfs:label ?placeLabel }
}
GROUP BY ?person ?label ?birthYear
ORDER BY ?birthYear
```

| ?person | ?label | ?birthYear | ?statedBirthPlace |
|---|---|---|---|
| vidbr:Dương_Thanh_Biểu | Dương Thanh Biểu |  | Nam Đàn (huyện), Nghệ An |
| vidbr:Lê_Hải_Hòa | Lê Hải Hòa |  | Nghệ An |
| vidbr:Nguyễn_Trung_Hanh | Nguyễn Trung Hanh |  | Nghệ An |
| vidbr:Nguyễn_Văn_Nguyên_(Nghệ_An) | Nguyễn Văn Nguyên (Nghệ An) |  | Nghệ An |
| vidbr:Nguyễn_Thị_Hương_Giang | Nguyễn Thị Hương Giang |  | Nghệ An, Quỳnh Lưu (định hướng) |
| vidbr:Nguyễn_Xuân_Diệu | Nguyễn Xuân Diệu |  | Nghệ An, Thanh Chương |
| vidbr:Đặng_Xuân_Loan | Đặng Xuân Loan |  | Nghệ An, Thanh Chương |
| vidbr:Xaysethathirath_II | Xaysethathirath II |  | Việt Nam, Vietnam, Con Cuông (huyện), Nghệ An, Xứ Nghệ, Đàng Ngoài, Đại Việt, Trà Lân (phủ |
| vidbr:Mai_Hắc_Đế | Mai Hắc Đế | 0670 | Nghệ An, Xứ Nghệ, Nghĩa Thái (định hướng) |
| vidbr:Nguyễn_Cảnh_Chân | Nguyễn Cảnh Chân | 1355 | Nghệ An, Thanh Chương |

## CQ9: Các tỉnh/thành cấp 1: số đơn vị cấp xã, dân số, diện tích, mật độ (adminLevel=3 → ThirdLevelUnit; luật R5)

`queries/cq09_province_statistics.rq` — **28 kết quả**, 110 ms

```sparql
# CQ9: Các tỉnh/thành cấp 1: số đơn vị cấp xã, dân số, diện tích, mật độ (adminLevel=3 → ThirdLevelUnit; luật R5)
SELECT ?label ?communes ?population ?area ?density
WHERE {
  { SELECT ?p (COUNT(DISTINCT ?x) AS ?communes) WHERE {
      ?x a vidbo:ThirdLevelUnit ; vidbo:province ?p . } GROUP BY ?p }
  ?p a vidbo:FirstLevelUnit ; rdfs:label ?label .
  OPTIONAL { ?p vidbo:population ?population }
  OPTIONAL { ?p vidbo:area ?area }
  OPTIONAL { ?p vidbo:populationDensity ?density }
}
ORDER BY DESC(?communes)
```

| ?label | ?communes | ?population | ?area | ?density |
|---|---|---|---|---|
| Thanh Hóa | 166 | 4320947 | 11114.71 | 388.8 |
| Phú Thọ | 148 | 4022638 | 9361.38 | 429.7 |
| Gia Lai | 136 | 4182700 | 21580.9 | 193.8 |
| Nghệ An | 130 | 3831694 | 16486.5 | 232.4 |
| Ninh Bình | 129 | 4412264 | 3942.62 | 1119.1 |
| Tuyên Quang | 124 | 1865270 | 13795.5 | 135.2 |
| Lâm Đồng | 124 | 4356400 | 24239.1 | 179.7 |
| Vĩnh Long | 124 | 4257580 | 6296.2 | 676.2 |
| Hưng Yên | 105 | 3752238 | 2514.81 | 1492.1 |
| Đắk Lắk | 102 | 3849200 | 18099.8 | 212.7 |

## CQ10: Vua trị vì đúng lúc triều đại của mình tham chiến (luật thời gian R6)

`queries/cq10_reigned_during_conflict.rq` — **166 kết quả**, 30 ms

```sparql
# CQ10: Vua trị vì đúng lúc triều đại của mình tham chiến (luật thời gian R6)
SELECT ?monarchLabel ?conflictLabel ?year
WHERE {
  ?m vidbo:reignedDuringConflict ?c ; rdfs:label ?monarchLabel .
  ?m a vidbo:VietnameseMonarch .
  ?c rdfs:label ?conflictLabel ; vidbo:startYear ?year .
}
ORDER BY ?year
```

| ?monarchLabel | ?conflictLabel | ?year |
|---|---|---|
| Lý Nam Đế | Chiến tranh Tiền Lý – Lương (545–550) | 0545 |
| Hậu Lý Nam Đế | Chiến tranh Tùy–Vạn Xuân | 0602 |
| Lý Sư Lợi | Chiến tranh Tùy–Vạn Xuân | 0602 |
| Lê Đại Hành | Chiến tranh Việt – Chiêm (982) | 0982 |
| Lê Long Kính | Đại Cồ Việt tấn công nhà Tống | 0995 |
| Lê Long Thâu | Đại Cồ Việt tấn công nhà Tống | 0995 |
| Lê Long Tích | Đại Cồ Việt tấn công nhà Tống | 0995 |
| Lê Long Đinh | Đại Cồ Việt tấn công nhà Tống | 0995 |
| Lê Đại Hành | Đại Cồ Việt tấn công nhà Tống | 0995 |
| Lý Thái Tông | Chiến tranh Việt – Chiêm (1044) | 1044 |

## CQ11: Anh chị em, chú/bác/cô và ông bà của Trần Nhân Tông (luật R1 + chain uncleOrAunt = hasParent ∘ sibling)

`queries/cq11_family_relations.rq` — **20 kết quả**, 34 ms

```sparql
# CQ11: Anh chị em, chú/bác/cô và ông bà của Trần Nhân Tông (luật R1 + chain uncleOrAunt = hasParent ∘ sibling)
SELECT ?relation ?label
WHERE {
  { vidbr:Trần_Nhân_Tông vidbo:sibling ?x . BIND("anh chị em" AS ?relation) }
  UNION
  { vidbr:Trần_Nhân_Tông vidbo:uncleOrAunt ?x . BIND("chú / bác / cô" AS ?relation) }
  UNION
  { vidbr:Trần_Nhân_Tông vidbo:hasGrandparent ?x . BIND("ông / bà" AS ?relation) }
  ?x rdfs:label ?label .
}
ORDER BY ?relation ?label
```

| ?relation | ?label |
|---|---|
| anh chị em | Thiên Thụy Công chúa |
| anh chị em | Trần Quốc Kiện |
| anh chị em | Trần Đức Diệp |
| chú / bác / cô | An Tư Công chúa |
| chú / bác / cô | Thiên Thành Công chúa |
| chú / bác / cô | Thiều Dương Công chúa Trần Thị Thúy |
| chú / bác / cô | Thái Đường Công chúa |
| chú / bác / cô | Thụy Bảo công chúa |
| chú / bác / cô | Trần Doãn |
| chú / bác / cô | Trần Hưng Đạo |

## CQ12: Nhân vật thọ từ 100 tuổi trở lên (luật R2 ageAtDeath, R3 CentenarianPerson)

`queries/cq12_centenarians.rq` — **50 kết quả**, 41 ms

```sparql
# CQ12: Nhân vật thọ từ 100 tuổi trở lên (luật R2 ageAtDeath, R3 CentenarianPerson)
SELECT ?label ?birthYear ?deathYear ?age
WHERE {
  ?p a vidbo:CentenarianPerson ; rdfs:label ?label ;
     vidbo:birthYear ?birthYear ; vidbo:deathYear ?deathYear ; vidbo:ageAtDeath ?age .
}
ORDER BY DESC(?age)
LIMIT 50
```

| ?label | ?birthYear | ?deathYear | ?age |
|---|---|---|---|
| Văn Tư Minh Vương | 0394 | 0519 | 125 |
| Nguyễn Thị Trù | 1893 | 2016 | 123 |
| Jeanne Calment | 1875 | 1997 | 122 |
| Izumi Shigechiyo | 1865 | 1986 | 121 |
| Triệu Vũ Vương | -0257 | -0137 | 120 |
| Nghiêu | -2377 | -2257 | 120 |
| Sarah Knauss | 1880 | 1999 | 119 |
| Trần Thị Viết | 1892 | 2011 | 119 |
| Tanaka Kane | 1903 | 2022 | 119 |
| Lucile Randon | 1904 | 2023 | 119 |

## CQ13: Truy vấn liên hợp: lấy mô tả tiếng Anh và ảnh từ DBpedia cho các vua nhà Lý qua owl:sameAs (cần Internet)

`queries/cq13_federated_dbpedia.rq` — **9 kết quả**, 1698 ms

```sparql
# CQ13: Truy vấn liên hợp: lấy mô tả tiếng Anh và ảnh từ DBpedia cho các vua nhà Lý qua owl:sameAs (cần Internet)
# Jena evaluates the SERVICE block first, so it is restricted to Vietnamese monarchs on the DBpedia side;
# the join with the local data (memberOfDynasty Nhà Lý, owl:sameAs) happens in ViDBpedia.
# (The current DBpedia release no longer publishes dbo:abstract; dbo:description is used instead.)
SELECT ?label ?dbpedia ?descriptionEn ?thumbnail
WHERE {
  SERVICE <https://dbpedia.org/sparql> {
    ?dbpedia <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:Vietnamese_monarchs> .
    OPTIONAL { ?dbpedia <http://dbpedia.org/ontology/description> ?descriptionEn . FILTER(LANG(?descriptionEn) = "en") }
    OPTIONAL { ?dbpedia <http://dbpedia.org/ontology/thumbnail> ?thumbnail }
  }
  ?m owl:sameAs ?dbpedia ;
     vidbo:memberOfDynasty vidbr:Nhà_Lý ;
     a vidbo:Monarch ;
     rdfs:label ?label .
}
ORDER BY ?label
```

| ?label | ?dbpedia | ?descriptionEn | ?thumbnail |
|---|---|---|---|
| Lý Anh Tông | dbr:Lý_Anh_Tông | Vietnamese emperor |  |
| Lý Cao Tông | dbr:Lý_Cao_Tông | Vietnamese emperor |  |
| Lý Chiêu Hoàng | dbr:Lý_Chiêu_Hoàng | Empress regnant of Vietnam from 1224 to 1225 | http://commons.wikimedia.org/wiki/Special:FilePath/Southeast_Asian_history_-_13th_century. |
| Lý Huệ Tông | dbr:Lý_Huệ_Tông | Vietnamese emperor |  |
| Lý Nhân Tông | dbr:Lý_Nhân_Tông | Vietnamese emperor | http://commons.wikimedia.org/wiki/Special:FilePath/Lý_Nhân_Tông.jpg?width=300 |
| Lý Thái Tông | dbr:Lý_Thái_Tông | 2nd emperor of the Lý dynasty | http://commons.wikimedia.org/wiki/Special:FilePath/LýTháiTông.jpg?width=300 |
| Lý Thái Tổ | dbr:Lý_Thái_Tổ | Vietnamese emperor | http://commons.wikimedia.org/wiki/Special:FilePath/Tượng_Lý_Thái_Tổ_2.jpg?width=300 |
| Lý Thánh Tông | dbr:Lý_Thánh_Tông | Vietnamese Emperor | http://commons.wikimedia.org/wiki/Special:FilePath/Lý_Thánh_Tông.jpg?width=300 |
| Lý Thần Tông | dbr:Lý_Thần_Tông | Vietnamese emperor |  |

## CQ14: Vị quân chủ nào có nhiều quan lại nhất (RoyalCourtOfficial ≡ OfficeHolder ⊓ ∃servedUnder.Monarch; servedUnder = holdsOffice ∘ underMonarch)

`queries/cq14_court_officials.rq` — **15 kết quả**, 39 ms

```sparql
# CQ14: Vị quân chủ nào có nhiều quan lại nhất (RoyalCourtOfficial ≡ OfficeHolder ⊓ ∃servedUnder.Monarch; servedUnder = holdsOffice ∘ underMonarch)
SELECT ?monarchLabel (COUNT(DISTINCT ?p) AS ?officials) (GROUP_CONCAT(DISTINCT ?pLabel; separator=" | ") AS ?examples)
WHERE {
  ?p a vidbo:RoyalCourtOfficial ; vidbo:servedUnder ?m ; rdfs:label ?pLabel .
  ?m a vidbo:Monarch ; rdfs:label ?monarchLabel .
}
GROUP BY ?monarchLabel
ORDER BY DESC(?officials)
LIMIT 15
```

| ?monarchLabel | ?officials | ?examples |
|---|---|---|
| Elizabeth II | 30 | Alec Douglas-Home / Andrew Juxon-Smith / Banja Tejan-Sie / Bill Shorten / Boris Johnson /  |
| Victoria của Anh | 21 | Arthur Wellesley, Công tước thứ 2 xứ Wellington / Charles Canning, Bá tước Canning thứ 1 / |
| Norodom Sihanouk | 11 | Chan Nak / Chhean Vam / Hun Sen / Huy Kanthoul / Ieu Koeus / Leng Ngeth / Sisowath Moniret |
| George VI của Anh | 10 | Alexander Cambridge, Bá tước thứ nhất xứ Athlone / Archibald Wavell, Bá tước Wavell thứ 1  |
| George V | 9 | Alexander Cambridge, Bá tước thứ nhất xứ Athlone / Alfred Mond / Charles Hardinge, Nam tướ |
| Edward VII | 9 | Frederic Thesiger, Tử tước Chelmsford thứ 1 / George Curzon, Hầu tước Curzon thứ 1 xứ Kedl |
| George III của Anh | 6 | Charles Cornwallis, Hầu tước Cornwallis thứ 1 / Francis Rawdon-Hastings, Hầu tước thứ 1 xứ |
| Norodom Suramarit | 6 | Ek Yi Oun / Khim Tit / Leng Ngeth / Oum Chheang Sun / San Yun / Sim Var |
| Norodom Sihamoni | 6 | Heng Samrin / Hun Manet / Hun Sen / Pa Socheatvong / Prak Sokhonn / Say Chhum |
| Charles III | 5 | Chris Hipkins / Christopher Luxon / Jeremiah Manele / Keir Starmer / Rishi Sunak |

## CQ15: Ai chịu ảnh hưởng (trực tiếp hoặc gián tiếp) của Nguyễn Du? (influenced = influencedBy⁻, intellectualLineage bắc cầu)

`queries/cq15_literary_influence.rq` — **2 kết quả**, 10 ms

```sparql
# CQ15: Ai chịu ảnh hưởng (trực tiếp hoặc gián tiếp) của Nguyễn Du? (influenced = influencedBy⁻, intellectualLineage bắc cầu)
SELECT ?label ?kind
WHERE {
  ?w vidbo:intellectualLineage vidbr:Nguyễn_Du ; rdfs:label ?label .
  BIND(IF(EXISTS { ?w vidbo:influencedBy vidbr:Nguyễn_Du }, "trực tiếp", "gián tiếp") AS ?kind)
}
ORDER BY ?kind ?label
```

| ?label | ?kind |
|---|---|
| Nguyễn Khắc Xương | gián tiếp |
| Tản Đà | trực tiếp |

## CQ16: Các huyện đã giải thể từ 1/7/2025 (SecondLevelUnit ⊑ HistoricalAdministrativeUnit) theo tỉnh

`queries/cq16_abolished_districts.rq` — **65 kết quả**, 48 ms

```sparql
# CQ16: Các huyện đã giải thể từ 1/7/2025 (SecondLevelUnit ⊑ HistoricalAdministrativeUnit) theo tỉnh
SELECT ?provinceLabel (COUNT(DISTINCT ?d) AS ?abolishedDistricts) (SAMPLE(?dLabel) AS ?example)
WHERE {
  ?d a vidbo:HistoricalAdministrativeUnit ; rdfs:label ?dLabel ; vidbo:province ?p .
  ?p rdfs:label ?provinceLabel .
}
GROUP BY ?provinceLabel
ORDER BY DESC(?abolishedDistricts)
```

| ?provinceLabel | ?abolishedDistricts | ?example |
|---|---|---|
| Thanh Hóa | 31 | Bá Thước (huyện) |
| Nghệ An | 21 | Anh Sơn (huyện) |
| Quảng Nam | 20 | Bắc Trà My |
| Gia Lai | 17 | An Khê (thị xã) |
| Long An (tỉnh) | 17 | Bến Lức (huyện) |
| Đắk Lắk | 16 | Buôn Hồ (thị xã) |
| Cao Bằng | 15 | Bảo Lâm (huyện Cao Bằng) |
| Kiên Giang | 14 | An Biên (huyện) |
| Quảng Ninh | 14 | Ba Chẽ (huyện) |
| Quảng Ngãi | 13 | Ba Tơ (huyện) |

## CQ17: Kiểm tra chất lượng: năm mất trước năm sinh, hoặc vừa là Người vừa là Địa điểm (vi phạm Person ⊥ Place)

`queries/cq17_data_quality.rq` — **100 kết quả**, 417 ms

```sparql
# CQ17: Kiểm tra chất lượng: năm mất trước năm sinh, hoặc vừa là Người vừa là Địa điểm (vi phạm Person ⊥ Place)
SELECT ?x ?label ?problem
WHERE {
  {
    ?x vidbo:birthYear ?b ; vidbo:deathYear ?d .
    FILTER(xsd:integer(STR(?d)) < xsd:integer(STR(?b)))
    BIND("năm mất trước năm sinh" AS ?problem)
  } UNION {
    ?x a vidbo:Person , vidbo:Place .
    BIND("vừa là Person vừa là Place (Person ⊥ Place)" AS ?problem)
  }
  OPTIONAL { ?x rdfs:label ?label }
}
LIMIT 100
```

| ?x | ?label | ?problem |
|---|---|---|
| vidbr:Anna_Freud | Anna Freud | năm mất trước năm sinh |
| vidbr:Hedvig_Sofia_của_Thụy_Điển | Hedvig Sofia của Thụy Điển | năm mất trước năm sinh |
| vidbr:Hiệp_Hòa | Hiệp Hòa | năm mất trước năm sinh |
| vidbr:Cố_Luân_Trang_Tĩnh_Công_chúa | Cố Luân Trang Tĩnh Công chúa | năm mất trước năm sinh |
| vidbr:Cung_Hiến_Hiền_phi | Cung Hiến Hiền phi | năm mất trước năm sinh |
| vidbr:Antonino_Natoli | Antonino Natoli | năm mất trước năm sinh |
| vidbr:Lev_Aleksandrovich_Mey | Lev Aleksandrovich Mey | năm mất trước năm sinh |
| vidbr:Valeriu_Arteni | Valeriu Arteni | năm mất trước năm sinh |
| vidbr:Thrasybulus | Thrasybulus | năm mất trước năm sinh |
| vidbr:Tần_Hầu | Tần Hầu | năm mất trước năm sinh |

## CQ18: Tỷ lệ thực thể của mỗi lớp đã liên kết owl:sameAs tới DBpedia tiếng Anh

`queries/cq18_linking_coverage.rq` — **6 kết quả**, 2051 ms

```sparql
# CQ18: Tỷ lệ thực thể của mỗi lớp đã liên kết owl:sameAs tới DBpedia tiếng Anh
SELECT ?class (COUNT(DISTINCT ?x) AS ?entities) (COUNT(DISTINCT ?linked) AS ?linkedToDBpedia)
       (ROUND(100 * COUNT(DISTINCT ?linked) / COUNT(DISTINCT ?x)) AS ?percent)
WHERE {
  VALUES ?class { vidbo:Person vidbo:Monarch vidbo:MilitaryConflict vidbo:AdministrativeUnit vidbo:State vidbo:Writer }
  ?x a ?class .
  OPTIONAL { ?x owl:sameAs ?d . FILTER(STRSTARTS(STR(?d), "http://dbpedia.org/resource/")) BIND(?x AS ?linked) }
}
GROUP BY ?class
ORDER BY DESC(?entities)
```

| ?class | ?entities | ?linkedToDBpedia | ?percent |
|---|---|---|---|
| vidbo:Person | 58242 | 21988 | 38.0 |
| vidbo:AdministrativeUnit | 4173 | 1452 | 35.0 |
| vidbo:MilitaryConflict | 4048 | 2144 | 53.0 |
| vidbo:Monarch | 3981 | 3358 | 84.0 |
| vidbo:State | 1963 | 1732 | 88.0 |
| vidbo:Writer | 1442 | 1002 | 69.0 |
