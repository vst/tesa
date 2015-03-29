// Define cart identifier:
var IDENTIFIER_CART = "tesa:cart";

// Define the CartItem object:
function CartItem (id,
                   code,
                   name,
                   price,
                   quantity,
                   tag,
                   location,
                   cfor) {
    this.id = id;
    this.code = code;
    this.name = name;
    this.price = price;
    this.quantity = quantity;
    this.tag = tag;
    this.location = location;
    this.cfor = cfor;
    this.hashid = (this.id + "-" + this.code + "-" + this.name + "-" + this.price + "-" + this.quantity + "-" + this.tag + "-" + this.location + "-" + this.cfor).hashCode();
    this.createdAt = new Date().getTime();
}

function clearCart () {
    window.localStorage.setItem(IDENTIFIER_CART, JSON.stringify({}));
}

function getCart () {
    var cart = window.localStorage.getItem(IDENTIFIER_CART);
    if (cart == null) {
        clearCart();
    }
    return JSON.parse(window.localStorage.getItem(IDENTIFIER_CART));
}

function addToCart (item) {
    var items = getCart();
    items[item.hashid] = item;
    window.localStorage.setItem(IDENTIFIER_CART, JSON.stringify(items));
}

function removeFromCart (hashid) {
    var items = getCart();
    delete items[hashid];
    window.localStorage.setItem(IDENTIFIER_CART, JSON.stringify(items));
    return getCart();
}

function actionSACartDialog (id) {
    // Get OEMs:
    SAProduct.query(SAProductSearchFields)
        .filter([["id", "=", id]])
        .all().then(function (items) {
            // Check items:
            if (items.length == 0) {
                alert("No product found.");
                return;
            }

            // Get item:
            var item = items[0]

            var source   = $("#tesaSAProductCartDialogTemplate").html();
            var template = Handlebars.compile(source);
            var html = template(item);

            $("#tesaSAProductCartDialogContainer").html(html);
            $("#tesaSAProductCartDialog").modal("toggle");
        });
}

function actionSACartIt (id) {
    // Get data:
    var name = $("#tesaSAProductCartName").val().trim();
    var code = $("#tesaSAProductCartCode").val().trim();
    var id = parseInt($("#tesaSAProductCartId").val().trim());
    var price = parseFloat($("#tesaSAProductCartPrice").val().trim() || 1);
    var quantity = parseInt($("#tesaSAProductCartQuantity").val().trim() || 1);
    var tag = $("#tesaSAProductCartTag").val().trim() || "None"
    var location = $("input[name=tesaSAProductCartLocation]:checked").val().trim();
    var cfor = $("input[name=tesaSAProductCartFor]:checked").val().trim();

    // Prepare the cart item:
    var item = new CartItem (id, code, name, price, quantity, tag, location, cfor);
    addToCart(item);
    alert("Item added to the cart.");
}

function actionSAShowCart () {
    var source   = $("#tesaSACartTemplate").html();
    var template = Handlebars.compile(source);
    var html = template(Object.keys(getCart()).map(function (x) {return getCart()[x];}));
    $("#tesaSAShowCartContainer").html(html);
    $("#tesaSAShowCartDialog").modal("toggle");
}

function getCartSelectedItems () {
    var allVals = [];

    $('input[class=tesa-cart-item]:checked').each(function() {
        allVals.push(JSON.parse($(this).val()));
    });

    if (allVals.length == 0) {
        return [];
    }

    return allVals;
}


function actionCartFromProductPage () {
    var code = $(".tesa-default-code:last span span").html();
    if (code && code.trim()) {
        actionCartProductByCode(code.trim());
    }
}

function actionCartProductByCode (code) {
    var Product = new openerp.Model("product.product");
    Product.query(["id"])
        .filter([["default_code", "=", code]])
        .all().then (function (items) {
            if (items && items.length == 1) {
                actionSACartDialog(items[0].id);
            }
            else {
                alert("Cannot find item...");
            }
        });
}
