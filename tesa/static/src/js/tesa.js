openerp.tesa = function (instance) {
    // Loading tesa:
    console.log("Loading tesa");

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

    // Add new menu items:
    $(".oe_application_menu_placeholder").append(
        "<li style='display: block;'><a href='javascript:actionSAShowCart()' class='oe_menu_leaf'><i class='glyphicon glyphicon-shopping-cart'></i></a>"
    );

    // Initiate the user voice widget:
    UserVoiceWidget();

    ////////////////
    // EXTENSIONS //
    ////////////////

    openerp.tesa.goToProduct = function (id, target) {
        // Get defaults:
        target = target || "new";

        // Declare the action:
        var action = {
            type: "ir.actions.act_window",
            res_model: "product.product",
            res_id: id,
            views: [[false, "form"]],
            target: target,
            context: {},
            flags: {action_buttons: true},
        };

        // Execute:
        openerp.webclient.action_manager.do_action(action);
    }
};
