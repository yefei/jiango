/**
 * Created by Feiye on 2017/7/12.
 */

function ColorSelect(selectEl, inputEl) {
  var s = $('#' + selectEl + '>li');
  s.click(function () {
    var t = $(this);
    s.removeClass('selected');
    t.addClass('selected');
    $('#' + inputEl).val(t.data('value'));
  })
}
