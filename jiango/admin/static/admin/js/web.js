// (C) 2015 by Yefei

var Web = {};

$.ajaxSetup({cache:false, dataType:'json'});

$.ajaxPrefilter(function(options, originalOptions, xhr){
	if (!options.crossDomain) {
		var token = $('meta[name="csrf-token"]').attr('content');
		if (token) xhr.setRequestHeader('X-CSRFToken', token);
	}
});

$.notifySetup({sound: static_prefix + 'admin/audio/notify.wav'});

/**
 * modal 浮层对话框
 */
Web.modal_defaults = {
	header: null,
	body: '',
	footer: null,
	closeButton: '<button class="btn" data-dismiss="modal" aria-hidden="true">关闭</button>',
	// bootstrap model options
	backdrop: true,
	keyboard: true,
	show: true,
	remote: false
};
Web.modal = function(options){
	var opts = $.extend({}, Web.modal_defaults, options);
	var header = null, footer = null;
	
	if (opts.header) {
		header = $('<div></div>').addClass('modal-header').append(opts.header);
	}
	
	if (opts.footer || opts.closeButton) {
		footer = $('<div></div>').addClass('modal-footer');
		opts.footer && footer.append(opts.footer);
		opts.closeButton && footer.append(opts.closeButton);
	}
	
	var body = $('<div></div>').addClass('modal-body').append(opts.body);
	var modal = $('<div></div>').addClass('modal fade').append(header).append(body).append(footer).modal({
		backdrop: opts.backdrop,
		keyboard: opts.keyboard,
		show: opts.show,
		remote: opts.remote
	});
	
	modal.on('hidden', function(){
		$(this).remove();
	});
};

/**
 * 全局 Ajax 错误处理
 */
$(document).ajaxError(function(event, xhr, ajaxSettings, thrownError){
	if (xhr.status >= 500 && xhr.status < 600) {
		$('<p>500: 服务器程序错误</p>').notify('error');
	}
	else if (xhr.status == 401) {
		$('<p>401: 未授权，请登陆帐号</p>').notify('error');
	}
	else if (xhr.status == 403) {
		$('<p>403: 没有权限</p>').notify('error');
	}
	else if (xhr.status == 404) {
		$('<p>404: 请求的资源不存在</p>').notify('error');
	}
	else if (xhr.status == 422) {
		var data = $.parseJSON(xhr.responseText);
		switch (data.type) {
		case 'FormError':
			var body = $('<div class="form-error"></div>');
			body.html($.map(data.message, function(v){
				return '<p>' + (v.label?'<label>'+v.label+'：</label>':'') + v.message + '</p>';
			}));
			Web.modal({body:body, header:'<b>请修正以下问题</b>'});
			break;
		case 'Deny':
			Web.modal({body:data.message, header:'<b>操作被禁止</b>'});
			break;
		}
	}
});

/**
 * 全选/取消全选
 * 如果 input 在 form 中则使用 form 的 context 否则使用 body
 * 使用样例:
 * 		<input type="checkbox" data-spy="checkall" data-for="[name='id']">
 */
$(window).on('load', function () {
	$('input[type="checkbox"][data-spy="checkall"][data-for]').each(function(){
		var context = this.form || document.body;
		var checkfor = $(this).data('for');
		$(this).click(function(){
			var is = $(this).is(':checked');
			$(checkfor, context).prop('checked', is);
		});
	});
});
