openerp.tesa = function (instance) {
    // Loading tesa:
    console.log("Loading tesa");

    // Add the flow chart action:
    instance.web.client_actions.add("flowchart.action", "instance.tesa.action_flowchart");
    instance.tesa.action_flowchart = instance.web.Widget.extend({template: "flowchart.action"});

    // Add the search action:
    instance.web.client_actions.add("search.action", "instance.tesa.action_search");
    instance.tesa.action_search = instance.web.Widget.extend({template: "search.action"});

    // Connect keybinding for product search:
    $(document).bind("keydown", "ctrl+e", function () {
        var code = prompt("Enter the exact product code:");
        if (code && code.trim()) {
            actionCartProductByCode(code.trim());
        }
    });

    // // Connect keybinding for product search:
    // $(document).bind('keydown', 'ctrl+s', showProductSearch);

    // // Connect search button:
    // $("#tesaProductSearchButton").click(searchProduct);
    // $("#tesaMultipleProductSearchButton").click(searchMultipleProduct);

    // // Add new menu items:
    // $(".oe_application_menu_placeholder").append(
    //     "<li style='display: block;'><a href='javascript:actionSAShowCart()' class='oe_menu_leaf'><i class='glyphicon glyphicon-shopping-cart'></i></a>" +
    //     "<li style='display: block;'><a href='javascript:showProductSearch()' class='oe_menu_leaf'><i class='glyphicon glyphicon-search'></i></a>" +
    //     "<li style='display: block;'><a href='javascript:showMultipleProductSearch()' class='oe_menu_leaf'><i class='glyphicon glyphicon-list'></i></a>"
    // );

    // Add new menu items:
    $(".oe_application_menu_placeholder").append(
        "<li style='display: block;'><a href='javascript:actionSAShowCart()' class='oe_menu_leaf'><i class='glyphicon glyphicon-shopping-cart'></i></a>"
    );

    // Initiate the user voice widget:
    UserVoiceWidget();
};
