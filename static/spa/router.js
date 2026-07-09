// Juda kichik client-side router. Vue Router o'rniga — tashqi kutubxonasiz,
// faqat History API + Solid signal. Loyihada bor-yo'g'i 4 ta route bo'lgani
// uchun to'liq router kutubxonasini ulashning hojati yo'q — bu ham tezroq.
import { createSignal } from 'solid-js';

export const BASE = '/app';

// "/app" yoki "/app/" ga kirilsa — /app/orders ga darhol almashtiramiz (history'ga
// qo'shimcha yozuv qoldirmasdan), xuddi Vue'dagi { path: '/', redirect: '/orders' } kabi.
let initialPath = window.location.pathname;
if (initialPath === BASE || initialPath === BASE + '/') {
    initialPath = BASE + '/orders';
    window.history.replaceState({}, '', initialPath);
}

const [pathname, setPathname] = createSignal(initialPath);
export { pathname };

export function navigate(path, replace = false) {
    if (path === window.location.pathname) return;
    if (replace) window.history.replaceState({}, '', path);
    else window.history.pushState({}, '', path);
    setPathname(path);
}

window.addEventListener('popstate', () => setPathname(window.location.pathname));

// path -> { component, params } ni topadi. routes: [{ pattern: RegExp, component, params: [...nomlar] }]
export function matchRoute(routes, path) {
    for (const r of routes) {
        const m = path.match(r.pattern);
        if (m) {
            const params = {};
            (r.params || []).forEach((name, i) => { params[name] = m[i + 1]; });
            return { component: r.component, params };
        }
    }
    return null;
}
