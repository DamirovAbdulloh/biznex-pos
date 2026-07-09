# Biznex — Vue.js SPA migratsiyasi (1-bosqich)

## Nima o'zgardi?

**Asosiy sabab (sekinlik):** `base.html` da Tailwind CSS CDN orqali (`cdn.tailwindcss.com`)
ulangan edi — bu har bir sahifa yuklanganda CSS'ni qaytadan generatsiya qiladigan JIT
kompilyator, va bundan tashqari har bir link bosilganda **butun sahifa** qayta yuklanardi
(klassik Django ko'p-sahifali arxitektura).

**Yechim:** `/app/` manzili ostida yangi **Vue 3 SPA** (Single Page Application) qo'shildi:

- Sidebar va header **bir marta** render bo'ladi, keyin hech qachon qayta yuklanmaydi
- Sahifalar orasida o'tish — Vue Router orqali, faqat kerakli JSON ma'lumot fetch qilinadi
- Tailwind faqat bitta marta yuklanadi (SPA sahifasida)
- **Build vositasi (npm/vite) shart emas** — Vue va Vue Router to'g'ridan-to'g'ri brauzerda
  ES module sifatida CDN'dan yuklanadi (`importmap`, `static/spa/app.js`)

## Hozircha nima migratsiya qilindi?

✅ **Buyurtmalar** (`/app/orders`, `/app/orders/:id`) — ro'yxat, status filtri, detail, to'lash
✅ **Taomlar** (`/app/products`) — ro'yxat, kategoriya filtri, qidiruv
✅ **Kategoriyalar** (`/app/categories`) — ro'yxat, qo'shish, o'chirish

Bu sahifalarga eski panel ichidagi yashil **"⚡ Yangi tezkor panel"** tugmasi orqali
yoki to'g'ridan-to'g'ri `/app/orders` manzilidan kirish mumkin.

## Nima hali eski (klassik Django) sahifalarda qoldi?

Joylar, Hisobotlar, Ombor, Smena, Hodimlar, Mijozlar, Sozlamalar, **Ofitsant paneli**,
**Oshpaz paneli** va **POS (kassa) ekrani**. Bularni ataylab hozircha o'zgartirmadim, chunki:

- POS/Kitchen/Ofitsant panellari — chek chop etish (`silentPrintReceipt`), real-vaqt
  yangilanish kabi nozik funksiyalarga bog'liq; sinovsiz o'zgartirish ishlab turgan
  kassani buzib qo'yishi mumkin
- Qolganlari (Hisobotlar, Ombor va h.k.) kamroq tez-tez ochiladi — shu sabab ularni
  tezlashtirish ustuvorlik emas

## Qolganlarini qanday migratsiya qilish kerak (naqsh/pattern)

Har bir modul uchun 3 qadam:

1. **`<app>/api.py`** — mavjud `views.py` dagi biznes logikani qayta ishlatib,
   `JsonResponse` qaytaradigan funksiyalar yozing (`orders/api.py`, `products/api.py`ga qarang)
2. **`<app>/urls.py`** — `api/...` prefiksi bilan yangi yo'llarni qo'shing
3. **`static/spa/pages/YangiSahifa.js`** — Vue komponent yozing (`OrdersList.js`ga qarang),
   so'ng uni `static/spa/app.js` dagi `routes` massiviga qo'shing va
   `Sidebar.js` da havolani "klassik" ro'yxatdan Vue `router-link`ga o'tkazing

## Ishga tushirish

Kod tuzilishi o'zgarmadi — oddiy Django loyihasi kabi ishga tushiring:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Keyin brauzerda: klassik panel — `http://127.0.0.1:8000/`, yangi tezkor panel —
`http://127.0.0.1:8000/app/orders`

**Eslatma:** Men bu muhitda tarmoq (internet) va Django o'rnatilmagan bo'lgani uchun
serverni real ishga tushirib sinab ko'ra olmadim — kodni qo'lda sintaksis va mantiq
bo'yicha tekshirdim (barcha `.py` va `.js` fayllar sintaksis xatosiz). Birinchi marta
ishga tushirganda, iltimos, `/app/orders` va `/app/products` sahifalarini diqqat bilan
sinab ko'ring.
