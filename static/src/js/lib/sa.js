// Get the product class:
var SAProduct = new openerp.Model("product.product");

// Define search fields:
var SAProductSearchFields = [
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
    "outgoing_qty",
    "virtual_available",
    "stock_A_real",
    "stock_B_real",
    "stock_C_real"];


function SearchTerm (keyword) {
    this.keyword = keyword;
    this.hashid = keyword.hashCode();
}

function tesaSADisplayOEMS (id) {
    // Check if toggle:
    if ($(".product-oem-for-" + id).length > 0) {
        $(".product-oem-for-" + id).remove()
        $(".tesaSAProductSearchResultRow-" + id).css("border-top", "none");
        $(".tesaSAProductSearchResultRow-" + id).css("border-left", "none");
        $(".tesaSAProductSearchResultRow-" + id).css("border-right", "none");
        $(".tesaSAProductSearchResultRow-" + id).find("i").removeClass("glyphicon-chevron-down")
        $(".tesaSAProductSearchResultRow-" + id).find("i").addClass("glyphicon-chevron-right")
        return;
    }

    // Get OEMs:
    SAProduct.query(["id", "related_oems"])
        .filter([["id", "=", id]])
        .all().then (function (items) {
            if (items && items.length > 0) {
                // Get revids:
                revids = items[0].related_oems

                $(".tesaSAProductSearchResultRow-" + id).find("i").removeClass("glyphicon-chevron-right")
                $(".tesaSAProductSearchResultRow-" + id).find("i").addClass("glyphicon-chevron-down")
                $(".tesaSAProductSearchResultRow-" + id).css("border-top", "2px solid black");
                $(".tesaSAProductSearchResultRow-" + id).css("border-left", "2px solid black");
                $(".tesaSAProductSearchResultRow-" + id).css("border-right", "2px solid black");

                if(revids.length > 0) {
                    // Filter and display:
                    SAProduct.query(SAProductSearchFields)
                        .filter([["id", "in", revids]])
                        .all().then(function (items) {
                            var source   = $("#tesaSAOEMProductSearchResultRowTemplate").html();
                            var template = Handlebars.compile(source);
                            var html = template({items: items, id: id});
                            $(".tesaSAProductSearchResultRow-" + id).after(html);
                        });
                }
                else {
                    var source   = $("#tesaSAOEMProductSearchResultEmptyRowTemplate").html();
                    var template = Handlebars.compile(source);
                    var html = template({id: id});
                    $(".tesaSAProductSearchResultRow-" + id).after(html);
                }
            }
        });
}

function searchExact (terms, callback) {
    // Do the search:
    SAProduct.query(SAProductSearchFields)
        .filter([["default_code", "in", _.map(terms, _.property("keyword"))]])
        .all()
        .then(function (items) {
            items.forEach(function (item) {
                callback(new SearchTerm(item.default_code), [item]);
            });
        })
        .fail(function () {
            console.error("Error during search");
        });
}

function searchLikeWorker (car, cdr, callback) {
    // Termination condition:
    if (!car) {
        console.debug("Aborting..");
        return
    }

    // Do the search and proceed with the next item on success:
    console.debug("Searching " + car.keyword);
    SAProduct.query(SAProductSearchFields)
        .filter([["default_code", "ilike", car.keyword]])
        .limit(100)
        .all()
        .then(function (items) {
            callback(car, items);
            searchLikeWorker(cdr.shift(), cdr, callback);
        })
        .fail(function () {
            console.error("Error during search");
        });
}

function searchLike (terms, callback) {
    searchLikeWorker(terms.shift(), terms, callback);
}

function renderResults (term, items) {
    var source   = $("#tesaSAProductSearchResultBodyTemplate").html();
    var template = Handlebars.compile(source);
    $("#tesaSAProductSearchResultTable").append(template({
        keyword: term.keyword,
        hashid: term.hashid,
        items: items,
    }));
}

function toggleSAMode() {
    $("#tesaSAProductSearchKeyword").toggle();
    $("#tesaSAProductSearchKeywordML").toggle();
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

function addToExistingSO () {
    var name = $("#tesaSAProductCartName").val().trim();
    var id = parseInt($("#tesaSAProductCartId").val().trim());
    var price = parseFloat($("#tesaSAProductCartPrice").val().trim() || 1);
    var quantity = parseInt($("#tesaSAProductCartQuantity").val().trim() || 1);
    var so = $("#tesaSAProductCartOrderName").val().trim()
    var SalesOrder = new openerp.Model("sale.order");
    SalesOrder.query(["id", "state"])
        .filter([["name", "=", so]])
        .limit(1)
        .all()
        .then(function (items) {
            if (items.length == 0) {
                alert("Cannot find the Sales Order with ID: " + so);
                return;
            }
            else if (items[0].state != "draft"){
                alert("Cannot add item to orders which are not in draft state");
                return;
            }
            var SalesOrderLine = new openerp.Model("sale.order.line");
            SalesOrderLine.call("create", [{
                order_id: items[0].id,
                delay: 0,
                name: name,
                product_id: id,
                price_unit: price,
                product_uom_qty: quantity
            }], {})
                .then(function (saleOrderLineId) {
                    if (!saleOrderLineId) {
                        alert("Can not create. Contact administrator.");
                        return;
                    }
                    else {
                        alert("Added.");
                    }
                })
                .fail(function () {
                    alert("Error during sales order line create.");
                });
        })
        .fail(function () {
            console.error("Error during sales order search");
        });
}

function addToExistingPO () {
    var name = $("#tesaSAProductCartName").val().trim();
    var id = parseInt($("#tesaSAProductCartId").val().trim());
    var price = parseFloat($("#tesaSAProductCartPrice").val().trim() || 1);
    var quantity = parseInt($("#tesaSAProductCartQuantity").val().trim() || 1);
    var po = $("#tesaSAProductCartOrderName").val().trim()
    var PurchaseOrder = new openerp.Model("purchase.order");
    PurchaseOrder.query(["id", "state"])
        .filter([["name", "=", po]])
        .limit(1)
        .all()
        .then(function (items) {
            if (items.length == 0) {
                alert("Cannot find the Purchase Order with ID: " + so);
                return;
            }
            else if (items[0].state != "draft"){
                alert("Cannot add item to orders which are not in draft state");
                return;
            }
            var PurchaseOrderLine = new openerp.Model("purchase.order.line");
            PurchaseOrderLine.call("create", [{
                order_id: items[0].id,
                delay: 0,
                name: name,
                product_id: id,
                price_unit: price,
                product_qty: quantity,
                date_planned: new Date().toISOString(),
            }], {})
                .then(function (purchaseOrderLineId) {
                    if (!purchaseOrderLineId) {
                        alert("Can not create. Contact administrator.");
                        return;
                    }
                    else {
                        alert("Added.");
                    }
                })
                .fail(function () {
                    alert("Error during purchase order line create.");
                });
        })
        .fail(function () {
            console.error("Error during purchase order search");
        });
}

function tesaSAProductSearchAction () {
    // Get search line:
    var searchLine = ($("#tesaSAProductSearchKeyword").is(":visible")) ? $("#tesaSAProductSearchKeyword").val() : $("#tesaSAProductSearchKeywordML").val();

    // Get search keywords:
    var keywords = _.flatten(searchLine.split("\n").map(function (x) {return x.split(",")}))
        .map(function (x) {return x.trim()})
        .filter(function (x) {return x;});

    // Get the search terms:
    var searchTerms = keywords.map(function (keyword) {
        return new SearchTerm(keyword);
    });

    // Remove duplicates:
    var _cache = {}
    searchTerms = searchTerms.filter(function (term) {
        if (term.keyword in _cache) {
            return false;
        }
        _cache[term.keyword] = true;
        return true;
    });
    delete _cache;

    // Check if there is anything to be searched:
    if (searchTerms.length == 0) {
        console.log("Nothing to be searched. Doing nothing...");
        return;
    }
    console.log("Will search for " + searchTerms.length + " terms.");
    console.debug(searchTerms);

    // Get the search type:
    var type = $("input[name=tesaSAProductSearchType]:checked").val() || "exact";

    // Cleanup:
    $(".tesaSAProductSearchResultThead").remove();
    $(".tesaSAProductSearchResultTbody").remove();

    // Do the search depending on the type:
    if (type == "like") {
        console.log("Will do a 'like' search.");
        searchLike(searchTerms, renderResults);
    }
    else {
        console.log("Will do an 'exact' search.");
        searchExact(searchTerms, renderResults);
    }
}
