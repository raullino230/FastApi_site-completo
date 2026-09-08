const products = [
  { id: "margherita", name: "Margherita", category: "classicas", tag: "mais pedida", description: "Molho da casa, mozzarella, tomate italiano e manjericão.", price: 49, color: "#d94b38", rotation: "-9deg" },
  { id: "pepperoni", name: "Pepperoni", category: "classicas", tag: "favorita", description: "Molho artesanal, mozzarella e pepperoni crocante.", price: 54, color: "#b83228", rotation: "8deg" },
  { id: "calabresa", name: "Calabresa", category: "classicas", tag: "", description: "Calabresa defumada, cebola roxa e azeitonas pretas.", price: 51, color: "#bd4b30", rotation: "-2deg" },
  { id: "quatro-queijos", name: "Quatro Queijos", category: "especiais", tag: "especial", description: "Mozzarella, gorgonzola, parmesão e provolone.", price: 57, color: "#e4c35b", rotation: "11deg" },
  { id: "funghi", name: "Funghi & Trufa", category: "especiais", tag: "", description: "Cogumelos salteados, mozzarella e azeite trufado.", price: 63, color: "#83674b", rotation: "-8deg" },
  { id: "burrata", name: "Burrata al Pesto", category: "especiais", tag: "novidade", description: "Pesto fresco, burrata cremosa e tomatinhos assados.", price: 65, color: "#548249", rotation: "6deg" },
  { id: "vegetariana", name: "Horta da Estação", category: "vegetarianas", tag: "veg", description: "Abobrinha, berinjela, tomate, rúcula e mozzarella.", price: 55, color: "#638b44", rotation: "-6deg" },
  { id: "brie-mel", name: "Brie & Mel", category: "vegetarianas", tag: "", description: "Queijo brie, nozes, mel e alecrim fresco.", price: 61, color: "#e1ac52", rotation: "9deg" },
];

const sizes = { P: 0.82, M: 1, G: 1.24 };
const state = {
  cart: JSON.parse(localStorage.getItem("fornoRossoCart") || "[]"),
  filter: "todos",
  expanded: false,
  token: localStorage.getItem("fornoRossoToken"),
  pendingCheckout: false,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const money = (value) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
const escapeHtml = (value) => String(value).replace(/[&<>"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[character]));

function itemPrice(item) {
  return item.basePrice * (sizes[item.size] || 1);
}

function miniPizza(productOrItem, className = "") {
  return `<span class="mini-pizza ${className}" style="--pizza-color:${productOrItem.color};--rotation:${productOrItem.rotation || "0deg"}" aria-hidden="true"></span>`;
}

function persistCart() {
  localStorage.setItem("fornoRossoCart", JSON.stringify(state.cart));
}

function renderMenu() {
  const grid = $("[data-menu-grid]");
  const filtered = state.filter === "todos" ? products : products.filter((product) => product.category === state.filter);
  const visible = state.expanded || state.filter !== "todos" ? filtered : filtered.slice(0, 4);
  grid.innerHTML = visible.map((product) => `
    <article class="pizza-card">
      <div class="pizza-thumb">
        ${product.tag ? `<span class="pizza-tag">${product.tag}</span>` : ""}
        ${miniPizza(product)}
      </div>
      <div class="pizza-card-body">
        <div class="pizza-card-title"><h3>${product.name}</h3></div>
        <p>${product.description}</p>
        <div class="pizza-card-footer">
          <span class="price">${money(product.price)} <small>/ média</small></span>
          <button class="add-button" type="button" data-add-product="${product.id}" aria-label="Adicionar ${product.name} ao carrinho">+</button>
        </div>
      </div>
    </article>`).join("");
  const moreButton = $("[data-show-all]");
  moreButton.closest(".center-action").classList.toggle("hidden", state.filter !== "todos");
  moreButton.innerHTML = state.expanded ? "Mostrar menos <span>↑</span>" : "Ver cardápio completo <span>↓</span>";
}

function renderCart() {
  const items = $("[data-cart-items]");
  const empty = $("[data-cart-empty]");
  const footer = $("[data-cart-footer]");
  const cartCount = state.cart.reduce((total, item) => total + item.quantity, 0);
  const cartTotal = state.cart.reduce((total, item) => total + itemPrice(item) * item.quantity, 0);
  $("[data-cart-count]").textContent = cartCount;
  $("[data-cart-total]").textContent = money(cartTotal);
  empty.classList.toggle("hidden", state.cart.length > 0);
  footer.classList.toggle("hidden", state.cart.length === 0);
  items.innerHTML = state.cart.map((item) => `
    <article class="cart-item">
      ${miniPizza(item)}
      <div>
        <h3>${escapeHtml(item.name)}</h3>
        <p>Tamanho: <select class="size-select" data-size="${item.id}" aria-label="Tamanho de ${escapeHtml(item.name)}">
          ${Object.keys(sizes).map((size) => `<option value="${size}" ${item.size === size ? "selected" : ""}>${size === "P" ? "Pequena" : size === "M" ? "Média" : "Grande"}</option>`).join("")}
        </select></p>
        <div class="quantity-picker"><button type="button" data-change-quantity="${item.id}" data-step="-1" aria-label="Diminuir quantidade">−</button><span>${item.quantity}</span><button type="button" data-change-quantity="${item.id}" data-step="1" aria-label="Aumentar quantidade">+</button></div>
      </div>
      <div><button class="remove-item" type="button" data-remove-item="${item.id}" aria-label="Remover ${escapeHtml(item.name)}">×</button><div class="cart-item-price">${money(itemPrice(item) * item.quantity)}</div></div>
    </article>`).join("");
  persistCart();
}

function addProduct(productId) {
  const product = products.find((entry) => entry.id === productId);
  if (!product) return;
  const sameItem = state.cart.find((entry) => entry.productId === product.id && entry.size === "M");
  if (sameItem) {
    sameItem.quantity += 1;
  } else {
    state.cart.push({ productId: product.id, id: `${product.id}-${Date.now()}`, name: product.name, basePrice: product.price, size: "M", quantity: 1, color: product.color, rotation: product.rotation });
  }
  renderCart();
  openCart();
  showToast(`${product.name} foi adicionada ao carrinho.`);
}

function updateCartItem(itemId, updater) {
  const item = state.cart.find((entry) => entry.id === itemId);
  if (!item) return;
  updater(item);
  state.cart = state.cart.filter((entry) => entry.quantity > 0);
  renderCart();
}

function openCart() {
  $("[data-cart-drawer]").classList.add("open");
  $("[data-cart-drawer]").setAttribute("aria-hidden", "false");
  $("[data-scrim]").classList.add("visible");
}

function closeCart() {
  $("[data-cart-drawer]").classList.remove("open");
  $("[data-cart-drawer]").setAttribute("aria-hidden", "true");
  $("[data-scrim]").classList.remove("visible");
}

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type === "error" ? "error" : ""}`;
  toast.textContent = message;
  $("[data-toast-region]").append(toast);
  window.setTimeout(() => toast.remove(), 3600);
}

function apiError(payload) {
  if (!payload) return "Não foi possível concluir a ação. Tente novamente.";

  if (typeof payload.detail === "string") return payload.detail;
  if (Array.isArray(payload.detail)) {
    const first = payload.detail[0];
    if (typeof first === "string") return first;
    if (first?.msg) return first.msg;
    if (first?.message) return first.message;
  }
  if (payload.detail && typeof payload.detail === "object") {
    if (typeof payload.detail.msg === "string") return payload.detail.msg;
    if (typeof payload.detail.message === "string") return payload.detail.message;
  }
  if (typeof payload.message === "string") return payload.message;

  return "Não foi possível concluir a ação. Tente novamente.";
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (options.body) headers["Content-Type"] = "application/json";
  const response = await fetch(path, { ...options, headers });
  let payload = null;
  try { payload = await response.json(); } catch { /* API returned no JSON */ }
  if (!response.ok) {
    if (response.status === 401) updateAccount(null);
    throw new Error(apiError(payload));
  }
  return payload;
}

function getUserId() {
  try {
    const part = state.token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const payload = JSON.parse(decodeURIComponent(atob(part).split("").map((character) => `%${(`00${character.charCodeAt(0).toString(16)}`).slice(-2)}`).join("")));
    return Number(payload.sub);
  } catch {
    return null;
  }
}

function updateAccount(token) {
  state.token = token;
  if (token) localStorage.setItem("fornoRossoToken", token);
  else localStorage.removeItem("fornoRossoToken");
  const loggedIn = Boolean(getUserId());
  $("[data-account-label]").textContent = loggedIn ? "Minha conta" : "Entrar";
  $("[data-open-orders]").classList.toggle("hidden", !loggedIn);
}

function setAuthView(view) {
  const login = view === "login";
  $("[data-login-form]").classList.toggle("hidden", !login);
  $("[data-register-form]").classList.toggle("hidden", login);
  $$("[data-auth-view]").forEach((tab) => tab.classList.toggle("active", tab.dataset.authView === view));
  $("[data-auth-title]").textContent = login ? "Que bom ter você aqui." : "A sua mesa está esperando.";
  $("[data-auth-text]").textContent = login ? "Entre para pedir sua pizza e acompanhar seus pedidos." : "Crie sua conta e deixe os próximos pedidos ainda mais fáceis.";
  $("[data-auth-message]").textContent = "";
  $("[data-auth-message]").classList.remove("success");
}

function openAuth(view = "login") {
  setAuthView(view);
  $("[data-auth-dialog]").showModal();
}

async function authenticate(event, isRegistration) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $("button[type=submit]", form);
  const message = $("[data-auth-message]");
  const data = Object.fromEntries(new FormData(form));
  button.disabled = true;
  button.textContent = isRegistration ? "Criando conta..." : "Entrando...";
  try {
    if (isRegistration) {
      await api("/auth/criar_conta", { method: "POST", body: JSON.stringify({ ...data, ativo: true, admin: false }) });
      message.textContent = "Conta criada! Agora entre com seu e-mail e senha.";
      message.classList.add("success");
      setAuthView("login");
      $("[data-login-form] input[name=email]").value = data.email;
      return;
    }
    const result = await api("/auth/login", { method: "POST", body: JSON.stringify(data) });
    updateAccount(result.access_token);
    $("[data-auth-dialog]").close();
    showToast("Login realizado. Sua mesa está reservada!");
    if (state.pendingCheckout) {
      state.pendingCheckout = false;
      await checkout();
    }
  } catch (error) {
    message.textContent = error.message;
    message.classList.remove("success");
  } finally {
    button.disabled = false;
    button.innerHTML = isRegistration ? "Criar minha conta <span>→</span>" : "Entrar na minha conta <span>→</span>";
  }
}

async function checkout() {
  if (!state.cart.length) return;
  if (!getUserId()) {
    state.pendingCheckout = true;
    closeCart();
    openAuth("login");
    return;
  }
  const button = $("[data-checkout]");
  button.disabled = true;
  button.textContent = "Enviando pedido...";
  try {
    const order = await api("/orders/pedido", { method: "POST", body: JSON.stringify({ id_usuario: getUserId() }) });
    const orderId = Number(String(order?.Mensagem || "").match(/(\d+)/)?.[1]);
    if (!orderId) throw new Error("O pedido foi criado, mas não conseguimos identificar seu número.");
    for (const item of state.cart) {
      await api(`/orders/pedido/adicionar-item/${orderId}`, {
        method: "POST",
        body: JSON.stringify({ quantidade: item.quantity, sabor: item.name, tamanho: item.size, ["preço_unitario"]: itemPrice(item) }),
      });
    }
    state.cart = [];
    renderCart();
    closeCart();
    showToast(`Pedido #${orderId} recebido! Já estamos preparando sua pizza.`);
    await openOrders();
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    button.disabled = false;
    button.innerHTML = "Finalizar pedido <span>→</span>";
  }
}

function statusClass(status) {
  return String(status || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

async function openOrders() {
  if (!getUserId()) return openAuth("login");
  const dialog = $("[data-orders-dialog]");
  const list = $("[data-orders-list]");
  list.innerHTML = '<p class="order-empty">Buscando seus pedidos...</p>';
  if (!dialog.open) dialog.showModal();
  try {
    const orders = await api("/orders/listar/pedidos-usuario");
    if (!orders.length) {
      list.innerHTML = '<p class="order-empty">Você ainda não fez pedidos. Que tal escolher uma pizza?</p>';
      return;
    }
    list.innerHTML = orders.slice().reverse().map((order) => {
      const total = Number(order.preço || 0);
      const count = order.itens?.reduce((sum, item) => sum + Number(item.quantidade || 0), 0) || 0;
      const status = order.status || "Pendente";
      const canCancel = statusClass(status) === "pendente";
      return `<article class="order-card"><div class="order-card-top"><h3>Pedido #${order.id}</h3><span class="status ${statusClass(status)}">${escapeHtml(status)}</span></div><p>${count} ${count === 1 ? "pizza" : "pizzas"} · <strong>${money(total)}</strong></p>${canCancel ? `<div class="order-card-actions"><button class="cancel-order" type="button" data-cancel-order="${order.id}">Cancelar pedido</button></div>` : ""}</article>`;
    }).join("");
  } catch (error) {
    list.innerHTML = `<p class="order-empty">${escapeHtml(error.message)}</p>`;
  }
}

async function cancelOrder(orderId) {
  try {
    await api(`/orders/pedido/canacelar/${orderId}`, { method: "POST" });
    showToast(`Pedido #${orderId} cancelado.`);
    await openOrders();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function initReveal() {
  if (!("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (entry.isIntersecting) { entry.target.style.opacity = "1"; entry.target.style.transform = "none"; observer.unobserve(entry.target); }
  }), { threshold: 0.12 });
  $$(".reveal").forEach((element) => { element.style.opacity = "0"; element.style.transform = "translateY(15px)"; element.style.transition = "opacity .55s ease, transform .55s ease"; observer.observe(element); });
}

document.addEventListener("click", (event) => {
  const addButton = event.target.closest("[data-add-product]");
  if (addButton) addProduct(addButton.dataset.addProduct);
  if (event.target.closest("[data-open-cart]")) openCart();
  if (event.target.closest("[data-close-cart]") || event.target.matches("[data-scrim]")) closeCart();
  if (event.target.closest("[data-open-auth]")) getUserId() ? openOrders() : openAuth();
  if (event.target.closest("[data-close-auth]")) $("[data-auth-dialog]").close();
  if (event.target.closest("[data-close-orders]")) $("[data-orders-dialog]").close();
  if (event.target.closest("[data-open-orders]")) openOrders();
  if (event.target.closest("[data-logout]")) { updateAccount(null); $("[data-orders-dialog]").close(); showToast("Você saiu da sua conta."); }
  if (event.target.closest("[data-checkout]")) checkout();
  const cancelOrderButton = event.target.closest("[data-cancel-order]");
  if (cancelOrderButton) cancelOrder(cancelOrderButton.dataset.cancelOrder);
  const quantity = event.target.closest("[data-change-quantity]");
  if (quantity) updateCartItem(quantity.dataset.changeQuantity, (item) => { item.quantity += Number(quantity.dataset.step); });
  const remove = event.target.closest("[data-remove-item]");
  if (remove) { state.cart = state.cart.filter((item) => item.id !== remove.dataset.removeItem); renderCart(); }
  const tab = event.target.closest("[data-filter]");
  if (tab) { state.filter = tab.dataset.filter; state.expanded = false; $$("[data-filter]").forEach((entry) => entry.classList.toggle("active", entry === tab)); renderMenu(); }
  if (event.target.closest("[data-show-all]")) { state.expanded = !state.expanded; renderMenu(); }
  const authTab = event.target.closest("[data-auth-view]");
  if (authTab) setAuthView(authTab.dataset.authView);
  const menuToggle = event.target.closest(".menu-toggle");
  if (menuToggle) { const nav = $(".main-nav"); nav.classList.toggle("open"); menuToggle.setAttribute("aria-expanded", nav.classList.contains("open")); }
  if (event.target.closest(".main-nav a")) $(".main-nav").classList.remove("open");
});

document.addEventListener("change", (event) => {
  if (event.target.matches("[data-size]")) updateCartItem(event.target.dataset.size, (item) => { item.size = event.target.value; });
});

$("[data-login-form]").addEventListener("submit", (event) => authenticate(event, false));
$("[data-register-form]").addEventListener("submit", (event) => authenticate(event, true));
$("[data-auth-dialog]").addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); });
$("[data-orders-dialog]").addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); });

renderMenu();
renderCart();
updateAccount(state.token);
initReveal();
