// AvtoKontrient Main JavaScript - Enhanced Version
$(document).ready(function() {
    // CSRF Token setup for Django
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    // Configure AJAX defaults
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    });

    // Notification system - Xabarnoma ko'rsatish funksiyasi
    function showNotification(message, type = 'success') {
        const types = {
            success: 'alert-success',
            error: 'alert-danger',
            info: 'alert-info',
            warning: 'alert-warning'
        };

        const alertClass = types[type] || types.success;
        const notificationId = 'notification-' + Date.now();

        const notification = $(`
            <div id="${notificationId}" class="alert ${alertClass} alert-dismissible fade show position-fixed"
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);

        $('body').append(notification);

        // 3 soniyadan keyin avtomatik o'chirish
        setTimeout(() => {
            const alert = bootstrap.Alert.getOrCreateInstance(`#${notificationId}`);
            alert.close();
        }, 3000);
    }

    // Add to cart functionality - Savatga qo'shish funksiyasi
    $('.add-to-cart').click(function() {
        const button = $(this);
        const productId = button.data('product-id');
        const originalHTML = button.html();

        if (!productId) {
            console.error('Xatolik: product-id topilmadi!');
            showNotification('Mahsulot ID topilmadi. Iltimos, sahifani yangilang.', 'error');
            return;
        }

        // Yuklanish holatini ko'rsatish
        button.html('<span class="spinner-border spinner-border-sm"></span> Qo\'shilmoqda...');
        button.prop('disabled', true);

        $.ajax({
            url: `/orders/add-to-cart/${productId}/`,
            method: 'POST',
            dataType: 'json'
        })
        .done(function(data) {
            if (data.success) {
                $('#cart-count').text(data.cart_count);
                button.html('<i class="fas fa-check"></i> Qo\'shildi');
                showNotification(data.message, "success");

                setTimeout(() => {
                    button.html(originalHTML);
                    button.prop('disabled', false);
                }, 2000);
            } else {
                button.html(originalHTML);
                button.prop('disabled', false);
                showNotification(data.message || "Mahsulotni savatga qo'shishda xatolik yuz berdi.", "error");
            }
        })
        .fail(function(xhr) {
            button.html(originalHTML);
            button.prop('disabled', false);

            let errorMsg = "Xatolik yuz berdi!";
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMsg = xhr.responseJSON.message;
            } else if (xhr.status === 404) {
                errorMsg = "Mahsulot topilmadi yoki URL noto'g'ri.";
            } else if (xhr.status === 500) {
                errorMsg = "Serverda ichki xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.";
            }
            showNotification(errorMsg, "error");
            console.error('Savatga qo\'shishda AJAX xatosi:', xhr.responseText);
        });
    });

    // Enhanced Wishlist functionality - Sevimlilar funksiyasi
    $('.wishlist-btn').click(function() {
        const productId = $(this).data('product-id');
        const button = $(this);
        const icon = button.find('i');

        const originalHTML = button.html();
        button.html('<span class="spinner-border spinner-border-sm"></span>');
        button.prop('disabled', true);

        $.ajax({
            url: `/wishlist/${productId}/`,
            method: 'POST',
            dataType: 'json'
        })
        .done(function(data) {
            if (data.wishlisted) {
                button.removeClass('btn-outline-danger').addClass('btn-danger');
                icon.removeClass('far').addClass('fas');
                showNotification(data.message || "Sevimlilar ro'yxatiga qo'shildi!", "success");
            } else {
                button.removeClass('btn-danger').addClass('btn-outline-danger');
                icon.removeClass('fas').addClass('far');
                showNotification(data.message || "Sevimlilar ro'yxatidan o'chirildi!", "info");
            }
        })
        .fail(function(xhr) {
            const errorMsg = xhr.responseJSON?.message || "Xatolik yuz berdi!";
            showNotification(errorMsg, "error");
            console.error('Wishlist error:', xhr.responseText);
        })
        .always(function() {
            button.html(icon);
            button.prop('disabled', false);
        });
    });

    // Smooth scrolling
    $('a[href^="#"]').click(function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 800);
        }
    });

    // Load cart count on page load
    function loadCartCount() {
        $.get('/orders/cart-count/')
        .done(function(data) {
            if (data.success) {
                $('#cart-count').text(data.count);
            } else {
                $('#cart-count').text('0');
                console.error("Savat sonini yuklashda xatolik:", data.message);
            }
        })
        .fail(function(xhr) {
            $('#cart-count').text('0');
            console.error('Savat sonini yuklashda AJAX xatosi:', xhr.responseText);
        });
    }

    loadCartCount();

    // Auto-hide alerts
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);

    // Back to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            if ($('#back-to-top').length === 0) {
                $('body').append(`
                    <button id="back-to-top" class="btn btn-primary position-fixed"
                            style="bottom: 20px; right: 20px; z-index: 999; border-radius: 50%; width: 50px; height: 50px;">
                        <i class="fas fa-arrow-up"></i>
                    </button>
                `);

                $('#back-to-top').click(function() {
                    $('html, body').animate({ scrollTop: 0 }, 800);
                });
            }
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });

    // Kategoriyalar uchun JavaScript
    function toggleCategory(categoryId) {
        const subcategories = document.getElementById(categoryId);
        const allSubcategories = document.querySelectorAll('.subcategories');

        // Barcha subkategoriyalarni yopish
        allSubcategories.forEach(item => {
            if (item.id !== categoryId) {
                item.classList.remove('active');
            }
        });

        // Tanlangan kategoriyani ochish/yopish
        subcategories.classList.toggle('active');

        // Agar "Boshqa kategoriyalar" bosilsa, boshqa kategoriyalarni yopish
        if (categoryId === 'moreCategories') {
            document.querySelectorAll('.subcategories:not(#moreCategories)').forEach(item => {
                item.classList.remove('active');
            });
        } else {
            document.getElementById('moreCategories').classList.remove('active');
        }
    }

    // Kategoriyalar uchun hodisalar
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', function() {
            const categoryId = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            toggleCategory(categoryId);
        });
    });
});