odoo.define('atharva_theme_general.customs_shop', function(require){
    'use strict';
    
    var ajax = require('web.ajax');

    $(document).on('click', '#load_more_products', function(event){
        event.preventDefault();

        var $btnEle = $(this);
        $btnEle.addClass("disabled");
        $btnEle.parent().siblings(".wait_loader_gif").removeClass("d-none");

        var $products_grid = $("div#products_grid");
        var temp_attr_list = [];
        var temp_attr_tag_list = [];
        var temp_attr_brand_list = [];

        if($("form.js_attributes").length > 0){
            $("form.js_attributes ul input[name*='attrib']").each(function(){
                if($(this).is(':checked')){
                    temp_attr_list.push($(this).val());
                }
            });

            $("form.js_attributes ul select option:selected").each(function(){
                temp_attr_list.push($(this).val());
            })

            $("form.js_attributes ul input[name*='tags']").each(function(){
                if($(this).is(':checked')){
                    temp_attr_tag_list.push($(this).val())
                }
            });

            $("form.js_attributes ul input[name*='brand']").each(function(){
                if($(this).is(':checked')){
                    temp_attr_brand_list.push($(this).val())
                }
            });
        }
        var param_dict = {
            loaded_products: $btnEle.siblings("input[name='loaded_products_count']").val(),
            ppg: parseInt($products_grid.find("div.shop-filter-item_qty select.custom-select").val() || 10),
            category: $btnEle.siblings("input[name='curr_category']").val(),
            search: $(".as-search form input[name='search']").val(),
            'attrib': temp_attr_list,
            'tags': temp_attr_tag_list,
            'brand': temp_attr_brand_list
        }
        var order_val = $products_grid.find(".products_pager .dropdown_sorty_by > a.dropdown-toggle").attr("data-sort_key_value");
        if(order_val !== '')
            param_dict.order = order_val;

        $.get("/shop/load_next_products", param_dict).then(function(data){
            if(data.trim()){
                $btnEle.removeClass("disabled");
                $btnEle.parent().siblings(".wait_loader_gif").addClass("d-none");
                $("div#products_grid div.as-product-list > .row:first").append(data);
                $btnEle.siblings("input[name='loaded_products_count']").val($("div#products_grid div.as-product-list > .row:first > div > form[action='/shop/cart/update']").length);
            }
            else{
                $btnEle.text("No More Products").addClass("disabled");
                $btnEle.parent().siblings(".wait_loader_gif").addClass("d-none");
            }
        });
    });

    $(document).on('change', 'div#products_grid div.shop-filter-item_qty select.custom-select', function(){
        var $selEle = $(this);
        var ppg = parseInt($selEle.val());

        var currentUrl = window.location.href;
        var url = new URL(currentUrl);

        url.searchParams.set("ppg", ppg);
        window.location.href = url.href;
    });

    $(document).ready(function(){
        if($(".oe_website_sale").length === 0){
            $("div#wrap").addClass("oe_website_sale");
        }

        //------------------------------------------
        // Share Product START
        //------------------------------------------
        $(".o_twitter, .o_facebook, .o_linkedin, .o_google").on('click', function(event){
            var url = '';
            var product_title_complete = $('#product_details h1').html().trim() || '';
            if ($(this).hasClass('o_twitter')){
                url = 'https://twitter.com/intent/tweet?tw_p=tweetbutton&text=Amazing product : '+product_title_complete+"! Check it live: "+window.location.href;
            } else if ($(this).hasClass('o_facebook')){
                url = 'https://www.facebook.com/sharer/sharer.php?u='+window.location.href;
            } else if ($(this).hasClass('o_linkedin')){
                url = 'https://www.linkedin.com/shareArticle?mini=true&url='+window.location.href+'&title='+product_title_complete;
            }
            window.open(url, "", "menubar=no, width=500, height=400");
        });
        //------------------------------------------
        // Share Product END
        //------------------------------------------


        //------------------------------------------
        // Clear Filter on Shop Page START
        //------------------------------------------
        $("#products_grid_before .js_attributes .clear_attr_filter").on("click", function(e){
            e.stopPropagation();
            var $attr_box = $(this).parents("li");
            var val_selector_str = "";
            $attr_box.find("input[name='attrib'][value^='" + $(this).data("attr_id") + "-']").each(function(){
                $(this).prop("checked", false);
            });
            $attr_box.find("input[name='brand']").each(function(){
                $(this).removeAttr('checked');
            });
            $attr_box.find("input[name='tags']").each(function(){
                $(this).removeAttr('checked');
            });
            $attr_box.find("select[name='attrib']").val("");
            $(this).parents("form.js_attributes").submit();
        });
        $("#products_grid_before .js_attributes .collapsible_attr_name").on("click", function(){
            $(this).toggleClass("section_open");
        });
        //------------------------------------------
        // Clear Filter on Shop Page END
        //------------------------------------------
    });

    //------------------------------------------
    // cart Popover START
    //------------------------------------------
    $(document).on("click", "#wrapwrap header #my_cart .my_cart_btn", function(e){
        var $target = $(this);
        $.get("/shop/cart/popup", {type: 'cart_lines_popup'}).then(function(data){
            if(data.trim()){
                var $mini_cart_popup = $target.parents("header").find(".cart_lines_popup");
                $mini_cart_popup.empty().append(data.trim()).addClass("show_mini_cart");
                $("body").addClass("cart-open-on-body");
            }
        });
        e.stopPropagation();
    });
    $(document).on("click", "header .cart_lines_popup .m_c_close", function(){
        $(this).parents(".cart_lines_popup").removeClass("show_mini_cart");
        $("body").removeClass("cart-open-on-body");
    });
    //------------------------------------------
    // cart Popover END
    //------------------------------------------

    $(document).on("submit", "header .h-search .as-search form", function(){
        $(this).find("input[name='ppg']").remove();
        var $ppgEle = $("div#products_grid div.shop-filter-item_qty select.custom-select");
        if($ppgEle.length === 1)
            $(this).append("<input type='hidden' name='ppg' value='" + $ppgEle.val() + "'>");
    });
});