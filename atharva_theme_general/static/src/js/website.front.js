odoo.define('atharva_theme_general.front',function(require){
    'use strict';
    
    var sAnimation = require('website.content.snippets.animation');
    var concurrency = require('web.concurrency');
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    
    function initialize_owl(el, autoplay=false, items=4){
        el.owlCarousel({
            items: items,
            navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
            margin: 25,
            dots: true,
            autoplay: autoplay,
            autoplayHoverPause:true,
            autoplayTimeout: 3000,
            nav: true,
            responsive: {
                0: {
                    items: 1,
                },
                481: {
                    items: 2,
                },
                768: {
                    items: 2,
                },
                1024: {
                    items: 4,
                },
                1280: {
                    items: 4,
                },
                1600: {
                    items: items,
                }
            }
        });
    }
    
    function initialize_owl_1(el, autoplay=false, items=4){
        el.owlCarousel({
            items: items,
            navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
            margin: 25,
            dots: true,
            autoplay: autoplay,
            autoplayHoverPause:true,
            autoplayTimeout: 3000,
            nav: true,
            responsive: {
                0: {
                    items: 1,
                },
                481: {
                    items: 2,
                },
                768: {
                    items: 2,
                },
                1024: {
                    items: 4,
                },
                1200: {
                    items: items,
                }
            }
        });
    }

    function initialize_owl_multi(el, autoplay=false, items=4){
        el.owlCarousel({
            items: items,
            navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
            margin: 25,
            dots: true,
            autoplay: autoplay,
            autoplayHoverPause:true,
            autoplayTimeout: 3000,
            nav: true,
            responsive: {
                0: {
                    items: 1,
                },
                481: {
                    items: 2,
                },
                768: {
                    items: 3,
                },
                1024: {
                    items: 4,
                },
                1200: {
                    items: items,
                }
            }

        });
    }
    
    function destory_owl(el){
        if(el && el.data('owlCarousel')){
            el.data('owlCarousel').destroy();
            el.find('.owl-stage-outer').children().unwrap();
            el.removeData();
        }
    }

    publicWidget.registry.latest_blog = publicWidget.Widget.extend({
        selector : ".web_blog_slider",
        disabledInEditableMode: false,
        start: function (editable_mode) {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="seaction-head"><h1>Blog Slider</h1></div>');
            }
            if (!self.editableMode) {
                var list_id=self.$target.attr('data-blog_list-id') || false;
                $.get("/blog/get_blog_content",{'blog_config_id':list_id}).then(function (data){
                    if(data){
                        self.$target.empty().append(data);
                        self.$target.removeClass("hidden");
                        $(".tqt-blog-slide").owlCarousel({
                            items: 4,
                            navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
                            margin: 30,
                            dots: true,
                            nav: true,
                            responsive: {
                                0: {
                                    items: 1,
                                },
                                481: {
                                    items: 2,
                                },
                                768: {
                                    items: 2,
                                },
                                1024: {
                                    items: 3,
                                }
                            }
                        });
                    }
                });
            }
        },
    });

    sAnimation.registry.s_brand_multi_with_header = sAnimation.Class.extend({
        selector: ".js_brand_multi_collection",
        disabledInEditableMode: false,
        start: function(editable_mode) {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="container"><div class="product_slide" contentEditable="false"><div class="col-md-12"><div class="seaction-head"<div class="h1">Brand Collection Slider</div></div></div></div></div>');
            }
            if (!self.editableMode) {
                var list_id = self.$target.attr('data-list-id') || false;
                ajax.jsonRpc("/shop/get_brand_multi_tab_content", 'call', {
                    'collection_id': list_id
                }).then(function(data) {
                    if (data) {
                        var slider = data.slider
                        var auto_slider_value = data.auto_slider_value
                        var item_count = data.item_count
                        var slider_timing = data.slider_timing
                        self.$target.empty().append(slider);
                        $(".js_brand_multi_collection").removeClass('hidden');
                        self.$target.find("#as_our_brand").owlCarousel({
                            items: parseInt(item_count) || 4,
                            margin: 10,
                            autoplay: auto_slider_value || false,
                            autoplaySpeed: parseInt(slider_timing) || 5000,
                            autoplayHoverPause: true,
                            dots: true,
                            nav: true,
                            navText: ['<span aria-label="Previous"></span>', '<span aria-label="Next"></span>'],
                            responsive: {
                                0: {
                                    items: 2,
                                },
                                481: {
                                    items: 3,
                                },
                                768: {
                                    items: 4,
                                },
                                1024: {
                                    items: parseInt(item_count) || 4,
                                }
                            }
                        });
                    }
                });
            }
        },
    });
    
    
    sAnimation.registry.product_slider_actions = sAnimation.Class.extend({
        selector : ".s_product_slider",
        disabledInEditableMode: false,
        start: function (editable_mode) {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>' + self.$target.attr("data-collection_name") + '</h2></div></div>');
            }
            if(!self.editableMode){
                $.get("/shop/get_product_snippet_content",{
                    'snippet_type': self.$target.attr('data-snippet_type') || '',
                    'collection_id': self.$target.attr('data-collection_id') || 0,
                    'snippet_layout': self.$target.attr('data-snippet_layout') || ''
                }).then(function( data ) {
                    if(data){
                        self.$target.empty().append(data);
                        var autoplay = self.$target.attr('data-prod-auto') || false;
                        var prod_count = parseInt(self.$target.attr('data-prod-count')) || 8;
                        if(self.$target.attr('data-snippet_layout') === 'slider' && self.$target.find('> .prod_slider').length === 1){
                            initialize_owl_1(self.$target.find("> .prod_slider .tqt-pro-slide"), autoplay, prod_count);
                        }
                        else if(self.$target.attr('data-snippet_layout') === 'fw_slider' && self.$target.find('> .fw_prod_slider').length === 1){
                            initialize_owl(self.$target.find("> .fw_prod_slider .tqt-pro-slide"), autoplay, prod_count);
                        }
                        else if(self.$target.attr('data-snippet_layout') === 'horiz_tab' && self.$target.find('> .h_tab_prod_snip').length === 1){
                            self.$target.find('> .h_tab_prod_snip a[data-toggle="tab"]').on('shown.bs.tab', function () {
                                initialize_owl_multi(self.$target.find("> .h_tab_prod_snip .tab-content .active .multi_slider"), autoplay, prod_count);
                            }).on('hide.bs.tab', function () {
                                destory_owl(self.$target.find("> .h_tab_prod_snip .tab-content .active .multi_slider"));
                            });
                            initialize_owl_multi(self.$target.find("> .h_tab_prod_snip .tab-content .active .multi_slider"), autoplay, prod_count);
                        }
                    }
                });
            }
        }
    });

    sAnimation.registry.s_eComm_cat_multi_with_header = sAnimation.Class.extend({
        selector: ".js_ecomm_cat_multi_collection",
        disabledInEditableMode: false,
        start: function(editable_mode) {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="container"><div class="category" contentEditable="false"><div class="col-md-12"><div class="seaction-head"<div class="h1">eCommerce Category Grid</div></div></div></div></div>');
            }
            if (!self.editableMode) {
                var list_id = self.$target.attr('data-list-id') || false;
                ajax.jsonRpc("/shop/get_collection_categories", 'call', {
                    'collection_id': list_id
                }).then(function(data) {
                    if (data) {
                        var categories = data.categories         
                        self.$target.empty().append(categories);
                        $(".js_ecomm_cat_multi_collection").removeClass('hidden');
                    }
                });
            }
        },
    });

});
