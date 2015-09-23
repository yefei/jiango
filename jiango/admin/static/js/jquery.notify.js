/**
 * jQuery notify
 * 2015 Yefei <316606233@qq.com>
 * 
 * $('<p>Hello World!</p>').notify();
 * $('<p>Hello World!</p>').notify('error');
 * $('<p>Hello World!</p>').notify({sticky: true});
 * 
 * <p class="notify" data-notify-type="error">Error!</p>
 * $('.notify').notify();
 */

!function($) {
	var types = ['notice', 'warning', 'error', 'success'];
	var audio;
	
	var settings = {
		inEffect: {
			opacity: 'show'
		},
		inEffectDuration: 100,
		stayTime: 3000,
		sticky: false,
		type: 'notice',
		position: 'top-right',
		sound: null
	};
	
	var Notify = function(el, options){
		var el = $(el);
		var $this = this;
		var dataSettings = {}, data;
		
		data = el.data('notify-type');
		if (data && types.indexOf(data) > -1) {
			dataSettings['type'] = data;
		}
		
		data = el.data('notify-stay');
		if (data) {
			dataSettings['stayTime'] = data;
		}
		
		data = el.data('notify-position');
		if (data) {
			dataSettings['position'] = data;
		}
		
		data = el.data('notify-sticky');
		if (data) {
			dataSettings['sticky'] = data == 'yes' ? true : false;
		}
		
		this.opts = $.extend({}, settings, dataSettings, typeof options == 'object' && options);
		
		var wrapAll = (!$('.notify-container').length) ? $('<div></div>').addClass('notify-container').addClass('notify-position-' + this.opts.position).appendTo('body') : $('.notify-container');
		var itemOuter = $('<div></div>').addClass('notify-item-wrapper');
		
		this.itemInner = $('<div></div>').hide().addClass('notify-item notify-type-' + this.opts.type).appendTo(wrapAll).append(el).animate(this.opts.inEffect, this.opts.inEffectDuration).wrap(itemOuter);
		
		$('<div></div>').addClass('notify-item-close').prependTo(this.itemInner).click(function(){$this.close()});
		$('<div></div>').addClass('notify-item-image').addClass('notify-item-image-' + this.opts.type).prependTo(this.itemInner);

        navigator.userAgent.match(/MSIE 6/i) && wrapAll.css({top: document.documentElement.scrollTop});
		!this.opts.sticky && setTimeout(function(){$this.close()}, this.opts.stayTime);
		this.opts.sound && audio && audio.play();
	};
	
	Notify.prototype.close = function () {
		var obj = this.itemInner;
		obj.animate({opacity: '0'}, 600, function() {
			obj.parent().animate({height: '0px'}, 300, function() {
				obj.parent().remove();
			});
		});
	};
	
	$.notifySetup = function(options) {
		$.extend(settings, options);
		if (options['sound']) {
			if (window.HTMLAudioElement) {
				audio = new Audio();
				audio.src = options['sound'];
			}
		}
	};
	
	$.fn.notify = function(options) {
		return this.each(function () {
			if (typeof options == 'string' && types.indexOf(options) > -1) {
				return new Notify(this, {type: options});
			}
			return new Notify(this, options);
		});
	};

}(window.jQuery);
