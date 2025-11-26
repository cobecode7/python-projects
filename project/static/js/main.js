
// JavaScript للمتجر الإلكتروني

// عند تحميل الصفحة بالكامل
document.addEventListener('DOMContentLoaded', function() {
    // تهيئة جميع المكونات
    initCarousel();
    initProductGallery();
    initQuantitySelector();
    initPaymentMethod();
    initAddressForm();
    initWishlist();
    initSearch();
});

// تهيئة عرض الشرائح
function initCarousel() {
    const carouselElement = document.querySelector('#mainCarousel');
    if (carouselElement) {
        const carousel = new bootstrap.Carousel(carouselElement, {
            interval: 5000,
            wrap: true
        });
    }
}

// تهيئة معرض الصور للمنتج
function initProductGallery() {
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    const mainImage = document.querySelector('.product-image');

    if (thumbnails && mainImage) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // إزالة الفئة النشطة من جميع الصور المصغرة
                thumbnails.forEach(thumb => thumb.classList.remove('active'));

                // إضافة الفئة النشطة للصورة المصغرة المحددة
                this.classList.add('active');

                // تغيير الصورة الرئيسية
                mainImage.src = this.src.replace('thumb', 'large');
            });
        });
    }
}

// تهيئة منتقي الكمية
function initQuantitySelector() {
    const quantitySelectors = document.querySelectorAll('.quantity-selector');

    quantitySelectors.forEach(selector => {
        const decreaseBtn = selector.querySelector('.decrease-quantity');
        const increaseBtn = selector.querySelector('.increase-quantity');
        const quantityInput = selector.querySelector('.quantity-input');

        if (decreaseBtn && increaseBtn && quantityInput) {
            decreaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(quantityInput.value);
                if (currentValue > 1) {
                    quantityInput.value = currentValue - 1;
                }
            });

            increaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(quantityInput.value);
                const max = parseInt(quantityInput.getAttribute('max') || 999);
                if (currentValue < max) {
                    quantityInput.value = currentValue + 1;
                }
            });
        }
    });
}

// تهيئة طرق الدفع
function initPaymentMethod() {
    const paymentMethods = document.querySelectorAll('.payment-method');

    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            // إزالة الفئة المحددة من جميع طرق الدفع
            paymentMethods.forEach(m => m.classList.remove('selected'));

            // إضافة الفئة المحددة لطريقة الدفع المحددة
            this.classList.add('selected');

            // تحديث قيمة الحقل المخفي
            const paymentInput = document.querySelector('#payment_method');
            if (paymentInput) {
                paymentInput.value = this.getAttribute('data-method');
            }
        });
    });
}

// تهيئة نموذج العنوان
function initAddressForm() {
    const addressForm = document.querySelector('#address-form');
    const sameAsShippingCheckbox = document.querySelector('#same_as_shipping');
    const billingAddressFields = document.querySelectorAll('.billing-address-field');

    if (sameAsShippingCheckbox && billingAddressFields.length > 0) {
        sameAsShippingCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // إخفاء حقول عنوان الفوترة
                billingAddressFields.forEach(field => {
                    field.closest('.mb-3').style.display = 'none';
                });
            } else {
                // إظهار حقول عنوان الفوترة
                billingAddressFields.forEach(field => {
                    field.closest('.mb-3').style.display = 'block';
                });
            }
        });
    }
}

// تهيئة قائمة الرغبات
function initWishlist() {
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');

    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const productId = this.getAttribute('data-product-id');
            const isInWishlist = this.classList.contains('active');

            // إرسال طلب إلى الخادم
            fetch(`/api/wishlist/${productId}/`, {
                method: isInWishlist ? 'DELETE' : 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // تغيير حالة الزر
                    this.classList.toggle('active');

                    // عرض رسالة نجاح
                    showToast(data.message, 'success');
                } else {
                    // عرض رسالة خطأ
                    showToast(data.message, 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('حدث خطأ ما. يرجى المحاولة مرة أخرى.', 'danger');
            });
        });
    });
}

// تهيئة البحث
function initSearch() {
    const searchInput = document.querySelector('#search-input');
    const searchResults = document.querySelector('#search-results');

    if (searchInput && searchResults) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(() => {
                // إرسال طلب بحث
                fetch(`/api/products/search/?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    if (data.results && data.results.length > 0) {
                        // عرض النتائج
                        let html = '';
                        data.results.forEach(product => {
                            html += `
                                <div class="search-result p-2 border-bottom">
                                    <div class="d-flex">
                                        <img src="${product.image}" alt="${product.name}" class="me-3" width="50" height="50">
                                        <div>
                                            <h6 class="mb-0">${product.name}</h6>
                                            <small class="text-muted">${product.price} ريال</small>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });

                        searchResults.innerHTML = html;
                        searchResults.style.display = 'block';
                    } else {
                        searchResults.innerHTML = '<div class="p-2 text-center">لا توجد نتائج</div>';
                        searchResults.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }, 300);
        });

        // إخفاء النتائج عند النقر خارجها
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
}

// الحصول على قيمة الكوكيز
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// عرض رسالة تنبيه
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('#toast-container');

    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '11';
        document.body.appendChild(container);
    }

    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    document.querySelector('#toast-container').insertAdjacentHTML('beforeend', toastHtml);

    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// تحديث عدد العناصر في السلة
function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('.cart-count');

    cartCountElements.forEach(element => {
        if (count > 0) {
            element.textContent = count;
            element.style.display = 'inline-block';
        } else {
            element.style.display = 'none';
        }
    });
}

// إضافة منتج للسلة
function addToCart(productId, quantity = 1) {
    fetch('/api/cart/add/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // تحديث عدد العناصر في السلة
            updateCartCount(data.cart_count);

            // عرض رسالة نجاح
            showToast('تمت إضافة المنتج إلى السلة', 'success');
        } else {
            // عرض رسالة خطأ
            showToast(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('حدث خطأ ما. يرجى المحاولة مرة أخرى.', 'danger');
    });
}
