// static/js/main.js
const $ = window.jQuery; // $ ni global qilib e'lon qilish

$(document).ready(() => {
  // CSRF Tokenini AJAX so'rovlariga qo'shish uchun sozlash
  $.ajaxSetup({
    beforeSend: (xhr, settings) => {
      // Faqat o'zingizning domainingizdagi POST so'rovlarga CSRF tokenini qo'shing
      if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        xhr.setRequestHeader("X-CSRFToken", window.CSRF_TOKEN); // Global CSRF_TOKEN ishlatiladi
      }
    },
  });

  // Savatga qo'shish funksionalligi
  $(".add-to-cart").on("click", function () {
    const url = $(this).data("add-to-cart-url");
    const button = $(this);
    const originalText = button.html();

    if (!url) {
      console.error("Add to cart URL not found.");
      showNotification("Savatga qo'shish URL manzili topilmadi!", "error");
      return;
    }

    button.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Qo\'shilmoqda...');
    button.prop("disabled", true);

    $.ajax({
      url: url,
      type: "POST",
      data: {}, // POST so'rovida ma'lumot bo'lmasa ham bo'sh obyekt yuborish
      success: (data) => {
        if (data.success) {
          $("#cart-count").text(data.cart_count); // Savatdagi mahsulotlar sonini yangilash
          button.html('<i class="fas fa-check"></i> Qo\'shildi');
          showNotification(data.message, "success");
          setTimeout(() => {
            button.html(originalText);
            button.prop("disabled", false);
          }, 2000);
        } else {
          showNotification(data.message || "Xatolik yuz berdi!", "error");
          button.html(originalText);
          button.prop("disabled", false);
        }
      },
      error: (jqXHR, textStatus, errorThrown) => {
        console.error("Add to cart AJAX error:", textStatus, errorThrown, jqXHR.responseText);
        showNotification("Mahsulotni savatga qo'shishda xatolik yuz berdi!", "error");
        button.html(originalText);
        button.prop("disabled", false);
      },
    });
  });

  // Sevimlilar funksionalligi
$(".wishlist-btn").on("click", function () {
  const url = $(this).data("toggle-wishlist-url");
  const button = $(this);

  if (!url) {
    console.error("Wishlist toggle URL not found.");
    showNotification("Sevimlilar URL manzili topilmadi!", "error");
    return;
  }

  const isCurrentlyWishlisted = button.hasClass("btn-danger");
  button.prop("disabled", true);

  // Optimistik UI: holatni oldindan o'zgartiramiz
  if (isCurrentlyWishlisted) {
    // Agar hozirda sevimlida bo'lsa → o'chirish
    button.removeClass("btn-danger").addClass("btn-outline-danger");
    button.find("i").removeClass("fas fa-heart").addClass("far fa-heart");
    showNotification("Sevimlilardan olib tashlandi!", "info");
  } else {
    // Aks holda → qo'shish
    button.removeClass("btn-outline-danger").addClass("btn-danger");
    button.find("i").removeClass("far fa-heart").addClass("fas fa-heart");
    showNotification("Sevimlilarga qo'shildi!", "success");
  }

  $.ajax({
    url: url,
    type: "POST",
    data: {},
    success: (data) => {
      // Server success bo'lsa, hech narsa qilmaymiz, UI oldindan o'zgargan
      button.prop("disabled", false);
    },
    error: (jqXHR, textStatus, errorThrown) => {
      console.error("Wishlist AJAX error:", textStatus, errorThrown, jqXHR.responseText);
      // Agar xato bo'lsa, UI ni oldingi holatga qaytaramiz:
      if (isCurrentlyWishlisted) {
        // Bu holda oldin sevimlida edi → biz o'chirdik → qaytaramiz
        button.removeClass("btn-outline-danger").addClass("btn-danger");
        button.find("i").removeClass("far fa-heart").addClass("fas fa-heart");
        showNotification("Sevimlilarga qaytarildi!", "success");
      } else {
        // Bu holda oldin sevimlida emas edi → biz qo'shdik → qaytaramiz
        button.removeClass("btn-danger").addClass("btn-outline-danger");
        button.find("i").removeClass("fas fa-heart").addClass("far fa-heart");
        showNotification("Sevimlilar ro'yxatidan olib tashlandi!", "info");
      }
      button.prop("disabled", false);
    },
  });
});


  // Xabar ko'rsatish funksiyasi
  function showNotification(message, type) {
    const alertClass = type === "success" ? "alert-success" : type === "error" ? "alert-danger" : "alert-info";
    // Eski xabarlarni tozalash
    $(".notification-alert").remove();

    const notification = `
      <div class="alert ${alertClass} alert-dismissible fade show position-fixed notification-alert"
           style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
          ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;

    $("body").append(notification);

    // 4 soniyadan keyin avtomatik yopish
    setTimeout(() => {
      $(".notification-alert").fadeOut(() => {
        $(this).remove();
      });
    }, 4000);
  }

  // Sahifa yuklanganda savat sonini yuklash
  loadCartCount();

  function loadCartCount() {
    if (window.CART_COUNT_URL) {
      $.ajax({
        url: window.CART_COUNT_URL,
        type: "GET",
        success: (data) => {
          if (data.success) {
            $("#cart-count").text(data.count);
          } else {
            $("#cart-count").text("0");
            console.error("Failed to load cart count:", data.message);
          }
        },
        error: (jqXHR, textStatus, errorThrown) => {
          console.error("Cart count AJAX error:", textStatus, errorThrown, jqXHR.responseText);
          $("#cart-count").text("0");
        },
      });
    } else {
      console.warn("window.CART_COUNT_URL is not defined. Cart count might not load.");
      $("#cart-count").text("0");
    }
  }

  // Alertsni avtomatik yashirish
  setTimeout(() => {
    $(".alert").fadeOut();
  }, 5000);

  // Tepaga qaytish tugmasi
  $(window).scroll(function () {
    if ($(this).scrollTop() > 300) {
      if ($("#back-to-top").length === 0) {
        $("body").append(`
                <button id="back-to-top" class="btn btn-primary position-fixed"
                        style="bottom: 20px; right: 20px; z-index: 999; border-radius: 50%; width: 50px; height: 50px;">
                    <i class="fas fa-arrow-up"></i>
                </button>
            `);
      }
      $("#back-to-top").fadeIn();
    } else {
      $("#back-to-top").fadeOut();
    }
  });

  $(document).on("click", "#back-to-top", () => {
    $("html, body").animate({ scrollTop: 0 }, 800);
  });
});
console.log(window.CSRF_TOKEN)
