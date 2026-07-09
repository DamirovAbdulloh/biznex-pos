import { createSignal } from 'solid-js';
import html from 'solid-js/html';
import { render } from 'solid-js/web';
import Sidebar from './components/Sidebar.js';
import { pathname, matchRoute } from './router.js';
import OrdersList from './pages/OrdersList.js';
import OrderDetail from './pages/OrderDetail.js';
import ProductsList from './pages/ProductsList.js';
import CategoriesPage from './pages/CategoriesPage.js';

// Build bosqichisiz, statik import — 4 ta sahifa uchun lazy-loading shart emas,
// hammasi bir zumda yuklanadi (Vue versiyadagi defineAsyncComponent'ga hojat yo'q).
const routes = [
    { pattern: /^\/app\/orders\/?$/, component: OrdersList },
    { pattern: /^\/app\/orders\/(\d+)\/?$/, component: OrderDetail, params: ['id'] },
    { pattern: /^\/app\/products\/?$/, component: ProductsList },
    { pattern: /^\/app\/categories\/?$/, component: CategoriesPage },
];

function CurrentPage() {
    const match = matchRoute(routes, pathname());
    if (!match) {
        return html`<div class="card p-10 text-center text-slate-400">Sahifa topilmadi</div>`;
    }
    const Page = match.component;
    return html`<${Page} params=${match.params} />`;
}

const [sidebarOpen, setSidebarOpen] = createSignal(false);

const App = () => html`
  <div class="min-h-screen flex">
    <${Sidebar} open=${sidebarOpen} onClose=${() => setSidebarOpen(false)} />
    <main id="main-content" class="flex-1 lg:ml-64 min-h-screen flex flex-col w-full">
      <header class="bg-white border-b border-slate-100 px-4 sm:px-8 py-4 flex items-center justify-between sticky top-0 z-20 gap-3">
        <div class="flex items-center gap-3 min-w-0">
          <button onClick=${() => setSidebarOpen(true)} class="lg:hidden text-gray-500 hover:text-gray-800 p-2 -ml-2 shrink-0">
            <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
          </button>
          <h1 class="text-gray-900 font-bold text-base sm:text-lg truncate">Biznex</h1>
        </div>
      </header>
      <div class="p-4 sm:p-6 lg:p-8 flex-1 overflow-x-auto">
        ${CurrentPage}
      </div>
    </main>
  </div>
`;

render(App, document.getElementById('app'));
