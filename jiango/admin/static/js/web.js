// (C) 2015 by Yefei

var Web = {};

$.ajaxSetup({cache:false, dataType:'json'});

$.ajaxPrefilter(function(options, originalOptions, xhr){
	if (!options.crossDomain) {
		var token = $('meta[name="csrf-token"]').attr('content');
		if (token) xhr.setRequestHeader('X-CSRFToken', token);
	}
});

if (window.HTMLAudioElement) {
	Web._notify_audio = new Audio();
	Web._notify_audio.src = static_prefix + 'audio/notify.wav';
}

Web.notify = function(tags, message){
	$().toastmessage('showToast', {text:message, type:tags});
	if (Web._notify_audio) Web._notify_audio.play();
};

$(document).ajaxError(function(event, xhr, ajaxSettings, thrownError){
	if (xhr.status >= 500 && xhr.status < 600) {
		Web.notify('error', '500: 服务器程序错误');
	}
	else if (xhr.status == 401) {
		Web.notify('error', '401: 未授权，请登陆帐号');
	}
	else if (xhr.status == 403) {
		Web.notify('error', '403: 没有权限');
	}
	else if (xhr.status == 404) {
		Web.notify('error', '404: 请求的资源不存在');
	}
	else if (xhr.status == 422) {
		var data = $.parseJSON(xhr.responseText);
		switch (data.type) {
		case 'FormError':
			var body = $('<div class="form-error"></div>');
			body.html($.map(data.message, function(v){
				return '<p>' + (v.label?'<label>'+v.label+'：</label>':'') + v.message + '</p>';
			}));
			//Boxy.alert(body);
			break;
		case 'Deny':
			//Boxy.alert(data.message);
			break;
		}
	}
});
