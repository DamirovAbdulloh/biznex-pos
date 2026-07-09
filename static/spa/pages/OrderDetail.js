import { createSignal, createEffect } from 'solid-js';
import html from 'solid-js/html';
import { api } from '../api.js';
import { navigate } from '../router.js';

export default function OrderDetail(props) {
    const [order, setOrder] = createSignal(null);
    const [loading, setLoading] = createSignal(true);

    async function load() {
        setLoading(true);
        try {
            setOrder(await api.get(`/orders/api/${props.params.id}/`));
        } finally {
            setLoading(false);
        }
    }

    async function markPaid() {
        await api.post(`/orders/api/${props.params.id}/mark-paid/`, { payment_type: 'cash' });
        load();
    }

    createEffect(load);

    return html`
    <div>
      <button class="btn-secondary mb-4" onClick=${() => navigate('/app/orders')}>← Orqaga</button>
      ${() => (loading()
        ? html`<div class="text-slate-400 text-sm py-8 text-center">Yuklanmoqda...</div>`
        : order()
          ? html`<div class="card p-6 max-w-xl">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold">Buyurtma #${order().id}</h2>
                <span class=${order().status === 'closed' ? 'tag' : 'tag-yellow'}>${order().status_display}</span>
              </div>
              <p class="text-sm text-slate-500 mb-1">Stol: ${order().table ? order().table.name : '—'}</p>
              <p class="text-sm text-slate-500 mb-4">Xodim: ${order().employee ? order().employee.name : '—'}</p>

              <table class="w-full text-sm mb-4">
                <thead><tr class="text-left text-slate-400">
                  <th class="pb-2">Taom</th><th class="pb-2">Miqdor</th><th class="pb-2 text-right">Summa</th>
                </tr></thead>
                <tbody>
                  ${order().items.map((it) => html`
                    <tr class="border-t border-slate-100">
                      <td class="py-2">${it.product_name}</td>
                      <td class="py-2">${it.quantity} ${it.unit}</td>
                      <td class="py-2 text-right">${Number(it.subtotal).toLocaleString()}</td>
                    </tr>
                  `)}
                </tbody>
              </table>

              <div class="flex items-center justify-between border-t pt-4">
                <span class="font-semibold">Jami</span>
                <span class="text-xl font-bold">${Number(order().total).toLocaleString()} UZS</span>
              </div>

              ${order().status === 'open' && !order().is_paid
                ? html`<button onClick=${markPaid} class="btn-primary w-full justify-center mt-5">To'landi deb belgilash</button>`
                : ''}
            </div>`
          : html`<div class="card p-10 text-center text-slate-400">Buyurtma topilmadi</div>`)}
    </div>
    `;
}
