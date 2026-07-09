import html from 'solid-js/html';
import { pathname, navigate } from '../router.js';

export default function Sidebar(props) {
    function isActive(path) {
        return pathname().startsWith(path);
    }
    function linkClass(path) {
        return `sidebar-item cursor-pointer flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm ${isActive(path) ? 'active' : 'text-gray-400'}`;
    }
    function go(path) {
        navigate(path);
        props.onClose && props.onClose();
    }

    return html`
    <div>
      ${() => (props.open() ? html`<div onClick=${() => props.onClose()} class="fixed inset-0 bg-black/40 z-30 lg:hidden"></div>` : '')}
      <aside id="sidebar" class=${() => `w-64 min-h-screen fixed left-0 top-0 z-40 flex flex-col ${props.open() ? 'sidebar-open' : ''}`}
             style="background:linear-gradient(180deg,#0d1117 0%,#161b22 100%)">
        <div class="px-5 py-5 border-b flex items-center justify-between" style="border-color:rgba(255,255,255,0.06)">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl flex items-center justify-center" style="background:linear-gradient(135deg,#16a34a,#22c55e)">
              <svg width="18" height="18" fill="white" viewBox="0 0 24 24"><path d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" stroke="white" stroke-width="1.5" fill="none"/></svg>
            </div>
            <div>
              <span class="text-white font-bold text-lg tracking-wide">Biznex</span>
              <p class="text-xs" style="color:#4ade80">POS Tizimi · Solid</p>
            </div>
          </div>
          <button onClick=${() => props.onClose()} class="lg:hidden text-gray-400 hover:text-white p-1">
            <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M6 6l12 12M6 18L18 6"/></svg>
          </button>
        </div>

        <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          <p class="text-xs font-semibold uppercase tracking-widest px-4 py-2" style="color:#4b5563">Asosiy</p>
          <a onClick=${() => go('/app/orders')} class=${() => linkClass('/app/orders')}>
            <svg width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
            <span class="font-medium">Buyurtmalar</span>
          </a>
          <a onClick=${() => go('/app/products')} class=${() => linkClass('/app/products')}>
            <svg width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
            <span class="font-medium">Taomlar</span>
          </a>
          <a onClick=${() => go('/app/categories')} class=${() => linkClass('/app/categories')}>
            <svg width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
            <span class="font-medium">Kategoriyalar</span>
          </a>

          <p class="text-xs font-semibold uppercase tracking-widest px-4 py-2 pt-4" style="color:#4b5563">Boshqaruv</p>
          <p class="px-4 py-1.5 text-[11px]" style="color:#374151">Quyidagilar hozircha klassik sahifalarda (migratsiya navbatda):</p>
          <a href="/locations/" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Joylar</span></a>
          <a href="/reports/" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Hisobotlar</span></a>
          <a href="/warehouse/" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Ombor</span></a>
          <a href="/employees/panels/" target="_blank" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Panellar</span></a>
          <a href="/employees/" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Hodimlar</span></a>
          <a href="/clients/" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Mijozlar</span></a>
          <a href="/settings/" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Sozlamalar</span></a>
          <div class="px-4 pt-3 pb-1">
            <p class="text-xs font-semibold uppercase" style="color:rgba(255,255,255,0.25)">Panel</p>
          </div>
          <a href="/employees/waiter/" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Ofitsant paneli</span></a>
          <a href="/orders/kitchen/" target="_blank" class="sidebar-item text-gray-400 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm"><span class="font-medium">Oshpaz paneli</span></a>
        </nav>

        <div class="px-4 py-4 border-t" style="border-color:rgba(255,255,255,0.06)">
          <div class="flex items-center gap-3 px-3 py-2 rounded-xl" style="background:rgba(255,255,255,0.04)">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white" style="background:linear-gradient(135deg,#16a34a,#22c55e)">AD</div>
            <div class="flex-1 min-w-0">
              <p class="text-white text-sm font-semibold truncate">Admin</p>
              <p class="text-xs truncate" style="color:#6b7280">Bosh admin</p>
            </div>
          </div>
        </div>
      </aside>
    </div>
    `;
}
