// Price Range Filter
document.addEventListener("DOMContentLoaded", function () {
  const minInput = document.getElementById("price-min");
  const maxInput = document.getElementById("price-max");
  const minRange = document.getElementById("price-range-min");
  const maxRange = document.getElementById("price-range-max");
  const applyBtn = document.querySelector(".apply-price-filter");

  // Sync number inputs with range sliders
  minInput.addEventListener("input", () => {
    const val = parseFloat(minInput.value);
    if (val < parseFloat(maxInput.value)) {
      minRange.value = val;
    }
  });

  maxInput.addEventListener("input", () => {
    const val = parseFloat(maxInput.value);
    if (val > parseFloat(minInput.value)) {
      maxRange.value = val;
    }
  });

  minRange.addEventListener("input", () => {
    const val = parseFloat(minRange.value);
    if (val < parseFloat(maxRange.value)) {
      minInput.value = val;
    }
  });

  maxRange.addEventListener("input", () => {
    const val = parseFloat(maxRange.value);
    if (val > parseFloat(minRange.value)) {
      maxInput.value = val;
    }
  });

  // Apply filter
  applyBtn.addEventListener("click", () => {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set("price_min", minInput.value);
    urlParams.set("price_max", maxInput.value);
    window.location.search = urlParams.toString();
  });
});

// AJAX to send the product id to add to cart view
document.addEventListener("DOMContentLoaded", function () {
  const addToCartForms = document.querySelectorAll(".add-to-cart-form");

  addToCartForms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const productId = this.querySelector('input[name="product_id"]').value;
      const button = this.querySelector(".add-to-cart");
      const originalText = button.innerText;

      const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
      ).value;

      fetch("{% url 'payments:add_to_cart' %}", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: 1,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            button.innerText = "Added!";
            button.style.backgroundColor = "#28a745";

            const cartCount = document.querySelector(".cart-count");
            if (cartCount && data.cart_count) {
              cartCount.innerText = data.cart_count;
            }

            setTimeout(() => {
              button.innerText = originalText;
              button.style.backgroundColor = "";
            }, 2000);
          } else {
            button.innerText = "Error!";
            button.style.backgroundColor = "#dc3545";
            setTimeout(() => {
              button.innerText = originalText;
              button.style.backgroundColor = "";
            }, 2000);
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          button.innerText = "Error!";
          button.style.backgroundColor = "#dc3545";
          setTimeout(() => {
            button.innerText = originalText;
            button.style.backgroundColor = "";
          }, 2000);
        });
    });
  });
});
