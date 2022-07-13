# -*- coding: utf-8 -*-

import re
import os
import xml.sax.saxutils as saxutils
from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify

class Assets(models.AbstractModel):
    _inherit = 'web_editor.assets'

    def make_scss_customization(self, url, values):
        custom_url = self.make_custom_asset_file_url(url, 'web.assets_common')
        updatedFileContent = self.get_asset_content(custom_url) or self.get_asset_content(url)
        updatedFileContent = updatedFileContent.decode('utf-8')
        for name, value in values.items():
            if url == '/atharva_theme_general/static/src/scss/atg_theme.scss':
                updatedFileContent = name + ": " + value + " !default;"
            else:
                pattern = "'%s': %%s,\n" % name
                regex = re.compile(pattern % ".+")
                replacement = pattern % value
                if regex.search(updatedFileContent):
                    updatedFileContent = re.sub(regex, replacement, updatedFileContent)
                else:
                    updatedFileContent = re.sub(r'( *)(.*hook.*)', r'\1%s\1\2' % replacement, updatedFileContent)

        self.save_asset(url, 'web.assets_common', updatedFileContent, 'scss')

class Website(models.Model):
    _inherit = 'website'

    bread_cum_image = fields.Binary(string='Breadcrumb Image')
    breadcrumb_color = fields.Char('Backgroud Color #', default='#000000',help="For eg. #0000ff")
    breadcrumb_text_color = fields.Char('Text Color #', default='#FFFFFF',help="For eg. #0000ff")
    is_breadcum = fields.Boolean(string='Do you want to disable Breadcrumb?')
    breadcrumb_height = fields.Char(string='Padding', default='50px', help='For eg. 50px;')
    breadcum_background_image = fields.Boolean(string='Remove Breadcrumb background image?')
    shop_product_loader = fields.Selection(selection=[('infinite_loader','Infinite Loader'),('pagination','Pagination')], string='Shop Product Loader', default='pagination', translate=True)

    def get_colors_scss(self):
        data=[]
        scss = '/static/src/scss/options/colors/color_picker.scss'
        if self.id:
            scss ='/static/src/scss/options/colors/website_'+str(self.id)+'_color_picker.scss'
        module_str = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
        try:
            f = open(module_str + scss, 'r')
            f.close()
            return '/atharva_theme_general'+scss
        except:
            return '/atharva_theme_general/static/src/scss/options/colors/color_picker.scss'
            
    @api.model
    def get_category_breadcum(self, category):
        data=[]
        parent_categ=False
        if category:
            categ_data=self.env['product.public.category'].search([('id','=',int(category))])
            data.append(categ_data)
            parent_categ=categ_data
            if categ_data and categ_data.parent_id:
                parent_categ=categ_data.parent_id
                data.append(parent_categ)
                while parent_categ.parent_id:
                    parent_categ=parent_categ.parent_id
                    data.append(parent_categ)
            data.reverse()
        return data

    @api.model
    def new_page(self, name=False, add_menu=False, template='website.default_page', ispage=True, namespace=None):
        res = super(Website,self).new_page(name,add_menu,template,ispage=True,namespace=namespace)
        if  ispage:  
            arch = "<?xml version='1.0'?><t t-name='website."+slugify(str(name))+"'><t t-call='website.layout'> \
                    <div id='wrap' class='oe_structure oe_empty'>"

            arch=arch+'<t t-if="not website.is_breadcum">'

            arch =arch+'<t t-if="website.breadcum_background_image">'\
                '<nav class="is-breadcrumb shop-breadcrumb" role="navigation" aria-label="breadcrumbs" t-attf-style="background:none;background-color:#{website.breadcrumb_color};padding:#{website.breadcrumb_height};">'\
                      '<div class="container">'\
                        '<h1><span t-attf-style="color:#{website.breadcrumb_text_color}">'+saxutils.escape(str(name))+'</span></h1>'\
                        '<ul class="breadcrumb">'\
                            '<li><a href="/page/homepage" t-attf-style="color:#{website.breadcrumb_text_color}">Home</a></li>'\
                            '<li class="active"><span t-attf-style="color:#{website.breadcrumb_text_color}">'+saxutils.escape(str(name))+'</span></li>'\
                        '</ul>'\
                      '</div>'\
                '</nav>'\
                '</t>'
            arch=arch+'<t t-if="not website.breadcum_background_image">'\
                '<t t-set="bread_cum" t-value="website.image_url(website,'+repr('bread_cum_image')+')"/>'\
                '<nav class="is-breadcrumb shop-breadcrumb" role="navigation" aria-label="breadcrumbs" t-attf-style="background-image:url(#{bread_cum}#);padding:#{website.breadcrumb_height};">'\
                    '<div class="container">'\
                        '<h1><span t-attf-style="color:#{website.breadcrumb_text_color}">'+saxutils.escape(str(name))+'</span></h1>'\
                        '<ul class="breadcrumb">'\
                            '<li><a href="/page/homepage" t-attf-style="color:#{website.breadcrumb_text_color}">Home</a></li>'\
                            '<li class="active"><span t-attf-style="color:#{website.breadcrumb_text_color}">'+saxutils.escape(str(name))+'</span></li>'\
                        '</ul>'\
                      '</div>'\
                '</nav>'\
            '</t>'
            arch =arch+'</t>'
            arch =arch+'<div class="oe_structure"/>'
            arch = arch+'</div></t></t>'
            view_id = res['view_id']
            view = self.env['ir.ui.view'].browse(int(view_id))
            view.write({'arch':arch})
        return res
