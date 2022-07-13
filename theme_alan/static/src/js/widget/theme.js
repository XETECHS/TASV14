odoo.define('theme_alan.theme', function (require) {
    'use strict';

    var Theme = require('website.theme');
    var ColorpickerDialog = require('web.ColorpickerDialog');

    Theme.include({
        _pickColor: function (colorElement) {
            var self = this;
            var $color = $(colorElement);
            var colorName = $color.data('color');
            var colorType = $color.data('colorType');

            return new Promise(function (resolve, reject) {
                var colorpicker = new ColorpickerDialog(self, {
                    defaultColor: $color.css('background-color'),
                });
                var chosenColor = undefined;
                colorpicker.on('colorpicker:saved', self, function (ev) {
                    ev.stopPropagation();
                    chosenColor = ev.data.cssColor;
                });
                colorpicker.on('closed', self, function (ev) {
                    if (chosenColor === undefined) {
                        resolve();
                        return;
                    }

                    if (colorName === 'theme'){
                        var url = _.str.sprintf('/atharva_theme_general/static/src/scss/atg_theme.scss');

                        var colors = {};
                        colors['$as-theme'] = chosenColor;
                        self._makeSCSSCusto(url, colors).then(resolve).guardedCatch(resolve);
                    }
                    else{
                        var baseURL = '/website/static/src/scss/options/colors/';
                        var url = _.str.sprintf('%suser_%scolor_palette.scss', baseURL, (colorType ? (colorType + '_') : ''));

                        var colors = {};
                        colors[colorName] = chosenColor;
                        if (colorName === 'alpha') {
                            colors['beta'] = 'null';
                            colors['gamma'] = 'null';
                            colors['delta'] = 'null';
                            colors['epsilon'] = 'null';
                        }
                        self._makeSCSSCusto(url, colors).then(resolve).guardedCatch(resolve);
                    }
                });
                colorpicker.open();
            });
        },
    });

});
