import requests
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from matplotlib import font_manager
from bidi.algorithm import get_display
import arabic_reshaper
import matplotlib.colors as mcolors
import squarify
import os
import jdatetime  ### NEW: برای تاریخ شمسی

# بررسی وجود فونت
font_path = "X Nazanin Bold.ttf"
if not os.path.exists(font_path):
    print(f"Font file {font_path} not found!")
    exit(1)

# تنظیم فونت فارسی
font_prop = font_manager.FontProperties(fname=font_path)

def bidi_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# لیست صندوق‌های حذف‌شده
excluded_names = [
    "آتیه ملت", "آکورد", "دامون", "فردا", "پاداش", "ارمغان", "فیروزا", "اعتماد", "آلا", "داریک", "هامرز", "افران",
    "امین یکم", "اندوخته داریوش", "اوصتا", "بازده", "بمان", "پارند", "پایا", "تداوم", "ترنج ثابت", "رابین", "نیک گستر",
    "آکام", "آوند", "مانی", "ثبات", "فاخر", "خاتم", "دارا", "آرامش", "یارا", "ارکیده", "اطمینان", "ثابت اکسیژن",
    "پاسارگاد", "پایش", "تصمیم", "توسکا", "ماکان", "نخل", "سام", "شمیم", "کارآمد", "کمند", "کیان", "اونیکس", "کارما",
    "سپنتارود", "ماهور", "نشان", "کارین", "درین", "رشد", "زمرد کوروش", "ساحل", "سپر", "سخند", "سیناد", "سپیدما",
    "ستاره", "بلوط", "خورشید", "طلوع", "کامیاب", "صایند", "گنجینه", "گنجین", "لبخند", "دیبا", "خزانه ملت", "آسامید",
    "اصیل", "هدف", "آسان", "آسود", "صنهال", "اعتبار", "آفاق", "کاج", "رایکا", "کارا", "نیلی", "همای", "همگام", "یاقوت"
]

# درخواست به API با مدیریت خطا
url = "https://rahavard365.com/api/v2/market-data/etf-funds"
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "fa",
    "application-name": "rahavard",
    "referer": "https://rahavard365.com/fund?keyword=",
    "user-agent": "Mozilla/5.0"
}
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()["data"]
except requests.RequestException as e:
    print(f"Error fetching data: {e}")
    exit(1)

# فیلتر صندوق‌ها
filtered = [f for f in data if f["name"] not in excluded_names]
for item in filtered:
    item["change"] = item["real_close_price_change_percent"] * 100

# انتخاب ۷۰ صندوق با بیشترین ارزش معاملات
top_70 = sorted(filtered, key=lambda x: x["value"], reverse=True)[:70]

# استخراج اطلاعات
names = [item["name"] for item in top_70]
values = [item["value"] for item in top_70]
changes = [item["change"] for item in top_70]

# ایجاد پالت رنگی سفارشی (قرمز پررنگ -> سفید -> سبز پررنگ)
colors_list = [
    (1, 0, 0),  # قرمز پررنگ برای -3%
    (1, 1, 1),  # سفید برای 0%
    (0, 0.7, 0) # سبز پررنگ برای +3%
]
cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", colors_list)

# نرمال‌سازی برای نگاشت تغییرات
norm = mcolors.TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3)
colors = [cmap(norm(ch)) for ch in changes]

# رسم نقشه حرارتی با خطوط جداکننده
fig, ax = plt.subplots(figsize=(20, 10))
ax.axis("off")

labels = [f"{bidi_text(n)}\n{c:+.2f}%" for n, c in zip(names, changes)]

squarify.plot(
    sizes=values,
    label=labels,
    color=colors,
    alpha=0.9,
    ax=ax,
    text_kwargs={'fontsize': 11, 'fontproperties': font_prop, 'color': 'black'},
    edgecolor='black',
    linewidth=1.7
)

# عنوان اصلی
plt.title(
    bidi_text("نقشه بازار صندوق‌های قابل معامله (به جز صندوق های درآمد ثابت)"),
    fontproperties=font_prop,
    fontsize=18,
    pad=30  ### NEW: افزایش فاصله برای جا دادن زیرنویس
)

# افزودن تاریخ شمسی به‌عنوان زیرنویس ### NEW
current_date = jdatetime.date.today()
date_str = bidi_text(f"به‌روزرسانی: {current_date.strftime('%Y/%m/%d')}")
fig.text(
    0.5, 0.94,  # موقعیت زیر عنوان
    date_str,
    fontproperties=font_prop,
    fontsize=14,
    ha='center',
    va='center'
)

# افزودن راهنما برای رنگ‌ها
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = plt.colorbar(sm, ax=ax, label=bidi_text("درصد تغییر قیمت"), pad=0.02)
cbar.ax.tick_params(labelsize=10)
cbar.set_label(bidi_text("درصد تغییر قیمت"), fontproperties=font_prop, fontsize=12)

plt.tight_layout()
plt.savefig("heatmap_funds_custom_colors_with_date.png", dpi=300)
plt.show()