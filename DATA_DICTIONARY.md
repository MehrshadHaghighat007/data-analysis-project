<div dir="rtl" align="right">

# فرهنگ داده و خروجی‌ها

<table dir="rtl" align="right">
<thead>
<tr>
<th dir="rtl" align="right">ستون</th>
<th dir="rtl" align="right">معنی و واحد</th>
</tr>
</thead>
<tbody>
<tr>
<td dir="ltr" align="right"><code>path</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">مسیر فایل در آرشیو اصلی؛ کلید یکتای ردیف</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>label</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">فرمان مورد انتظار، استخراج‌شده از نام پوشه</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>speaker_id</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">شناسهٔ ناشناس قبل از <code dir="ltr">_nohash_</code>؛ واحد گروه‌بندی، نه هویت تأییدشدهٔ شخص</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>file_bytes</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">اندازهٔ فایل WAV، بایت</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>file_sha256</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">هش تمام بایت‌های فایل، شامل سربرگ</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>sample_rate</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">نرخ نمونه‌برداری، هرتز</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>channels</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">تعداد کانال؛ در دادهٔ حاضر ۱</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>sample_width_bytes</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">پهنای نمونه به بایت؛ در دادهٔ حاضر ۲، معادل ۱۶ بیت</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>n_samples</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">تعداد نمونهٔ زمانی</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>duration_s</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">طول فایل: تعداد نمونه تقسیم بر نرخ، ثانیه</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>peak</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">بیشینهٔ قدر مطلق دامنه پس از تقسیم PCM بر ۳۲۷۶۸</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>rms</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">ریشهٔ میانگین مربعات دامنهٔ نرمال‌شده به مقیاس ثابت</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>rms_dbfs</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">انرژی نسبی دیجیتال: ۲۰ <code dir="ltr">log10(max(RMS, 1e-12))</code>؛ واحد dBFS، نه فشار صوت فیزیکی</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>dc_offset</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">میانگین دامنهٔ سیگنال؛ بیانگر مؤلفهٔ ثابت</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>zero_fraction</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">سهم نمونه‌هایی که دقیقاً صفر هستند؛ لزوماً سهم سکوت نیست</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>clipping_fraction</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">سهم نمونه‌های برابر با دو حد PCM، یعنی منفی ۳۲۷۶۸ و مثبت ۳۲۷۶۷</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>low_energy_frame_fraction</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">سهم قاب‌های کامل ۲۰ میلی‌ثانیه‌ای با RMS کمتر از منفی ۴۵ dBFS؛ قاب انتهایی ناقص کنار گذاشته می‌شود</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>all_zero</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">آیا تمام نمونه‌های صوت دقیقاً صفرند؟</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>low_energy</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">آیا RMS کل کلیپ زیر آستانهٔ منفی ۴۰ dBFS است؟</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>very_short</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">آیا طول کمتر از ۰٫۲۵ ثانیه است؟</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>pcm_sha256</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">هش نرخ نمونه‌برداری به همراه بایت‌های PCM؛ برای تشخیص موج دقیقاً یکسان</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>split_group</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">شناسهٔ گروه گوینده پس از ادغام احتمالی گویندگان دارای PCM مشترک</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>split</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">train، validation یا test؛ تخصیص قطعی با هش گروه و نمک ثابت</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>exact_duplicate</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">عضویت در گروه موج تکراری؛ تمام اعضا از جمله نسخهٔ منتخب True هستند</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>use_for_analysis</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">انتخاب یک نسخهٔ موج یکتا؛ فقط این ردیف‌ها برای EDA یا مدل استفاده می‌شوند</div></td>
</tr>
<tr>
<td dir="ltr" align="right"><code>clipping_flag</code></td>
<td dir="rtl" align="right"><div dir="rtl" align="right">سهم اشباع حداقل ۰٫۰۰۱، یعنی ۰٫۱ درصد نمونه‌ها</div></td>
</tr>
</tbody>
</table>
<br clear="all">


## معنای سایر فایل‌ها

- <code dir="ltr">read_errors.csv</code>: فایل غیرقابل خواندن یا دارای نام/برچسب نامعتبر؛ در این اجرا فقط سرستون دارد.
- <code dir="ltr">flagged_files.csv</code>: اجتماع پرچم‌ها؛ یک فایل ممکن است چند پرچم داشته باشد، پس جمع شمارش پرچم‌ها تعداد فایل‌های متمایز نیست.
- <code dir="ltr">speaker_class_counts.csv</code>: تعداد هر فرمان برای هر شناسه در دادهٔ خام؛ total جمع فایل‌ها و n_classes تعداد فرمان‌های حاضر است.
- <code dir="ltr">split_summary.csv</code> و <code dir="ltr">class_split_counts.csv</code>: شمارش خام تقسیم‌ها.
- <code dir="ltr">analysis_split_summary.csv</code> و <code dir="ltr">analysis_class_split_counts.csv</code>: شمارش پس از انتخاب موج‌های یکتا.
- <code dir="ltr">train_class_summary.csv</code>: آمار هر کلاس در آموزش یکتا؛ سرستون چندسطحی دارد. خواندن: <code dir="ltr">pd.read_csv(..., header=[0,1], index_col=0)</code>.
- <code dir="ltr">train_descriptive.csv</code>: میانگین، انحراف معیار، صدک‌ها و کران‌ها در آموزش یکتا.
- <code dir="ltr">train_spearman.csv</code>: همبستگی رتبه‌ای، فقط آموزش یکتا.
- <code dir="ltr">energy_threshold_sensitivity.csv</code>: تعداد فایل‌های آموزشی زیر هر آستانه؛ تحلیل حساسیت توصیفی، نه تنظیم آستانه با آزمون.
- <code dir="ltr">plot_examples.csv</code>: فهرست ۲۴ فایل آموزشی با انتخاب قطعی برای نمودارها.
- <code dir="ltr">manual_review.csv</code>: صف پیشنهادی شنود؛ ستون‌های خالی عمداً نشان می‌دهند شنود ثبت نشده است. نسخهٔ تکمیل‌شده را با نام <code dir="ltr">manual_review_completed.csv</code> ذخیره کنید.
- <code dir="ltr">summary.json</code>: خلاصهٔ ماشینی نتایج؛ مقدار train_majority_fraction صرفاً سهم کلاس اکثریت در آموزش است.
- <code dir="ltr">environment.json</code>: نسخه‌های کتابخانه‌های اصلی اجرای تحلیل.
- <code dir="ltr">splits/manifest.csv</code>: مرجع عضویت فایل‌ها؛ ستون use_for_analysis برای کنارگذاشتن تکرارها ضروری است.
- <code dir="ltr">splits/*_files.csv</code>: فهرست تمام فایل‌های خام آن تقسیم؛ برای مدل‌سازی از manifest و فیلتر use_for_analysis استفاده کنید.

**حدود تفسیر:** این شاخص‌ها نسبت سیگنال به نویز واقعی، درستی برچسب، جنسیت، لهجه یا هویت واقعی را مشخص نمی‌کنند. هیچ‌یک از پرچم‌های کم‌انرژی و اشباع موجب حذف خودکار نشده است.

</div>
