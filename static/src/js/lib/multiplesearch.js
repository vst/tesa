function clearMultipleSearchResults () {
    $("#tesaMultipleProductSearchResultContainer").html("");
}

function searchMultipleProduct () {
    // Get the keyword:
    var keywords = $("#teseMultipleProductSearchKeyword").val().trim();
    keywords = keywords.split("\n").map(function (line) {
        var tuple = line.split("\t");
        return {
            code: tuple[0].trim(),
            qty: (tuple.length > 1 ? tuple[1].trim() : 1)
        }
    });

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

    // Add the table:
    var source   = $("#tesaProductSearchResultTableTemplate").html();
    var template = Handlebars.compile(source);
    $("#tesaMultipleProductSearchResultContainer").html(template());

    // Put the search terms:
    keywords.forEach ( function (keyword) {
        var source   = $("#tesaProductSearchResultBodyTemplate").html();
        var template = Handlebars.compile(source);
        $(".tesaProductSearchResultTable").append(template({searchcode: keyword.code, searchcodehash: keyword.code.hashCode()}));
    });

    // Filter and display:
    keywords = keywords.map(function (x) {return x.code});

    Product.query(fields)
        .filter([["default_code", "in", keywords]])
        .all()
        .then(function (items) {
            items.forEach (function (item) {
                var keyword = item.default_code;
                if (items.length > 0) {
                    var source   = $("#tesaProductSearchResultTemplate").html();
                    var template = Handlebars.compile(source);
                    $(".tesaProductSearchResults-" + keyword.hashCode()).html(template({searchkey: keyword, fields: fields, items: [item]}));
                    $(".tesaProductSearchResultsHeader-" + keyword.hashCode() + " .tesa-loading").html("");
                }
                else {
                    $(".tesaProductSearchResultsHeader-" + keyword.hashCode() + " .tesa-loading").html("");
                    $(".tesaProductSearchResultsHeader-" + keyword.hashCode()).parent().removeClass("bg-primary").addClass("bg-danger");
                }
            });
            keywords.forEach (function (keyword) {
                var item = $(".tesaProductSearchResultsHeader-" + keyword.hashCode() + " .tesa-loading").html();
                if (item) {
                    $(".tesaProductSearchResultsHeader-" + keyword.hashCode() + " .tesa-loading").html("");
                    $(".tesaProductSearchResultsHeader-" + keyword.hashCode() + " .tesa-loading").parent().removeClass("bg-primary").addClass("bg-danger").css("color", "black");
                }
            });
        })
        .fail(function () {
            console.log("Fail");
        });

    // // Filter and display:
    // keywords.forEach ( function (keyword) {
    //     Product.query(fields)
    //         .filter([["default_code", "=", keyword.code]])
    //         .limit(100)
    //         .all()
    //         .then(function (items) {
    //             if (items.length > 0) {
    //                 keyword.result = items;
    //                 var source   = $("#tesaProductSearchResultTemplate").html();
    //                 var template = Handlebars.compile(source);
    //                 $(".tesaProductSearchResults-" + keyword.code.hashCode()).html(template({searchkey: keyword.code, fields: fields, items: items}));
    //                 $(".tesaProductSearchResultsHeader-" + keyword.code.hashCode() + " .tesa-loading").html("");
    //             }
    //             else {
    //                 $(".tesaProductSearchResultsHeader-" + keyword.code.hashCode() + " .tesa-loading").html("");
    //                 $(".tesaProductSearchResultsHeader-" + keyword.code.hashCode()).parent().removeClass("bg-primary").addClass("bg-danger");
    //             }
    //         })
    //         .fail(function () {
    //             console.log("Fail");
    //         });
    // });
}

function showMultipleProductSearch () {
    $("#tesaMultipleProductSearchDialog").modal("toggle").on('shown.bs.modal', function () {
        $("#teseMultipleProductSearchKeyword").focus();
    });
}
