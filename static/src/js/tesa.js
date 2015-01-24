openerp.tesa = function (instance) {
    // Loading tesa:
    console.log("Loading tesa");

    // Connect keybinding for product search:
    $(document).bind('keydown', 'ctrl+s', showProductSearch);

    // Connect search button:
    $("#tesaProductSearchButton").click(searchProduct);
    $("#tesaMultipleProductSearchButton").click(searchMultipleProduct);

    // Add the flow chart action:
    instance.web.client_actions.add("flowchart.action", "instance.tesa.action");
    instance.tesa.action = instance.web.Widget.extend({template: "flowchart.action"});

    // Add new menu items:
    $(".oe_application_menu_placeholder").append(
        "<li style='display: block;'><a href='javascript:showCart()' class='oe_menu_leaf'><i class='glyphicon glyphicon-shopping-cart'></i></a>" +
        "<li style='display: block;'><a href='javascript:showProductSearch()' class='oe_menu_leaf'><i class='glyphicon glyphicon-search'></i></a>" +
        "<li style='display: block;'><a href='javascript:showMultipleProductSearch()' class='oe_menu_leaf'><i class='glyphicon glyphicon-list'></i></a>"
    );

    // Initiate the user voice widget:
    UserVoiceWidget();
};
