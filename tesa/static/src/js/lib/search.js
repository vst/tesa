function tesaDisplayOEMS (id) {
    // Check if toggle:
    if ($(".product-oem-for-" + id).length > 0) {
        $(".product-oem-for-" + id).remove()
        $("#product-" + id).css("border-top", "none");
        $("#product-" + id).css("border-left", "none");
        $("#product-" + id).css("border-right", "none");
        $("#product-" + id).find("i").removeClass("glyphicon-chevron-down")
        $("#product-" + id).find("i").addClass("glyphicon-chevron-right")
        return;
    }

    // Get the product class:
    var Product = new openerp.Model("product.product");

    // Fields:
    var fields = [
        "default_code",
        "name",
        "brand",
        "lst_price",
        "minimum_cash_sales_price",
        "export_sales_price",
        "minimum_sales_price",
        "special_sales_price",
        "qty_available",
        "incoming_qty",
        "virtual_available",
        "stock_A_real",
        "stock_B_real",
        "stock_C_real"]

    // Get OEMs:
    Product.query(["id", "related_oems"])
        .filter([["id", "=", id]])
        .all().then (function (items) {
            if (items && items.length > 0) {
                // Get revids:
                revids = items[0].related_oems

                $("#product-" + id).find("i").removeClass("glyphicon-chevron-right")
                $("#product-" + id).find("i").addClass("glyphicon-chevron-down")
                $("#product-" + id).css("border-top", "2px solid black");
                $("#product-" + id).css("border-left", "2px solid black");
                $("#product-" + id).css("border-right", "2px solid black");

                if(revids.length > 0) {
                    // Filter and display:
                    Product.query(fields)
                        .filter([["id", "in", revids]])
                        .all().then(function (items) {
                            var source   = $("#tesaProductSearchResultRowTemplate").html();
                            var template = Handlebars.compile(source);
                            var html = template({items: items, id: id});
                            $("#product-" + id).after(html);
                        });
                }
                else {
                    var source   = $("#tesaProductSearchResultEmptyRowTemplate").html();
                    var template = Handlebars.compile(source);
                    var html = template({id: id});
                    $("#product-" + id).after(html);
                }
            }
        });
}

function showProductSearch () {
    $("#tesaProductSearchDialog").modal("toggle").on('shown.bs.modal', function () {
        $("#teseProductSearchKeyword").focus();
    });
}

function searchProduct () {
    // Get the keyword:
    var keyword = $("#teseProductSearchKeyword").val().trim();

    // Get the product class:
    var Product = new openerp.Model("product.product");

    // Fields:
    var fields = [
        "default_code",
        "name",
        "brand",
        "lst_price",
        "minimum_cash_sales_price",
        "export_sales_price",
        "minimum_sales_price",
        "special_sales_price",
        "qty_available",
        "incoming_qty",
        "virtual_available",
        "stock_A_real",
        "stock_B_real",
        "stock_C_real"]

    var source   = $("#tesaProductSearchResultTableTemplate").html();
    var template = Handlebars.compile(source);
    $("#tesaProductSearchResultContainer").html(template());

    source   = $("#tesaProductSearchResultBodyTemplate").html();
    template = Handlebars.compile(source);
    $(".tesaProductSearchResultTable").append(template({searchcode: keyword, searchcodehash: keyword.hashCode()}));

    // Filter and display:
    var Product = new openerp.Model("product.product");
    Product.query(fields)
        .filter([["default_code", "ilike", keyword]])
        .limit(100)
        .all().then(function (items) {
            var source   = $("#tesaProductSearchResultTemplate").html();
            var template = Handlebars.compile(source);
            $(".tesaProductSearchResults-" + keyword.hashCode()).html(template({searchkey: keyword, fields: fields, items: items}));
            $(".tesaProductSearchResultsHeader-" + keyword.hashCode() + " .tesa-loading").html("");
        });
}
