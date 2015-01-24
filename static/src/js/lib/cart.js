var IDENTIFIER_CART = "tesa:cart";

function clearCart () {
    window.localStorage.setItem(IDENTIFIER_CART, JSON.stringify([]));
}

function getCart () {
    var cart = window.localStorage.getItem(IDENTIFIER_CART);
    if (cart == null) {
        window.localStorage.setItem(IDENTIFIER_CART, JSON.stringify([]));
    }
    return JSON.parse(window.localStorage.getItem(IDENTIFIER_CART));
}

function addItemToCart (item) {
    var items = getCart();
    items.push(item);
    window.localStorage.setItem(IDENTIFIER_CART, JSON.stringify(items));
    return getCart();
}

function putItemsToCart (items) {
    window.localStorage.setItem(IDENTIFIER_CART, JSON.stringify(items));
    return getCart();
}

function removeItemFromCart (uid) {
    var items = getCart();
    putItemsToCart(items.filter(function (x) {
        return x.uid != uid;
    }));
}

function showCart () {
    var source   = $("#tesaCartTemplate").html();
    var template = Handlebars.compile(source);
    var html = template(getCart());
    $("#tesaShowCartContainer").html(html);
    $("#tesaShowCartDialog").modal("toggle");
}

function createNewSalesOrder () {
    var allVals = [];
    $('input[class=tesa-cart-item]:checked').each(function() {
        allVals.push(JSON.parse($(this).val()));
    });

    if (allVals.length == 0) {
        alert("No products chosen.");
        return;
    }

    var Sale = new openerp.Model("sale.order");
    Sale.call("create", [{partner_id: 1}], {}).then(function (saleOrderId) {
        if (!saleOrderId) {
            alert("Can not create. Contact administrator.");
            return;
        }
        var order_lines = [];
        allVals.forEach(function (line) {
            order_lines.push([0, false, {
                delay: 0,
                name: line.name,
                product_id: line.id,
                price_unit: line.price,
                product_uom_qty: line.qty
            }]);
        });
        Sale.call("write", [[saleOrderId], {order_line: order_lines}], {}).then(function () {
            Sale.query(["id", "name"])
                .filter([["id", "=", saleOrderId]])
                .all()
                .then(function (data) {
                    alert("Sales order created: " + data[0].name);
                    allVals.forEach(function (x) {
                        removeItemFromCart(x.uid);
                    });
                    $("#tesaShowCartDialog").modal("toggle");
                })
        })
    })
}
