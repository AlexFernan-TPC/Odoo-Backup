from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_buyoff = fields.Boolean(default=False)
    to_mui_cip = fields.Boolean(default=False)
    is_reversed = fields.Boolean(default=False)
    new_picking_id = fields.Many2one('stock.picking', compute='_compute_new_picking', string='To Buy-off', copy=False,
                                     store=True)
    total_received_amt = fields.Float(string="Total", compute='_compute_total_amnt_received')

    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 domain="[('company_id', '=', company_id)]")

    def _compute_total_amnt_received(self):
        for rec in self:
            rec.total_received_amt = sum([line.qty_received * line.price_unit for line in rec.order_line])

    def _prepare_journal_items(self, order_line, journal):
        vals = []

        name_list = [line.name for line in order_line if line.qty_received != 0.0]
        product = [line.product_id for line in order_line][0]
        received_cost = sum([(line.qty_received - line.initial_quantity) * line.price_unit for line in order_line])
        total = order_line.currency_id.compute(received_cost, journal.company_id.currency_id)

        vals_line_debit = {
            'name': ", ".join(name_list),
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'credit': 0.0,
            'debit': total,
            'account_id': product.categ_id.accrual_transaction.id,
        }
        vals.append(vals_line_debit)

        vals_line_credit = {
            'name': ", ".join(name_list),
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'credit': total,
            'debit': 0.0,
            'account_id': self.partner_id.accrual_transaction.id,
        }
        vals.append(vals_line_credit)
        return vals

    def _prepare_journal_items_reverse(self, order_line, journal, partner_id):
        vals = []

        name_list = [line.name for line in order_line if line.qty_received != 0.0]
        product = [line.product_id for line in order_line][0]
        received_cost = sum(
            [(line.qty_received - line.initial_quantity_reversed) * line.price_unit for line in order_line])
        total = order_line.currency_id.compute(received_cost, journal.company_id.currency_id)

        vals_line_debit = {
            'name': ", ".join(name_list),
            'partner_id': partner_id.id,
            'credit': total,
            'debit': 0.0,
            'account_id': partner_id.accrual_transaction.id,
        }
        vals.append(vals_line_debit)

        vals_line_credit = {
            'name': ", ".join(name_list),
            'partner_id': partner_id.id,
            'credit': 0.0,
            'debit': total,
            'account_id': product.categ_id.accrual_transaction.id,
        }
        vals.append(vals_line_credit)

        return vals

    def action_view_picking(self):
        if not self.partner_ref:
            raise UserError(_("Vendor Reference should not be blank!"))
        new_ref = self.partner_ref.split()
        purchase_ref = self.name + " " + new_ref[-1]
        journal = self.env["account.journal"].search([("name", "=", "Inventory Valuation")], limit=1)
        journal_ref = self.env["account.move"].search([("ref", "=", purchase_ref)])
        received_qty = sum([rec.qty_received for rec in self.order_line])

        if received_qty == 0.0:
            raise UserError(_("Unable to receive products with No Received Quantities! Please validate the "
                              "Receipt."))
        if journal_ref:
            raise UserError(_("Journal with reference {} already exist.").format(self.partner_ref))
        else:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = self.env['account.move'].create({
                'journal_id': self.journal_id.id,
                'line_ids': [(0, 0, line) for line in self._prepare_journal_items(self.order_line, self.journal_id)],
                'date': date,
                'ref': self.name + " " + new_ref[-1],
                'partner_id': self.partner_id.id,
                'type': 'entry',
            })
            new_account_move.post()

        for order in self.order_line:
            order.write({
                'initial_quantity': order.qty_received
            })

        return super(PurchaseOrder, self).action_view_picking()

    def action_reverse_journal(self):

        purchase_ids = self.browse(self.env.context['active_ids'])
        for purchase in purchase_ids:
            if not purchase.partner_ref:
                raise UserError(_("Vendor Reference should not be blank!"))
            new_ref = purchase.partner_ref.split()
            purchase_ref = purchase.name + " " + new_ref[-1]
            journal_ref = self.env["account.move"].search([("ref", "=", purchase_ref)])
            journal = self.env["account.journal"].search([("name", "=", "Inventory Valuation")], limit=1)
            r_ref = "Reversal of: {}".format(purchase_ref)
            reversed_journal_ref = self.env["account.move"].search([("ref", "=", r_ref)])

            if not purchase.new_picking_id:
                raise UserError(_("You are only allowed to reverse Purchase Orders in Buy-off Results!"))

            if reversed_journal_ref:
                raise UserError(_("Journal with reference {} has already been reversed!").format(purchase.partner_ref))
            else:
                date = self._context.get('force_period_date', fields.Date.context_today(self))
                new_account_move = self.env['account.move'].create({
                    'journal_id': purchase.journal_id.id,
                    'line_ids': [(0, 0, line) for line in
                                 self._prepare_journal_items_reverse(purchase.order_line, purchase.journal_id,
                                                                     purchase.partner_id)],
                    'date': date,
                    'ref': r_ref,
                    'partner_id': purchase.partner_id.id,
                    'type': 'entry',
                })
                new_account_move.post()

            purchase.write({
                "is_reversed": True
            })

            for order in purchase.order_line:
                order.write({
                    'initial_quantity_reversed': order.qty_received
                })

    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
        # Invoice_ids may be filtered depending on the user. To ensure we get all
        # invoices related to the purchase order, we read them in sudo to fill the
        # cache.
        self.sudo()._read(['invoice_ids'])
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_invoice_origin'] = self.name
        result['context']['default_ref'] = self.origin
        result['context']['default_invoice_payment_ref'] = self.partner_ref
        result['context']['default_is_mui_cip_transaction'] = self.to_mui_cip
        return result

    @api.depends('order_line.new_move_ids.picking_id')
    def _compute_picking(self):
        for order in self:
            pickings = order.order_line.mapped('new_move_ids.picking_id')
            order.picking_ids = pickings
            order.picking_count = len(pickings)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:

            for line in order.order_line:
                stock_move = self.env['stock.move'].search(
                    [('origin', '=', line.order_id.name), ('product_id', '=', line.product_id.id)])
                line.write({
                    "new_move_ids": stock_move
                })

            order.write({'show_submit_request': True})

        return res

    @api.depends('order_line.new_move_ids.picking_id', 'picking_ids', 'picking_ids.state')
    def _compute_new_picking(self):
        for purchase in self:
            for rec in purchase.picking_ids:
                if rec.location_dest_id.name == "Accept" and rec.state == 'done':
                    purchase.new_picking_id = rec

    @api.model
    def create(self, vals):

        partner = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if partner.local:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=company_id).next_by_code(
                    'purchase.order.local',
                    sequence_date=seq_date) or '/'
            elif partner.indent:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=company_id).next_by_code(
                    'purchase.order.indent',
                    sequence_date=seq_date) or '/'
            else:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=company_id).next_by_code(
                    'purchase.order',
                    sequence_date=seq_date) or '/'

        return super(PurchaseOrder, self.with_context(company_id=company_id)).create(vals)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    initial_quantity = fields.Float()
    initial_quantity_reversed = fields.Float()
    partial_subtotal = fields.Float()
    new_move_ids = fields.One2many('stock.move', 'purchase_line_id_new', readonly=True, ondelete='set null', copy=False)





