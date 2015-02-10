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
    "manual_cost_price",
    "standard_price",
    "etk_cost_price",
    "previous_local_deal_cost_price",
    "current_local_deal_cost_price",
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
        .limit(500)
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
                alert("Cannot find the Purchase Order with ID: " + po);
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

function actionSACopyPrice (price) {
    $("#tesaSAProductCartPrice").val(price);
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

function getLocation(code, callback) {
    var name = "Physical Locations / " + code.trim() + " / Stock";
    var Location = new openerp.Model("stock.location")
    Location.query(["id"])
        .filter([["complete_name", "=", name]])
        .limit(1)
        .all()
        .then(function (items) {
            if (items.length == 0) {
                alert("Cannot find location.");
                return;
            }
            callback(items[0].id);
        })
        .fail(function () {
            alert("Cannot find location.");
            return;
        })
}

function getPickingType(location, callback) {
    var PickingType = new openerp.Model("stock.picking.type")
    PickingType.query(["id"])
        .filter([["default_location_dest_id", "=", location], ["code", "=", "incoming"]])
        .limit(1)
        .all()
        .then(function (items) {
            if (items.length == 0) {
                alert("Cannot find location.");
                return;
            }
            callback(items[0].id);
        })
        .fail(function () {
            alert("Cannot find location.");
            return;
        })
}

function getWarehouse(code, callback) {
    var Warehouse = new openerp.Model("stock.warehouse")
    Warehouse.query(["id"])
        .filter([["code", "=", code.trim()]])
        .limit(1)
        .all()
        .then(function (items) {
            if (items.length == 0) {
                alert("Cannot find warehouse.");
                return;
            }
            callback(items[0].id);
        })
        .fail(function () {
            alert("Cannot find warehouse.");
            return;
        })
}

function createNewSalesOrder (partner, location, items) {
    // Get the order object:
    var Sale = new openerp.Model("sale.order");

    // Create:
    Sale.call("create", [{partner_id: partner, warehouse_id: location}], {}).then(function (orderId) {
        // Check the ID:
        if (!orderId) {
            alert("Can not create. Contact administrator.");
            return;
        }

        // Populate order lines:
        var order_lines = [];
        items.forEach(function (line) {
            order_lines.push([0, false, {
                delay: 0,
                name: line.name,
                product_id: line.id,
                price_unit: line.price,
                product_uom_qty: line.quantity
            }]);
        });
        console.log(order_lines);
        Sale.call("write", [[orderId], {order_line: order_lines}], {}).then(function () {
            Sale.query(["id", "name"])
                .filter([["id", "=", orderId]])
                .all()
                .then(function (data) {
                    alert("Order created: " + data[0].name);
                    items.forEach(function (x) {
                        removeFromCart(x.hashid);
                    });
                    $("#tesaSAShowCartDialog").modal("toggle");
                })
        })
    })
}

function createNewPurchaseOrder (partner, location, picking, items) {
    // Create
    var Purchase = new openerp.Model("purchase.order");
    Purchase.call("create", [{
        partner_id: partner,
        location_id: location,
        picking_type_id: picking,
        pricelist_id: 2,
    }], {}).then(function (orderId) {
        if (!orderId) {
            alert("Can not create. Contact administrator.");
            return;
        }
        var order_lines = [];
        items.forEach(function (line) {
            order_lines.push([0, false, {
                delay: 0,
                name: line.name,
                product_id: line.id,
                price_unit: line.price,
                product_qty: line.quantity,
                date_planned: new Date().toISOString(),
            }]);
        });
        Purchase.call("write", [[orderId], {order_line: order_lines}], {}).then(function () {
            Purchase.query(["id", "name"])
                .filter([["id", "=", orderId]])
                .all()
                .then(function (data) {
                    alert("Purchase order created: " + data[0].name);
                    items.forEach(function (x) {
                        removeFromCart(x.hashid);
                    });
                    $("#tesaSAShowCartDialog").modal("toggle");
                })
        })
    })
}

function actionCreateNewSalesOrder () {
    var items = getCartSelectedItems();
    if (items.length == 0) {
        alert("No Items Selected");
        return;
    }

    var warehouse = $('input[name=tesaSAProductNewOLocation]:checked').val();
    getWarehouse(warehouse, function (warehouse_id) {
        createNewSalesOrder(1, warehouse_id, items);
    });
}

function actionCreateNewPurchaseOrder () {
    var items = getCartSelectedItems();
    if (items.length == 0) {
        alert("No Items Selected");
        return;
    }

    var location = $('input[name=tesaSAProductNewOLocation]:checked').val();
    getLocation(location, function (location_id) {
        getPickingType(location_id, function (picking_type_id) {
            createNewPurchaseOrder(1, location_id, picking_type_id, items);
        });
    });
}
