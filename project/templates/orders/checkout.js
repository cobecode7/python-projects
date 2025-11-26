
// وظائف الكوبونات
document.addEventListener('DOMContentLoaded', function() {
    // تطبيق الكوبون
    document.getElementById('apply-coupon').addEventListener('click', function() {
        const couponCode = document.getElementById('coupon-code').value.trim();

        if (!couponCode) {
            showCouponMessage('{% trans "يرجى إدخال كود الكوبون" %}', 'danger');
            return;
        }

        fetch('/api/coupons/api/apply/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `code=${encodeURIComponent(couponCode)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showCouponMessage(data.error, 'danger');
            } else {
                // عرض الكوبون المطبق
                document.getElementById('applied-coupon').classList.remove('d-none');
                document.getElementById('coupon-code').value = '';

                // تحديث نص الخصم
                const discountType = data.coupon.discount_type;
                const discountValue = data.coupon.discount_value;
                let discountText = '';

                if (discountType === 'percentage') {
                    discountText = `{% trans "خصم" %} ${discountValue}%`;
                } else {
                    discountText = `{% trans "خصم" %} ${discountValue}`;
                }

                document.getElementById('coupon-discount-text').textContent = discountText;

                // تحديث ملخص الطلب
                updateOrderTotals(data.cart_total, data.new_total, data.coupon.discount);

                showCouponMessage('{% trans "تم تطبيق الكوبون بنجاح" %}', 'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showCouponMessage('{% trans "حدث خطأ أثناء تطبيق الكوبون" %}', 'danger');
        });
    });

    // إزالة الكوبون
    document.getElementById('remove-coupon').addEventListener('click', function() {
        fetch('/api/coupons/api/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            // إخفاء الكوبون
            document.getElementById('applied-coupon').classList.add('d-none');

            // تحديث ملخص الطلب
            updateOrderTotals(data.cart_total, data.new_total, 0);

            showCouponMessage('{% trans "تم إزالة الكوبون" %}', 'info');
        })
        .catch(error => {
            console.error('Error:', error);
            showCouponMessage('{% trans "حدث خطأ أثناء إزالة الكوبون" %}', 'danger');
        });
    });

    // التحقق من وجود كوبون في الجلسة
    {% if request.session.coupon_code %}
        document.getElementById('applied-coupon').classList.remove('d-none');

        // تحديث نص الخصم
        document.getElementById('coupon-discount-text').textContent = `{% trans "خصم" %} {{ request.session.coupon_discount }}`;

        // تحديث ملخص الطلب
        const subtotal = parseFloat('{{ cart.get_total_price }}');
        const shipping = 10.00;
        const discount = parseFloat('{{ request.session.coupon_discount }}');
        updateOrderTotals(subtotal, subtotal + shipping - discount, discount);
    {% endif %}
});

function showCouponMessage(message, type) {
    const messageDiv = document.getElementById('coupon-message');
    messageDiv.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;

    // إخفاء الرسالة بعد 5 ثوانٍ
    setTimeout(() => {
        messageDiv.innerHTML = '';
    }, 5000);
}

function updateOrderTotals(subtotal, total, discount) {
    const shipping = 10.00;
    document.getElementById('subtotal').textContent = subtotal.toFixed(2);

    // عرض/إخفاء صف الخصم
    const discountRow = document.getElementById('coupon-discount-row');
    if (discount > 0) {
        discountRow.classList.remove('d-none');
        document.getElementById('coupon-discount-value').textContent = `-${discount.toFixed(2)}`;
    } else {
        discountRow.classList.add('d-none');
    }

    document.getElementById('total').textContent = total.toFixed(2);
}

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
