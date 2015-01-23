Handlebars.registerHelper("formatCurrency", function(value) {
    return numeral(value).format("0.00");
});

Handlebars.registerHelper("add1", function(value) {
    return value + 1;
});

Handlebars.registerHelper("cartsel", function(id, price, qty, xname, uid) {
    return JSON.stringify({
        id: id,
        price: price,
        qty: qty,
        name: xname,
        uid: uid,
    });
});

Handlebars.registerHelper("cartselname", function(id, price, qty) {
    return "" + id + price + qty + ("" + Math.random()).split(".")[1];
});
