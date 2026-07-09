import { createSignal, createEffect } from 'solid-js';
import html from 'solid-js/html';
import { api } from '../api.js';
import { navigate } from '../router.js';

export default function OrdersList() {
    const statuses = [
        { value: 'open', label: 'Ochiq' },
        { value: 'closed', label: 'Yopiq' },
        { value: 'cancelled', label: 'Bekor' },
    ];
    const [status, setStatus] = createSignal('open');
    const [orders, setOrders] = createSignal([]);
    const [loading, setLoading] = createSignal(true);

    async function load() {
        setLoading(true);
        try {
            const data = await api.get(`/orders/api/?status=${status()}`);
            setOrders(data.results);
        } finally {
            setLoading(false);
        }
    }

    async function markPaid(o) {
        await api.post(`/orders/api/${o.id}/mark-paid/`, { payment_type: 'cash' });
        load();
    }

    // status o'zgarganda avtomatik qayta yuklaydi (Vue'dagi watch(status, load) o'rniga)
    createEffect(load);

    return html`
    <div>
      <div class="flex items-center justify-between mb-5 flex-wrap gap-3">
        <div class="flex gap-2">
          ${statuses.map((s) => html`
            <button onClick=${() => setStatus(s.value)}
                    class=${() => `px-4 py-2 rounded-xl text-sm font-semibold ${status() === s.value ? 'btn-primary' : 'btn-secondary'}`}>
              ${s.label}
            </button>
          `)}
        </div>
        <button class="btn-secondary" onClick=${load}>↻ Yangilash</button>
      </div>

      ${() => (loading()
        ? html`<div class="text-slate-400 text-sm py-8 text-center">Yuklanmoqda...</div>`
        : orders().length === 0
          ? html`<div class="card p-10 text-center text-slate-400">Buyurtmalar topilmadi</div>`
          : html`<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              ${orders().map((o) => html`
                <div class="card p-4 cursor-pointer hover:shadow-md transition" onClick=${() => navigate('/app/orders/' + o.id)}>
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-bold text-slate-800">#${o.id} ${o.is_takeaway ? '(Saboy)' : ''}</span>
                    ${o.status === 'closed' ? html`<span class="tag">Yopiq</span>` : html`<span class="tag-yellow">Ochiq</span>`}
                  </div>
                  <p class="text-sm text-slate-500 mb-1">${o.table ? o.table.name : "Stol yo'q"}</p>
                  <p class="text-sm text-slate-500 mb-3">${o.employee ? o.employee.name : '—'}</p>
                  <div class="flex items-center justify-between">
                    <span class="font-bold text-lg text-slate-900">${Number(o.total).toLocaleString()} UZS</span>
                    ${o.status === 'open' && !o.is_paid
                      ? html`<button onClick=${(e) => { e.stopPropagation(); markPaid(o); }} class="btn-primary text-xs px-3 py-1.5">To'ladi</button>`
                      : ''}
                  </div>
                </div>
              `)}
            </div>`)}
    </div>
    `;
}
