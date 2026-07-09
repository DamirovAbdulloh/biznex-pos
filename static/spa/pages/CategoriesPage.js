import { createSignal, onMount } from 'solid-js';
import html from 'solid-js/html';
import { api } from '../api.js';

export default function CategoriesPage() {
    const [categories, setCategories] = createSignal([]);
    const [loading, setLoading] = createSignal(true);
    const [newName, setNewName] = createSignal('');
    const [newCode, setNewCode] = createSignal('');

    async function load() {
        setLoading(true);
        try {
            const data = await api.get('/products/api/categories/');
            setCategories(data.results);
        } finally {
            setLoading(false);
        }
    }

    async function create() {
        if (!newName()) return;
        await api.post('/products/api/categories/create/', { name: newName(), code: newCode() });
        setNewName('');
        setNewCode('');
        load();
    }

    async function remove(c) {
        try {
            await api.post(`/products/api/categories/${c.id}/delete/`, {});
            load();
        } catch (e) {
            alert(e.message);
        }
    }

    onMount(load);

    return html`
    <div>
      <div class="card p-5 mb-5 max-w-md">
        <h3 class="font-bold mb-3">Yangi kategoriya</h3>
        <div class="space-y-3">
          <div>
            <label>Nomi</label>
            <input value=${newName} onInput=${(e) => setNewName(e.target.value)} placeholder="Masalan: Ichimliklar" />
          </div>
          <div>
            <label>Kod</label>
            <input value=${newCode} onInput=${(e) => setNewCode(e.target.value)} placeholder="Masalan: DRK" />
          </div>
          <button class="btn-primary" onClick=${create} disabled=${() => !newName()}>Qo'shish</button>
        </div>
      </div>

      ${() => (loading()
        ? html`<div class="text-slate-400 text-sm py-8 text-center">Yuklanmoqda...</div>`
        : html`<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            ${categories().map((c) => html`
              <div class="card p-4 flex items-center justify-between">
                <div>
                  <p class="font-bold text-slate-800">${c.name}</p>
                  <p class="text-xs text-slate-400">${c.code} · ${c.product_count} ta taom</p>
                </div>
                <button class="btn-secondary text-xs px-3 py-1.5" onClick=${() => remove(c)}>O'chirish</button>
              </div>
            `)}
          </div>`)}
    </div>
    `;
}
