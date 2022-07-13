odoo.define('atharva_theme_general.editor',function(require){
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var weContext = require('web_editor.context');
    var web_editor = require('web_editor.editor');
    var options = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var qweb = core.qweb;
    var _t = core._t;

    ajax.loadXML('/atharva_theme_general/static/src/xml/product_slider_popup.xml', core.qweb);    

    options.registry['latest_blog'] = options.Class.extend({
        popup_template_id: "editor_new_blog_slider_template",
        popup_title: _t("Select Collection"),
        website_blog_configure: function (previewMode, value) {
            var self = this;
            var def = wUtils.prompt({
                'id': this.popup_template_id,
                'window_title': this.popup_title,
                'select': _t("Collection"),
                'init': function (field, dialog) {
                    return rpc.query({
                        model: 'blog.configure',
                        method: 'name_search',
                        args: ['', []],
                        context: self.options.recordInfo.context,
                    }).then(function (data) {
                        $(dialog).find('.btn-primary').prop('disabled', !data.length);
                        return data;
                    });
                },
            });
            def.then(function (result) {
                var collection_id = parseInt(result.val);
                self.$target.attr("data-blog_list-id", collection_id);
                rpc.query({
                    model: 'blog.configure',
                    method: 'read',
                    args: [[collection_id],['name']],
                }).then(function (data){
                    if(data && data[0] && data[0].name)
                        self.$target.empty().append('<div class="seaction-head"><h1>'+ data[0].name+'</h1></div>');
                });
            });
            return def;
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments);
        },
        onBuilt: function () {
            var self = this;
            this._super();
            this.website_blog_configure('click').guardedCatch(function () {
                self.getParent()._onRemoveClick($.Event( "click" ));                        
            });
        },
        cleanForSave: function(){
            this.$target.empty();
            $('.web_blog_slider').empty();
            var model = this.$target.parent().attr('data-oe-model');
            if(model){
                this.$target.parent().addClass('o_editable o_dirty');
            }
        },
    });

    options.registry['s_brand_multi_with_header']= options.Class.extend({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments);
        },
        select_collection: function (type, value) {
            var self = this;
            var def = wUtils.prompt({
                'id': this.popup_template_id,
                'window_title': this.popup_title,
                'select': _t("Collection"),
                'init': function (field, dialog) {
                    return rpc.query({
                        model: 'multitab.configure.brand',
                        method: 'name_search',
                        args: ['', []],
                        context: self.options.recordInfo.context,
                    }).then(function (data) {
                        $(dialog).find('.btn-primary').prop('disabled', !data.length);
                        return data;
                    });
                },
            });
            def.then(function (result) {
                var collection_id = parseInt(result.val);
                self.$target.attr("data-list-id", collection_id);
                rpc.query({
                    model: 'multitab.configure.brand',
                    method: 'read',
                    args: [[collection_id],['name']],
                }).then(function (data){
                    if(data && data[0] && data[0].name)
                        self.$target.empty().append('<div class="container"><div class="product_slide" contentEditable="false"><div class="col-md-12"><div class="seaction-head"<div class="h1">'+ data[0].name +'</div></div></div></div></div>');                                  
                });
            });
           return def;
        },
        onBuilt: function () {
            var self = this;
            this._super();
            this.select_collection('click').guardedCatch(function () {
                self.getParent()._onRemoveClick($.Event( "click" ));                        
            });
        },
        cleanForSave: function () {
            this.$target.empty();
            $('.js_brand_multi_collection').empty();
            var model = this.$target.parent().attr('data-oe-model');
            if(model){
                this.$target.parent().addClass('o_editable o_dirty');
            }
        },
    });

    options.registry['product_slider_actions'] = options.Class.extend({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments);
        },
        product_slider_configure: function(previewMode, value){
            var self = this;
            if(previewMode === false || previewMode === "click"){
                self.$modal = $(qweb.render("atharva_theme_general.p_slider_popup_template"));
                $('body > #product_slider_modal').remove();
                self.$modal.appendTo('body');
                self._rpc({
                    model: 'multitab.configure',
                    method: 'name_search',
                    args: ['', []],
                    context: weContext.get()
                }).then(function(data){
                    var s_tab_ele = $("#product_slider_modal select[name='s_tab_collection']");
                    s_tab_ele.empty();
                    var val_in_list_flag = true;
                    var val_in_list = false;
                    if(data){
                        for(var i = 0; i < data.length; i++){
                            s_tab_ele.append("<option value='" + data[i][0] + "'>" + data[i][1] + "</option>");
                            if(data[i][0].toString() === self.$target.attr("data-collection_id") && val_in_list_flag){
                                val_in_list = true;
                                val_in_list_flag = false;
                            }
                        }
                        if(self.$target.attr("data-collection_id") !== "0" && val_in_list && self.$target.attr("data-snippet_type") === "single"){
                            s_tab_ele.val(self.$target.attr("data-collection_id"));
                        }
                    }
                    self._rpc({
                        model: 'collection.configure',
                        method: 'name_search',
                        args: ['', []],
                        context: weContext.get()
                    }).then(function(data){
                        var m_tab_ele = $("#product_slider_modal select[name='m_tab_collection']");
                        m_tab_ele.empty();
                        val_in_list_flag = true;
                        val_in_list = false;
                        if(data){
                            for(var i = 0; i < data.length; i++){
                                m_tab_ele.append("<option value='" + data[i][0] + "'>" + data[i][1] + "</option>");
                                if(data[i][0].toString() === self.$target.attr("data-collection_id") && val_in_list_flag){
                                    val_in_list = true;
                                    val_in_list_flag = false;
                                }
                            }
                            if(val_in_list && self.$target.attr("data-collection_id") !== "0" && val_in_list && self.$target.attr("data-snippet_type") === "multi"){
                                m_tab_ele.val(self.$target.attr("data-collection_id"));
                            }
                        }
                    });
                });
                self.$modal.on('change', self.$modal.find("select[name='slider_type']"), function(){
                    var $sel_ele = $(this).find("select[name='slider_type']");
                    var $form = $(this).find("form");
                    if($sel_ele.val() === "single"){
                        $form.find(".s_tab_collection_container").show();
                        $form.find(".m_tab_collection_container").hide();                                               

                    }
                    else if($sel_ele.val() === "multi"){
                        $form.find(".s_tab_collection_container").hide();
                        $form.find(".m_tab_collection_container").show();
                    }
                });
                self.$modal.on('change', self.$modal.find("select[name='s_tab_layout'],select[name='m_tab_layout']"), function(e){
                    var $sel_ele;
                    var val_list = [];
                    if(self.$modal.find("select[name='slider_type']").val() === 'single')
                        $sel_ele = self.$modal.find("select[name='s_tab_layout']");
                    else if(self.$modal.find("select[name='slider_type']").val() === 'multi')
                        $sel_ele = self.$modal.find("select[name='m_tab_layout']");
                    else
                        return;
                    if($sel_ele.val() == 'slider' || $sel_ele.val() == 'fw_slider' || $sel_ele.val() == 'horiz_tab'){
                        self.$modal.find(".auto_load").show();
                        self.$modal.find(".prod_count").show();
                    }
                    else{
                        self.$modal.find(".auto_load").hide();
                        self.$modal.find(".prod_count").hide();
                    }
                    self.$modal.find("form .p_slider_sample_view img.snip_sample_img").attr("src", "/atharva_theme_general/static/src/img/snippets/" + $sel_ele.val() + ".png");
                    
                });
                // self.$modal.
                self.$modal.on('click', ".btn_apply", function(){
                    var $sel_ele = self.$modal.find("select[name='slider_type']");
                    var $form = self.$modal.find("form");
                    var $prod_auto = self.$modal.find("#prod-auto");
                    var $prod_count = self.$modal.find("#prod-count");
                    var collection_name = '';
                    var check = false;

                    // Check if autoPlay
                    if($prod_auto.is(":checked")){
                        check = true;
                    }

                    if($sel_ele.val() === "single"){

                        collection_name = $form.find("select[name='s_tab_collection'] option:selected").text();
                        if(!collection_name)
                            collection_name = "NO COLLECTION SELECTED";
                        self.$target.attr('data-snippet_type', $sel_ele.val());
                        self.$target.attr("data-collection_id", $form.find("select[name='s_tab_collection']").val());
                        self.$target.attr("data-collection_name", collection_name);
                        self.$target.attr("data-snippet_layout", $form.find("select[name='s_tab_layout']").val());
                        self.$target.attr("data-prod-auto", check);
                        self.$target.attr("data-prod-count", $prod_count.val());
                    }
                    else if($sel_ele.val() === "multi"){

                        collection_name = $form.find("select[name='m_tab_collection'] option:selected").text();
                        if(!collection_name)
                            collection_name = "NO COLLECTION SELECTED";
                        self.$target.attr('data-snippet_type', $sel_ele.val());
                        self.$target.attr("data-collection_id", $form.find("select[name='m_tab_collection']").val());
                        self.$target.attr("data-collection_name", collection_name);
                        self.$target.attr("data-snippet_layout", $form.find("select[name='m_tab_layout']").val());
                        self.$target.attr("data-prod-auto", check);
                        self.$target.attr("data-prod-count", $prod_count.val());
                    }
                    else{
                        collection_name = 'NO COLLECTION SELECTED';
                    }
                    self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>' + collection_name + '</h2></div></div>');
                });
                var sn_type = self.$target.attr("data-snippet_type");
                var sn_col = self.$target.attr("data-collection_id");
                var sn_layout = self.$target.attr("data-snippet_layout");
                var sn_count = self.$target.attr("data-prod-count");
                var sn_play = self.$target.attr("data-prod-auto");                                
                $('#prod-auto').prop('checked', sn_play);

                if(sn_type !== "0" && sn_layout !== "0" && sn_col !== "0"){
                    self.$modal.find("form select[name='slider_type']").val(sn_type);
                    if(self.$target.attr("data-snippet_type") === "single"){
                        self.$modal.find("form select[name='s_tab_layout']").val(sn_layout);
                    }
                    else if(self.$target.attr("data-snippet_type") === "multi"){
                        self.$modal.find("form select[name='m_tab_layout']").val(sn_layout);
                    }                   
                }

                // Set Count in Modify
                if(sn_count !== "0")
                {
                    self.$modal.find("form input[name='prod-count']").val(sn_count);
                }
                self.$modal.find("select[name='slider_type']").trigger("change");
                self.$modal.modal();
            }
            return self;
        },
        onBuilt: function(){
            var self = this;
            this._super();
            this.product_slider_configure('click');
        },
        cleanForSave: function () {
            this.$target.empty();
            $('.s_product_slider').empty();
            var model = this.$target.parent().attr('data-oe-model');
            if(model){
                this.$target.parent().addClass('o_editable o_dirty');
            }
        },
    });

options.registry['s_ecomm_cat_multi_with_header']= options.Class.extend({
        popup_template_id: "category_collection_template",
        popup_title: _t("Select Collection"),

        start: function () {
            var self = this;
            return this._super.apply(this, arguments);
        },
        select_collection: function (previewMode, value) {
            var self = this;
            var def = wUtils.prompt({
                'id': this.popup_template_id,
                'window_title': this.popup_title,
                'select': _t("Collection"),
                'init': function (field, dialog) {
                    return rpc.query({
                        model: 'category.collection',
                        method: 'name_search',
                        args: ['', []],
                        context: self.options.recordInfo.context,
                    }).then(function (data) {
                        $(dialog).find('.btn-primary').prop('disabled', !data.length);
                        return data;
                    });
                },
            });
            def.then(function (result) {
                var collection_id = parseInt(result.val);
                self.$target.attr("data-list-id", collection_id);
                rpc.query({
                    model: 'category.collection',
                    method: 'read',
                    args: [[collection_id],['name']],
                }).then(function (data){
                    if(data && data[0] && data[0].name)
                        self.$target.empty().append('<div class="container"><div class="category" contentEditable="false"><div class="col-md-12"><div class="seaction-head"<div class="h1">'+ data[0].name +'</div></div></div></div></div>');                                  
                });
            });
           return def;
        },
        onBuilt: function () {
            var self = this;
            this._super();
            this.select_collection('click').guardedCatch(function () {
                self.getParent()._onRemoveClick($.Event( "click" ));                        
            });
        },
        cleanForSave: function(){
            this.$target.empty();
            $('.js_ecomm_cat_multi_collection').empty();
            var model = this.$target.parent().attr('data-oe-model');
            if(model){
                this.$target.parent().addClass('o_editable o_dirty');
            }
        },
    });

});
