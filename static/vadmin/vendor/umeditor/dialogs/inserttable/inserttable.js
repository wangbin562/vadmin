/* eslint-disable */
(function () {
    var contains = function(elA, elB){
        return elA && elB && (elA === elB ? false : (
            elA.contains ? elA.contains(elB) :
                elA.compareDocumentPosition(elB) & 16
            ));
    }
    var editor = null;
    UM.registerWidget('inserttable', {

        tpl: '<link type=\"text/css\" rel=\"stylesheet\" href=\"<%=inserttable_url%>inserttable.css\"><div id="<%=randomId%>" class="edui-tablepicker">' +
                '<div class="edui-tablepicker-body">' +
                '<div class="edui-infoarea">' +
                '<span id="<%=randomId%>_label" class="edui-label">0列 x 0行</span>' +
                '</div>' +
                '<div class="edui-pickarea"' +
                '>' +
                '<div id="<%=randomId%>_overlay" class="edui-overlay"></div>' +
                '</div>' +
                '</div>' +
            '</div>',
        randomId: 'tablepicker' + parseInt(Math.random() * 10000000),
        numRows: 10,
        numCols: 10,
        lengthOfCellSide: 22,
        initContent: function (_editor, $widget) {
            var me = this,
                inserttableUrl = UMEDITOR_CONFIG.UMEDITOR_HOME_URL + 'dialogs/inserttable/',
                options = $.extend({}, {'inserttable_url': inserttableUrl, 'randomId': me.randomId }),
                $root = me.root();

            if (me.inited) {
                me.preventDefault();
                return;
            }
            me.inited = true;

            editor = _editor;
            me.$widget = $widget;
            $root.html($.parseTmpl(me.tpl, options));
        },
        initEvent: function () {
            var me = this;

            //防止点击过后关闭popup
            me.root().on('click', function (e) {
                return false;
            });


            // 绑定事件
            var pickareaDom = me.root().find('.edui-pickarea')
            pickareaDom.on('mousemove', function (evt) {
                var element = evt.target || evt.srcElement;
                var targetInfo = element.getBoundingClientRect();
                var offset = {
                    left: evt.clientX - targetInfo.left,
                    top: evt.clientY - targetInfo.top
                }
                var sideLen = me.lengthOfCellSide;
                var numCols = Math.ceil(offset.left / sideLen);
                var numRows = Math.ceil(offset.top / sideLen);
                me._track(numCols, numRows);
            });
            pickareaDom.on('mouseover', function (evt) {
                var el = this;
                var rel = evt.relatedTarget || evt.fromElement;
                if (!contains(el, rel) && el !== rel) {
                    var overlayDom = me.root().find('#' + me.randomId + '_overlay') || null;
                    if (overlayDom) overlayDom[0].style.visibility = '';
                    var label = me.root().find('#' + me.randomId + '_label') || null;;
                    if (label) label[0].innerHTML = '0列' +' x ' + '0行';
                }
            });

            pickareaDom.on('mouseout', function (evt) {
                var el = this;
                var rel = evt.relatedTarget || evt.fromElement;
                if (!contains(el, rel) && el !== rel) {
                    var overlayDom = me.root().find('#' + me.randomId + '_overlay') || null;
                    if (overlayDom) overlayDom[0].style.visibility = 'hidden';
                    var label = me.root().find('#' + me.randomId + '_label') || null;;
                    if (label) label[0].innerHTML = '0列' +' x ' + '0行';
                }
            });

            pickareaDom.on('click', function (evt) {
                me.clickFn(me.numCols, me.numRows);
                me.$widget.edui().hide();
                return false;
            });
        },
        _track: function (numCols, numRows){
            var me = this;
            var overlayDom = me.root().find('#' + this.randomId + '_overlay') || null;
            var style = overlayDom ? overlayDom[0].style : {};
            var sideLen = this.lengthOfCellSide;
            style.width = numCols * sideLen + 'px';
            style.height = numRows * sideLen + 'px';
            var label = me.root().find('#' + this.randomId + '_label') || null;;
            if (label) label[0].innerHTML = numCols + '列' +' x ' + numRows + '行';
            this.numCols = numCols;
            this.numRows = numRows;
        },
        clickFn: function (numCols, numRows){
            editor.execCommand('inserttable', {numRows:numRows, numCols:numCols, border:1});
        },
        width: 242,
        height: 300
    });

})();

