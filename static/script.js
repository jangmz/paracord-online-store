// ADD TO CART
document.addEventListener("DOMContentLoaded", function() {
    // event listener -> "add-to-cart" buttons
    var addToCartButtons = document.getElementsByClassName("add-to-cart-btn");
    for (var i = 0; i < addToCartButtons.length; i++) {
        addToCartButtons[i].addEventListener("click", addToCart);
    }

    // function to handle adding items to the cart
    function addToCart(event) {
        var button = event.target;
        var productId = button.dataset.productId;
        var productName = button.dataset.productName;
        var productPrice = button.dataset.productPrice;
        var productQuantity = button.dataset.productQuantity;

        if (productQuantity === "0") {
            showAlert("The product is out of stock! Cannot add to cart.");
            return;
        }
        // data object to send in the AJAX request
        var data = {
            productId: productId,
            productName: productName,
            productPrice: productPrice,
            productQuantity: productQuantity
        };

        // AJAX request to Flask to add the item to the cart
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/add_to_cart", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                // add to cart successful
                showAlert("Item added to cart.");
            }
        };
        xhr.send(JSON.stringify(data));
    }

    // display alert message
    function showAlert(message) {
        alert(message);
    }
});