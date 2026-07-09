# Biznex POS — Deploy qo'llanmasi

Loyiha endi ikki holatda ishlaydi: **veb-sayt (Railway)** va **Windows desktop dastur (.exe)**.
Desktop dastur **HAR DOIM mahalliy (offline)** ishlaydi — internet bo'lmasa ham hech qanday
xatosiz to'liq ishlayveradi. Internet bo'lganda esa fon rejimida saytga **sinxronlanadi**:
mahalliyda kiritilgan yangi narsalar saytga yuboriladi, saytda o'zgargan/qo'shilgan narsalar esa
(masalan mahsulot narxi, yangi xodim) mahalliyga tushadi. Bu darhol emas, balki internet bilan
keyingi ulanishda (odatda ~45 soniya ichida yoki "Sozlamalar" sahifasidagi "Hozir sinxronlash"
tugmasi bilan) sodir bo'ladi.

---

## 0. GitHub'ga yuklash (birinchi marta)

1. [github.com](http://github.com) da ro'yxatdan o'ting (agar hali yo'q bo'lsa).
2. Yuqori o'ng burchakda **+ → New repository** bosing. Nomini masalan `biznex-pos` deb qo'ying, **Private** tanlang, **Create repository** bosing.
3. Kompyuteringizda [Git](http://git-scm.com/downloads) o'rnatilganiga ishonch hosil qiling.
4. Loyiha papkasida (`biznex_v2` ichida) terminal/CMD oching va quyidagini bajaring:
   ```
   git init
   git add .
   git commit -m "Birinchi versiya"
   git branch -M main
   git remote add origin http://github.com/FOYDALANUVCHI_NOMI/biznex-pos.git
   git push -u origin main
   ```
   (`FOYDALANUVCHI_NOMI` o'rniga o'z GitHub nomingizni yozing — bu manzil repository yaratilgan sahifada ko'rsatiladi.)

---

## 1. Railway'ga deploy qilish

1. [railway.app](http://railway.app) ga kiring, **"Login with GitHub"** orqali ro'yxatdan o'ting (shu bitta tugma bilan, alohida parol kerak emas).
2. **New Project → Deploy from GitHub repo** ni bosing, `biznex-pos` repositoriyangizni tanlang.
3. Railway avtomatik `requirements.txt` va `Procfile`ni topib, build qila boshlaydi.
4. **PostgreSQL qo'shish** (saytning o'z bazasi uchun, tavsiya etiladi):
   - Loyiha ichida **+ New → Database → Add PostgreSQL** bosing.
   - Railway avtomatik `DATABASE_URL` degan o'zgaruvchini yaratadi va web-servisga ulaydi — qo'shimcha sozlash shart emas.
5. Web-servis (`biznex-pos`) ustiga bosib, **Variables** bo'limida qo'shing:
   - `SECRET_KEY` — uzun tasodifiy qiymat
   - `DEBUG` — `False`
   - `SYNC_API_KEY` — o'zingiz o'ylab topgan uzun, tasodifiy maxfiy kalit (masalan 32+ belgili tasodifiy satr). **Bu kalitni desktop `config.json`dagi `sync_api_key` bilan AYNAN bir xil qilib yozishingiz shart** — aks holda sinxronlash ishlamaydi. Buni hech kimga bermang: bu kalitsiz hech kim sizning ma'lumotlaringizga /sync/ orqali murojaat qila olmaydi.
6. **Settings → Networking → Generate Domain** bosing — sizga `http://biznex-pos-production.up.railway.app` kabi ochiq manzil beriladi. Shu manzilni **telefondan** ochib ko'rishingiz mumkin.
7. Birinchi marta demo ma'lumotlarni tozalab, kassir yaratish uchun Railway'ning **Shell** (loyiha sahifasida "..." menyu → "Open Shell" yoki CLI orqali `railway run python seed_demo.py`) orqali bajaring.

---

## 2. Desktop dasturni saytga sinxronlashga ulash

`.exe` yig'ilgach, uning yonida `config.json` fayli paydo bo'ladi:
```json
{
  "remote_url": "",
  "sync_api_key": ""
}
```
Shu faylni ochib, ikkalasini ham to'ldiring:
```json
{
  "remote_url": "https://biznex-pos-production.up.railway.app",
  "sync_api_key": "Railway'da SYNC_API_KEY ga yozgan xuddi shu maxfiy kalit"
}
```
Saqlang va `.exe`ni qayta oching. **Diqqat: dastur baribir HAR DOIM mahalliy oynani ko'rsatadi**
(sayt to'g'ridan-to'g'ri ochilmaydi) — `remote_url` endi faqat fon rejimida ma'lumot almashish
uchun ishlatiladi. Bu quyidagicha ishlaydi:
- Mahalliyda yaratilgan yangi buyurtma/tranzaksiya/ombor yozuvi — internet bor bo'lganda avtomatik saytga yuboriladi.
- Saytda (yoki boshqa filialdagi kompyuterda) qo'shilgan/o'zgartirilgan mahsulot, xodim, narx va h.k. — internet bor bo'lganda avtomatik mahalliyga tushadi.
- Ikkalasi ham darhol emas, balki fon rejimida ~45 soniyada bir marta yoki **Sozlamalar** sahifasidagi "Hozir sinxronlash" tugmasi bilan sodir bo'ladi.
- Internet bo'lmasa — hech qanday xatolik chiqmaydi, dastur to'liq mahalliy bazada ishlashda davom etadi, keyingi ulanishda o'zgarishlar avtomatik yuboriladi/olinadi.

Agar `remote_url` yoki `sync_api_key` bo'sh qoldirilsa, dastur faqat **mahalliy rejimda**
(sinxronlashsiz, faqat shu kompyuterda) ishlayveradi.

---

## 3. Windows uchun .exe yig'ish (avvalgidek)

```
cd biznex_v2
desktop\build.bat
```
Batafsil: yuqoridagi bo'limlar va `installer.iss` orqali haqiqiy o'rnatuvchi yaratish haqida pastda.

### Talablar
Windows kompyuterda Python 3.11+ o'rnatilgan bo'lishi kerak (yig'ish uchun; tayyor `.exe` foydalanuvchida Python talab qilmaydi).

> **Muammo bo'lsa (masalan "Could not find a version that satisfies..."):** bu odatda juda yangi Python versiyasi (masalan 3.14) bilan ba'zi kutubxonalarning eski versiyasi mos kelmasligidan bo'ladi. `desktop\requirements.txt` da versiyalar allaqachon moslashuvchan (`>=`) qilib qo'yilgan, shuning uchun avval quyidagini bajarib ko'ring:
> ```
> python -m pip install --upgrade pip
> desktop\build.bat
> ```
> Agar baribir xatolik chiqsa, [python.org](http://www.python.org/downloads/) dan Python 3.12 ni alohida o'rnatib, o'sha versiya bilan ishga tushiring (`py -3.12 -m pip install ...`).

### Haqiqiy o'rnatuvchi (Setup.exe) yaratish — ixtiyoriy
Agar Start Menu yorlig'i, Ish stoli yorlig'i va uninstaller bilan to'liq o'rnatuvchi kerak bo'lsa:
1. [Inno Setup](http://jrsoftware.org/isinfo.php) dasturini o'rnating (bepul).
2. `desktop\installer.iss` faylini Inno Setup Compiler'da oching va **Compile** bosing.
3. Natija: `desktop\dist_installer\BiznexPOS-Setup.exe` — shu faylni tarqating.

### Ma'lumotlar qayerda saqlanadi?
Dastur har doim mahalliy ishlagani uchun, baza va statik fayllar foydalanuvchi profilida saqlanadi:
`%APPDATA%\Biznex\db.sqlite3` — shu sababli dastur `C:\Program Files` kabi yozish huquqi cheklangan joyga o'rnatilsa ham muammosiz ishlayveradi, va har ishga tushganda avtomatik migratsiya bajariladi. Sinxronlash holati esa `%APPDATA%\Biznex\sync_state.json` faylida saqlanadi.

---

## 4. Mahalliy (lokal) ishga tushirish — o'zgarishsiz

```
cd biznex_v2
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```


## Tailwind CSS (statik build)

Loyihada Tailwind endi CDN (`cdn.tailwindcss.com`) orqali emas, oldindan build qilingan
`static/css/tailwind.css` fayli sifatida ulanadi. Bu tezroq yuklanadi va internetga bog'liq emas.

**Muhim:** Agar biror shablon yoki `static/spa/*.js` fayliga YANGI Tailwind klassi qo'shsangiz,
CSS avtomatik yangilanmaydi — qayta build qilish kerak:

```bash
npm install        # faqat birinchi marta
npm run build:css  # static/css/tailwind.css'ni qayta generatsiya qiladi
```

Ishlab chiqish paytida real vaqtda kuzatish uchun:

```bash
npm run watch:css
```

`node_modules/` va Node.js ilovaning ishlashi uchun shart emas — faqat CSS build qilish uchun kerak.
Production serverga faqat `static/css/tailwind.css` (build natijasi) yetkazilsa kifoya.
