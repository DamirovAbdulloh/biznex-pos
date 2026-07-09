import { createSignal, createEffect, onMount, onCleanup } from 'solid-js';
import html from 'solid-js/html';
import { api } from '../api.js';

export default function ProductsList() {
    const [products, setProducts] = createSignal([]);
    const [categories, setCategories] = createSignal([]);
    const [catId, setCatId] = createSignal('');
    const [q, setQ] = createSignal('');
    const [loading, setLoading] = createSignal(true);
    let debounceTimer = null;

    async function load() {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (catId()) params.set('cat', catId());
            if (q()) params.set('q', q());
            const data = await api.get(`/products/api/?${params.toString()}`);
            setProducts(data.results);
        } finally {
            setLoading(false);
        }
    }

    async function loadCategories() {
        const data = await api.get('/products/api/categories/');
        setCategories(data.results);
    }

    // catId o'zgarsa — darhol yuklaydi (Vue'dagi watch(catId, load) o'rniga)
    createEffect(load);

    function onSearchInput(e) {
        const val = e.target.value;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => setQ(val), 300);
    }

    onMount(loadCategories);
    onCleanup(() => clearTimeout(debounceTimer));

    return html`
    <div>
      <div class="flex items-center justify-between mb-5 flex-wrap gap-3">
        <div class="flex gap-2 flex-wrap">
          <button onClick=${() => setCatId('')}
                  class=${() => `px-4 py-2 rounded-xl text-sm font-semibold ${catId() === '' ? 'btn-primary' : 'btn-secondary'}`}>Barchasi</button>
          ${() => categories().map((c) => html`
            <button onClick=${() => setCatId(String(c.id))}
                    class=${() => `px-4 py-2 rounded-xl text-sm font-semibold ${catId() === String(c.id) ? 'btn-primary' : 'btn-secondary'}`}>
              ${c.name}
            </button>
          `)}
        </div>
        <input placeholder="Qidirish..." class="max-w-xs" onInput=${onSearchInput} />
      </div>

      ${() => (loading()
        ? html`<div class="text-slate-400 text-sm py-8 text-center">Yuklanmoqda...</div>`
        : products().length === 0
          ? html`<div class="card p-10 text-center text-slate-400">Taomlar topilmadi</div>`
          : html`<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              ${products().map((p) => html`
                <div class="card p-4">
                  <p class="font-bold text-slate-800 mb-1">${p.name}</p>
                  <p class="text-xs text-slate-400 mb-2">${p.category_name || 'Kategoriyasiz'}</p>
                  <p class="text-lg font-bold text-slate-900">${Number(p.price).toLocaleString()} UZS</p>
                  <p class="text-xs text-slate-400">Zaxira: ${p.quantity} ${p.unit}</p>
                </div>
              `)}
            </div>`)}
    </div>
    `;
}
