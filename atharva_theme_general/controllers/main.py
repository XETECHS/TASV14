# -*- coding: utf-8 -*-

import base64
import os
import uuid

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.website_sale.controllers import main
from odoo.addons.web_editor.controllers.main import Web_Editor
from lxml import etree, html


main.PPG = 18
PPG = main.PPG

class WebsiteSale(WebsiteSale):
    @http.route('/shop/brands', type='http', auth='public', website=True)
    def product_brands(self, **post):
        values = {}
        domain = [('active','=',True),('visible_slider','=',True)]
        if post.get('search'):
            domain += [('name', 'ilike', post.get('search'))]
        brand_ids = request.env['product.brand'].search(domain)

        keep = QueryURL('/shop/brands', brand_id=[])
        if brand_ids:
            values.update({
                'brands': brand_ids,
                'keep': keep
            })
        if post.get('search'):
            values.update({
                'search': post.get('search')
            })
        return request.render('atharva_theme_general.product_brands', values)


    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        quantities_per_page = None
        quantities_per_page = request.env[
            'product.qty_per_page'].search([], order='sequence')

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = quantities_per_page[0].name if quantities_per_page else 20
        if not ppg:
            if quantities_per_page:
                ppg = quantities_per_page[0].name
            else:
                ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        brand_ids = []
        if post.get('brand'):
            brand_list = request.httprequest.args.getlist('brand')
            brand_values = [[str(x) for x in v.rsplit("-",1)]
                        for v in brand_list if v]
            brand_ids = list(set([int(v[1]) for v in brand_values]))
            if len(brand_ids) > 0:
                domain += [('product_brand_id', 'in', brand_ids)]

        tag_ids = []
        if post.get('tags'):
            tag_list = request.httprequest.args.getlist('tags')
            tag_values = [[str(x) for x in v.rsplit("-",1)]
                        for v in tag_list if v]
            tag_ids = list(set([int(v[1]) for v in tag_values]))
            if len(tag_ids) > 0:
                domain += [('tag_ids', 'in', tag_ids)]

        if post.get('product_collection'):
            prod_collection_rec = request.env['multitab.configure'].search(
                [('id', '=', int(post.get('product_collection')))])
            if prod_collection_rec:
                prod_id_list = list({each_p.product_id.id for each_p in prod_collection_rec.product_ids})
                domain += [('id', 'in', prod_id_list)]

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        search_product = Product.search(domain)
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))
        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
            brands = request.env['product.brand'].search([('active','=',True),('visible_slider','=',True), ('product_ids', 'in', search_product.ids)])
            tags = request.env['product.tag'].search([('active','=',True), ('product_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)
            brands = request.env['product.brand'].search([('active','=',True),('visible_slider','=',True)])
            tags = request.env['product.tag'].search([('active','=',True)])

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'brands': brands,
            'brand_set': brand_ids,
            'tags': tags,
            'tag_set': tag_ids,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'quantities_per_page': quantities_per_page,
            'add_more': True if request.website.shop_product_loader == 'infinite_loader' else False,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    @http.route('/get_prod_quick_view_details', type='json', auth='public', website=True)
    def get_product_qv_details(self, **kw):
        product_id = int(kw.get('prod_id', 0))
        if product_id > 0:
            product = http.request.env['product.template'].search([('id', '=', product_id)])
            pricelist = request.website.get_current_pricelist()
            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
            return request.env.ref('atharva_theme_general.get_product_qv_details_template').render({
                'product': product,
                'compute_currency': compute_currency or None,
            })
        else:
            return request.env.ref('atharva_theme_general.get_product_qv_details_template').render({
                'error': _('There is some problem with this product.!')
            })

    @http.route(['/shop/load_next_products'], type="http", auth="public", website=True)
    def load_next_products(self, category='', loaded_products=0, search='', ppg=0, **post):
        if ppg:
            attrib_list = request.httprequest.args.getlist('attrib[]')
            attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}

            domain = self._get_search_domain(search, category, attrib_values)

            brand_ids = []
            if post.get('brand[]'):
                brand_list = request.httprequest.args.getlist('brand[]')
                brand_values = [[str(x) for x in v.rsplit("-",1)]
                            for v in brand_list if v]
                brand_ids = list(set([int(v[1]) for v in brand_values]))
                if len(brand_ids) > 0:
                    domain += [('product_brand_id', 'in', brand_ids)]

            tag_ids = []
            if post.get('tags[]'):
                tag_list = request.httprequest.args.getlist('tags[]')
                tag_values = [[str(x) for x in v.rsplit("-",1)]
                            for v in tag_list if v]
                tag_ids = list(set([int(v[1]) for v in tag_values]))
                if len(tag_ids) > 0:
                    domain += [('tag_ids', 'in', tag_ids)]

            keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

            pricelist_context, pricelist = self._get_pricelist_context()

            request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

            if search:
                post["search"] = search
            if attrib_list:
                post['attrib'] = attrib_list

            Product = request.env['product.template'].with_context(bin_size=True)

            Category = request.env['product.public.category']
            search_product = Product.search(domain)
            website_domain = request.website.website_domain()
            categs_domain = [('parent_id', '=', False)] + website_domain
            if search:
                search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
                categs_domain.append(('id', 'in', search_categories.ids))
            else:
                search_categories = Category
            categs = Category.search(categs_domain)

            url = "/shop"
            if category:
                category = request.env[
                    'product.public.category'].browse(int(category))
                url = "/shop/category/%s" % slug(category)

            product_count = len(search_product)
            #pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(domain, limit=int(ppg), offset=int(loaded_products), order=self._get_search_order(post))

            ProductAttribute = request.env['product.attribute']
            if products:
                # get all products without limit
                attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
                brands = request.env['product.brand'].search([('active','=',True),('visible_slider','=',True), ('product_ids', 'in', search_product.ids)])
                tags = request.env['product.tag'].search([('active','=',True), ('product_ids', 'in', search_product.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)
                brands = request.env['product.brand'].search([('active','=',True),('visible_slider','=',True)])
                tags = request.env['product.tag'].search([('active','=',True)])

            layout_mode = request.session.get('website_sale_shop_layout_mode')
            if not layout_mode:
                if request.website.viewref('website_sale.products_list_view').active:
                    layout_mode = 'list'
                else:
                    layout_mode = 'grid'

            values = {
                'add_more': True if request.website.shop_product_loader == 'infinite_loader' else False,
                'products': products,
                #'pager': pager,
                'pricelist': pricelist,
                'keep': keep,
                'brands': brands,
                'brand_set': brand_ids,
                'tags': tags,
                'tag_set': tag_ids,
                'layout_mode': layout_mode,
            }
            return request.render('atharva_theme_general.newly_loaded_products', values)
        else:
            return None


    @http.route('/shop/cart/popup',type='http', auth='public', website=True)
    def cart_popup(self, **post):
        values = {}
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()        

        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today())
        else:
            compute_currency = lambda price: price
        values.update({
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
            'website' : request.website,
            'date': fields.Date.today(),
        })
        if post.get('type') == 'cart_lines_popup':
            return request.render('atharva_theme_general.cart_lines_popup_content', values)
        return False
