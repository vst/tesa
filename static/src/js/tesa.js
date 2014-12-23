openerp.tesa = function (instance) {
    // Add the flow chart action:
    instance.web.client_actions.add("flowchart.action", "instance.tesa.action");
    instance.tesa.action = instance.web.Widget.extend({
        template: "flowchart.action"
    });
};
