
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/sale-workflow&target_branch=18.0)
[![Pre-commit Status](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=18.0)](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml?query=branch%3A18.0)
[![Build Status](https://github.com/OCA/sale-workflow/actions/workflows/test.yml/badge.svg?branch=18.0)](https://github.com/OCA/sale-workflow/actions/workflows/test.yml?query=branch%3A18.0)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/18.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/sale-workflow-18-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/sale-workflow-18-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# sale-workflow

sale-workflow

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[partner_sale_pivot](partner_sale_pivot/) | 18.0.1.0.0 | <a href='https://github.com/ernestotejeda'><img src='https://github.com/ernestotejeda.png' width='32' height='32' style='border-radius:50%;' alt='ernestotejeda'/></a> | Sales analysis from customer form view
[portal_sale_order_search](portal_sale_order_search/) | 18.0.1.0.0 | <a href='https://github.com/pilarvargas-tecnativa'><img src='https://github.com/pilarvargas-tecnativa.png' width='32' height='32' style='border-radius:50%;' alt='pilarvargas-tecnativa'/></a> | Allow customers to set and search their own order reference in portal
[portal_sale_personal_data_only](portal_sale_personal_data_only/) | 18.0.1.0.0 |  | Portal Sale Personal Data Only
[pricelist_cache](pricelist_cache/) | 18.0.1.0.0 |  | Provide a new model to cache price lists and update it, to make it easier to retrieve them.
[product_customerinfo_elaboration](product_customerinfo_elaboration/) | 18.0.1.0.0 |  | Allows to define default elaborations and elaboration notes on product customerinfos
[product_customerinfo_sale](product_customerinfo_sale/) | 18.0.1.0.0 |  | Loads in every sale order line the customer code defined in the product
[product_form_sale_link](product_form_sale_link/) | 18.0.1.0.1 |  | Adds a button on product forms to access Sale Lines
[product_set_sell_only_by_packaging](product_set_sell_only_by_packaging/) | 18.0.1.0.0 |  | Glue module between `sell_only_by_packaging` and `sale_product_set_packaging_qty`.
[sale_automatic_workflow](sale_automatic_workflow/) | 18.0.1.0.1 |  | Sale Automatic Workflow
[sale_automatic_workflow_job](sale_automatic_workflow_job/) | 18.0.1.0.2 |  | Execute sale automatic workflows in queue jobs
[sale_automatic_workflow_periodicity](sale_automatic_workflow_periodicity/) | 18.0.1.0.0 | <a href='https://github.com/TDu'><img src='https://github.com/TDu.png' width='32' height='32' style='border-radius:50%;' alt='TDu'/></a> | Adds a period for the execution of a workflow.
[sale_automatic_workflow_stock](sale_automatic_workflow_stock/) | 18.0.1.0.0 |  | Sale Automatic Workflow Stock
[sale_automatic_workflow_stock_job](sale_automatic_workflow_stock_job/) | 18.0.1.0.0 |  | Sale Automatic Workflow Stock Job
[sale_block_no_stock](sale_block_no_stock/) | 18.0.1.0.0 | <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> | Block Sales if products has not enough Quantity based on a chosen field
[sale_cancel_reason](sale_cancel_reason/) | 18.0.1.0.0 |  | Sale Cancel Reason
[sale_commercial_partner](sale_commercial_partner/) | 18.0.1.0.1 | <a href='https://github.com/alexis-via'><img src='https://github.com/alexis-via.png' width='32' height='32' style='border-radius:50%;' alt='alexis-via'/></a> | Add stored related field 'Commercial Entity' on sale orders
[sale_company_currency](sale_company_currency/) | 18.0.1.0.0 |  | Company Currency in Sale Orders
[sale_delivery_split_date](sale_delivery_split_date/) | 18.0.1.0.0 |  | Sale Deliveries split by date
[sale_delivery_state](sale_delivery_state/) | 18.0.1.2.1 |  | Show the delivery state on the sale order
[sale_discount_display_amount](sale_discount_display_amount/) | 18.0.1.0.0 |  | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_elaboration](sale_elaboration/) | 18.0.1.0.2 | <a href='https://github.com/CarlosRoca13'><img src='https://github.com/CarlosRoca13.png' width='32' height='32' style='border-radius:50%;' alt='CarlosRoca13'/></a> <a href='https://github.com/rafaelbn'><img src='https://github.com/rafaelbn.png' width='32' height='32' style='border-radius:50%;' alt='rafaelbn'/></a> <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> <a href='https://github.com/yajo'><img src='https://github.com/yajo.png' width='32' height='32' style='border-radius:50%;' alt='yajo'/></a> | Set an elaboration for any sale line
[sale_exception](sale_exception/) | 18.0.2.1.0 |  | Custom exceptions on sale order
[sale_exception_product_sale_manufactured_for](sale_exception_product_sale_manufactured_for/) | 18.0.1.0.0 |  | The partner set in the sales order can order only if he/she has a commercial entity that is listed as one of the partners for which the products can be manufactured for.
[sale_fixed_discount](sale_fixed_discount/) | 18.0.1.0.0 |  | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 18.0.1.0.1 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_global_discount](sale_global_discount/) | 18.0.1.0.0 |  | Sale Global Discount
[sale_invoice_blocking](sale_invoice_blocking/) | 18.0.1.0.0 |  | Allow you to block the creation of invoices from a sale order.
[sale_invoice_frequency](sale_invoice_frequency/) | 18.0.1.0.1 | <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> <a href='https://github.com/yajo'><img src='https://github.com/yajo.png' width='32' height='32' style='border-radius:50%;' alt='yajo'/></a> <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> | Define the invoice frequency for customers
[sale_invoice_policy](sale_invoice_policy/) | 18.0.1.1.0 |  | Sales Management: let the user choose the invoice policy on the order
[sale_invoice_split_payment](sale_invoice_split_payment/) | 18.0.1.0.0 |  | Split by payment term generated invoices from sale orders
[sale_mail_autosubscribe](sale_mail_autosubscribe/) | 18.0.1.0.0 | <a href='https://github.com/ivantodorovich'><img src='https://github.com/ivantodorovich.png' width='32' height='32' style='border-radius:50%;' alt='ivantodorovich'/></a> | Automatically subscribe partners to their company's sale orders
[sale_manual_delivery](sale_manual_delivery/) | 18.0.1.0.1 |  | Create manually your deliveries
[sale_mrp_bom](sale_mrp_bom/) | 18.0.1.0.0 |  | Allows define a BOM in the sales lines.
[sale_order_amount_to_invoice](sale_order_amount_to_invoice/) | 18.0.1.0.0 |  | Show total amount to invoice in quotations/sales orders
[sale_order_archive](sale_order_archive/) | 18.0.1.0.0 |  | Archive Sale Orders
[sale_order_carrier_auto_assign](sale_order_carrier_auto_assign/) | 18.0.1.0.0 | <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Auto assign delivery carrier on sale order confirmation
[sale_order_disable_user_autosubscribe](sale_order_disable_user_autosubscribe/) | 18.0.1.0.0 |  | Remove the salesperson from autosubscribed sale followers
[sale_order_general_discount](sale_order_general_discount/) | 18.0.1.0.0 |  | General discount per sale order
[sale_order_invoicing_finished_task](sale_order_invoicing_finished_task/) | 18.0.1.0.0 |  | Control invoice order lines if their related task has been set to invoiceable
[sale_order_line_chained_move](sale_order_line_chained_move/) | 18.0.1.0.0 | <a href='https://github.com/rousseldenis'><img src='https://github.com/rousseldenis.png' width='32' height='32' style='border-radius:50%;' alt='rousseldenis'/></a> | This module adds a field on sale order line to get all related move lines
[sale_order_line_date](sale_order_line_date/) | 18.0.1.0.2 |  | Adds a commitment date to each sale order line.
[sale_order_line_delivery_state](sale_order_line_delivery_state/) | 18.0.1.0.0 |  | Show the delivery state on the sale order line
[sale_order_line_input](sale_order_line_input/) | 18.0.1.0.0 |  | Search, create or modify directly sale order lines
[sale_order_line_menu](sale_order_line_menu/) | 18.0.1.0.0 |  | Adds a Sale Order Lines Menu
[sale_order_line_note](sale_order_line_note/) | 18.0.1.0.0 |  | Note on sale order line
[sale_order_line_price_history](sale_order_line_price_history/) | 18.0.1.0.0 | <a href='https://github.com/CarlosRoca13'><img src='https://github.com/CarlosRoca13.png' width='32' height='32' style='border-radius:50%;' alt='CarlosRoca13'/></a> <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> | Sale order line price history
[sale_order_line_remove](sale_order_line_remove/) | 18.0.1.0.0 |  | Allows removal of sale order lines from confirmed orders if not invoiced or received
[sale_order_line_sequence](sale_order_line_sequence/) | 18.0.1.0.0 |  | Propagates SO line sequence to invoices and stock picking.
[sale_order_line_stock_move_history](sale_order_line_stock_move_history/) | 18.0.1.0.0 | <a href='https://github.com/ppyczko'><img src='https://github.com/ppyczko.png' width='32' height='32' style='border-radius:50%;' alt='ppyczko'/></a> | Show stock moves history for sale order lines
[sale_order_line_tag](sale_order_line_tag/) | 18.0.1.0.0 | <a href='https://github.com/smaciaosi'><img src='https://github.com/smaciaosi.png' width='32' height='32' style='border-radius:50%;' alt='smaciaosi'/></a> <a href='https://github.com/dreispt'><img src='https://github.com/dreispt.png' width='32' height='32' style='border-radius:50%;' alt='dreispt'/></a> <a href='https://github.com/ckolobow'><img src='https://github.com/ckolobow.png' width='32' height='32' style='border-radius:50%;' alt='ckolobow'/></a> | Add tags to classify sales order line reasons
[sale_order_lot_selection](sale_order_lot_selection/) | 18.0.1.1.0 | <a href='https://github.com/bodedra'><img src='https://github.com/bodedra.png' width='32' height='32' style='border-radius:50%;' alt='bodedra'/></a> | Sale Order Lot Selection
[sale_order_note_template](sale_order_note_template/) | 18.0.1.0.0 |  | Add sale orders terms and conditions template that can be used to quickly fullfill sale order terms and conditions
[sale_order_price_recalculation](sale_order_price_recalculation/) | 18.0.1.0.0 |  | Recalculate prices / Reset descriptions on sale order lines
[sale_order_priority](sale_order_priority/) | 18.0.1.0.0 |  | Define priority on sale orders
[sale_order_product_assortment](sale_order_product_assortment/) | 18.0.1.0.0 | <a href='https://github.com/CarlosRoca13'><img src='https://github.com/CarlosRoca13.png' width='32' height='32' style='border-radius:50%;' alt='CarlosRoca13'/></a> | Module that allows to use the assortments on sale orders
[sale_order_product_availability_inline](sale_order_product_availability_inline/) | 18.0.1.0.1 | <a href='https://github.com/ernestotejeda'><img src='https://github.com/ernestotejeda.png' width='32' height='32' style='border-radius:50%;' alt='ernestotejeda'/></a> | Show product availability in sales order line product drop-down.
[sale_order_product_recommendation](sale_order_product_recommendation/) | 18.0.1.0.0 | <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> <a href='https://github.com/rafaelbn'><img src='https://github.com/rafaelbn.png' width='32' height='32' style='border-radius:50%;' alt='rafaelbn'/></a> <a href='https://github.com/yajo'><img src='https://github.com/yajo.png' width='32' height='32' style='border-radius:50%;' alt='yajo'/></a> | Recommend products to sell to customer based on history
[sale_order_report_without_price](sale_order_report_without_price/) | 18.0.1.0.0 |  | Allow you to generate quotation and order reports without price.
[sale_order_requested_delivery](sale_order_requested_delivery/) | 18.0.1.0.0 |  | This module adds two new fields `requested_delivery_period_start` and `requested_delivery_period_end` to both the `sale.order` and `sale.order.line` models.
[sale_order_revision](sale_order_revision/) | 18.0.1.0.0 |  | Keep track of revised quotations
[sale_order_secondary_unit](sale_order_secondary_unit/) | 18.0.1.0.0 |  | Sale product in a secondary unit
[sale_order_split_strategy](sale_order_split_strategy/) | 18.0.1.0.0 | <a href='https://github.com/grindtildeath'><img src='https://github.com/grindtildeath.png' width='32' height='32' style='border-radius:50%;' alt='grindtildeath'/></a> | Define strategies to split sales orders
[sale_order_tag](sale_order_tag/) | 18.0.1.0.0 | <a href='https://github.com/patrickrwilson'><img src='https://github.com/patrickrwilson.png' width='32' height='32' style='border-radius:50%;' alt='patrickrwilson'/></a> | Adds Tags to Sales Orders.
[sale_order_transmit_method](sale_order_transmit_method/) | 18.0.1.0.0 |  | Set transmit method (email, post, portal, ...) in sale order and propagate it to invoices
[sale_order_type](sale_order_type/) | 18.0.1.1.0 |  | Sale Order Type
[sale_order_warn_message](sale_order_warn_message/) | 18.0.1.0.1 |  | Add a popup warning on sale to ensure warning is populated
[sale_packaging_default](sale_packaging_default/) | 18.0.1.0.0 | <a href='https://github.com/yajo'><img src='https://github.com/yajo.png' width='32' height='32' style='border-radius:50%;' alt='yajo'/></a> | Simplify using products default packaging for sales
[sale_partner_address_restrict](sale_partner_address_restrict/) | 18.0.1.0.0 |  | Restrict addresses domain in the sales order form taking into account the partner selected
[sale_partner_incoterm](sale_partner_incoterm/) | 18.0.1.0.0 |  | Set the customer preferred incoterm on each sales order
[sale_partner_primeship](sale_partner_primeship/) | 18.0.1.0.0 | <a href='https://github.com/nayatec'><img src='https://github.com/nayatec.png' width='32' height='32' style='border-radius:50%;' alt='nayatec'/></a> <a href='https://github.com/paradoxxxzero'><img src='https://github.com/paradoxxxzero.png' width='32' height='32' style='border-radius:50%;' alt='paradoxxxzero'/></a> | Allow you to manage time limited prime memberships and prime membership activation products.
[sale_partner_selectable_option](sale_partner_selectable_option/) | 18.0.1.0.0 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Sale Partner Selectable Option
[sale_pricelist_display_surcharge](sale_pricelist_display_surcharge/) | 18.0.1.0.0 |  | This module shows to the customer the surcharges if wanted.
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 18.0.1.0.1 |  | Base module for multiple procurement group by Sale order
[sale_product_identification](sale_product_identification/) | 18.0.1.0.0 |  | Sale Product Identification Numbers
[sale_product_set](sale_product_set/) | 18.0.1.0.0 |  | Sales product set
[sale_product_set_packaging_qty](sale_product_set_packaging_qty/) | 18.0.1.0.0 |  | Manage packaging and quantities on product set lines
[sale_quotation_number](sale_quotation_number/) | 18.0.1.0.0 |  | Different sequence for sale quotations
[sale_readonly_security](sale_readonly_security/) | 18.0.1.0.0 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Sale Readonly Security
[sale_require_po_doc](sale_require_po_doc/) | 18.0.1.0.0 |  | Sale Orders Require PO or Sales Documentation
[sale_shipping_info_helper](sale_shipping_info_helper/) | 18.0.1.0.0 |  | Add shipping amounts on sale order
[sale_sourced_by_line](sale_sourced_by_line/) | 18.0.1.0.1 |  | Multiple warehouse source locations for Sale order
[sale_stock_cancel_restriction](sale_stock_cancel_restriction/) | 18.0.1.0.0 |  | Sale Stock Cancel Restriction
[sale_stock_delivery_state](sale_stock_delivery_state/) | 18.0.1.0.0 |  | Change the way to compute the delivery state
[sale_stock_line_customer_ref](sale_stock_line_customer_ref/) | 18.0.1.0.0 | <a href='https://github.com/sebalix'><img src='https://github.com/sebalix.png' width='32' height='32' style='border-radius:50%;' alt='sebalix'/></a> | Allow you to add a customer reference on order lines propagaged to move operations.
[sale_stock_line_sequence](sale_stock_line_sequence/) | 18.0.1.0.0 |  | Glue Module for Sale Order Line Sequence and Stock Picking Line Sequence
[sale_stock_partner_warehouse](sale_stock_partner_warehouse/) | 18.0.1.0.0 |  | Allow to choose by default a warehouse on SO based on a Partner parameter
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 18.0.1.0.2 |  | Allow you to block the creation of deliveries from a sale order.
[sale_stock_picking_note](sale_stock_picking_note/) | 18.0.1.1.0 | <a href='https://github.com/carlosdauden'><img src='https://github.com/carlosdauden.png' width='32' height='32' style='border-radius:50%;' alt='carlosdauden'/></a> <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> <a href='https://github.com/chienandalu'><img src='https://github.com/chienandalu.png' width='32' height='32' style='border-radius:50%;' alt='chienandalu'/></a> <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> | Add picking note in sale and purchase order
[sale_stock_return_request](sale_stock_return_request/) | 18.0.1.0.1 | <a href='https://github.com/chienandalu'><img src='https://github.com/chienandalu.png' width='32' height='32' style='border-radius:50%;' alt='chienandalu'/></a> | Sale Stock Return Request
[sale_substate](sale_substate/) | 18.0.1.0.0 |  | Sale Sub State
[sale_tier_validation](sale_tier_validation/) | 18.0.1.0.0 |  | Extends the functionality of Sale Orders to support a tier validation process.
[sale_transaction_form_link](sale_transaction_form_link/) | 18.0.1.0.0 | <a href='https://github.com/rousseldenis'><img src='https://github.com/rousseldenis.png' width='32' height='32' style='border-radius:50%;' alt='rousseldenis'/></a> | Allows to display a link to payment transactions on Sale Order form view.
[sale_wishlist](sale_wishlist/) | 18.0.1.0.0 |  | Handle sale wishlist for partners
[sales_team_security](sales_team_security/) | 18.0.1.0.0 | <a href='https://github.com/pedrobaeza'><img src='https://github.com/pedrobaeza.png' width='32' height='32' style='border-radius:50%;' alt='pedrobaeza'/></a> <a href='https://github.com/ivantodorovich'><img src='https://github.com/ivantodorovich.png' width='32' height='32' style='border-radius:50%;' alt='ivantodorovich'/></a> | New group for seeing only sales channel's documents
[sell_only_by_packaging](sell_only_by_packaging/) | 18.0.1.0.2 |  | Manage sale of packaging

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
