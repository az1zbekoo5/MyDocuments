// SavdoShop front-end: plain JavaScript + fetch() calls to our Express API
const som = (n) => Number(n).toLocaleString('ru-RU') + " so'm";
// escape user text before putting it into HTML (prevents XSS attacks)
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

async function api(url, options = {}) {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

// ---------- Cart is stored in the browser (localStorage) ----------
const getCart = () => JSON.parse(localStorage.getItem('cart') || '[]');
const saveCart = (cart) => { localStorage.setItem('cart', JSON.stringify(cart)); updateCartCount(); };
function updateCartCount() {
  const el = document.getElementById('cart-count');
  if (el) el.textContent = getCart().reduce((s, i) => s + i.quantity, 0);
}
function addToCart(p) {
  const cart = getCart();
  const line = cart.find((i) => i.productId === p.product_id);
  if (line) line.quantity++;
  else cart.push({ productId: p.product_id, name: p.name, price: Number(p.price), quantity: 1 });
  saveCart(cart);
}

// ---------- Home page ----------
async function loadHome() {
  const cats = await api('/api/categories');
  document.getElementById('category').innerHTML += cats
    .map((c) => `<option value="${c.category_id}">${esc(c.name)}</option>`).join('');

  async function search() {
    const params = new URLSearchParams({
      q: document.getElementById('q').value,
      category: document.getElementById('category').value
    });
    const products = await api('/api/products?' + params);
    document.getElementById('products').innerHTML = products.map((p) => `
      <a class="card product" href="/product.html?id=${p.product_id}">
        <img src="${esc(p.image_url)}" alt="${esc(p.name)}">
        <h3>${esc(p.name)}</h3>
        <p class="muted">${esc(p.category)}</p>
        <p class="price">${som(p.price)}</p>
      </a>`).join('') || '<p>No products found.</p>';
  }
  document.getElementById('filters').addEventListener('submit', (e) => { e.preventDefault(); search(); });
  search();
}

// ---------- Product page ----------
async function loadProduct() {
  const id = new URLSearchParams(location.search).get('id');
  const p = await api('/api/products/' + id);
  document.title = p.name + ' - SavdoShop';
  document.getElementById('detail').innerHTML = `
    <div class="card detail">
      <img src="${esc(p.image_url)}" alt="${esc(p.name)}">
      <div>
        <h1>${esc(p.name)}</h1>
        <p class="muted">${esc(p.category)} | in stock: ${p.stock}</p>
        <p>${esc(p.description)}</p>
        <p class="price">${som(p.price)}</p>
        <p>Rating: ${p.avgRating ? p.avgRating.toFixed(1) + ' / 5' : 'no reviews yet'}</p>
        <button id="add">Add to cart</button>
      </div>
    </div>`;
  document.getElementById('add').onclick = () => { addToCart(p); alert('Added to cart'); };
  document.getElementById('reviews').innerHTML = p.reviews.map((r) => `
    <div class="card"><b>${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}</b>
    ${esc(r.comment)} <span class="muted">- ${esc(r.author || 'Customer #' + r.customerId)}</span></div>`).join('');

  document.getElementById('review-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    await api(`/api/products/${id}/reviews`, {
      method: 'POST',
      body: JSON.stringify({
        author: document.getElementById('author').value,
        rating: document.getElementById('rating').value,
        comment: document.getElementById('comment').value
      })
    });
    location.reload();
  });
}

// ---------- Cart + checkout page ----------
function loadCart() {
  const render = () => {
    const cart = getCart();
    const total = cart.reduce((s, i) => s + i.price * i.quantity, 0);
    document.getElementById('cart-items').innerHTML = cart.length === 0 ? '<p>Cart is empty.</p>' :
      cart.map((i, idx) => `<div class="card row">${esc(i.name)} x ${i.quantity}
        <span>${som(i.price * i.quantity)} <button data-idx="${idx}">Remove</button></span></div>`).join('') +
      `<p class="price">Total: ${som(total)}</p>`;
    document.querySelectorAll('#cart-items button').forEach((b) => b.onclick = () => {
      const c = getCart(); c.splice(Number(b.dataset.idx), 1); saveCart(c); render();
    });
  };
  render();

  document.getElementById('checkout').addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = document.getElementById('message');
    const val = (id) => document.getElementById(id).value;
    try {
      const result = await api('/api/orders', {
        method: 'POST',
        body: JSON.stringify({
          customer: { fullName: val('fullName'), email: val('email'), phone: val('phone'), city: val('city') },
          items: getCart().map(({ productId, quantity }) => ({ productId, quantity })),
          paymentMethod: val('paymentMethod')
        })
      });
      saveCart([]); render();
      msg.textContent = `Thank you! Order #${result.orderId}, total ${som(result.total)}`;
    } catch (err) {
      msg.textContent = 'Error: ' + err.message;
    }
  });
}

// ---------- Dashboard page ----------
function bars(rows, label, value) {
  const max = Math.max(...rows.map(value), 1);
  return rows.map((r) => `<div class="bar-row"><span>${esc(label(r))}</span>
    <div class="bar" style="width:${(value(r) / max) * 100}%"></div><b>${value(r).toLocaleString()}</b></div>`).join('');
}
async function loadDashboard() {
  const funnel = await api('/api/stats/funnel');
  document.getElementById('funnel').innerHTML =
    bars(Object.entries(funnel), (r) => r[0], (r) => r[1]);
  const top = await api('/api/stats/top-viewed');
  document.getElementById('top-viewed').innerHTML = bars(top, (r) => r.name, (r) => r.views);
  const city = await api('/api/stats/sales-by-city');
  document.getElementById('by-city').innerHTML = bars(city, (r) => r.city, (r) => r.revenue);
}

// ---------- Start the right page ----------
updateCartCount();
const pages = { home: loadHome, product: loadProduct, cart: loadCart, dashboard: loadDashboard };
const page = pages[document.body.dataset.page];
if (page) Promise.resolve(page()).catch((err) => alert('Error: ' + err.message));
