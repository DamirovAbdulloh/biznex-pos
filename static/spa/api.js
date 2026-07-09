// Kichik fetch wrapper — Django CSRF cookie'ni avtomatik qo'shadi.
function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? decodeURIComponent(match.pop()) : '';
}

async function request(url, options = {}) {
    const opts = {
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
        ...options,
    };
    if (opts.method && opts.method !== 'GET') {
        opts.headers['X-CSRFToken'] = getCookie('csrftoken');
    }
    const res = await fetch(url, opts);
    let data = null;
    try { data = await res.json(); } catch (e) { /* bo'sh javob */ }
    if (!res.ok) {
        const err = new Error((data && data.error) || `So'rov xatoligi (${res.status})`);
        err.data = data;
        throw err;
    }
    return data;
}

export const api = {
    get: (url) => request(url),
    post: (url, body) => request(url, { method: 'POST', body: JSON.stringify(body || {}) }),
};
