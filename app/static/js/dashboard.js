/* Dashboard admin: KPIs, listas de productos, usuarios. */
(function () {
  "use strict";

  const TOKEN = localStorage.getItem("storai_token");
  const USER = JSON.parse(localStorage.getItem("storai_user") || "null");

  if (!TOKEN) {
    window.location.href = "/admin";
    return;
  }

  const auth = { headers: { Authorization: `Bearer ${TOKEN}` } };

  // --- User chip ---
  const userChip = document.getElementById("user-chip");
  if (USER) {
    const initial = (USER.full_name || USER.username || "U")[0].toUpperCase();
    userChip.innerHTML = `
      <div>
        <div style="font-weight:600;">${escapeHTML(USER.full_name || USER.username)}</div>
        <div class="role">${escapeHTML(USER.role || "")}</div>
      </div>
      <div class="avatar">${escapeHTML(initial)}</div>
    `;
  }

  document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("storai_token");
    localStorage.removeItem("storai_user");
    window.location.href = "/admin";
  });

  // --- Load data ---
  Promise.all([
    fetch("/api/v1/inventory/products/?limit=200", auth).then(handle),
    fetch("/api/v1/inventory/products/low-stock/", auth).then(handle),
    fetch("/api/v1/inventory/products/out-of-stock/", auth).then(handle),
    fetch("/api/v1/users/users/", auth).then(handle),
  ])
    .then(([all, low, out, users]) => {
      setKPI("kpi-products", all.length);
      setKPI("kpi-low", low.length);
      setKPI("kpi-out", out.length);
      setKPI("kpi-users", users.length);
      renderProducts(all);
      renderUsers(users);
    })
    .catch((err) => {
      console.error(err);
      if (err && err.status === 401) {
        localStorage.clear();
        window.location.href = "/admin";
      }
    });

  function handle(res) {
    if (!res.ok) {
      const e = new Error("HTTP " + res.status);
      e.status = res.status;
      throw e;
    }
    return res.json();
  }

  function setKPI(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    // Cuenta animada
    let start = 0;
    const end = Number(value);
    const duration = 700;
    const startTime = performance.now();
    function step(t) {
      const p = Math.min(1, (t - startTime) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(start + (end - start) * eased);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = end;
    }
    requestAnimationFrame(step);
  }

  function renderProducts(products) {
    const body = document.getElementById("products-body");
    if (!products.length) {
      body.innerHTML = '<tr class="skeleton-row"><td colspan="5">No hay productos.</td></tr>';
      return;
    }
    body.innerHTML = "";
    products.slice(0, 10).forEach((p) => {
      const status = p.stock_status;
      const tag =
        status === "out_of_stock"
          ? '<span class="tag out"><span class="tag-dot"></span>Sin stock</span>'
          : status === "low_stock"
          ? '<span class="tag low"><span class="tag-dot"></span>Stock bajo</span>'
          : '<span class="tag ok"><span class="tag-dot"></span>Disponible</span>';
      body.innerHTML += `
        <tr>
          <td class="sku">${escapeHTML(p.sku)}</td>
          <td>${escapeHTML(p.name)}</td>
          <td class="price">$${Number(p.sale_price).toFixed(2)}</td>
          <td>${p.stock_current}</td>
          <td>${tag}</td>
        </tr>
      `;
    });
  }

  function renderUsers(users) {
    const body = document.getElementById("users-body");
    if (!users.length) {
      body.innerHTML = '<tr class="skeleton-row"><td colspan="4">No hay usuarios.</td></tr>';
      return;
    }
    body.innerHTML = "";
    users.forEach((u) => {
      const role = u.role || "—";
      body.innerHTML += `
        <tr>
          <td><strong>${escapeHTML(u.full_name || u.username)}</strong></td>
          <td class="muted">${escapeHTML(u.email)}</td>
          <td><span class="tag role">${escapeHTML(role)}</span></td>
          <td>${
            u.is_active
              ? '<span class="tag ok"><span class="tag-dot"></span>Activo</span>'
              : '<span class="tag out"><span class="tag-dot"></span>Inactivo</span>'
          }</td>
        </tr>
      `;
    });
  }

  function escapeHTML(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
})();
