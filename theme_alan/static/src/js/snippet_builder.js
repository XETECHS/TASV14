odoo.define('theme_alan.snippet_builder',function(require) {
    'use strict';

    var core = require('web.core');
    var QWeb = core.qweb;
    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var _t = core._t;
    var Dialog = require('web.Dialog');
   
    options.registry.summernote_embeded = options.Class.extend({
        xmlDependencies: ['/theme_alan/static/src/xml/website_snippet_builder.xml'],
        start: function () {
            var self = this;
            this.id = this.$target.attr("id");
        },
        select_snippet: function(type, value) {
            var self = this;
            this.id = this.$target.attr("id");
            var markupStr =this.$target.html();
            if(type == false || type == 'click'){
                var dialog = new Dialog(self, {
                    size: 'extra-large',
                    title: 'Alan Snippet Builder',
                    $content: QWeb.render("theme_alan.builder_block"),
                    buttons: [{text: _t('Save'), classes: 'btn-primary', close: true, click: function () {
                        var snippet = $("input[name='radio-snippet']:checked").closest('.snippet-as').find('textarea').val();
                        var data = self.$target.empty().append(snippet);
                        var model = self.$target.parent().attr('data-oe-model');
                        if(model){
                            self.$target.parent().addClass('o_editable o_dirty');
                        }
                    }}, {text: _t('Discard'), close: true}],
                });
                dialog.open();
                return self;
            }
        },
        onBuilt: function () {
          var self = this;
          this._super();
          this.select_snippet("click", "true");
        },
    });

    $(document).on('click', '.edit-snippet-builder-box .e-sb-tab label', function(){
        $('.edit-snippet-builder-box .e-sb-tab label').removeClass('e-sb-active');
        $(this).addClass('e-sb-active');
        var tagid = $(this).data('tag');
        $('.e-sb-tab--content').removeClass('active').addClass('d-none');
        $('#'+tagid).addClass('active').removeClass('d-none');
    });
});

