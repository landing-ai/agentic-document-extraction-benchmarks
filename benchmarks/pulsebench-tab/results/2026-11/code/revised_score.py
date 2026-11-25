"""Revised (diagnostic) PulseBench-Tab score: Pulse's T-LAG scorer, unchanged, with answer-key
writing conventions ignored on BOTH the answer key and the prediction.

This is not the PulseBench-Tab score. The official score is the unmodified scorer's output
(results/2026-11/scores.json). This script measures how much of the gap to 100 comes from how
printed text is written down (spaces, dot leaders, punctuation width, ...) as opposed to how
the table was read.

How it works
- Imports Pulse's `tlag_scorer.py` (fetched by download_data.py at the pinned commit; not
  redistributed here) and replaces only its `normalize_text` function. The scorer's parsing,
  neighbour-pair extraction, 7th-power text similarity and matching are untouched.
- Every rule is applied identically to the answer key and the prediction.
- `arabic_order`: for Arabic samples only, the prediction is also scored with each row's cells
  in reverse order, and the higher of the two scores is kept, because the answer key stores
  Arabic tables in both column orders.
- With no rule applied the script reproduces the official per-sample scores exactly.

Usage (from the repository root, after download_data.py):
  python benchmarks/pulsebench-tab/results/2026-11/code/revised_score.py \
      --data data/pulsebench-tab \
      --pred benchmarks/pulsebench-tab/results/2026-11/predictions \
      --out revised_scores.json
"""
import argparse, json, re, statistics as st, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

T = None  # tlag_scorer module, loaded per process

# ---- The five formatting rules ----------------------------------------------------------
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎", "0123456789+-=()ni0123456789+-=()")
def spaces(t):  return re.sub(r"\s+", "", t)                                  # all whitespace, incl. words joined at <br>
def hyphens(t): return re.sub(r"[-­‐‑]", "", t)               # hyphens (dashes are mapped to '-' by the scorer first)
def dots(t):
    t = t.replace("…", "")
    t = re.sub(r"(?:\s*\.){2,}", " ", t)                                       # dot leaders ". . ." / "...."
    return re.sub(r"^[\s.:]+|[\s.:]+$", "", t)                                 # stray leading/trailing dots and colons
def supsub(t):  return t.translate(SUP)                                        # super/subscript digits -> plain
def bold(t):    return re.sub(r"\*+|(?<!\w)_{1,2}|_{1,2}(?!\w)", "", t)        # Markdown bold/italic markers

# ---- The six language conventions -------------------------------------------------------
FW = {i: i - 0xFEE0 for i in range(0xFF01, 0xFF5F)}; FW[0x3000] = 0x20
def width(t):   return t.translate(FW)                                         # full-width forms -> ASCII
QT = str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "´": "'", "“": '"', "”": '"'})
def quotes(t):  return t.translate(QT)                                         # curly -> straight quotes
def middot(t):  return re.sub(r"(?<=\d)[·•∙](?=\d)", ".", t)                  # raised-dot decimals 22·7 -> 22.7
AD = {ord(c): str(i) for i, c in enumerate("٠١٢٣٤٥٦٧٨٩")}                     # Arabic-Indic digits -> ASCII (Persian digits deliberately not mapped)
AD.update({ord("ى"): "ي", ord("ی"): "ي", ord("أ"): "ا", ord("إ"): "ا", ord("آ"): "ا", ord("٫"): ",", ord("٬"): ",", ord("ـ"): None})
def arabic(t):  return re.sub(r"[ً-ٰٟ]", "", t).translate(AD)  # vowel marks, letter variants, tatweel, separators
def ditto(t):   return t.replace(",,", "„").replace("〃", "„").replace("″", "„")
def bullets(t): return re.sub(r"[•○◦▪➢●·]\s*", "", t)                          # bullets and middle-dot leaders

FIVE = [supsub, bold, dots, hyphens, spaces]
SIX = [width, quotes, middot, arabic, ditto, bullets]
VARIANTS = {  # name: (rules, accept either Arabic column order)
    "official": ([], False),
    "spaces": ([spaces], False), "hyphens": ([hyphens], False), "dots": ([dots], False),
    "supsub": ([supsub], False), "bold": ([bold], False), "formatting_all_five": (FIVE, False),
    "width": ([width], False), "quotes": ([quotes], False), "middot": ([middot], False),
    "arabic_letters": ([arabic], False), "ditto": ([ditto], False), "bullets": ([bullets], False),
    "arabic_order": ([], True), "conventions_all_six": (SIX, True),
    "revised": (SIX + FIVE, True),
}

def _load(scorer_dir):
    global T, BASE
    if T is None:
        sys.path.insert(0, str(scorer_dir))
        import tlag_scorer
        T = tlag_scorer; BASE = T.normalize_text
    return T

def _norm(fns):
    def n(text):
        t = BASE(text)
        if t == "[NULL]": return t
        for f in fns: t = f(t)
        t = re.sub(r"\s+", " ", t).strip()
        return "[NULL]" if t == "" else t
    return n

def _reverse_columns(h):
    from lxml import html as LH
    d = LH.fromstring(h)
    for tr in d.xpath("//tr"):
        k = list(tr); [tr.remove(x) for x in k]; [tr.append(x) for x in reversed(k)]
    return LH.tostring(d, encoding="unicode")

def _work(a):
    scorer_dir, variant, sid, gt, pred = a
    _load(scorer_dir)
    fns, order = VARIANTS[variant]
    T.normalize_text = _norm(fns) if fns else BASE
    s = T.score_single(gt, pred)["score"]
    if order and sid.startswith("arabic"):
        s = max(s, T.score_single(gt, _reverse_columns(pred))["score"])
    return variant, sid, s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="folder written by download_data.py")
    ap.add_argument("--pred", required=True, help="folder of <sample_id>.html predictions")
    ap.add_argument("--out", default="revised_scores.json")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    data, pred = Path(a.data).resolve(), Path(a.pred)
    preds = {p.stem: p.read_text(encoding="utf-8") for p in sorted(pred.glob("*.html"))}
    tasks = [(data, v, sid, (data / "ground_truth" / f"{sid}.html").read_text(encoding="utf-8"), h)
             for v in VARIANTS for sid, h in preds.items()]
    per = {v: {} for v in VARIANTS}
    with ProcessPoolExecutor(a.workers) as ex:
        for v, sid, s in ex.map(_work, tasks, chunksize=20):
            per[v][sid] = round(s, 6)
    mean = {v: round(st.mean(per[v].values()) * 100, 2) for v in VARIANTS}
    out = {"note": "Diagnostic only. The official PulseBench-Tab score is 'official' (missing samples excluded).",
           "samples_scored": len(preds), "mean_tlag_excl_missing": mean,
           "change_vs_official": {v: round(mean[v] - mean["official"], 2) for v in VARIANTS if v != "official"},
           "per_sample": per}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for v in VARIANTS: print(f"{v:22s} {mean[v]:6.2f}")

if __name__ == "__main__":
    main()
