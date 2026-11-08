from pathlib import Path
import json, pandas as pd

R = Path(__file__).resolve().parents[1]
O = R / "reports/phase1"
O.mkdir(parents=True, exist_ok=True)
s = json.loads((R / "tables/summary.json").read_text(encoding="utf-8"))
d = pd.read_csv(R / "tables/inventory.csv")
t = d[(d.split == "train") & d.use_for_analysis]


def table(name, headers, rows, width=None):
    spec = width or "r" * len(headers)
    text = (
        "\\begin{center}\n\\begin{tabular}{"
        + spec
        + "}\n\\toprule\n"
        + " & ".join(headers)
        + " \\\\\n\\midrule\n"
    )
    text += "\n".join(" & ".join(map(str, row)) + " \\\\" for row in rows)
    text += "\n\\bottomrule\n\\end{tabular}\n\\end{center}\n"
    (O / name).write_text(text, encoding="utf-8")


table(
    "overview.tex",
    ["شاخص", "مقدار"],
    [
        ["تعداد فایل خام", s["total_files"]],
        ["موج یکتا برای تحلیل", s["analysis_files"]],
        ["شناسهٔ گوینده", s["speakers"]],
        ["کلاس", 8],
        ["نرخ نمونه‌برداری", r"۱۶۰۰۰ هرتز"],
        ["قالب", "تک‌کاناله، ۱۶ بیت"],
        ["کلیپ کوتاه‌تر از یک ثانیه", s["shorter_than_1s"]],
        ["کمینه و بیشینهٔ طول", "۰٫۴۲۷ و ۱٫۰۰۰ ثانیه"],
    ],
)
table(
    "quality.tex",
    ["بررسی روی کل داده", "تعداد", "تصمیم اولیه"],
    [
        ["خطای خواندن", s["read_errors"], "هیچ مورد"],
        ["نسخهٔ اضافی PCM", s["pcm_duplicate_extra"], "یک نسخه در تحلیل"],
        ["تعارض برچسب تکراری", s["duplicate_label_conflicts"], "هیچ مورد"],
        ["تمام نمونه‌ها صفر", s["all_zero"], "هیچ مورد"],
        ["کمتر از ۰٫۲۵ ثانیه", s["very_short"], "هیچ مورد"],
        ["انرژی کمتر از منفی ۴۰", s["low_energy"], "ثبت و بررسی؛ حفظ"],
        ["اشباع حداقل ۰٫۱ درصد", s["clipping_flag"], "ثبت و بررسی؛ حفظ"],
    ],
)
table(
    "split_table.tex",
    ["بخش", "فایل خام", "فایل تحلیل", "گوینده"],
    [
        [
            title,
            s["splits"][key]["files"],
            s["analysis_splits"][key],
            s["splits"][key]["speakers"],
        ]
        for key, title in [
            ("train", "آموزش"),
            ("validation", "اعتبارسنجی"),
            ("test", "آزمون"),
        ]
    ],
)
g = t.groupby("label").agg(
    n=("path", "size"),
    speakers=("speaker_id", "nunique"),
    energy=("rms_dbfs", "median"),
    quiet=("low_energy", "sum"),
    clip=("clipping_flag", "sum"),
)
table(
    "class_table.tex",
    ["فرمان", "تعداد", "گوینده", "میانه انرژی", "کم‌انرژی", "اشباع"],
    [
        [
            r"\lr{" + l + "}",
            int(a.n),
            int(a.speakers),
            r"\lr{" + f"{a.energy:.2f}" + "}",
            int(a.quiet),
            int(a["clip"]),
        ]
        for l, a in g.iterrows()
    ],
)
macros = {
    "TrainCount": s["analysis_splits"]["train"],
    "ValCount": s["analysis_splits"]["validation"],
    "TestCount": s["analysis_splits"]["test"],
    "LowTrain": s["train_low_energy"],
    "ClipTrain": s["train_clipping"],
    "MajorityPct": f"{100 * s['train_majority_fraction']:.2f}",
}
(O / "numbers.tex").write_text(
    "\n".join("\\newcommand{\\" + k + "}{" + str(v) + "}" for k, v in macros.items()),
    encoding="utf-8",
)
