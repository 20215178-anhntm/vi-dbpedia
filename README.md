# ViDBpedia — DBpedia tiếng Việt

Đồ thị tri thức Linked Data 5★ về **lịch sử, địa lý và danh nhân Việt Nam**, xây dựng từ Wikipedia tiếng Việt
theo đúng quy trình của DBpedia:

| Bước đề bài | Thành phần trong dự án |
|---|---|
| 1. Định nghĩa ontology | [`ontology/vidbo.ttl`](ontology/vidbo.ttl) (OWL 2 DL), [`ontology/shapes.ttl`](ontology/shapes.ttl) (SHACL), [`rules/`](rules/) (luật SPARQL), [`docs/competency_questions.md`](docs/competency_questions.md) |
| 2. Thu thập bài viết Wikipedia | [`src/collect_dump.py`](src/collect_dump.py) (dump XML + SQL của Wikimedia) |
| 3. Chuyển sang dữ liệu 4★ | [`mappings/infobox_mappings.yaml`](mappings/infobox_mappings.yaml), [`src/extract.py`](src/extract.py), [`src/parsers.py`](src/parsers.py), [`src/reason.py`](src/reason.py), [`src/validate.py`](src/validate.py) |
| 4. Liên kết tới DBpedia tiếng Anh | [`src/link.py`](src/link.py), [`linking/silk_vidbpedia_dbpedia.xml`](linking/silk_vidbpedia_dbpedia.xml) |
| 5. SPARQL endpoint / terminal | Apache Jena Fuseki ([`endpoint/`](endpoint/)), web UI ([`web/app.py`](web/app.py)), CLI ([`src/query.py`](src/query.py)), câu truy vấn [`queries/`](queries/) |

Báo cáo chi tiết: [`docs/BAO_CAO.md`](docs/BAO_CAO.md).

## Cài đặt

Yêu cầu: Python ≥ 3.10, Java ≥ 17 (cho Fuseki), ~3 GB dung lượng đĩa.

```bash
pip install -r requirements.txt
```

Apache Jena Fuseki 5.6.0 được đặt trong `endpoint/apache-jena-fuseki-5.6.0/`
(tải tại https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-5.6.0.zip nếu chưa có).

## Chạy toàn bộ pipeline

```bash
# 0. Tải dump Wikipedia tiếng Việt (~1.4 GB)
mkdir -p data/dumps && cd data/dumps
for f in pages-articles.xml.bz2 langlinks.sql.gz page_props.sql.gz; do
  curl -O https://dumps.wikimedia.org/viwiki/latest/viwiki-latest-$f; done
cd ../..

# Chạy tất cả (~1,5 giờ):  python run_pipeline.py      (hoặc --from reason, --skip link)
python src/collect_dump.py        # 2. lọc bài theo infobox/thể loại + mở rộng theo liên kết   (~15 phút)
python src/extract.py             # 3. infobox -> RDF (data/rdf/*.ttl)                          (~5 phút)
python src/reason.py              # 3b. suy diễn OWL 2 RL + luật -> data/rdf/inferred.ttl
python src/validate.py            # 3c. kiểm tra SHACL -> data/rdf/shacl_report.json
python src/link.py                # 4. owl:sameAs tới DBpedia (cần Internet)
python src/load_endpoint.py       # 5a. nạp vào Fuseki TDB2 (4 named graph)
python src/serve.py               # 5b. Fuseki :3030 + Web UI :5000
```

## Sử dụng

* Web: http://127.0.0.1:5000 — trang tài nguyên kiểu DBpedia (`/page/Trần_Hưng_Đạo`), editor SPARQL, duyệt ontology.
* URI dereference (Linked Data): `curl -L -H "Accept: text/turtle" http://127.0.0.1:5000/resource/Trần_Hưng_Đạo`
* SPARQL endpoint: `http://localhost:3030/vidbpedia/sparql` (hoặc `http://127.0.0.1:5000/sparql`)
* Terminal:
  ```bash
  python src/query.py --list        # danh sách câu hỏi năng lực
  python src/query.py --cq 2        # chạy câu hỏi số 2
  python src/query.py "SELECT ?v WHERE { ?v a vidbo:VietnameseMonarch } LIMIT 10"
  python src/query.py               # chế độ tương tác
  ```
* Protégé: mở `ontology/vidbo.ttl` (+ `ontology/examples/tran_dynasty_sample.ttl`), chạy HermiT.
* Kiểm thử: `python tests/test_hermit.py` (HermiT trên tập mẫu nhà Trần), `python tests/test_parsers.py` (bộ phân tích giá trị),
  `python src/run_cqs.py` (chạy 18 câu hỏi năng lực → `docs/cq_results.md`).

> Trên Windows nên mở `http://127.0.0.1:5000` thay vì `localhost:5000` (localhost thử IPv6 trước nên chậm ~2 giây mỗi trang).

## Không gian tên

| Prefix | IRI |
|---|---|
| `vidbo:` | `http://vi.dbpedia.example.org/ontology/` |
| `vidbr:` | `http://vi.dbpedia.example.org/resource/` |
| named graphs | `http://vi.dbpedia.example.org/graph/{ontology,data,inferred,links}` |

Dữ liệu có nguồn gốc từ Wikipedia tiếng Việt, giấy phép CC BY-SA 4.0.
