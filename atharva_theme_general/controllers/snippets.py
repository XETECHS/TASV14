# -*- coding: utf-8 -*-

from odoo import fields, http
from odoo import SUPERUSER_ID
from odoo.http import request
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteBlogSnippets(WebsiteBlog):
    @http.route(['/blog/get_blog_content'], type='http', auth='public', website=True)
    def get_blog_content_data(self, **post):
        value={}
        if post.get('blog_config_id') != 'false' and post.get('blog_config_id'):
            collection_data=request.env['blog.configure'].browse(int(post.get('blog_config_id')))
            value.update({'blog_slider':collection_data})
        return request.render("atharva_theme_general.blog_slider_content", value)

class WebsiteSaleSnippets(WebsiteSale):
    @http.route(['/shop/get_brand_multi_tab_content'], type='json', auth='public', website=True)
    def get_product_brand_slider(self, **post):
        values = {}
        if post.get('collection_id') and post.get('collection_id') != 'false':
            collection_data = request.env['multitab.configure.brand'].browse(
                int(post.get('collection_id')))
            if collection_data:
                values.update({
                    'auto_slider_value': collection_data.auto_slider,
                    'slider_timing': collection_data.slider_time * 1000,
                    'item_count': int(collection_data.item_count),
                    'slider': request.env.ref("atharva_theme_general.s_brand_collection_configure").render({'obj': collection_data})
                })
        return values

    def get_single_products_content(self, **post):
        values = {}
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today())

        if post.get('collection_id'):
            collection = request.env['multitab.configure'].browse(int(post.get('collection_id')))
            if collection:
                values.update({
                    'product_collection': collection,
                    'compute_currency': compute_currency,
                    'limit' : post.get('limit') or 0,
                    'full_width': post.get('full_width')
                })
            if post.get('snippet_layout') == 'slider' or post.get('snippet_layout') == 'fw_slider':
                return request.render("atharva_theme_general.product_slider_content", values)
            elif post.get('snippet_layout') == 'grid' or post.get('snippet_layout') == 'fw_grid':
                return request.render("atharva_theme_general.latest_p_content", values)
            elif post.get('snippet_layout') == 'slider_img_left':
                return request.render("atharva_theme_general.product_slider_2_content", values)
        return False

    def get_multi_tab_content(self, **post):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today())
        value = {'compute_currency': compute_currency}
        if post.get('label'):
            value.update({
                'header' : post.get('label')
            })
        if post.get('collection_id'):
            collection_data=request.env['collection.configure'].browse(int(post.get('collection_id')))
            value.update({
                'obj': collection_data
            })
            if post.get('snippet_layout') == 'horiz_tab':
                return request.render("atharva_theme_general.s_collection_configure", value)
            elif post.get('snippet_layout') == 'vertic_tab':
                return request.render("atharva_theme_general.product_tab_content", value)
        return False    

    @http.route('/shop/get_product_snippet_content', type='http', auth='public', website=True)
    def get_product_snippet_content(self, **post):
        if post.get('snippet_type') and post.get('collection_id') and post.get('snippet_layout'):
            if post.get('snippet_type') == 'single':
                if post.get('snippet_layout') == 'fw_slider' or post.get('snippet_layout') == 'fw_grid':
                    post['full_width'] = True
                return self.get_single_products_content(**post)
            elif post.get('snippet_type') == 'multi':
                return self.get_multi_tab_content(**post)
        return False


class WebsiteSnippets(WebsiteSale):
    @http.route(['/shop/get_collection_categories'], type='json', auth='public', website=True)
    def get_collection_categories(self, **post):
        values = {}
        if post.get('collection_id') and post.get('collection_id') != 'false':
            collection_data = request.env['category.collection'].browse(int(post.get('collection_id')))
            if collection_data:
                values.update({
                    'categories': request.env.ref("atharva_theme_general.s_ecommerce_category_configure").render({'obj': collection_data})
                })
        return values
