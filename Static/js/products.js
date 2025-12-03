const PRODUCTS_API_BASE = window.location.port === '5500' ? 'http://127.0.0.1:5000' : '';
const CART_STORAGE_KEY = 'halltek_cart';

document.addEventListener('DOMContentLoaded', () => {
  const loader = document.getElementById('productsLoader');
  const grid = document.getElementById('productsGrid');
  const emptyState = document.getElementById('productsEmptyState');
  const cartToggle = document.getElementById('cartToggle');
  const cartClose = document.getElementById('cartClose');
  const cartPanel = document.getElementById('cartPanel');
  const cartItemsList = document.getElementById('cartItems');
  const cartEmpty = document.getElementById('cartEmpty');
  const cartCount = document.getElementById('cartCount');
  const cartTotal = document.getElementById('cartTotal');
  const cartCheckout = document.getElementById('cartCheckout');
  const loginLink = document.getElementById('navLoginLink');
  const logoutButton = document.getElementById('navLogoutButton');
  const rewardsLink = document.getElementById('navRewardsLink');

  let cartItems = [];
  let isAuthenticated = false;

  if (!grid) {
    return;
  }

  const loadCart = () => {
    try {
      const saved = localStorage.getItem(CART_STORAGE_KEY);
      cartItems = saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.warn('Unable to load cart from storage', error);
      cartItems = [];
    }
    updateCartUI();
  };

  const saveCart = () => {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
  };

  const updateAuthUI = () => {
    if (!loginLink || !logoutButton) return;
    if (isAuthenticated) {
      loginLink.style.display = 'none';
      logoutButton.hidden = false;
    } else {
      loginLink.style.display = '';
      logoutButton.hidden = true;
    }
  };

  const toggleCart = () => {
    if (!cartPanel) return;
    cartPanel.hidden = !cartPanel.hidden;
  };

  const logout = async () => {
    try {
      await fetch(`${PRODUCTS_API_BASE}/logout`, {
        method: 'GET',
        credentials: 'include'
      });
      isAuthenticated = false;
      updateAuthUI();
      closeCart();
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  const closeCart = () => {
    if (!cartPanel) return;
    cartPanel.hidden = true;
  };

  const updateCartUI = () => {
    if (!cartItemsList || !cartCount || !cartTotal || !cartEmpty) return;

    cartItemsList.innerHTML = '';

    if (!cartItems.length) {
      cartEmpty.hidden = false;
      cartTotal.textContent = '₹0.00';
      cartCount.textContent = '0';
      return;
    }

    cartEmpty.hidden = true;
    let total = 0;
    cartItems.forEach((item, index) => {
      total += item.price * item.quantity;
      const row = document.createElement('div');
      row.className = 'cart-item';
      row.innerHTML = `
        <div>
          <strong>${item.name}</strong>
          <p>₹${item.price.toFixed(2)} × ${item.quantity}</p>
        </div>
        <div class="cart-item-actions">
          <button data-action="decrease" data-index="${index}">-</button>
          <button data-action="increase" data-index="${index}">+</button>
          <button data-action="remove" data-index="${index}">&times;</button>
        </div>
      `;
      cartItemsList.appendChild(row);
    });

    cartTotal.textContent = `₹${total.toFixed(2)}`;
    cartCount.textContent = cartItems.reduce((sum, item) => sum + item.quantity, 0);
  };

  const handleCartAction = (action, index) => {
    const item = cartItems[index];
    if (!item) return;

    if (action === 'increase') {
      item.quantity += 1;
    } else if (action === 'decrease') {
      item.quantity -= 1;
      if (item.quantity <= 0) {
        cartItems.splice(index, 1);
      }
    } else if (action === 'remove') {
      cartItems.splice(index, 1);
    }
    saveCart();
    updateCartUI();
  };

  const addToCart = (product) => {
    const existing = cartItems.find((item) => item.id === product.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      cartItems.push({
        id: product.id,
        name: product.name,
        price: Number(product.price || 0),
        image: product.image || '',
        quantity: 1
      });
    }
    saveCart();
    updateCartUI();
  };

  if (cartToggle) {
    cartToggle.addEventListener('click', toggleCart);
  }
  if (cartClose) {
    cartClose.addEventListener('click', closeCart);
  }
  if (cartItemsList) {
    cartItemsList.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-action]');
      if (!button) return;
      const { action, index } = button.dataset;
      handleCartAction(action, Number(index));
    });
  }
  if (cartCheckout) {
    cartCheckout.addEventListener('click', () => {
      if (!cartItems.length) {
        alert('Add items to the cart before checking out.');
        return;
      }
      alert('Checkout flow coming soon!');
    });
  }

  if (rewardsLink) {
    rewardsLink.addEventListener('click', (event) => {
      if (!isAuthenticated) {
        event.preventDefault();
        alert('Please log in to access rewards.');
        window.location.href = 'login.html?next=rewards.html';
      }
    });
  }

  if (logoutButton) {
    logoutButton.addEventListener('click', logout);
  }

  const normalizeProduct = (product) => {
    return {
      id: product.id || product._id || product.slug || product.name,
      name: product.name || 'Untitled Product',
      description: product.description || '',
      price: Number(product.price || 0),
      image: product.image || '',
    };
  };

  const createProductCard = (product) => {
    const card = document.createElement('div');
    card.className = 'product-card';

    const imageContent = product.image
      ? `<img src="${product.image}" alt="${product.name}">`
      : '<div class="no-image"><i class="fas fa-image"></i></div>';

    card.innerHTML = `
      <div class="product-image">
        ${imageContent}
      </div>
      <div class="product-info">
        <h2>${product.name}</h2>
        <p class="product-description">${product.description || ''}</p>
        <p class="product-price">₹${Number(product.price || 0).toFixed(2)}</p>
        <button class="cart-add-btn" data-product-id="${product.id}">Add to Cart</button>
      </div>
    `;

    const addButton = card.querySelector('.cart-add-btn');
    addButton.addEventListener('click', () => addToCart(product));

    return card;
  };

  const renderProducts = (products) => {
    grid.innerHTML = '';
    if (!products.length) {
      emptyState.hidden = false;
      return;
    }

    emptyState.hidden = true;
    const fragment = document.createDocumentFragment();
    products.forEach((product) => fragment.appendChild(createProductCard(product)));
    grid.appendChild(fragment);
  };

  const loadProducts = async () => {
    try {
      const response = await fetch(`${PRODUCTS_API_BASE}/api/products`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();
      const products = Array.isArray(data) ? data : data.products || [];
      const normalizedProducts = products.map(normalizeProduct);
      renderProducts(normalizedProducts);
    } catch (error) {
      console.error('Failed to load products:', error);
      emptyState.hidden = false;
      emptyState.querySelector('p').textContent = 'Unable to load products right now. Please try again later.';
    } finally {
      if (loader) {
        loader.remove();
      }
    }
  };

  const loadSession = async () => {
    try {
      const response = await fetch(`${PRODUCTS_API_BASE}/api/session`, {
        method: 'GET',
        credentials: 'include',
        headers: { 'Accept': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        isAuthenticated = !!data.authenticated;
        updateAuthUI();
      }
    } catch (error) {
      console.error('Failed to load session info:', error);
    }
  };

  loadCart();
  loadSession();
  loadProducts();
});


