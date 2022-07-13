odoo.define('atharva_theme_general.custom', function(require){
    'use strict';

    $(document).ready(function() {
        $('#as_accessory_product').owlCarousel({
            items: 6,
            margin: 10,
            navigation: true,
            pagination: false,
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
                    items: 5,
                },
                1400: {
                    items: 6,
                }
            }
        });

        $('#as_alternative').owlCarousel({
            items: 6,
            margin: 10,
            navigation: true,
            pagination: false,
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
                    items: 5,
                },
                1400: {
                    items: 6,
                }
            }
        });


        // Shop Filter
        $(".shop_filter").click(function() {
            $('.shop-filter-mob').toggleClass("shop_filter_box_mob");
            $('#products_grid_before').toggleClass("mob_filter_btn_open");
        });


        // Magnific Popup Gallery 
        if ($(".popup-youtube") && $(".popup-youtube").length > 0) {
            $(".popup-youtube").magnificPopup({
                disableOn: 700,
                type: 'iframe',
                mainClass: 'mfp-fade',
                removalDelay: 160,
                preloader: false,
                fixedContentPos: false
            });
        }

        if ($(".slider-popup-img") && $(".slider-popup-img").length > 0) {
            $(".slider-popup-img").magnificPopup({
                type: "image",
                gallery: {
                    enabled: true,
                }
            });
        }
        $('img.theme-slider-gallary').on('load', function(ev) {
            var $link = $(ev.currentTarget);
            var a = $link.parent().find("a");
            a.attr('href', this.src);
        });
        if ($(".slider-popup-product") && $(".slider-popup-product").length > 0) {
            $(".slider-popup-product").magnificPopup({
                type: "image",
                gallery: {
                    enabled: true,
                }
            });
        }

        // Back to Top
        var offset = 300,
            offset_opacity = 1200,
            scroll_top_duration = 700,
            $back_to_top = $('.cd-top');

        $(window).scroll(function() {
            ($(this).scrollTop() > offset) ? $back_to_top.addClass('cd-is-visible'): $back_to_top.removeClass('cd-is-visible cd-fade-out');
            if ($(this).scrollTop() > offset_opacity) {
                $back_to_top.addClass('cd-fade-out');
            }
        });

        //smooth scroll to top
        $back_to_top.on('click', function(event) {
            event.preventDefault();
            $('body,html').animate({
                scrollTop: 0,
            }, scroll_top_duration);
        });


        //Search
        $("header .search_open").on("click", function(event) {
            $(".h-search").toggleClass("hm-search-open");
            event.stopPropagation();
        });
        $(".h-search").on("click", function(event) {
            event.stopPropagation();
        });
        $(document).on("click", function(event) {
            $(".h-search").removeClass("hm-search-open");
        });

        // full width search
        $(".fw_search_open").click(function() {
            $('.full-width-search').addClass('fw-open-search');
        });

        $(".fw_close_search").click(function() {
            $('.full-width-search').removeClass('fw-open-search');
        });

        // Mobile Menu
        $("header .mobile_toggle_menu").click(function() {
            $(this).toggleClass("open");
            $('body').toggleClass("mob-main-nav-open");
        });


        /*Mega Menu*/
        $(".mm-mega-menu > a").after("<span class='mob_menu'></span>")
        $(".mm-cat-level-1 .cat-level-title").after("<span class='mob_menu'></span>")
        $(".mm-cat-level-1-v2 .cat-level-title").after("<span class='mob_menu'></span>")


        $(".mm-mega-menu .mob_menu").click(function() {
            $(this).parent('li').toggleClass("open-mob-menu");
            $(this).toggleClass("mob-menu-open");
        });

        $(".navbar-top-collapse .dropdown > .dropdown-toggle").after("<span class='mob_menu' data-toggle='dropdown' aria-expanded='false'></span>")
        /*Mega Menu End*/


        $('#getting-started').countdown('2024/03/27', function(event) {
            var $this = $(this);
            $this.html(event.strftime(''
                +
                '<ul>' +
                '<li><span>%D</span><label>days</label></li>' +
                '<li><span>%H</span><label>hr</label></li>' +
                '<li><span>%M</span><label>min</label></li>' +
                '<li><span>%S</span><label>sec</label></li>' +
                '</ul>'
            ));
        });

    });
    


    // Header Fiex
    $(window).on("scroll", function(){
        var HscrollTop  = $(window).scrollTop();  
        if (HscrollTop >= 196) {
           $('body').addClass('fixed-header');
        }
        else {
           $('body').removeClass('fixed-header');
        }
    });


    // Mega Category Level Menu
    $(document).on('mouseenter', 'header li.mm-mega-menu', function() {
        if ($(this).find(".mm-maga-main.mm-mega-cat-level").length > 0) {
            var $first_tab = $(this).find(".mm-category-level .mm-cat-level-1:eq(0)");
            $first_tab.find(".cat-level-title").addClass("active-li");
            $first_tab.find(".mm-cat-level-2").addClass("menu-active");
        }
    });

    $(document).on('mouseenter', '.mm-cat-level-1', function() {
        var $first_div = $(this).find('.cat-level-title');
        $first_div.addClass("active-li");
        $(this).find('.mm-cat-level-2').addClass("menu-active");
    });

    $(document).on('mouseleave', '.mm-cat-level-1', function() {
        var $first_div = $(this).find('.cat-level-title')
        $first_div.removeClass("active-li");
        $(this).find('.mm-cat-level-2').removeClass("menu-active");
    });

    // Mega Category Level Menu v2
    $(document).on('mouseenter', 'header li.mm-mega-menu', function() {
        if ($(this).find(".mm-maga-main.mm-mega-cat-level").length > 0) {
            var $first_tab_v2 = $(this).find(".mm-category-level-v2 .mm-cat-level-1-v2:eq(0)");
            $first_tab_v2.find(".cat_level_title_1").addClass("active-li");
            $first_tab_v2.find(".mm-cat-level-1-in-v2").addClass("menu-active");
        }

        if ($(this).find(".mm-maga-main.mm-mega-cat-level").length > 0) {
            var $first_tab_v2_in = $(this).find(".mm-cat-level-1-in-v2 .mm-cat-level-2-v2:eq(0)");
            $first_tab_v2_in.find(".cat_level_title_2").addClass("active-li");
            $first_tab_v2_in.find(".mm-cat-level-3-v2").addClass("menu-active");
        }
    });

    $(document).on('mouseenter', '.mm-cat-level-1-v2', function() {
        var $first_div = $(this).find('.cat_level_title_1');
        $first_div.addClass("active-li");
        var $first_ul = $(this).find('.mm-cat-level-1-in-v2');
        $first_ul.addClass("menu-active");
        var $first_tab_v2_in = $first_ul.find('.mm-cat-level-2-v2:eq(0)');
        $first_tab_v2_in.find(".cat_level_title_2").addClass("active-li");
        $first_tab_v2_in.find(".mm-cat-level-3-v2").addClass("menu-active");
    });

    $(document).on('mouseleave', '.mm-cat-level-1-v2', function() {
        var $first_div = $(this).find('.cat_level_title_1')
        $first_div.removeClass("active-li");
        var $first_ul = $(this).find('.mm-cat-level-1-in-v2');
        $first_ul.removeClass("menu-active");
        var $first_tab_v2_in = $first_ul.find('.mm-cat-level-2-v2:eq(0)');
        $first_tab_v2_in.find(".cat_level_title_2").removeClass("active-li");
        $first_tab_v2_in.find(".mm-cat-level-3-v2").removeClass("menu-active");
    });

    //Level 2
    $(document).on('mouseenter', '.mm-cat-level-2-v2', function() {
        $(this).siblings().children(".cat_level_title_2").removeClass("active-li");
        $(this).siblings().children(".mm-cat-level-3-v2").removeClass("menu-active");
        var $first_div = $(this).find('.cat_level_title_2');
        $first_div.addClass("active-li");
        $(this).find('.mm-cat-level-3-v2').addClass("menu-active");
    });

    $(document).on('mouseleave', '.mm-cat-level-2-v2', function() {
        var $first_div = $(this).find('.cat_level_title_2')
        $first_div.removeClass("active-li");
        $(this).find('.mm-cat-level-3-v2').removeClass("menu-active");
    });

});
