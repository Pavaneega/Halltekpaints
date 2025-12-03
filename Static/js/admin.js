// Admin Product Management JavaScript

// Global variables
const API_BASE = window.location.port === '5500' ? 'http://127.0.0.1:5000' : '';
let currentEditId = null;
let productsData = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  loadProducts();
  setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
  const form = document.getElementById('productForm');
  if (form) {
    form.addEventListener('submit', handleFormSubmit);
  }

  // Font family preview
  const fontSelect = document.getElementById('fontFamily');
  if (fontSelect) {
    fontSelect.addEventListener('change', updateFontPreview);
  }

  // Close modal on outside click
  const modal = document.getElementById('productModal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeModal();
      }
    });
  }

  // Drag and drop for image upload
  const fileUploadLabel = document.querySelector('.file-upload-label');
  if (fileUploadLabel) {
    fileUploadLabel.addEventListener('dragover', handleDragOver);
    fileUploadLabel.addEventListener('dragleave', handleDragLeave);
    fileUploadLabel.addEventListener('drop', handleDrop);
  }
}

// Load products from server
async function loadProducts() {
  try {
    const response = await fetch(`${API_BASE}/api/products`, {
      credentials: 'include'
    });
    if (response.ok) {
      productsData = await response.json();
      renderProducts();
    }
  } catch (error) {
    console.error('Error loading products:', error);
  }
}

// Render products to the grid
function renderProducts() {
  const grid = document.getElementById('productsGrid');
  if (!grid) return;

  if (productsData.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-box-open"></i>
        <h2>No Products Yet</h2>
        <p>Click "Add New Product" to create your first product</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = productsData.map(product => `
    <div class="product-card" data-id="${product._id || product.id}">
      <div class="product-image">
        ${product.image 
          ? `<img src="${product.image}" alt="${product.name}">`
          : '<div class="no-image"><i class="fas fa-image"></i></div>'
        }
      </div>
      <div class="product-info">
        <h3 style="font-family: ${product.font_family || 'Inter'}">${product.name}</h3>
        <p class="product-description">${product.description || ''}</p>
        <p class="product-price">₹${parseFloat(product.price).toFixed(2)}</p>
        ${product.font_family 
          ? `<p class="product-font"><i class="fas fa-font"></i> ${product.font_family}</p>`
          : ''
        }
      </div>
      <div class="product-actions">
        <button class="btn-edit" onclick="openEditModal('${product._id || product.id}')">
          <i class="fas fa-edit"></i> Edit
        </button>
        <button class="btn-delete" onclick="deleteProduct('${product._id || product.id}', '${product.name}')">
          <i class="fas fa-trash"></i> Delete
        </button>
      </div>
    </div>
  `).join('');
}

// Open modal for adding new product
function openAddModal() {
  currentEditId = null;
  const modal = document.getElementById('productModal');
  const modalTitle = document.getElementById('modalTitle');
  const form = document.getElementById('productForm');
  
  if (modalTitle) {
    modalTitle.innerHTML = '<i class="fas fa-plus-circle"></i> Add New Product';
  }
  
  if (form) {
    form.reset();
    document.getElementById('productId').value = '';
    document.getElementById('existingImage').value = '';
    clearImagePreview();
  }
  
  if (modal) {
    modal.classList.add('active');
  }
}

// Open modal for editing product
async function openEditModal(productId) {
  currentEditId = productId;
  const modal = document.getElementById('productModal');
  const modalTitle = document.getElementById('modalTitle');
  
  if (modalTitle) {
    modalTitle.innerHTML = '<i class="fas fa-edit"></i> Edit Product';
  }

  try {
    const response = await fetch(`${API_BASE}/api/products/${productId}`, {
      credentials: 'include'
    });
    if (response.ok) {
      const product = await response.json();
      populateForm(product);
      
      if (modal) {
        modal.classList.add('active');
      }
    } else {
      showFlashMessage('Error loading product details', 'danger');
    }
  } catch (error) {
    console.error('Error loading product:', error);
    showFlashMessage('Error loading product details', 'danger');
  }
}

// Populate form with product data
function populateForm(product) {
  document.getElementById('productId').value = product._id || product.id;
  document.getElementById('productName').value = product.name || '';
  document.getElementById('productPrice').value = product.price || '';
  document.getElementById('productDescription').value = product.description || '';
  document.getElementById('fontFamily').value = product.font_family || 'Inter';
  document.getElementById('existingImage').value = product.image || '';
  
  // Show existing image preview
  if (product.image) {
    showImagePreview(product.image);
  }
  
  // Update font preview
  updateFontPreview();
}

// Close modal
function closeModal() {
  const modal = document.getElementById('productModal');
  if (modal) {
    modal.classList.remove('active');
  }
  currentEditId = null;
  clearImagePreview();
}

// Handle form submission
async function handleFormSubmit(e) {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const productId = document.getElementById('productId').value;
  
  // If no new image is selected, use existing image
  const imageFile = formData.get('image');
  const existingImageValue = document.getElementById('existingImage').value;
  if ((!imageFile || !imageFile.name) && existingImageValue) {
    formData.set('image_url', existingImageValue);
  }
  
  try {
    const url = productId ? `${API_BASE}/api/products/${productId}` : `${API_BASE}/api/products`;
    const method = productId ? 'PUT' : 'POST';
    
    const response = await fetch(url, {
      method: method,
      credentials: 'include',
      body: formData
    });
    
    if (response.ok) {
      const result = await response.json();
      showFlashMessage(
        productId ? 'Product updated successfully!' : 'Product added successfully!',
        'success'
      );
      closeModal();
      loadProducts(); // Reload products
    } else {
      const error = await response.json();
      showFlashMessage(error.message || 'Error saving product', 'danger');
    }
  } catch (error) {
    console.error('Error saving product:', error);
    showFlashMessage('Error saving product', 'danger');
  }
}

// Delete product
async function deleteProduct(productId, productName) {
  if (!confirm(`Are you sure you want to delete "${productName}"?`)) {
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE}/api/products/${productId}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    
    if (response.ok) {
      showFlashMessage('Product deleted successfully!', 'success');
      loadProducts(); // Reload products
    } else {
      const error = await response.json();
      showFlashMessage(error.message || 'Error deleting product', 'danger');
    }
  } catch (error) {
    console.error('Error deleting product:', error);
    showFlashMessage('Error deleting product', 'danger');
  }
}

// Image preview
function previewImage(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      showImagePreview(e.target.result);
    };
    reader.readAsDataURL(file);
  }
}

function showImagePreview(src) {
  const preview = document.getElementById('imagePreview');
  if (preview) {
    preview.innerHTML = `<img src="${src}" alt="Preview">`;
    preview.classList.add('active');
  }
}

function clearImagePreview() {
  const preview = document.getElementById('imagePreview');
  if (preview) {
    preview.innerHTML = '';
    preview.classList.remove('active');
  }
}

// Drag and drop handlers
function handleDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  e.currentTarget.style.borderColor = 'var(--primary-color)';
  e.currentTarget.style.background = 'rgba(79, 70, 229, 0.1)';
}

function handleDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  e.currentTarget.style.borderColor = 'var(--border-color)';
  e.currentTarget.style.background = '#f9fafb';
}

function handleDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  
  const fileInput = document.getElementById('productImage');
  const files = e.dataTransfer.files;
  
  if (files.length > 0 && files[0].type.startsWith('image/')) {
    fileInput.files = files;
    previewImage({ target: fileInput });
  }
  
  e.currentTarget.style.borderColor = 'var(--border-color)';
  e.currentTarget.style.background = '#f9fafb';
}

// Update font preview
function updateFontPreview() {
  const fontSelect = document.getElementById('fontFamily');
  const preview = document.getElementById('fontPreview');
  
  if (fontSelect && preview) {
    const selectedFont = fontSelect.value;
    const previewText = preview.querySelector('p');
    if (previewText) {
      previewText.style.fontFamily = selectedFont;
      previewText.textContent = `Preview: ${selectedFont}`;
    }
  }
}

// Show flash message
function showFlashMessage(message, category = 'info') {
  const container = document.querySelector('.flash-messages') || createFlashContainer();
  
  const flashDiv = document.createElement('div');
  flashDiv.className = `flash-message flash-${category}`;
  flashDiv.innerHTML = `
    <span>${message}</span>
    <button class="flash-close" onclick="this.parentElement.remove()">&times;</button>
  `;
  
  container.appendChild(flashDiv);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    flashDiv.remove();
  }, 5000);
}

function createFlashContainer() {
  const container = document.createElement('div');
  container.className = 'flash-messages';
  document.body.appendChild(container);
  return container;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
  // ESC to close modal
  if (e.key === 'Escape') {
    const modal = document.getElementById('productModal');
    if (modal && modal.classList.contains('active')) {
      closeModal();
    }
  }
  
  // Ctrl/Cmd + N to add new product
  if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
    e.preventDefault();
    openAddModal();
  }
});
