from pathlib import Path
import re
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import arabic_reshaper
from bidi.algorithm import get_display


def fa(text):
    import matplotlib
    from packaging.version import Version

    text = str(text)

    # نسخه‌های جدید خودشان حروف و جهت فارسی را تنظیم می‌کنند.
    if Version(matplotlib.__version__) >= Version("3.11"):
        return text

    # سازگاری با نسخه‌های قدیمی
    return get_display(arabic_reshaper.reshape(text), base_dir="R")


def setup_plotting(root=None):
    """فونت محلی با پشتیبانی فارسی؛ بدون دانلود اینترنتی فونت."""
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    for file in (root / "reports/phase1/fonts").glob("*.ttf"):
        fm.fontManager.addfont(str(file))
    available = {font.name for font in fm.fontManager.ttflist}
    font = next(
        (
            name
            for name in [
                "Vazirmatn",
                "Vazir",
                "IRANSans",
                "Noto Naskh Arabic",
                "Noto Sans Arabic",
                "Tahoma",
                "DejaVu Sans",
            ]
            if name in available
        ),
        "DejaVu Sans",
    )
    plt.rcParams.update(
        {
            "font.family": font,
            "font.size": 10,
            "axes.unicode_minus": False,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 120,
            "text.usetex": False,
        }
    )
    return font


def T(ax, title=None, xl=None, yl=None):
    """تمام عنوان‌ها و برچسب‌های فارسی جدید را از این تابع عبور دهید."""
    if title is not None:
        ax.set_title(fa(title), fontsize=12, fontweight="bold")
    if xl is not None:
        ax.set_xlabel(fa(xl))
    if yl is not None:
        ax.set_ylabel(fa(yl))


NOTEBOOK_CSS = """
<style>
.fa-box, .fa-table { direction: rtl; text-align: right;
    font-family: Vazirmatn, Vazir, Tahoma, 'DejaVu Sans', sans-serif; line-height: 1.9; }
.fa-table { overflow-x: auto; max-width: 100%; }
.fa-table table.dataframe { direction: rtl; font-family: inherit; margin: 0 0 1em auto; }
.fa-table table.dataframe th, .fa-table table.dataframe td {
    text-align: right !important; unicode-bidi: plaintext; white-space: nowrap; }
.fa-box code, .fa-box pre { direction: ltr; unicode-bidi: isolate; }
.fa-box { border-right: 4px solid #187b8d; padding: 10px 16px; }
</style>
"""


def setup_notebook(root=None):
    from IPython.display import HTML, display
    import pandas as pd

    font = setup_plotting(root)
    pd.set_option("display.max_columns", 40)
    pd.set_option("display.width", 160)
    display(HTML(NOTEBOOK_CSS))
    print("فونت نمودار:", font)
    return font


def display_table(value):
    """متن HTML را reshape نکنید؛ مرورگر اتصال حروف و جهت را انجام می‌دهد."""
    import pandas as pd
    from IPython.display import HTML, display

    if isinstance(value, pd.Series):
        value = value.to_frame()
    if not isinstance(value, pd.DataFrame):
        raise TypeError("display_table expects a pandas DataFrame or Series")
    html = value.to_html(escape=True, max_rows=30, max_cols=40)
    display(HTML(NOTEBOOK_CSS + '<div class="fa-table" dir="rtl">' + html + "</div>"))
