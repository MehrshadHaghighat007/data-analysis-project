from pathlib import Path
import argparse, collections, hashlib, io, json, platform, re, urllib.request, wave, zipfile
import numpy as np
import pandas as pd
import scipy
from scipy import signal
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from persian_display import fa, setup_plotting

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def split_for(group, cfg):
    u = int(sha((cfg["split_salt"] + ":" + group).encode())[:16], 16) / 2**64
    return (
        "train"
        if u < cfg["train_fraction"]
        else "validation"
        if u < cfg["train_fraction"] + cfg["validation_fraction"]
        else "test"
    )


def decode(data):
    with wave.open(io.BytesIO(data)) as w:
        sr, channels, width, frames = (
            w.getframerate(),
            w.getnchannels(),
            w.getsampwidth(),
            w.getnframes(),
        )
        pcm = w.readframes(frames)
    if width != 2 or channels != 1 or not frames:
        raise ValueError("قالب غیرمنتظره؛ انتظار PCM تک‌کاناله ۱۶ بیتی و غیرخالی")
    if len(pcm) != frames * width * channels:
        raise ValueError("داده PCM ناقص")
    a = np.frombuffer(pcm, dtype="<i2")
    return a.astype(np.float64) / 32768, sr, channels, width, pcm


def db(x):
    return 20 * np.log10(max(float(x), 1e-12))


def measure(data, cfg):
    x, sr, ch, width, pcm = decode(data)
    k = max(1, round(sr * cfg["frame_ms"] / 1000))
    # فقط قاب‌های کامل: قاب انتهایی ناقص در نسبت قاب کم‌انرژی وارد نمی‌شود.
    frames = x[: len(x) // k * k].reshape(-1, k)
    frms = (
        np.sqrt(np.mean(frames**2, axis=1))
        if len(frames)
        else np.array([np.sqrt(np.mean(x * x))])
    )
    frame_db = 20 * np.log10(np.maximum(frms, 1e-12))
    rms = float(np.sqrt(np.mean(x * x)))
    clipped = (x <= -1) | (x >= 32767 / 32768)
    return dict(
        sample_rate=sr,
        channels=ch,
        sample_width_bytes=width,
        n_samples=len(x),
        duration_s=len(x) / sr,
        peak=float(np.max(np.abs(x))),
        rms=rms,
        rms_dbfs=db(rms),
        dc_offset=float(x.mean()),
        zero_fraction=float(np.mean(x == 0)),
        clipping_fraction=float(clipped.mean()),
        low_energy_frame_fraction=float(
            np.mean(frame_db < cfg["frame_low_energy_dbfs"])
        ),
        all_zero=bool(np.all(x == 0)),
        low_energy=bool(db(rms) < cfg["low_energy_dbfs"]),
        very_short=bool(len(x) / sr < cfg["very_short_seconds"]),
        pcm_sha256=sha(str(sr).encode() + b":" + pcm),
    )


def prepare(root=ROOT):
    root = Path(root)
    for d in ["data", "tables", "figures", "splits", "reports/phase1"]:
        (root / d).mkdir(parents=True, exist_ok=True)
    cfg = json.loads((root / "configs/phase1.json").read_text(encoding="utf-8"))
    archive = root / "data/mini_speech_commands.zip"
    if not archive.exists():
        tmp = archive.with_suffix(".part")
        print("دریافت داده از منبع رسمی ...", flush=True)
        urllib.request.urlretrieve(cfg["dataset_url"], tmp)
        if sha(tmp.read_bytes()) != cfg["archive_sha256"]:
            raise ValueError("هش داده دریافت‌شده مطابق نسخه ثبت‌شده نیست")
        tmp.replace(archive)
    if sha(archive.read_bytes()) != cfg["archive_sha256"]:
        raise ValueError("هش فایل خام تغییر کرده است")
    return cfg, archive


def audit(root=ROOT):
    root = Path(root)
    cfg, archive = prepare(root)
    rows = []
    errors = []
    with zipfile.ZipFile(archive) as z:
        names = sorted(
            n
            for n in z.namelist()
            if n.endswith(".wav") and not n.startswith("__MACOSX/")
        )
        for n in names:
            parts = Path(n).parts
            label = parts[-2]
            filename = parts[-1]
            match = re.fullmatch(r"(.+)_nohash_(\d+)\.wav", filename)
            if label not in cfg["classes"] or not match:
                errors.append(dict(path=n, error="برچسب یا نام فایل نامعتبر"))
                continue
            b = z.read(n)
            try:
                metrics = measure(b, cfg)
            except Exception as e:
                errors.append(dict(path=n, error=str(e)))
                continue
            rows.append(
                dict(
                    path=n,
                    label=label,
                    speaker_id=match.group(1),
                    file_bytes=len(b),
                    file_sha256=sha(b),
                    **metrics,
                )
            )
        readmes = [
            n
            for n in z.namelist()
            if n.endswith("README.md") and not n.startswith("__MACOSX/")
        ]
        if readmes:
            (root / "data/SOURCE_README.md").write_bytes(z.read(readmes[0]))
    df = pd.DataFrame(rows).sort_values("path").reset_index(drop=True)
    # ادغام گویندگان مرتبط با PCM تکراری؛ جلوگیری از عبور نسخه‌های یکسان از مرز تقسیم.
    parent = {s: s for s in sorted(df.speaker_id.unique())}

    def find(s):
        while parent[s] != s:
            parent[s] = parent[parent[s]]
            s = parent[s]
        return s

    for _, g in df.groupby("pcm_sha256", sort=True):
        ids = sorted(g.speaker_id.unique())
        for a in ids[1:]:
            x, y = find(ids[0]), find(a)
            parent[max(x, y)] = min(x, y)
    df["split_group"] = df.speaker_id.map(find)
    df["split"] = df.split_group.map(lambda x: split_for(x, cfg))
    df["exact_duplicate"] = df.duplicated("pcm_sha256", keep=False)
    df["use_for_analysis"] = ~df.duplicated("pcm_sha256", keep="first") & ~df.all_zero
    df["clipping_flag"] = df.clipping_fraction >= cfg["clipping_fraction_threshold"]
    assert df.groupby("speaker_id").split.nunique().max() == 1
    assert df.groupby("pcm_sha256").split.nunique().max() == 1
    assert set(df.label) == set(cfg["classes"])
    assert set(df.split) == {"train", "validation", "test"}
    assert (pd.crosstab(df.label, df.split) > 0).all().all()
    df.to_csv(root / "tables/inventory.csv", index=False)
    pd.DataFrame(errors, columns=["path", "error"]).to_csv(
        root / "tables/read_errors.csv", index=False
    )
    df[
        [
            "path",
            "label",
            "speaker_id",
            "split_group",
            "split",
            "pcm_sha256",
            "use_for_analysis",
        ]
    ].to_csv(root / "splits/manifest.csv", index=False)
    for split, g in df.groupby("split"):
        g[["path"]].to_csv(root / f"splits/{split}_files.csv", index=False)
    speakers = pd.crosstab(df.speaker_id, df.label).reindex(
        columns=cfg["classes"], fill_value=0
    )
    speakers["total"] = speakers.sum(axis=1)
    speakers["n_classes"] = (speakers[cfg["classes"]] > 0).sum(axis=1)
    speakers.to_csv(root / "tables/speaker_class_counts.csv")
    pd.crosstab(df.label, df.split).reindex(cfg["classes"]).to_csv(
        root / "tables/class_split_counts.csv"
    )
    split_summary = df.groupby("split").agg(
        files=("path", "size"), speakers=("speaker_id", "nunique")
    )
    split_summary.to_csv(root / "tables/split_summary.csv")
    train = df[(df.split == "train") & df.use_for_analysis].copy()
    df[df.use_for_analysis].groupby("split").agg(
        files=("path", "size"), speakers=("speaker_id", "nunique")
    ).to_csv(root / "tables/analysis_split_summary.csv")
    pd.crosstab(df[df.use_for_analysis].label, df[df.use_for_analysis].split).to_csv(
        root / "tables/analysis_class_split_counts.csv"
    )
    metrics = [
        "duration_s",
        "rms_dbfs",
        "peak",
        "dc_offset",
        "clipping_fraction",
        "low_energy_frame_fraction",
    ]
    train.groupby("label")[metrics].agg(["mean", "median", "std", "min", "max"]).to_csv(
        root / "tables/train_class_summary.csv"
    )
    train[metrics].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).to_csv(
        root / "tables/train_descriptive.csv"
    )
    train[metrics].corr(method="spearman").to_csv(root / "tables/train_spearman.csv")
    flags = df[
        df.low_energy
        | df.very_short
        | df.clipping_flag
        | df.exact_duplicate
        | df.all_zero
    ].copy()
    flags.to_csv(root / "tables/flagged_files.csv", index=False)
    # آستانه حساسیت فقط روی آموزش: پرچم‌های کیفیت دلیل خودکار حذف نیستند.
    sensitivity = []
    for threshold in [-50, -45, -40, -35]:
        sensitivity.append(
            dict(
                threshold_dbfs=threshold,
                train_clips_below=int((train.rms_dbfs < threshold).sum()),
            )
        )
    pd.DataFrame(sensitivity).to_csv(
        root / "tables/energy_threshold_sensitivity.csv", index=False
    )
    examples = []
    for label in cfg["classes"]:
        g = train[train.label == label].copy()
        g["selection_key"] = g.path.map(lambda p: sha(("examples-v1:" + p).encode()))
        examples.extend(
            g.sort_values("selection_key").head(cfg["examples_per_class"]).path.tolist()
        )
    example_rows = train.set_index("path").loc[examples].reset_index()
    example_rows.to_csv(root / "tables/plot_examples.csv", index=False)
    # صف شنود دستی: داده آزمون وارد این صف نمی‌شود؛ هیچ شنود انسانی ادعا نشده است.
    queue = pd.concat(
        [
            example_rows,
            train.sort_values("rms_dbfs").head(8),
            train.sort_values("clipping_fraction", ascending=False).head(8),
        ]
    ).drop_duplicates("path")
    queue = queue[
        ["path", "label", "speaker_id", "rms_dbfs", "clipping_fraction"]
    ].copy()
    queue["listened"] = ""
    queue["label_correct"] = ""
    queue["audible_noise"] = ""
    queue["notes"] = ""
    queue.to_csv(root / "tables/manual_review.csv", index=False)
    counts = train.label.value_counts().reindex(cfg["classes"])
    majority = counts.idxmax()
    summary = dict(
        dataset="mini_speech_commands",
        archive_sha256=cfg["archive_sha256"],
        analysis_files=int(df.use_for_analysis.sum()),
        analysis_splits=df[df.use_for_analysis].groupby("split").size().to_dict(),
        total_files=len(names),
        valid_files=len(df),
        read_errors=len(errors),
        speakers=int(df.speaker_id.nunique()),
        classes=df.label.value_counts().sort_index().to_dict(),
        sample_rates=df.sample_rate.value_counts().to_dict(),
        channels=df.channels.value_counts().to_dict(),
        duration_min=float(df.duration_s.min()),
        duration_max=float(df.duration_s.max()),
        shorter_than_1s=int((df.duration_s < 1).sum()),
        all_zero=int(df.all_zero.sum()),
        pcm_duplicate_extra=int(df.duplicated("pcm_sha256").sum()),
        pcm_duplicate_members=int(df.exact_duplicate.sum()),
        duplicate_label_conflicts=int(
            (df.groupby("pcm_sha256").label.nunique() > 1).sum()
        ),
        low_energy=int(df.low_energy.sum()),
        clipping_flag=int(df.clipping_flag.sum()),
        very_short=int(df.very_short.sum()),
        splits=split_summary.to_dict("index"),
        train_majority_class=majority,
        train_majority_fraction=float(counts.max() / len(train)),
        train_low_energy=int(train.low_energy.sum()),
        train_clipping=int(train.clipping_flag.sum()),
        train_speaker_median_clips=float(train.groupby("speaker_id").size().median()),
        train_rms_median=float(train.rms_dbfs.median()),
        train_low_frame_median=float(train.low_energy_frame_fraction.median()),
        training_examples_plotted=len(examples),
        manual_listening_completed=False,
        notes="ممیزی ساختاری کل داده؛ تحلیل اکتشافی فقط آموزش؛ هیچ معیار مدل روی آزمون محاسبه نشده است",
    )
    (root / "tables/summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    versions = {
        m: __import__(m).__version__
        for m in ["numpy", "pandas", "scipy", "matplotlib", "arabic_reshaper"]
    }
    versions["python"] = platform.python_version()
    (root / "tables/environment.json").write_text(json.dumps(versions, indent=2))
    make_figures(root, df, train, example_rows, archive, cfg)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return df, summary


def make_figures(root, df, train, examples, archive, cfg):
    setup_plotting(root)
    colors = [
        "#187b8d",
        "#dd8c2b",
        "#6957a6",
        "#be5164",
        "#408e69",
        "#497cb5",
        "#925f43",
        "#747981",
    ]
    labels = cfg["classes"]

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(root / f"figures/{name}.png", dpi=160, bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 3.5))
    c = df.label.value_counts().reindex(labels)
    ax.bar(labels, c.values, color=colors)
    ax.set_ylabel(fa("تعداد فایل"))
    ax.set_title(fa("کل زیرمجموعه: تعداد برابر فایل در هشت کلاس"))
    save(fig, "01_class_balance")
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax, col, title, xl in [
        (axs[0], "duration_s", "توزیع طول کلیپ در آموزش", "ثانیه"),
        (axs[1], "rms_dbfs", "توزیع انرژی در آموزش", "dBFS"),
    ]:
        ax.hist(train[col], bins=35, color="#187b8d", edgecolor="white")
        ax.set_title(fa(title))
        ax.set_xlabel(fa(xl))
        ax.set_ylabel(fa("تعداد"))
    save(fig, "02_distributions")
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.7))
    for ax, col, title in [
        (axs[0], "duration_s", "طول کلیپ بر حسب فرمان؛ آموزش"),
        (axs[1], "rms_dbfs", "انرژی بر حسب فرمان؛ آموزش"),
    ]:
        ax.boxplot(
            [train[train.label == l][col] for l in labels],
            tick_labels=labels,
            showfliers=True,
            flierprops={"markersize": 2},
        )
        ax.set_title(fa(title))
        ax.tick_params(axis="x", rotation=35)
    axs[0].set_ylabel(fa("ثانیه"))
    axs[1].set_ylabel("dBFS")
    save(fig, "03_class_quality")
    s = train.groupby("speaker_id").agg(
        n=("path", "size"), nclasses=("label", "nunique")
    )
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    axs[0].hist(s.n, bins=np.arange(0, s.n.max() + 2) - 0.5, color="#187b8d")
    axs[0].set_xlabel(fa("تعداد کلیپ هر گوینده"))
    axs[1].hist(s.nclasses, bins=np.arange(0.5, 9.5), color="#dd8c2b")
    axs[1].set_xlabel(fa("تعداد فرمان‌های هر گوینده"))
    for ax in axs:
        ax.set_ylabel(fa("تعداد گوینده"))
    fig.suptitle(fa("تنوع و مشارکت گویندگان در آموزش"))
    save(fig, "04_speakers")
    fig, ax = plt.subplots(figsize=(10, 4))
    tab = pd.crosstab(train.speaker_id, train.label).reindex(
        columns=labels, fill_value=0
    )
    top = tab.sum(axis=1).sort_values(ascending=False, kind="stable").head(20).index
    im = ax.imshow(tab.loc[top], aspect="auto", cmap="Blues")
    ax.set_xticks(range(8), labels)
    ax.set_yticks(range(20), [f"S{i + 1:02}" for i in range(20)])
    ax.set_title(fa("۲۰ گوینده با بیشترین کلیپ آموزشی؛ نام‌های نمایشی"))
    fig.colorbar(im, ax=ax, label=fa("تعداد"))
    save(fig, "05_speaker_class")
    numeric = [
        "duration_s",
        "rms_dbfs",
        "peak",
        "clipping_fraction",
        "low_energy_frame_fraction",
    ]
    names = ["طول", "انرژی", "اوج دامنه", "اشباع", "قاب کم‌انرژی"]
    corr = train[numeric].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(6, 4.5))
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(5), [fa(x) for x in names], rotation=25)
    ax.set_yticks(range(5), [fa(x) for x in names])
    for i in range(5):
        for j in range(5):
            ax.text(
                j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9
            )
    ax.set_title(fa("همبستگی اسپیرمن؛ فقط آموزش"))
    fig.colorbar(im, ax=ax)
    save(fig, "06_correlations")
    fig, ax = plt.subplots(figsize=(7, 4))
    for l, c in zip(labels, colors):
        g = train[train.label == l]
        ax.scatter(g.duration_s, g.rms_dbfs, s=7, alpha=0.35, label=l, color=c)
    ax.set_xlabel(fa("طول کلیپ؛ ثانیه"))
    ax.set_ylabel("RMS (dBFS)")
    ax.set_title(fa("رابطه طول و انرژی بر حسب فرمان؛ آموزش"))
    ax.legend(ncol=4, fontsize=8)
    save(fig, "07_duration_energy")
    # سه نمونه برای هر کلاس؛ هر فایل یک موج و یک طیف با مقیاس رنگ مشترک دارد.
    with zipfile.ZipFile(archive) as z:
        for part in range(2):
            fig, axs = plt.subplots(4, 6, figsize=(16, 9))
            for row, l in enumerate(labels[part * 4 : (part + 1) * 4]):
                for j, p in enumerate(examples[examples.label == l].path):
                    x, sr, *_ = decode(z.read(p))
                    a, b = axs[row, j * 2 : j * 2 + 2]
                    a.plot(np.arange(len(x)) / sr, x, lw=0.5, color="#187b8d")
                    a.set_xlim(0, 1)
                    a.set_ylim(-1, 1)
                    a.set_title(f"{l} | {j + 1}", fontsize=9)
                    f, t, power = signal.spectrogram(
                        x,
                        fs=sr,
                        window="hann",
                        nperseg=400,
                        noverlap=240,
                        nfft=512,
                        scaling="density",
                        mode="psd",
                    )
                    b.pcolormesh(
                        t,
                        f / 1000,
                        10 * np.log10(np.maximum(power, 1e-14)),
                        vmin=-100,
                        vmax=-20,
                        cmap="magma",
                        shading="auto",
                    )
                    b.set_xlim(0, 1)
                    b.set_ylim(0, 8)
                    if row == 3:
                        a.set_xlabel(fa("ثانیه"))
                        b.set_xlabel(fa("ثانیه"))
                    if j == 0:
                        a.set_ylabel(fa("دامنه"))
                        b.set_ylabel("kHz")
            fig.suptitle(
                fa("نمونه‌های آموزش: موج و طیف؛ مقیاس طیف از منفی ۱۰۰ تا منفی ۲۰ دسی‌بل"),
                fontsize=13,
            )
            save(fig, f"08_examples_{part + 1}")
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.5))
    axs[0].hist(train.low_energy_frame_fraction, bins=25, color="#187b8d")
    axs[0].set_xlabel(fa("نسبت قاب‌های زیر منفی ۴۵ دسی‌بل"))
    axs[0].set_ylabel(fa("تعداد کلیپ"))
    thresholds = [-50, -45, -40, -35]
    vals = [int((train.rms_dbfs < t).sum()) for t in thresholds]
    axs[1].bar([str(t) for t in thresholds], vals, color="#dd8c2b")
    axs[1].set_xlabel(fa("آستانه انرژی کل کلیپ؛ دسی‌بل"))
    axs[1].set_ylabel(fa("تعداد پرچم کم‌انرژی"))
    save(fig, "09_low_energy")
    counts = pd.crosstab(df.label, df.split).reindex(
        index=labels, columns=["train", "validation", "test"]
    )
    fig, ax = plt.subplots(figsize=(9, 3.8))
    bottom = np.zeros(8)
    for split, color, title in [
        ("train", "#187b8d", "آموزش"),
        ("validation", "#dd8c2b", "اعتبارسنجی"),
        ("test", "#6957a6", "آزمون"),
    ]:
        ax.bar(labels, counts[split], bottom=bottom, label=fa(title), color=color)
        bottom += counts[split].values
    ax.legend()
    ax.set_ylabel(fa("تعداد فایل"))
    ax.set_title(fa("ممیزی تقسیم: گروه‌های گوینده بدون اشتراک"))
    save(fig, "10_splits")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    a = p.parse_args()
    audit(a.root)
