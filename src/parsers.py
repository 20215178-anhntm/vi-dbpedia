"""Value parsers for Vietnamese Wikipedia infobox fields (dates, numbers, periods, links)."""
import calendar
import re

import mwparserfromhell as mw

IGNORED_NS = ("tập tin:", "file:", "hình:", "image:", "thể loại:", "category:", "bản mẫu:",
              "template:", "wikipedia:", "wp:", "commons:", "wikt:", "s:", "q:", ":")

DATE_LINK = re.compile(r"^(\d{1,4}( TCN)?|\d{1,2} tháng \d{1,2}|tháng \d{1,2}|năm \d+|thập niên .*|thế kỷ .*|"
                       r"\d+ tháng \d+ năm \d+)$", re.I)

DATE_TEMPLATES = {"birth date", "death date", "birth date and age", "death date and age", "ngày sinh",
                  "ngày mất", "ngày sinh và tuổi", "ngày mất và tuổi", "start date", "end date",
                  "date", "dts", "birth-date", "death-date", "start date and age", "end date and age",
                  "birth year and age", "death year and age", "năm sinh và tuổi", "năm mất và tuổi",
                  "birth year", "death year", "bda", "dda", "ngày", "film date"}


def is_ignored(link_target):
    """File / category / template ... links ('Tập_tin:', 'Tập tin :', ':Category:' all count)."""
    t = re.sub(r"[\s_]+", " ", link_target).strip().lower()
    t = re.sub(r"\s*:\s*", ":", t)
    return t.startswith(IGNORED_NS)


def norm_title(t):
    """MediaWiki title normalisation: underscores->spaces, strip, drop fragment, uppercase first letter."""
    t = t.split("#", 1)[0].replace("_", " ").strip()
    t = re.sub(r"\s+", " ", t)
    return t[:1].upper() + t[1:] if t else t


def wikilinks_in(value):
    """Titles of article links inside a wikicode value (recursing into templates like {{plainlist}})."""
    if isinstance(value, str):
        value = mw.parse(value)
    out = []
    for wl in value.filter_wikilinks(recursive=True):
        t = str(wl.title).strip()
        if not t or is_ignored(t):
            continue
        t = norm_title(t)
        if not t or DATE_LINK.match(t):
            continue
        if t not in out:
            out.append(t)
    # {{ill|Target|vi}} / {{Liên kết ngôn ngữ|...}} interlanguage helpers
    for tpl in value.filter_templates(recursive=True):
        n = str(tpl.name).strip().lower()
        if n in ("ill", "interlanguage link", "ill2", "liên kết liên ngôn ngữ") and tpl.has(1):
            t = norm_title(str(tpl.get(1).value))
            if t and t not in out:
                out.append(t)
    return out


REF = re.compile(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", re.S | re.I)
COMMENT = re.compile(r"<!--.*?-->", re.S)
TAGS = re.compile(r"<[^>]+>")


def clean_text(value):
    """Plain text of a wikicode value: drops refs, comments, templates, files; keeps link text."""
    s = str(value)
    s = COMMENT.sub("", s)
    s = REF.sub("", s)
    s = re.sub(r"<br\s*/?>", ", ", s, flags=re.I)
    code = mw.parse(s)
    for wl in code.filter_wikilinks(recursive=True):  # images keep their "22px|caption" text otherwise
        if is_ignored(str(wl.title)):
            try:
                code.remove(wl)
            except ValueError:
                pass
    # keep the text of list-like templates (plainlist / ubl / hlist) before stripping
    for tpl in code.filter_templates(recursive=False):
        n = str(tpl.name).strip().lower()
        if n in ("plainlist", "plain list", "ubl", "unbulleted list", "hlist", "flatlist", "ublist", "nowrap", "lang", "nobold"):
            inner = ", ".join(str(p.value) for p in tpl.params if not str(p.name).strip().startswith(("class", "style")))
            inner = re.sub(r"\s*\*+\s*", ", ", inner)
            try:
                code.replace(tpl, inner)
            except ValueError:
                pass
    s = code.strip_code(normalize=True, collapse=True)
    s = TAGS.sub("", s)
    s = s.replace("&nbsp;", " ").replace("&ndash;", "–").replace("&mdash;", "—")
    s = re.sub(r"^\s*[*#:]+\s*", "", s, flags=re.M)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", ", ", s)
    s = re.sub(r"(,\s*)+", ", ", s)
    return s.strip(" ,;'\"")


# ---------------------------------------------------------------- dates

def _year(y, bce=False):
    y = int(y)
    return -y if bce else y


def fmt_year(y):
    return f"-{abs(y):04d}" if y < 0 else f"{y:04d}"


def _valid(y, m, d):
    if not (1 <= m <= 12 and 1 <= d <= 31 and -3000 < y < 2100):
        return False
    if y > 0:
        return d <= calendar.monthrange(y, m)[1]
    return True


def parse_date(value):
    """Return (year, month, day) with month/day possibly None, or None.

    Handles {{birth date|1911|08|25}}, {{ngày sinh|1766|1|3}}, "25 tháng 8 năm 1911",
    "[[2 tháng 3]] năm [[1946]]", "1258", "năm 257 TCN", "25/8/1911", "1911-08-25".
    """
    if value is None:
        return None
    code = value if not isinstance(value, str) else mw.parse(value)
    for tpl in code.filter_templates(recursive=True):
        n = str(tpl.name).strip().lower()
        if n in DATE_TEMPLATES:
            nums = []
            for p in tpl.params:
                if p.showkey:
                    continue
                v = str(p.value).strip()
                if re.fullmatch(r"-?\d{1,4}", v):
                    nums.append(int(v))
            if nums:
                y = nums[0]
                m = nums[1] if len(nums) > 1 else None
                d = nums[2] if len(nums) > 2 else None
                if m and d and _valid(y, m, d):
                    return (y, m, d)
                return (y, None, None)
    text = clean_text(code) if not isinstance(value, str) else clean_text(value)
    return parse_date_text(text)


def parse_date_text(text):
    if not text:
        return None
    t = text.lower()
    bce = bool(re.search(r"\b(tcn|trước công nguyên|bc|bce)\b", t))
    sep = r"\s*,?\s*(?:năm)?\s*,?\s*"  # "5 tháng 3 năm 1990", "14 tháng 4, năm 2021", "5 tháng 3, 1990"
    m = re.search(r"(\d{1,2})\s*tháng\s*(\d{1,2})" + sep + r"(\d{1,4})", t)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), _year(m.group(3), bce)
        if _valid(y, mo, d):
            return (y, mo, d)
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", t)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if _valid(y, mo, d):
            return (y, mo, d)
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{3,4})\b", t)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if _valid(y, mo, d):
            return (y, mo, d)
    m = re.search(r"tháng\s*(\d{1,2})" + sep + r"(\d{3,4})", t)
    if m:
        return (_year(m.group(2), bce), None, None)
    # a bare year: prefer "năm N", then any 3-4 digit number; 1-2 digits only if that is all there is
    m = (re.search(r"năm\s*(\d{1,4})\b", t) or re.search(r"\b(\d{3,4})\b", t)
         or re.fullmatch(r"\s*(\d{1,2})\s*(?:tcn|trước công nguyên)?\s*", t))
    if m:
        y = _year(m.group(1), bce)
        if -3000 < y < 2100 and y != 0:
            return (y, None, None)
    return None


PERIOD_SPLIT = re.compile(r"\s*(?:–|—|&ndash;|&mdash;|−|\s-\s|đến|tới|\bto\b)\s*")


def parse_period(value):
    """'[[8 tháng 11]] năm [[1278]] – [[16 tháng 4]] năm [[1293]]' -> ((1278,11,8),(1293,4,16))."""
    s = str(value)
    s = COMMENT.sub("", REF.sub("", s))
    # drop {{số năm theo năm và ngày|...}} duration helpers which contain both dates
    code = mw.parse(s)
    for tpl in code.filter_templates(recursive=False):
        n = str(tpl.name).strip().lower()
        if n.startswith(("số năm", "age", "tuổi", "years", "duration")):
            try:
                code.remove(tpl)
            except ValueError:
                pass
    text = clean_text(code)
    text = re.sub(r"\(.*?\)", "", text)
    parts = [p for p in PERIOD_SPLIT.split(text, maxsplit=1) if p.strip()]
    if not parts:
        return None, None
    bce_all = bool(re.search(r"\b(tcn|trước công nguyên)\b", text.lower()))
    start = parse_date_text(parts[0] + (" TCN" if bce_all and "tcn" not in parts[0].lower() else ""))
    end = parse_date_text(parts[1]) if len(parts) > 1 else None
    if end and (start is None or start[0] != end[0] and start[1] is None and start[0] < 13):
        # "13 tháng 3 – 7 tháng 5 năm 1954": the year is only written once, after the end date
        m = re.search(r"(\d{1,2})\s*tháng\s*(\d{1,2})", parts[0])
        if m and _valid(end[0], int(m.group(2)), int(m.group(1))):
            start = (end[0], int(m.group(2)), int(m.group(1)))
    return start, end


# ---------------------------------------------------------------- numbers

def parse_number(value, integer=False):
    """Vietnamese formatting: '4.412.264 người' -> 4412264 ; '3.942,62 km²' -> 3942.62."""
    text = clean_text(value) if not isinstance(value, str) else clean_text(mw.parse(value))
    m = re.search(r"\d[\d.,\s]*", text)
    if not m:
        return None
    s = m.group(0).strip().replace(" ", "")
    s = s.rstrip(".,")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        parts = s.split(",")
        s = s.replace(",", ".") if len(parts) == 2 and len(parts[1]) != 3 else s.replace(",", "")
    elif "." in s:
        parts = s.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
            s = s.replace(".", "")
    try:
        x = float(s)
    except ValueError:
        return None
    mult = 1
    low = text.lower()
    if re.search(r"\d\s*(triệu|million)", low):
        mult = 1_000_000
    elif re.search(r"\d\s*(tỷ|tỉ|billion)", low):
        mult = 1_000_000_000
    x *= mult
    return int(round(x)) if integer else round(x, 4)


def abstract_of(wikitext, max_chars=700):
    """First paragraph of the article as plain text."""
    lead = re.split(r"\n==[^=]", wikitext, maxsplit=1)[0]
    code = mw.parse(lead)
    for tpl in code.filter_templates(recursive=False):
        try:
            code.remove(tpl)
        except ValueError:
            pass
    for wl in code.filter_wikilinks(recursive=False):
        if is_ignored(str(wl.title)):
            try:
                code.remove(wl)
            except ValueError:
                pass
    s = COMMENT.sub("", REF.sub("", str(code)))
    s = re.sub(r"\{\|.*?\|\}", "", s, flags=re.S)  # tables
    for para in s.split("\n\n"):
        txt = clean_text(mw.parse(para))
        txt = re.sub(r"\(\s*[,;]?\s*\)", "", txt).strip()
        if len(txt) > 40:
            if len(txt) > max_chars:
                cut = txt[:max_chars].rsplit(". ", 1)[0]
                txt = cut + "."
            return txt
    return None
