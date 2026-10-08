"""Unit tests for the Vietnamese infobox value parsers.   Run:  python tests/test_parsers.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from parsers import clean_text, parse_date, parse_number, parse_period, wikilinks_in  # noqa: E402

CASES = [
    (parse_date, "{{birth date|1911|08|25|df=y}}", (1911, 8, 25)),
    (parse_date, "{{ngày mất và tuổi|1820|9|16|1766|1|3}}", (1820, 9, 16)),
    (parse_date, "[[2 tháng 3]] năm [[1946]]", (1946, 3, 2)),
    (parse_date, "năm 257 TCN", (-257, None, None)),
    (parse_date, "16/6/2025<ref name=x/>", (2025, 6, 16)),
    (parse_date, "30 tháng 2 năm 1911", (1911, None, None)),          # invalid day -> year only
    (parse_date, "[[14 tháng 4]], năm 2021", (2021, 4, 14)),          # comma + "năm" (Bernard Madoff)
    (parse_date, "ngày 2", None),                                     # no year at all
    (parse_period, "[[8 tháng 11]] năm [[1278]] &ndash; [[16 tháng 4]] năm [[1293]]", ((1278, 11, 8), (1293, 4, 16))),
    (parse_period, "13 tháng 3 – 7 tháng 5 năm 1954", ((1954, 3, 13), (1954, 5, 7))),
    (parse_period, "257 TCN – 207 TCN", ((-257, None, None), (-207, None, None))),
    (lambda v: parse_number(v, integer=True), "4.412.264 người<ref/>", 4412264),
    (parse_number, "3.942,62 km²", 3942.62),
    (parse_number, "53,72 km²", 53.72),
    (wikilinks_in, "{{plain list| * [[Trần Anh Tông]] * [[thượng Trân Công chúa|X]]}} [[1946]] [[Tập_tin:a.png|22px]]",
     ["Trần Anh Tông", "Thượng Trân Công chúa"]),
    (clean_text, "[[Tập tin:Emblem VPA.svg|25px]]<br>[[Bộ Tổng Tư lệnh|Tổng Tư lệnh]]<ref>x</ref>", "Tổng Tư lệnh"),
]


def main():
    failed = 0
    for fn, arg, want in CASES:
        got = fn(arg)
        ok = got == want
        failed += not ok
        print(f"{'OK  ' if ok else 'FAIL'} {getattr(fn, '__name__', 'fn')}({arg[:45]!r}) = {got!r}" + ("" if ok else f"  expected {want!r}"))
    print(f"{len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
