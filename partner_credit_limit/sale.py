#-*- coding:utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import Warning


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.one
    def action_wait(self):
        self.check_limit()
        return super(sale_order, self).action_wait()

    @api.one
    def check_limit(self):
        ## Check the type of the order
        if self.order_policy == 'prepaid' or self.stype == "cash":
            return True

        # We sum from all the sale orders that are aproved, the sale order
        # lines that are not yet invoiced
        domain = [('order_id.partner_id', '=', self.partner_id.id),
                  ('invoiced', '=', False),
                  ('order_id.state', 'not in', ['draft', 'cancel', 'sent', 'done'])]
        order_lines = self.env['sale.order.line'].search(domain)
        none_invoiced_amount = sum([x.price_subtotal for x in order_lines])

        # We sum from all the invoices that are in draft the total amount
        domain = [
            ('partner_id', '=', self.partner_id.id), ('state', '=', 'draft')]
        draft_invoices = self.env['account.invoice'].search(domain)
        draft_invoices_amount = sum([x.amount_total for x in draft_invoices])

        available_credit = self.partner_id.credit_limit - \
            self.partner_id.credit - \
            none_invoiced_amount - draft_invoices_amount

        if self.amount_total > available_credit:
            raise Warning(_("Credit limit exceeded. Please refer to your supervisor."))
            return False
        return True
