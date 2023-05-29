/*! jRespond.js v 0.10 | Author: Jeremy Fields [jeremy.fields@viget.com], 2013 | License: MIT */
!function(a,b,c){"object"==typeof module&&module&&"object"==typeof module.exports?module.exports=c:(a[b]=c,"function"==typeof define&&define.amd&&define(b,[],function(){return c}))}(this,"jRespond",function(a,b,c){"use strict";return function(a){var b=[],d=[],e=a,f="",g="",i=0,j=100,k=500,l=k,m=function(){var a=0;return a="number"!=typeof window.innerWidth?0!==document.documentElement.clientWidth?document.documentElement.clientWidth:document.body.clientWidth:window.innerWidth},n=function(a){if(a.length===c)o(a);else for(var b=0;b<a.length;b++)o(a[b])},o=function(a){var e=a.breakpoint,h=a.enter||c;b.push(a),d.push(!1),r(e)&&(h!==c&&h.call(null,{entering:f,exiting:g}),d[b.length-1]=!0)},p=function(){for(var a=[],e=[],h=0;h<b.length;h++){var i=b[h].breakpoint,j=b[h].enter||c,k=b[h].exit||c;"*"===i?(j!==c&&a.push(j),k!==c&&e.push(k)):r(i)?(j===c||d[h]||a.push(j),d[h]=!0):(k!==c&&d[h]&&e.push(k),d[h]=!1)}for(var l={entering:f,exiting:g},m=0;m<e.length;m++)e[m].call(null,l);for(var n=0;n<a.length;n++)a[n].call(null,l)},q=function(a){for(var b=!1,c=0;c<e.length;c++)if(a>=e[c].enter&&a<=e[c].exit){b=!0;break}b&&f!==e[c].label?(g=f,f=e[c].label,p()):b||""===f||(f="",p())},r=function(a){if("object"==typeof a){if(a.join().indexOf(f)>=0)return!0}else{if("*"===a)return!0;if("string"==typeof a&&f===a)return!0}},s=function(){var a=m();a!==i?(l=j,q(a)):l=k,i=a,setTimeout(s,l)};return s(),{addFunc:function(a){n(a)},getBreakpoint:function(){return f}}}}(this,this.document));

var $ = jQuery.noConflict();

// Scrolled
$.fn.scrollEnd = function(callback, timeout) {
	$(this).scroll(function(){
		let container = $(this);
		if (container.data('scrollTimeout')) {
			clearTimeout(container.data('scrollTimeout'));
		}
		container.data('scrollTimeout', setTimeout(callback,timeout));
	});
};

(function() {
	let lastTime = 0;
	let vendors = ['ms', 'moz', 'webkit', 'o'];
	for(let x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
		window.requestAnimationFrame = window[vendors[x]+'RequestAnimationFrame'];
		window.cancelAnimationFrame = window[vendors[x]+'CancelAnimationFrame']
									|| window[vendors[x]+'CancelRequestAnimationFrame'];
	}

	if (!window.requestAnimationFrame)
		window.requestAnimationFrame = function(callback, element) {
			let currTime = new Date().getTime();
			let timeToCall = Math.max(0, 16 - (currTime - lastTime));
			let id = window.setTimeout(function() { callback(currTime + timeToCall); },
			  timeToCall);
			lastTime = currTime + timeToCall;
			return id;
		};

	if (!window.cancelAnimationFrame)
		window.cancelAnimationFrame = function(id) {
			clearTimeout(id);
		};
}());



function debounce(func, wait, immediate) {
	let timeout, args, context, timestamp, result;
	return function() {
		context = this;
		args = arguments;
		timestamp = new Date();
		let later = function() {
			let last = (new Date()) - timestamp;
			if (last < wait) {
				timeout = setTimeout(later, wait - last);
			} else {
				timeout = null;
				if (!immediate) result = func.apply(context, args);
			}
		};
		let callNow = immediate && !timeout;
		if (!timeout) {
			timeout = setTimeout(later, wait);
		}
		if (callNow) result = func.apply(context, args);
		return result;
	};
}


function onScrollSliderParallax() {
	SEMICOLON.slider.sliderParallax();
	SEMICOLON.slider.sliderElementsFade();
}


var SEMICOLON = SEMICOLON || {};
window.scwEvents = window.scwEvents || {};

(function($){

	// USE STRICT
	"use strict";

	SEMICOLON.initialize = {

		init: function(){

			SEMICOLON.initialize.defaults();
			SEMICOLON.initialize.pageTransition();
			SEMICOLON.initialize.goToTop();
			SEMICOLON.initialize.lazyLoad();
			SEMICOLON.initialize.lightbox();
			SEMICOLON.initialize.resizeVideos();
			SEMICOLON.initialize.dataResponsiveClasses();
			SEMICOLON.initialize.dataResponsiveHeights();
			SEMICOLON.initialize.stickFooterOnSmall();

		},

		execFunc: function( functionName, context ) {
			let args = Array.prototype.slice.call( arguments, 2 ),
				namespaces = functionName.split("."),
				func = namespaces.pop();

			for( let i = 0; i < namespaces.length; i++ ) {
				context = context[namespaces[i]];
			}

			if( typeof context[func] !== 'undefined' ) {
				return context[func].apply( context, args );
			} else {
				console.log( functionName + ' Function does not exist' );
			}
		},

		execPlugin: function( element, settings, available ) {
			let pluginActive = false,
				pluginLinkingInterval;

			if( available ) {

				if( settings.trigger && !scwEvents[settings.trigger] ) {
					$window.trigger( settings.trigger );
					scwEvents[settings.trigger] = true;
				}

				if( settings.execfn ) {
					SEMICOLON.initialize.execFunc( settings.execfn, window, element );
				}

				if( settings.class ) {
					$body.addClass( settings.class );
				}

			} else {
				if( settings.trigger && !scwEvents[settings.trigger] ) {
					pluginLinkingInterval = setInterval( function plugFn(){
						let pluginFnExec = settings.pluginfn();
						if( pluginFnExec ) {
							$window.trigger( settings.trigger );
							scwEvents[settings.trigger] = true;
							clearInterval( pluginLinkingInterval );
						}
						return plugFn;
					}(), 1000);
				} else {
					pluginActive = true;
				}

				if( settings.execfn ) {
					if( settings.trigger && !pluginActive ) {
						$window.on( settings.trigger, function(){
							SEMICOLON.initialize.execFunc( settings.execfn, window, element );
						});
					} else {
						SEMICOLON.initialize.execFunc( settings.execfn, window, element );
					}
				}

				if( settings.class ) {
					$body.addClass( settings.class );
				}
			}
		},

		jsLinking: function( element, settings ) {
			if( element.length < 1 ){
				return false;
			}

			if( settings.hiddendisable && ( element.filter(':hidden').length == element.length ) ) {
				return false;
			}

			let pluginFnExec = settings.pluginfn(),
				jsPath = 'js/', file,
				disableAJAX = false;

			if( typeof scwJsPath !== 'undefined' ) {
				jsPath = scwJsPath + '/';
			}

			if( typeof scwDisableJsAJAX !== 'undefined' && scwDisableJsAJAX === true ) {
				disableAJAX = true;
			}

			if( /^(f|ht)tps?:\/\//i.test( window.decodeURIComponent( settings.file ) ) ) {
				file = settings.file;
			} else {
				file = jsPath + settings.file;
			}

			if( pluginFnExec ) {
				SEMICOLON.initialize.execPlugin( element, settings, true );
			} else {
				if( !disableAJAX ) {
					$.ajax({
						url: file,
						dataType: "script",
						cache: true,
						crossDomain: true,
						timeout: 5000,
					}).done(function() {
						SEMICOLON.initialize.execPlugin( element, settings, false );
					}).fail(function() {
						console.log( settings.error );
					});
				} else {
					console.log( settings.error );
				}
			}
		},

		functions: function( settings ){
			let element, parent, item;

			if( typeof settings.element === 'object' && settings.element !== null ) {
				if( settings.element.parent !== 'undefined' ) {
					parent = settings.element.parent;
				}
				if( settings.element.el !== 'undefined' ) {
					settings.element = settings.element.el;
				}
			}

			if( settings.element ) {
				item = settings.element;
			} else {
				item = settings.default;
			}

			if( typeof parent === 'object' ) {
				element = parent.find( item );
			} else {
				element = $( item );
			}

			this.jsLinking( element, settings );
		},

		defaults: function(){
			let easingJs = {
				default: 'body',
				file: 'plugins.easing.js',
				error: 'plugins.easing.js: Plugin could not be loaded',
				pluginfn: () => typeof jQuery.easing["easeOutQuad"] !== "undefined",
				trigger: 'pluginEasingReady',
				class: 'has-plugin-easing'
			};

			let bootstrapJs = {
				default: 'body',
				file: 'plugins.bootstrap.js',
				error: 'plugins.bootstrap.js: Plugin could not be loaded',
				pluginfn: () => typeof bootstrap !== "undefined",
				trigger: 'pluginBootstrapReady',
				class: 'has-plugin-bootstrap'
			};

			let jRes = jRespond([
				{
					label: 'smallest',
					enter: 0,
					exit: 575
				},{
					label: 'handheld',
					enter: 576,
					exit: 767
				},{
					label: 'tablet',
					enter: 768,
					exit: 991
				},{
					label: 'laptop',
					enter: 992,
					exit: 1199
				},{
					label: 'desktop',
					enter: 1200,
					exit: 10000
				}
			]);

			jRes.addFunc([
				{
					breakpoint: 'desktop',
					enter: function() { $body.addClass('device-xl'); },
					exit: function() { $body.removeClass('device-xl'); }
				},{
					breakpoint: 'laptop',
					enter: function() { $body.addClass('device-lg'); },
					exit: function() { $body.removeClass('device-lg'); }
				},{
					breakpoint: 'tablet',
					enter: function() { $body.addClass('device-md'); },
					exit: function() { $body.removeClass('device-md'); }
				},{
					breakpoint: 'handheld',
					enter: function() { $body.addClass('device-sm'); },
					exit: function() { $body.removeClass('device-sm'); }
				},{
					breakpoint: 'smallest',
					enter: function() { $body.addClass('device-xs'); },
					exit: function() { $body.removeClass('device-xs'); }
				}
			]);

			SEMICOLON.initialize.functions( easingJs );
			SEMICOLON.initialize.functions( bootstrapJs );

			if( ! 'IntersectionObserver' in window ){
				let intersectObserve = {
					default: 'body',
					file: 'intersection-observer.js',
					error: 'intersection-observer.js: Plugin could not be loaded',
					pluginfn: () => typeof window.IntersectionObserver !== "undefined",
					trigger: 'intersectObservePolyfill',
					class: 'has-polyfill-intersection-observer'
				};

				SEMICOLON.initialize.functions( intersectObserve );
			}
		},

		goToTop: function(){
			let elementScrollSpeed = $goToTopEl.attr('data-speed'),
				elementScrollEasing = $goToTopEl.attr('data-easing');

			if( !elementScrollSpeed ) { elementScrollSpeed = 700; }
			if( !elementScrollEasing ) { elementScrollEasing = 'easeOutQuad'; }

			$goToTopEl.off( 'click' ).on( 'click', function() {
				$('body,html').stop(true).animate({
					'scrollTop': 0
				}, Number( elementScrollSpeed ), elementScrollEasing );
				return false;
			});
		},

		goToTopScroll: function(){
			let elementMobile = $goToTopEl.attr('data-mobile'),
				elementOffset = $goToTopEl.attr('data-offset');

			if( !elementOffset ) { elementOffset = 450; }

			if( elementMobile != 'true' && ( $body.hasClass('device-sm') || $body.hasClass('device-xs') ) ) { return true; }

			if( $window.scrollTop() > Number(elementOffset) ) {
				$goToTopEl.fadeIn();
				$body.addClass('gototop-active');
			} else {
				$goToTopEl.fadeOut();
				$body.removeClass('gototop-active');
			}
		},

		lightbox: function( element ){
			let settings = {
				element: element,
				default: '[data-lightbox]',
				file: 'plugins.lightbox.js',
				error: 'plugins.lightbox.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_lightboxInit',
				pluginfn: () => $().magnificPopup,
				trigger: 'pluginLightboxReady',
				class: 'has-plugin-lightbox'
			};

			SEMICOLON.initialize.functions( settings );
		},

		modal: function( element ){
			let settings = {
				element: element,
				default: '.modal-on-load',
				file: 'plugins.lightbox.js',
				error: 'plugins.lightbox.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_modalInit',
				pluginfn: () => $().magnificPopup,
				trigger: 'pluginLightboxReady',
				class: 'has-plugin-lightbox'
			};

			SEMICOLON.initialize.functions( settings );
		},

		resizeVideos: function(){
			let settings = {
				default: 'iframe[src*="youtube"],iframe[src*="vimeo"],iframe[src*="dailymotion"],iframe[src*="maps.google.com"],iframe[src*="google.com/maps"]',
				file: 'plugins.fitvids.js',
				error: 'plugins.fitvids.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_resizeVideosInit',
				pluginfn: () => $().fitVids,
				trigger: 'pluginfitVidsReady',
				class: 'has-plugin-fitvids'
			};

			SEMICOLON.initialize.functions( settings );
		},

		pageTransition: function(){
			let settings = {
				default: '.page-transition',
				file: 'plugins.pagetransition.js',
				error: 'plugins.pagetransition.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_pageTransitionInit',
				pluginfn: () => $().animsition,
				trigger: 'pluginPageTransitionReady',
				class: 'has-plugin-animsition'
			};

			SEMICOLON.initialize.functions( settings );
		},

		lazyLoad: function( element ) {
			let settings = {
				element: element,
				default: '.lazy',
				file: 'plugins.lazyload.js',
				error: 'plugins.lazyload.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_lazyLoadInit',
				pluginfn: () => typeof LazyLoad !== "undefined",
				trigger: 'pluginlazyLoadReady',
				class: 'has-plugin-lazyload'
			};

			SEMICOLON.initialize.functions( settings );
		},

		topScrollOffset: function() {
			let topOffsetScroll = 0;

			if( ( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) && !SEMICOLON.isMobile.any() ) {
				if( $header.hasClass('sticky-header') ) {
					if( $pagemenu.hasClass('dots-menu') ) { topOffsetScroll = 100; } else { topOffsetScroll = 144; }
				} else {
					if( $pagemenu.hasClass('dots-menu') ) { topOffsetScroll = 140; } else { topOffsetScroll = 184; }
				}

				if( !$pagemenu.length ) {
					if( $header.hasClass('sticky-header') ) { topOffsetScroll = 100; } else { topOffsetScroll = 140; }
				}
			} else {
				topOffsetScroll = 40;
			}

			return topOffsetScroll;
		},

		dataResponsiveClasses: function(){
			let settings = {
				default: '[data-class-xl],[data-class-lg],[data-class-md],[data-class-sm],[data-class-xs]',
				file: 'plugins.dataclasses.js',
				error: 'plugins.dataclasses.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_dataClassesInit',
				pluginfn: () => typeof scwDataClassesPlugin !== "undefined",
				trigger: 'pluginDataClassesReady',
				class: 'has-plugin-dataclasses'
			};

			SEMICOLON.initialize.functions( settings );
		},

		dataResponsiveHeights: function(){
			let settings = {
				default: '[data-height-xl],[data-height-lg],[data-height-md],[data-height-sm],[data-height-xs]',
				file: 'plugins.dataheights.js',
				error: 'plugins.dataheights.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_dataHeightsInit',
				pluginfn: () => typeof scwDataHeightsPlugin !== "undefined",
				trigger: 'pluginDataHeightsReady',
				class: 'has-plugin-dataheights'
			};

			SEMICOLON.initialize.functions( settings );
		},

		stickFooterOnSmall: function(){
			$footer.css({ 'margin-top': '' });
			let windowH = $window.height(),
				wrapperH = $wrapper.height();

			if( !$body.hasClass('sticky-footer') && $footer.length > 0 && $wrapper.has('#footer') ) {
				if( windowH > wrapperH ) {
					$footer.css({ 'margin-top': ( 0 ) });
				}
			}
		}

	};

	SEMICOLON.header = {

		init: function(){

			SEMICOLON.header.initialize();
			SEMICOLON.header.menufunctions();
			SEMICOLON.header.fullWidthMenu();
			SEMICOLON.header.stickyMenu();
			SEMICOLON.header.stickyPageMenu();
			SEMICOLON.header.sideHeader();
			SEMICOLON.header.sidePanel();
			SEMICOLON.header.onePageScroll();
			SEMICOLON.header.logo();
			SEMICOLON.header.topsearch();
			SEMICOLON.header.topcart();
			SEMICOLON.header.miscFunctions();

		},

		initialize: function() {

			initHeaderHeight = $headerWrap.outerHeight();

			if( $headerWrap.length > 0 ) {
				if( $('.header-wrap-clone').length < 1 ) {
					$headerWrap.after('<div class="header-wrap-clone"></div>');
				}
				$headerWrapClone = $('.header-wrap-clone');
			}

			if( $pagemenu.length > 0 ) {
				$pagemenu.find('#page-menu-wrap').after('<div class="page-menu-wrap-clone"></div>');
				$pageMenuClone = $('.page-menu-wrap-clone');
			}

			let menuItemSubs = $( '.menu-item:has(.sub-menu-container)' );

			menuItemSubs.addClass('sub-menu'); // , .primary-menu.with-arrows > .menu-container > .menu-item:has(.sub-menu-container) > .menu-link > div:not(:has(.icon-angle-down))
			$( '.top-links-item:has(.top-links-sub-menu,.top-links-section) > a:not(:has(.icon-angle-down)), .menu-item:not(.mega-menu-title):has(.sub-menu-container) > .menu-link > div:not(:has(.icon-angle-down)), .page-menu-item:has(.page-menu-sub-menu) > a > div:not(:has(.icon-angle-down))' ).append( '<i class="icon-angle-down"></i>' );
			$( '.menu-item:not(.mega-menu-title):has(.sub-menu-container):not(:has(.sub-menu-trigger))' ).append( '<button class="sub-menu-trigger icon-chevron-right"></button>' );

			SEMICOLON.header.menuInvert();

		},

		menuInvert: function( subMenuEl ) {
			let submenus = subMenuEl || $( '.mega-menu-content, .sub-menu-container, .top-links-section' );

			submenus.children().css({ 'display': 'block' });
			submenus.css({ 'display': 'block' });
			submenus.each( function( index, element ){
				let viewportOffset = element.getBoundingClientRect();

				if( $body.hasClass('rtl') ) {
					if( viewportOffset.left < 0 ) {
						element.classList.add('menu-pos-invert');
					}
				}

				if((viewportOffset.left + viewportOffset.width) - windowWidth > 0) {
					element.classList.add('menu-pos-invert');
				}
			});
			submenus.children().css({ 'display': '' });
			submenus.css({ 'display': '' });
		},

		includeOffset: function(){
			if( $headerInc.length < 1 ) {
				return true;
			}

			let headerInc = $header.outerHeight();
			if( $header.hasClass('floating-header') || $headerInc.hasClass('include-topbar') ) {
				headerInc = headerInc + $header.offset().top;
			}
			$headerInc.css({ 'margin-top': -headerInc });
			SEMICOLON.slider.sliderParallax();
		},

		menufunctions: function(){

			let menuItemSubs		= $( '.menu-item:has(.sub-menu-container)' ),
				menuItemSubsLinks	= menuItemSubs.children( '.menu-link' ),
				submenusT			= '.mega-menu-content, .sub-menu-container',
				submenus			= $( submenusT ),
				menuItemT			= '.menu-item',
				subMenuT			= '.sub-menu',
				menuSpeed			= primaryMenu.attr( 'data-trigger-speed' ) || 200,
				subMenuTriggerT		= '.sub-menu-trigger',
				menuItemTrigger;

			menuSpeed = Number( menuSpeed );

			menuItemTrigger	= menuItemSubs.children( subMenuTriggerT );

			if( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) {
				setTimeout( function(){
					if( $headerWrapClone.length > 0 ) {
						$headerWrapClone.css({ 'height': initHeaderHeight });
					}
					SEMICOLON.header.includeOffset();
				}, 1000);
				primaryMenu.find( submenus ).css({ 'display': '' });
			} else {
				$headerInc.css({ 'margin-top': '' });
			}

			if( ( $body.hasClass('overlay-menu') && primaryMenu.hasClass('on-click') ) && ( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) ) {
				menuItemSubsLinks.off( 'click' ).on( 'click', function(e){
					let triggerEl = $(this);
					triggerEl.parents( subMenuT ).siblings().find( submenus ).stop( true, true ).slideUp( menuSpeed );
					triggerEl.parent( menuItemT ).children( submenusT ).stop( true, true ).slideToggle( menuSpeed );
					e.preventDefault();
				});
			} else if( ( $body.hasClass('side-header') && primaryMenu.hasClass('on-click') ) || ( $body.hasClass('device-md') || $body.hasClass('device-sm') || $body.hasClass('device-xs') ) ) {
				menuItemTrigger.removeClass('icon-rotate-90');
				$( menuItemT ).find( submenus ).filter(':not(:animated)').stop( true, true ).slideUp( menuSpeed , function(){
					$body.toggleClass("primary-menu-open", false);
				});

				menuItemTrigger = menuItemTrigger.add( menuItemSubsLinks.filter('[href^="#"]') );

				menuItemTrigger.off( 'click' ).on( 'click', function(e){
					let triggerEl = $(this);
					triggerEl.parents( subMenuT ).siblings().find( subMenuTriggerT ).removeClass('icon-rotate-90');
					triggerEl.parents( subMenuT ).siblings().find( submenus ).filter(':not(:animated)').stop( true, true ).slideUp( menuSpeed );
					triggerEl.parent( menuItemT ).children( submenusT ).filter(':not(:animated)').stop( true, true ).slideToggle( menuSpeed );

					let subMenuTriggerEl = triggerEl.parent( menuItemT ).children( subMenuTriggerT );

					if( !subMenuTriggerEl.hasClass( 'icon-rotate-90' ) ) {
						subMenuTriggerEl.addClass('icon-rotate-90');
					} else {
						subMenuTriggerEl.removeClass('icon-rotate-90');
					}

					e.preventDefault();
				});
			} else if( ( $body.hasClass('overlay-menu') || $body.hasClass('side-header') ) && ( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) ) {
				primaryMenu.find( submenus ).stop( true, true ).slideUp( menuSpeed );
				$( menuItemT ).hover( function(e){
					$(this).children( submenusT ).stop( true, true ).slideDown( menuSpeed );
				}, function(){
					$(this).children( submenusT ).stop( true, true ).slideUp( menuSpeed );
				});
			} else {
				if( primaryMenu.hasClass('on-click') ) {
					menuItemSubsLinks.off( 'click' ).on( 'click', function(e){
						let triggerEl = $(this);
						triggerEl.parents( subMenuT ).siblings().find( submenus ).removeClass('d-block');
						triggerEl.parent( menuItemT ).children( submenusT ).toggleClass('d-block');
						triggerEl.parent( menuItemT ).siblings().removeClass('current');
						triggerEl.parent( menuItemT ).toggleClass('current');
						e.preventDefault();
					});
				}
			}

			if( $('.top-links').hasClass('on-click') || ( $body.hasClass('device-md') || $body.hasClass('device-sm') || $body.hasClass('device-xs') ) ) {
				$('.top-links-item:has(.top-links-sub-menu,.top-links-section) > a').on( 'click', function(e){
					$(this).parents('li').siblings().find('.top-links-sub-menu,.top-links-section').removeClass('d-block');
					$(this).parent('li').children('.top-links-sub-menu,.top-links-section').toggleClass('d-block');
					e.preventDefault();
				});
			}

			SEMICOLON.header.menuInvert( $('.top-links-section') );

			$('#primary-menu-trigger').off( 'click' ).on( 'click', function() {
				if( $body.hasClass('device-md') || $body.hasClass('device-sm') || $body.hasClass('device-xs') ) {
					if( primaryMenu.find('.mobile-primary-menu').length > 0 ) {
						$( '.primary-menu:not(.mobile-menu-off-canvas) .mobile-primary-menu' ).stop( true, true ).slideToggle( menuSpeed );
						$( '.primary-menu.mobile-menu-off-canvas .mobile-primary-menu' ).toggleClass('d-block');
					} else {
						$( '.primary-menu:not(.mobile-menu-off-canvas) .menu-container' ).stop( true, true ).slideToggle( menuSpeed );
						$( '.primary-menu.mobile-menu-off-canvas .menu-container' ).toggleClass('d-block');
					}
				}
				$body.toggleClass("primary-menu-open");
				return false;
			});

			$( '.menu-container:not(.mobile-primary-menu)' ).css({ 'display': '' });
			if( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) {
				primaryMenu.find('.mobile-primary-menu').removeClass('d-block');
			}

		},

		fullWidthMenu: function(){

			if( $body.hasClass('device-md') || $body.hasClass('device-sm') || $body.hasClass('device-xs') ) {
				$('.mega-menu-content, .top-search-form').css({ 'width': '' });
				return true;
			}

			let headerWidth = $('.mega-menu:not(.mega-menu-full):not(.mega-menu-small) .mega-menu-content').parents('.header-row').width();

			if( $header.find('.container-fullwidth').length > 0 ) {
				$('.mega-menu:not(.mega-menu-full):not(.mega-menu-small) .mega-menu-content').css({ 'width': headerWidth });
			}

			if( $body.hasClass('stretched') ) {
				if( $header.hasClass('floating-header') ) {
					$('.mega-menu:not(.mega-menu-full):not(.mega-menu-small) .mega-menu-content, .top-search-form').css({ 'width': headerWidth + 80 });
				} else {
					$('.mega-menu:not(.mega-menu-full):not(.mega-menu-small) .mega-menu-content, .top-search-form').css({ 'width': headerWidth });
				}
			} else {
				if( $header.hasClass('full-header') ) {
					$('.mega-menu:not(.mega-menu-full):not(.mega-menu-small) .mega-menu-content').css({ 'width': headerWidth - 80 });
				}
			}

			if( $header.find('.header-row').length > 1 ) {
				let megaMenuContent	= $('.menu-container > .mega-menu:not(.mega-menu-small) .mega-menu-content').eq(0),
					offset			= $headerWrap.outerHeight() - megaMenuContent.parents('.header-row').outerHeight(),
					css				= '.menu-container > .mega-menu:not(.mega-menu-small) .mega-menu-content { top: calc( 100% - '+ offset +'px ); }',
					head			= document.head || document.getElementsByTagName('head')[0],
					style			= document.createElement('style');

				head.appendChild(style);

				style.type = 'text/css';
				style.appendChild(document.createTextNode(css));
			}
		},

		stickyMenu: function( headerOffset ){

			windowScrT	= $window.scrollTop();

			if( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) {
				if( windowScrT > headerOffset ) {

					if( !$body.hasClass('side-header') ) {
						$header.filter(':not(.no-sticky)').addClass('sticky-header');
						// if( !$headerWrap.hasClass('force-not-dark') ) { $headerWrap.removeClass('not-dark'); }
						SEMICOLON.header.stickyMenuClass();

						if( stickyShrink == 'true' && !$header.hasClass('no-sticky') ) {
							if( ( windowScrT - headerOffset ) > Number( stickyShrinkOffset ) ) {
								$header.addClass('sticky-header-shrink');
								if( headerSizeCustom ){
									logo.find('img').css({ 'height': Number( stickyLogoH ) });
									SEMICOLON.header.menuItemsSpacing( stickyMenuP );
								}
							} else {
								$header.removeClass('sticky-header-shrink');
								if( headerSizeCustom ){
									logo.find('img').css({ 'height': Number( defLogoH ) });
									SEMICOLON.header.menuItemsSpacing( defMenuP );
								}
							}
						}
					}

				} else {
					SEMICOLON.header.removeStickyness();
					if( headerSizeCustom ){
						logo.find('img').css({ 'height': Number( defLogoH ) });
						SEMICOLON.header.menuItemsSpacing( defMenuP );
					}
				}
			}

			if( $body.hasClass('device-xs') || $body.hasClass('device-sm') || $body.hasClass('device-md') ) {
				if( mobileSticky == 'true' ) {
					if( windowScrT > headerOffset ) {
						$header.filter(':not(.no-sticky)').addClass('sticky-header');
						SEMICOLON.header.stickyMenuClass();
					} else {
						SEMICOLON.header.removeStickyness();
						SEMICOLON.header.responsiveMenuClass();
					}
				} else {
					SEMICOLON.header.removeStickyness();
				}
				if( headerSizeCustom ){
					logo.find('img').css({ 'height': Number( mobileLogoH ) });
					SEMICOLON.header.menuItemsSpacing( '' );
				}
			}
		},

		menuItemsSpacing: function( spacing ) {

			let item	= primaryMenuMainItems;

			if( !$body.hasClass('side-header') && !$body.hasClass('overlay-menu') ) {
				if( primaryMenu.hasClass('menu-spacing-margin') ) {
					if( spacing == '' ) {
						item.css({ 'margin-top': '', 'margin-bottom': '' });
					} else {
						item.css({ 'margin-top': Number( spacing ), 'margin-bottom': Number( spacing ) });
					}
				} else {
					if( spacing == '' ) {
						item.css({ 'padding-top': '', 'padding-bottom': '' });
					} else {
						item.css({ 'padding-top': Number( spacing ), 'padding-bottom': Number( spacing ) });
					}
				}
			}

		},

		stickyPageMenu: function( pageMenuOffset ){
			if( $window.scrollTop() > pageMenuOffset ) {
				if( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) {
					$pagemenu.filter(':not(.dots-menu,.no-sticky)').addClass('sticky-page-menu');
					let headerHeight = $headerWrap.outerHeight();
					if( $header.length > 0 && !$header.hasClass('no-sticky') ) {
						$pagemenu.filter('.sticky-page-menu:not(.dots-menu,.no-sticky)').find( $pageMenuWrap ).css({ 'top': headerHeight +'px' });
					}
				} else if( $body.hasClass('device-sm') || $body.hasClass('device-xs') || $body.hasClass('device-md') ) {
					if( $pagemenu.attr('data-mobile-sticky') == 'true' ) {
						$pagemenu.filter(':not(.dots-menu,.no-sticky)').addClass('sticky-page-menu');
					}
				}
			} else {
				$pagemenu.removeClass('sticky-page-menu');
				$pagemenu.find( $pageMenuWrap ).css({ 'top': '' });
			}
		},

		removeStickyness: function(){
			if( $header.hasClass('sticky-header') ){
				$header.removeClass('sticky-header');
				$header.removeClass().addClass(oldHeaderClasses);
				$headerWrap.removeClass().addClass(oldHeaderWrapClasses);
				if( !$headerWrap.hasClass('force-not-dark') ) { $headerWrap.removeClass('not-dark'); }
				SEMICOLON.slider.swiperSliderMenu();
				SEMICOLON.slider.revolutionSliderMenu();
			}
			if( ( $body.hasClass('device-sm') || $body.hasClass('device-xs') || $body.hasClass('device-md') ) && ( typeof responsiveMenuClasses === 'undefined' ) ) {
				$header.removeClass().addClass(oldHeaderClasses);
				$headerWrap.removeClass().addClass(oldHeaderWrapClasses);
				if( !$headerWrap.hasClass('force-not-dark') ) { $headerWrap.removeClass('not-dark'); }
			}
		},

		sideHeader: function(){
			$("#header-trigger").off( 'click' ).on( 'click', function(){
				$('body.open-header').toggleClass("side-header-open");
				return false;
			});
		},

		sidePanel: function(){
			$(".side-panel-trigger").off( 'click' ).on( 'click', function(){
				$body.toggleClass("side-panel-open");
				if( $body.hasClass('device-touch') && $body.hasClass('side-push-panel') ) {
					$body.toggleClass("ohidden");
				}
				return false;
			});
		},

		onePageScroll: function( element ){
			let settings = {
				element: element,
				default: '.one-page-menu',
				file: 'plugins.onepage.js',
				error: 'plugins.onepage.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_onePageModule',
				pluginfn: () => typeof scwOnePageModulePlugin !== "undefined",
				trigger: 'pluginOnePageModuleReady',
				class: 'has-plugin-onepagemodule'
			};

			SEMICOLON.initialize.functions( settings );
		},

		logo: function(){
			let sLogo = defaultLogo.find('img'),
				rLogo = retinaLogo.find('img');
			if( ( $header.hasClass('dark') || $body.hasClass('dark') ) && !$headerWrap.hasClass('not-dark') ) {
				if( defaultDarkLogo && ( sLogo.attr('src') != defaultDarkLogo ) ){
					sLogo.attr('src', defaultDarkLogo);
				}

				if( retinaDarkLogo && ( rLogo.attr('src') != retinaDarkLogo ) ){
					rLogo.attr('src', retinaDarkLogo);
				}
			} else {
				if( defaultLogoImg && ( sLogo.attr('src') != defaultLogoImg ) ){
					sLogo.attr('src', defaultLogoImg);
				}

				if( retinaLogoImg && ( rLogo.attr('src') != retinaLogoImg ) ){
					rLogo.attr('src', retinaLogoImg);
				}
			}

			if( $header.hasClass('sticky-header') ) {
				if( defaultStickyLogo && ( sLogo.attr('src') != defaultStickyLogo ) ){
					sLogo.attr('src', defaultStickyLogo);
				}

				if( retinaStickyLogo && ( rLogo.attr('src') != retinaStickyLogo ) ){
					rLogo.attr('src', retinaStickyLogo);
				}
			}

			if( $body.hasClass('device-md') || $body.hasClass('device-sm') || $body.hasClass('device-xs') ) {
				if( defaultMobileLogo && ( sLogo.attr('src') != defaultMobileLogo ) ){
					sLogo.attr('src', defaultMobileLogo);
				}

				if( retinaMobileLogo && ( rLogo.attr('src') != retinaMobileLogo ) ){
					rLogo.attr('src', retinaMobileLogo);
				}
			}
		},

		stickyMenuClass: function(){
			let newClassesArray = '';

			if( stickyMenuClasses ) {
				newClassesArray = stickyMenuClasses.split(/ +/);
			}

			let noOfNewClasses = newClassesArray.length;

			if( noOfNewClasses > 0 ) {
				let i = 0;
				for( i=0; i<noOfNewClasses; i++ ) {
					if( newClassesArray[i] == 'not-dark' ) {
						$header.removeClass('dark');
						$headerWrap.filter(':not(.not-dark)').addClass('not-dark');
					} else if( newClassesArray[i] == 'dark' ) {
						$headerWrap.removeClass('not-dark force-not-dark');
						if( !$header.hasClass( newClassesArray[i] ) ) {
							$header.addClass( newClassesArray[i] );
						}
					} else if( !$header.hasClass( newClassesArray[i] ) ) {
						$header.addClass( newClassesArray[i] );
					}
				}
			}
		},

		responsiveMenuClass: function(){
			if( $body.hasClass('device-xl') || $body.hasClass('device-lg') ){
				return true;
			}

			let newClassesArray = '';

			if( responsiveMenuClasses ) {
				newClassesArray = responsiveMenuClasses.split(/ +/);
			}

			let noOfNewClasses = newClassesArray.length;

			if( noOfNewClasses > 0 ) {
				let i = 0;
				for( i=0; i<noOfNewClasses; i++ ) {
					if( newClassesArray[i] == 'not-dark' ) {
						$header.removeClass('dark');
						$headerWrap.addClass('not-dark');
					} else if( newClassesArray[i] == 'dark' ) {
						$headerWrap.removeClass('not-dark force-not-dark');
						if( !$header.hasClass( newClassesArray[i] ) ) {
							$header.addClass( newClassesArray[i] );
						}
					} else if( !$header.hasClass( newClassesArray[i] ) ) {
						$header.addClass( newClassesArray[i] );
					}
				}
			}

			SEMICOLON.header.logo();
		},

		topsearch: function(){
			$topSearch.parents('.header-row').addClass( 'top-search-parent' );
			let topSearchParent = $header.find('.top-search-parent');

			$("#top-search-trigger").off( 'click' ).on( 'click', function(e){
				clearTimeout( topSearchTimeOut );
				$body.toggleClass('top-search-open');
				$topCart.toggleClass('top-cart-open', false);
				if( $body.hasClass('device-md') || $body.hasClass('device-sm') || $body.hasClass('device-xs') ) {
					primaryMenu.filter( ':not(.mobile-menu-off-canvas)' ).find('.menu-container').slideUp(200);
					primaryMenu.filter( '.mobile-menu-off-canvas' ).find('.menu-container').toggleClass('d-block', false);
				}
				if( $body.hasClass('top-search-open') ) {
					topSearchParent.toggleClass('position-relative', true);
				} else {
					topSearchTimeOut = setTimeout( function(){
						topSearchParent.toggleClass('position-relative', false);
					}, 750);
				}
				$body.toggleClass("primary-menu-open", false);
				$pagemenu.toggleClass('page-menu-open', false);
				if ($body.hasClass('top-search-open')){
					$topSearch.find('input').focus();
				}
				e.stopPropagation();
				e.preventDefault();
			});
		},

		topcart: function(){
			if( $topCart.length < 1 ) {
				return true;
			}

			$("#top-cart-trigger").off( 'click' ).on( 'click', function(e){
				$pagemenu.toggleClass('page-menu-open', false);
				$topCart.toggleClass('top-cart-open');
				e.stopPropagation();
				e.preventDefault();
			});
		},

		miscFunctions: function(){
			let topSearchParent = $header.find('.top-search-parent');
			$(document).on('click', function(event) {
				if (!$(event.target).closest('.top-search-form').length) {
					$body.toggleClass('top-search-open', false);
					topSearchTimeOut = setTimeout( function(){
						topSearchParent.toggleClass('position-relative', false);
					}, 750);
				}
				if (!$(event.target).closest('#top-cart').length) {
					$topCart.toggleClass('top-cart-open', false);
				}
				if (!$(event.target).closest('#page-menu').length) { $pagemenu.toggleClass('page-menu-open', false); }
				if (!$(event.target).closest('#side-panel').length) { $body.toggleClass('side-panel-open', false); }
				if (!$(event.target).closest('.primary-menu.on-click').length) {
					primaryMenu.filter('.on-click').find('.menu-container').find('.d-block').removeClass('d-block');
					primaryMenu.filter('.on-click').find('.menu-item').removeClass('current');
				}
				if( primaryMenu.hasClass('mobile-menu-off-canvas') ) {
					if (!$(event.target).closest('.primary-menu.mobile-menu-off-canvas .menu-container').length) {
						primaryMenu.filter('.mobile-menu-off-canvas').find('.menu-container').toggleClass('d-block', false);
						$body.toggleClass("primary-menu-open", false);
					}
				}
				if (!$(event.target).closest('.top-links.on-click').length) {
					$('.top-links.on-click').find('.top-links-sub-menu,.top-links-section').removeClass('d-block');
				}
			});
		}

	};

	SEMICOLON.slider = {

		init: function() {

			SEMICOLON.slider.sliderDimensions();
			SEMICOLON.slider.sliderRun();
			SEMICOLON.slider.sliderParallax();
			SEMICOLON.slider.sliderElementsFade();

		},

		sliderDimensions: function(){

			let parallaxElHeight	= $sliderParallaxEl.outerHeight(),
				parallaxElWidth		= $sliderParallaxEl.outerWidth(),
				slInner				= $sliderParallaxEl.find('.slider-inner'),
				slSwiperW			= $slider.find('.swiper-wrapper'),
				slSwiperS			= $slider.find('.swiper-slide').first(),
				slFlexHeight		= $slider.hasClass('h-auto') || $slider.hasClass('min-vh-0');

			if( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) {
				setTimeout( function(){
					slInner.height( parallaxElHeight );
					if( slFlexHeight ) {
						parallaxElHeight = $sliderParallaxEl.find('.slider-inner').children().first().outerHeight();
						$sliderParallaxEl.height( parallaxElHeight );
						slInner.height( parallaxElHeight );
					}
				}, 500 );

				if( slFlexHeight ) {
					let slSwiperFC = slSwiperS.children().first();
					if( slSwiperFC.hasClass('container') || slSwiperFC.hasClass('container-fluid') ) {
						slSwiperFC = slSwiperFC.children().first();
					}
					if( slSwiperFC.outerHeight() > slSwiperW.outerHeight() ) {
						slSwiperW.css({ 'height': 'auto' });
					}
				}

				if( $body.hasClass('side-header') ) {
					slInner.width( parallaxElWidth );
				}

				if( !$body.hasClass('stretched') ) {
					parallaxElWidth = $wrapper.outerWidth();
					slInner.width( parallaxElWidth );
				}
			} else {
				slSwiperW.css({ 'height': '' });
				$sliderParallaxEl.css({ 'height': '' });
				slInner.css({ 'width': '', 'height': '' });
			}
		},

		sliderRun: function( element ){
			let settings = {
				element: element,
				default: '.swiper_wrapper',
				file: 'plugins.swiper.js',
				error: 'plugins.swiper.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_swiperInit',
				pluginfn: () => typeof Swiper !== "undefined",
				trigger: 'pluginSwiperReady',
				class: 'has-plugin-swiper'
			};

			SEMICOLON.initialize.functions( settings );
		},

		sliderParallaxOffset: function(){
			let sliderParallaxOffsetTop = 0,
				headerHeight = $header.outerHeight();
			if( $body.hasClass('side-header') || $header.next('.include-header').length > 0 ) { headerHeight = 0; }
			if( $pageTitle.length > 0 ) {
				sliderParallaxOffsetTop = $pageTitle.outerHeight() + headerHeight;
			} else {
				sliderParallaxOffsetTop = headerHeight;
			}

			if( $slider.next('#header').length > 0 ) { sliderParallaxOffsetTop = 0; }

			return sliderParallaxOffsetTop;
		},

		sliderParallaxSet: function( xPos, yPos, el ){
			if( el ) {
				el.style.transform = "translate3d(" + xPos + ", " + yPos + "px, 0)";
			}
		},

		sliderParallax: function(){
			if( $sliderParallaxEl.length < 1 ) {
				return true;
			}

			let parallaxOffsetTop = SEMICOLON.slider.sliderParallaxOffset(),
				parallaxElHeight = $sliderParallaxEl.outerHeight(),
				transform, transform2;

			xScrollPosition = window.pageXOffset;
			yScrollPosition = window.pageYOffset;

			if( ( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) && !SEMICOLON.isMobile.any() ) {
				if( ( parallaxElHeight + parallaxOffsetTop + 50 ) > yScrollPosition ){
					$sliderParallaxEl.addClass('slider-parallax-visible').removeClass('slider-parallax-invisible');
					if ( yScrollPosition > parallaxOffsetTop ) {
						if( $sliderParallaxEl.find('.slider-inner').length > 0 ) {

							transform = ((yScrollPosition-parallaxOffsetTop) * -.4 );
							transform2 = ((yScrollPosition-parallaxOffsetTop) * -.15 );

							SEMICOLON.slider.sliderParallaxSet( 0, transform, sliderParallaxElInner );
							SEMICOLON.slider.sliderParallaxSet( 0, transform2, sliderParallaxElCaption );
						} else {
							transform = ((yScrollPosition-parallaxOffsetTop) / 1.5 );
							transform2 = ((yScrollPosition-parallaxOffsetTop) / 7 );

							SEMICOLON.slider.sliderParallaxSet( 0, transform, sliderParallaxEl );
							SEMICOLON.slider.sliderParallaxSet( 0, transform2, sliderParallaxElCaption );
						}
					} else {
						if( $sliderParallaxEl.find('.slider-inner').length > 0 ) {
							SEMICOLON.slider.sliderParallaxSet( 0, 0, sliderParallaxElInner );
							SEMICOLON.slider.sliderParallaxSet( 0, 0, sliderParallaxElCaption );
						} else {
							SEMICOLON.slider.sliderParallaxSet( 0, 0, sliderParallaxEl );
							SEMICOLON.slider.sliderParallaxSet( 0, 0, sliderParallaxElCaption );
						}
					}
				} else {
					$sliderParallaxEl.addClass('slider-parallax-invisible').removeClass('slider-parallax-visible');
				}

				requestAnimationFrame(function(){
					SEMICOLON.slider.sliderParallax();
					SEMICOLON.slider.sliderElementsFade();
				});
			} else {
				if( $sliderParallaxEl.find('.slider-inner').length > 0 ) {
					SEMICOLON.slider.sliderParallaxSet( 0, 0, sliderParallaxElInner );
					SEMICOLON.slider.sliderParallaxSet( 0, 0, sliderParallaxElCaption );
				} else {
					SEMICOLON.slider.sliderParallaxSet( 0, 0, sliderParallaxEl );
					SEMICOLON.slider.sliderParallaxSet( 0, 0, sliderParallaxElCaption );
				}
				$sliderParallaxEl.addClass('slider-parallax-visible').removeClass('slider-parallax-invisible');
			}
		},

		sliderElementsFade: function(){
			if( $sliderParallaxEl.length < 1 ) {
				return true;
			}

			if( ( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) && !SEMICOLON.isMobile.any() ) {
				let parallaxOffsetTop = SEMICOLON.slider.sliderParallaxOffset(),
					parallaxElHeight = $sliderParallaxEl.outerHeight(),
					tHeaderOffset;

				if( $header.hasClass('transparent-header') || $body.hasClass('side-header') ) {
					tHeaderOffset = 100;
				} else {
					tHeaderOffset = 0;
				}
				$sliderParallaxEl.filter('.slider-parallax-visible').find('.slider-arrow-left,.slider-arrow-right,.slider-caption,.slider-element-fade').css({'opacity': 1 - ( ( ( yScrollPosition - tHeaderOffset ) * 1.85 ) / parallaxElHeight ) });
			} else {
				$sliderParallaxEl.find('.slider-arrow-left,.slider-arrow-right,.slider-caption,.slider-element-fade').css({'opacity': 1});
			}
		},

		swiperSliderMenu: function( onWinLoad ){
			onWinLoad = typeof onWinLoad !== 'undefined' ? onWinLoad : false;
			if( $body.hasClass('device-xl') || $body.hasClass('device-lg') || ( $header.hasClass('transparent-header-responsive') && !$body.hasClass('primary-menu-open') ) ) {
				let activeSlide = $slider.find('.swiper-slide.swiper-slide-active');
				SEMICOLON.slider.headerSchemeChanger(activeSlide, onWinLoad);
			}
		},

		revolutionSliderMenu: function( onWinLoad ){
			onWinLoad = typeof onWinLoad !== 'undefined' ? onWinLoad : false;
			if( $body.hasClass('device-xl') || $body.hasClass('device-lg') || ( $header.hasClass('transparent-header-responsive') && !$body.hasClass('primary-menu-open') ) ) {
				let activeSlide = $slider.find('.active-revslide');
				SEMICOLON.slider.headerSchemeChanger(activeSlide, onWinLoad);
			}
		},

		headerSchemeChanger: function( activeSlide, onWinLoad ){
			if( activeSlide.length > 0 ) {
				let darkExists = false,
					oldClassesArray, noOfOldClasses;
				if( activeSlide.hasClass('dark') ){
					if( oldHeaderClasses ) {
						oldClassesArray = oldHeaderClasses.split(/ +/);
					} else {
						oldClassesArray = '';
					}

					noOfOldClasses = oldClassesArray.length;

					if( noOfOldClasses > 0 ) {
						let i = 0;
						for( i=0; i<noOfOldClasses; i++ ) {
							if( oldClassesArray[i] == 'dark' && onWinLoad == true ) {
								darkExists = true;
								break;
							}
						}
					}
					$('#header.transparent-header:not(.sticky-header,.semi-transparent,.floating-header)').addClass('dark');
					if( !darkExists ) {
						$('#header.transparent-header.sticky-header,#header.transparent-header.semi-transparent.sticky-header,#header.transparent-header.floating-header.sticky-header').removeClass('dark');
					}
					$headerWrap.removeClass('not-dark');
				} else {
					if( $body.hasClass('dark') ) {
						activeSlide.addClass('not-dark');
						$('#header.transparent-header:not(.semi-transparent,.floating-header)').removeClass('dark');
						$('#header.transparent-header:not(.sticky-header,.semi-transparent,.floating-header)').find('#header-wrap').addClass('not-dark');
					} else {
						$('#header.transparent-header:not(.semi-transparent,.floating-header)').removeClass('dark');
						$headerWrap.removeClass('not-dark');
					}
				}
				if( $header.hasClass('sticky-header') ) {
					SEMICOLON.header.stickyMenuClass();
				}
				SEMICOLON.header.logo();
			}
		}

	};

	SEMICOLON.portfolio = {

		init: function(){

			SEMICOLON.portfolio.revealDesc();
			SEMICOLON.portfolio.ajaxload();

		},

		revealDesc: function(){
			let $portfolioReveal = $('.portfolio-reveal');

			if( $portfolioReveal < 1 ) {
				return true;
			}

			$portfolioReveal.each( function(){
				let element			= $(this),
					elementItems	= element.find('.portfolio-item');
				elementItems.each( function(){
					let element			= $(this).find('.portfolio-desc'),
						elementHeight	= element.outerHeight();
					element.css({ 'margin-top': '-'+elementHeight+'px' });
				});
			});
		},

		ajaxload: function(){
			let settings = {
				default: '.portfolio-ajax',
				file: 'plugins.ajaxportfolio.js',
				error: 'plugins.ajaxportfolio.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_portfolioAjaxloadInit',
				pluginfn: () => typeof scwAjaxPortfolioPlugin !== "undefined",
				trigger: 'pluginAjaxPortfolioReady',
				class: 'has-plugin-ajaxportfolio'
			};

			SEMICOLON.initialize.functions( settings );
		}

	};

	SEMICOLON.widget = {

		init: function(){

			SEMICOLON.widget.animations();
			SEMICOLON.widget.hoverAnimation();
			SEMICOLON.widget.youtubeBgVideo();
			SEMICOLON.widget.tabs();
			SEMICOLON.widget.toggles();
			SEMICOLON.widget.accordions();
			SEMICOLON.widget.counter();
			SEMICOLON.widget.countdown();
			SEMICOLON.widget.gmap();
			SEMICOLON.widget.roundedSkill();
			SEMICOLON.widget.progress();
			SEMICOLON.widget.twitterFeed();
			SEMICOLON.widget.flickrFeed();
			SEMICOLON.widget.instagramPhotos();
			SEMICOLON.widget.dribbbleShots();
			SEMICOLON.widget.navTree();
			SEMICOLON.widget.textRotator();
			SEMICOLON.widget.carousel();
			SEMICOLON.widget.linkScroll();
			SEMICOLON.widget.ajaxForm();
			SEMICOLON.widget.subscription();
			SEMICOLON.widget.shapeDivider();
			SEMICOLON.widget.stickySidebar();
			SEMICOLON.widget.cookieNotify();
			SEMICOLON.widget.cartQuantity();
			SEMICOLON.widget.readmore();
			SEMICOLON.widget.pricingSwitcher();
			SEMICOLON.widget.extras();

		},

		parallax: function( element ){
			let settings = {
				element: element,
				default: '.parallax,.page-title-parallax,.portfolio-parallax .portfolio-image',
				file: 'plugins.parallax.js',
				error: 'plugins.parallax.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_parallaxInit',
				pluginfn: () => typeof skrollr !== "undefined",
				trigger: 'pluginParallaxReady',
				class: 'has-plugin-parallax'
			};

			SEMICOLON.initialize.functions( settings );
		},

		animations: function( element ){
			let settings = {
				element: element,
				default: '[data-animate]',
				file: 'plugins.animations.js',
				error: 'plugins.animations.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_animationsInit',
				pluginfn: () => typeof scwAnimationsPlugin !== "undefined",
				trigger: 'pluginAnimationsReady',
				class: 'has-plugin-animations'
			};

			SEMICOLON.initialize.functions( settings );
		},

		hoverAnimation: function( element ){
			let settings = {
				element: element,
				default: '[data-hover-animate]',
				file: 'plugins.hoveranimation.js',
				error: 'plugins.hoveranimation.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_hoverAnimationInit',
				pluginfn: () => typeof scwHoverAnimationPlugin !== "undefined",
				trigger: 'pluginHoverAnimationReady',
				class: 'has-plugin-hoveranimation'
			};

			SEMICOLON.initialize.functions( settings );
		},

		gridInit: function( element ){
			let settings = {
				element: element,
				default: '.grid-container',
				file: 'plugins.isotope.js',
				error: 'plugins.isotope.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_gridContainerInit',
				pluginfn: () => $().isotope,
				trigger: 'pluginIsotopeReady',
				class: 'has-plugin-isotope'
			};

			SEMICOLON.initialize.functions( settings );
		},

		filterInit: function( element ){
			let settings = {
				element: element,
				default: '.grid-filter,.custom-filter',
				file: 'plugins.gridfilter.js',
				error: 'plugins.gridfilter.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_gridFilterInit',
				pluginfn: () => $().isotope && typeof scwGridFilterPlugin !== "undefined",
				trigger: 'pluginGridFilterReady',
				class: 'has-plugin-isotope-filter'
			};

			SEMICOLON.initialize.functions( settings );
		},

		loadFlexSlider: function( element ){
			let settings = {
				element: element,
				default: '.fslider',
				file: 'plugins.flexslider.js',
				error: 'plugins.flexslider.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_flexSliderInit',
				pluginfn: () => $().flexslider,
				trigger: 'pluginFlexSliderReady',
				class: 'has-plugin-flexslider'
			};

			SEMICOLON.initialize.functions( settings );
		},

		html5Video: function( element ){
			let settings = {
				element: element,
				default: '.video-wrap:has(video)',
				file: 'plugins.html5video.js',
				error: 'plugins.html5video.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_html5VideoInit',
				pluginfn: () => typeof scwHtml5VideoPlugin !== "undefined",
				trigger: 'pluginHtml5VideoReady',
				class: 'has-plugin-html5video'
			};

			SEMICOLON.initialize.functions( settings );
		},

		youtubeBgVideo: function( element ){
			let settings = {
				element: element,
				default: '.yt-bg-player',
				file: 'plugins.youtube.js',
				error: 'plugins.youtube.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_youtubeBgVideoInit',
				pluginfn: () => $().YTPlayer,
				trigger: 'pluginYoutubeBgVideoReady',
				class: 'has-plugin-youtubebg'
			};

			SEMICOLON.initialize.functions( settings );
		},

		tabs: function( element ){
			let settings = {
				element: element,
				default: '.tabs,[data-plugin="tabs"]',
				file: 'plugins.tabs.js',
				error: 'plugins.tabs.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_tabsInit',
				pluginfn: () => $().tabs,
				trigger: 'pluginTabsReady',
				class: 'has-plugin-tabs'
			};

			SEMICOLON.initialize.functions( settings );
		},

		toggles: function( element ){
			let settings = {
				element: element,
				default: '.toggle',
				file: 'plugins.toggles.js',
				error: 'plugins.toggles.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_togglesInit',
				pluginfn: () => typeof scwTogglesPlugin !== "undefined",
				trigger: 'pluginTogglesReady',
				class: 'has-plugin-toggles'
			};

			SEMICOLON.initialize.functions( settings );
		},

		accordions: function( element ){
			let settings = {
				element: element,
				default: '.accordion',
				file: 'plugins.accordions.js',
				error: 'plugins.accordions.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_accordionsInit',
				pluginfn: () => typeof scwAccordionsPlugin !== "undefined",
				trigger: 'pluginAccordionsReady',
				class: 'has-plugin-accordions'
			};

			SEMICOLON.initialize.functions( settings );
		},

		counter: function( element ){
			let settings = {
				element: element,
				default: '.counter',
				file: 'plugins.counter.js',
				error: 'plugins.counter.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_counterInit',
				pluginfn: () => $().countTo,
				trigger: 'pluginCounterReady',
				class: 'has-plugin-counter'
			};

			SEMICOLON.initialize.functions( settings );
		},

		countdown: function( element ){
			let momentSettings = {
				element: element,
				default: '.countdown',
				file: 'components/moment.js',
				error: 'components/moment.js: Plugin could not be loaded',
				execfn: false,
				pluginfn: () => typeof moment !== "undefined",
				trigger: 'pluginMomentReady',
				class: 'has-plugin-moment'
			};

			let settings = {
				element: element,
				default: '.countdown',
				file: 'plugins.countdown.js',
				error: 'plugins.countdown.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_countdownInit',
				pluginfn: () => $().countdown,
				trigger: 'pluginCountdownReady',
				class: 'has-plugin-countdown'
			};

			SEMICOLON.initialize.functions( momentSettings );
			SEMICOLON.initialize.functions( settings );
		},

		gmap: function( element ){
			let googleSettings = {
				element: element,
				default: '.gmap',
				file: 'https://maps.google.com/maps/api/js?key=' + googleMapsAPI,
				error: 'Google Maps API could not be loaded',
				execfn: false,
				pluginfn: () => typeof google !== "undefined",
				hiddendisable: true,
				class: 'has-plugin-gmapapi'
			};

			let settings = {
				element: element,
				default: '.gmap',
				file: 'plugins.gmap.js',
				error: 'plugins.gmap.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_gmapInit',
				pluginfn: () => typeof google !== "undefined" && $().gMap,
				hiddendisable: true,
				trigger: 'pluginGmapReady',
				class: 'has-plugin-gmap'
			};

			SEMICOLON.initialize.functions( googleSettings );
			SEMICOLON.initialize.functions( settings );
		},

		roundedSkill: function( element ){
			let settings = {
				element: element,
				default: '.rounded-skill',
				file: 'plugins.piechart.js',
				error: 'plugins.piechart.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_roundedSkillInit',
				pluginfn: () => $().easyPieChart,
				trigger: 'pluginRoundedSkillReady',
				class: 'has-plugin-piechart'
			};

			SEMICOLON.initialize.functions( settings );
		},

		progress: function( element ){
			let settings = {
				element: element,
				default: '.progress',
				file: 'plugins.progress.js',
				error: 'plugins.progress.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_progressInit',
				pluginfn: () => typeof scwProgressPlugin !== "undefined",
				trigger: 'pluginProgressReady',
				class: 'has-plugin-progress'
			};

			SEMICOLON.initialize.functions( settings );
		},

		twitterFeed: function( element ){
			let settings = {
				element: element,
				default: '.twitter-feed',
				file: 'plugins.twitter.js',
				error: 'plugins.twitter.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_twitterFeedInit',
				pluginfn: () => typeof sm_format_twitter !== "undefined" && typeof sm_format_twitter3 !== "undefined",
				trigger: 'pluginTwitterFeedReady',
				class: 'has-plugin-twitter'
			};

			SEMICOLON.initialize.functions( settings );
		},

		flickrFeed: function( element ){
			let settings = {
				element: element,
				default: '.flickr-feed',
				file: 'plugins.flickrfeed.js',
				error: 'plugins.flickrfeed.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_flickrFeedInit',
				pluginfn: () => $().jflickrfeed,
				trigger: 'pluginFlickrFeedReady',
				class: 'has-plugin-flickr'
			};

			SEMICOLON.initialize.functions( settings );
		},

		instagramPhotos: function( element ){
			let settings = {
				element: element,
				default: '.instagram-photos',
				file: 'plugins.instagram.js',
				error: 'plugins.instagram.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_instagramPhotosInit',
				pluginfn: () => typeof scwInstagramPlugin !== "undefined",
				trigger: 'pluginInstagramReady',
				class: 'has-plugin-instagram'
			};

			SEMICOLON.initialize.functions( settings );
		},

		dribbbleShots: function( element ){
			let settings = {
				element: element,
				default: '.dribbble-shots',
				file: 'plugins.dribbble.js',
				error: 'plugins.dribbble.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_dribbbleShotsInit',
				pluginfn: () => $.jribbble,
				trigger: 'pluginDribbbleReady',
				class: 'has-plugin-dribbble'
			};

			let imagesLoadedSettings = {
				element: element,
				default: '.dribbble-shots',
				file: 'plugins.imagesloaded.js',
				error: 'plugins.imagesloaded.js: Plugin could not be loaded',
				pluginfn: () => $().imagesLoaded,
				trigger: 'pluginImagesLoadedReady',
				class: 'has-plugin-imagesloaded'
			};

			SEMICOLON.initialize.functions( settings );
			SEMICOLON.initialize.functions( imagesLoadedSettings );
		},

		navTree: function( element ){
			let settings = {
				element: element,
				default: '.nav-tree',
				file: 'plugins.navtree.js',
				error: 'plugins.navtree.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_navtreeInit',
				pluginfn: () => typeof scwNavTreePlugin !== "undefined",
				trigger: 'pluginNavTreeReady',
				class: 'has-plugin-navtree'
			};

			SEMICOLON.initialize.functions( settings );
		},

		carousel: function( element ){
			let settings = {
				element: element,
				default: '.carousel-widget',
				file: 'plugins.carousel.js',
				error: 'plugins.carousel.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_carouselInit',
				pluginfn: () => $().owlCarousel,
				trigger: 'pluginCarouselReady',
				class: 'has-plugin-carousel'
			};

			SEMICOLON.initialize.functions( settings );
		},

		masonryThumbs: function( element ){
			let settings = {
				element: element,
				default: '.masonry-thumbs',
				file: 'plugins.masonrythumbs.js',
				error: 'plugins.masonrythumbs.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_masonryThumbsInit',
				pluginfn: () => $().isotope && typeof scwMasonryThumbsPlugin !== "undefined",
				trigger: 'pluginMasonryThumbsReady',
				class: 'has-plugin-masonrythumbs'
			};

			SEMICOLON.initialize.functions( settings );
		},

		notifications: function( element ){
			let settings = {
				element: element,
				default: false,
				file: 'plugins.notify.js',
				error: 'plugins.notify.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_notificationInit',
				pluginfn: () => typeof scwNotificationPlugin !== "undefined",
				trigger: 'pluginNotifyReady',
				class: 'has-plugin-toast'
			};

			SEMICOLON.initialize.functions( settings );
		},

		textRotator: function( element ){
			let settings = {
				element: element,
				default: '.text-rotater',
				file: 'plugins.textrotator.js',
				error: 'plugins.textrotator.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_textRotatorInit',
				pluginfn: () => $().Morphext,
				trigger: 'pluginTextRotatorReady',
				class: 'has-plugin-textrotator'
			};

			SEMICOLON.initialize.functions( settings );
		},

		linkScroll: function( element ){
			let settings = {
				element: element,
				default: 'a[data-scrollto]',
				file: 'plugins.linkscroll.js',
				error: 'plugins.linkscroll.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_linkScrollInit',
				pluginfn: () => typeof scwLinkScrollPlugin !== "undefined",
				trigger: 'pluginLinkScrollReady',
				class: 'has-plugin-linkscroll'
			};

			SEMICOLON.initialize.functions( settings );
		},

		ajaxForm: function( element ){
			let formSettings = {
				element: element,
				default: '.form-widget',
				file: 'plugins.form.js',
				error: 'plugins.form.js: Plugin could not be loaded',
				execfn: false,
				pluginfn: () => $().validate && $().ajaxSubmit,
				class: 'has-plugin-form'
			};

			let settings = {
				element: element,
				default: '.form-widget',
				file: 'plugins.ajaxform.js',
				error: 'plugins.ajaxform.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_ajaxFormInit',
				pluginfn: () => typeof scwAjaxFormPlugin !== "undefined",
				trigger: 'pluginAjaxFormReady',
				class: 'has-plugin-ajaxform'
			};

			SEMICOLON.initialize.functions( formSettings );
			SEMICOLON.initialize.functions( settings );
		},

		subscription: function( element ){
			let formSettings = {
				element: element,
				default: '.subscribe-widget',
				file: 'plugins.form.js',
				error: 'plugins.form.js: Plugin could not be loaded',
				execfn: false,
				pluginfn: () => $().validate && $().ajaxSubmit,
				class: 'has-plugin-form'
			};

			let settings = {
				element: element,
				default: '.subscribe-widget',
				file: 'plugins.subscribe.js',
				error: 'plugins.subscribe.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_subscribeFormInit',
				pluginfn: () => typeof scwSubscribeFormPlugin !== "undefined",
				trigger: 'pluginSubscribeFormReady',
				class: 'has-plugin-subscribeform'
			};

			SEMICOLON.initialize.functions( formSettings );
			SEMICOLON.initialize.functions( settings );
		},

		shapeDivider: function( element ){
			let settings = {
				element: element,
				default: '.shape-divider',
				file: 'plugins.shapedivider.js',
				error: 'plugins.shapedivider.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_shapeDividerInit',
				pluginfn: () => typeof scwShapeDividerPlugin !== "undefined",
				trigger: 'pluginShapeDividerReady',
				class: 'has-plugin-shapedivider'
			};

			SEMICOLON.initialize.functions( settings );
		},

		ticker: function( element ){
			let settings = {
				element: element,
				default: '.scw-ticker',
				file: 'plugins.ticker.js',
				error: 'plugins.ticker.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_tickerInit',
				pluginfn: () => typeof scwTickerPlugin !== "undefined",
				trigger: 'pluginTickerReady',
				class: 'has-plugin-ticker'
			};

			SEMICOLON.initialize.functions( settings );
		},

		stickySidebar: function( element ){
			let settings = {
				element: element,
				default: '.sticky-sidebar-wrap',
				file: 'plugins.stickysidebar.js',
				error: 'plugins.stickysidebar.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_stickySidebarInit',
				pluginfn: () => $().scwStickySidebar,
				trigger: 'pluginStickySidebarReady',
				class: 'has-plugin-stickysidebar'
			};

			SEMICOLON.initialize.functions( settings );
		},

		cookieNotify: function( element ){
			let settings = {
				element: element,
				default: '.gdpr-settings,[data-cookies]',
				file: 'plugins.cookie.js',
				error: 'plugins.cookie.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_cookieInit',
				pluginfn: () => typeof Cookies !== "undefined",
				trigger: 'pluginCookieReady',
				class: 'has-plugin-cookie'
			};

			SEMICOLON.initialize.functions( settings );
		},

		cartQuantity: function(){
			let settings = {
				default: '.qty',
				file: 'plugins.quantity.js',
				error: 'plugins.quantity.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_quantityInit',
				pluginfn: () => typeof scwQuantityPlugin !== "undefined",
				trigger: 'pluginQuantityReady',
				class: 'has-plugin-quantity'
			};

			SEMICOLON.initialize.functions( settings );
		},

		readmore: function(){
			let settings = {
				default: '[data-readmore]',
				file: 'plugins.readmore.js',
				error: 'plugins.readmore.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_readmoreInit',
				pluginfn: () => typeof scwReadMorePlugin !== "undefined",
				trigger: 'pluginReadMoreReady',
				class: 'has-plugin-readmore'
			};

			SEMICOLON.initialize.functions( settings );
		},

		pricingSwitcher: function(){
			let settings = {
				default: '.pts-switcher',
				file: 'plugins.pricingswitcher.js',
				error: 'plugins.pricingswitcher.js: Plugin could not be loaded',
				execfn: 'SEMICOLON_pricingSwitcherInit',
				pluginfn: () => typeof scwPricingSwitcherPlugin !== "undefined",
				trigger: 'pluginPricingSwitcherReady',
				class: 'has-plugin-pricing-switcher'
			};

			SEMICOLON.initialize.functions( settings );
		},

		extras: function(){
			let btsCheckIntevral = setInterval( function(){
				if( 'pluginBootstrapReady' in scwEvents ) {
					if( $().tooltip ) {
						$('[data-bs-toggle="tooltip"]').tooltip({container: 'body'});
					} else {
						console.log('extras: Bootstrap Tooltip not defined.');
					}

					if( $().popover ) {
						$('[data-bs-toggle="popover"]').popover({container: 'body'});
					} else {
						console.log('extras: Bootstrap Popover not defined.');
					}

					clearInterval( btsCheckIntevral );
				}
			}, 1000 );

			$('.style-msg').on( 'click', '.close', function(e){
				$( this ).parents( '.style-msg' ).slideUp();
				e.preventDefault();
			});

			$('#page-menu-trigger').off( 'click' ).on( 'click', function() {
				$body.toggleClass('top-search-open', false);
				$pagemenu.toggleClass("page-menu-open");
				return false;
			});

			$pagemenu.find('nav').off( 'click' ).on( 'click', function(e){
				$body.toggleClass('top-search-open', false);
				$topCart.toggleClass('top-cart-open', false);
			});

			if( SEMICOLON.isMobile.any() ){
				$body.addClass('device-touch');
			}

			if( $body.hasClass( 'adaptive-color-scheme' ) ) {

				let adaptiveEl 		= $('[data-adaptive-light-class], [data-adaptive-dark-class]'),
					adaptLightClass	= adaptiveEl.attr( 'data-adaptive-light-class' ),
					adaptDarkClass	= adaptiveEl.attr( 'data-adaptive-dark-class' );

				let adaptClasses = function( dark ) {
					if( dark ) {
						$body.toggleClass( 'dark', true );
						adaptiveEl.removeClass( adaptLightClass ).addClass( adaptDarkClass );
					} else {
						$body.toggleClass( 'dark', false );
						adaptiveEl.removeClass( adaptDarkClass ).addClass( adaptLightClass );
					}
					SEMICOLON.header.logo();
				};

				if( window.matchMedia ) {
					adaptClasses( window.matchMedia('(prefers-color-scheme: dark)').matches );

					window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
						adaptClasses( e.matches );
					});
				}
			}

			$body.off( 'click' ).on( 'click', 'a[href*="#"]', function() {
				$window.on('beforeunload', function() {
					$window.scrollTop(0);
				});
			});

			let linkElement = location.hash;
			if( $(linkElement).length > 0 && $('.one-page-menu').find('[data-href="'+linkElement+'"]').length > 0 ) {
				$window.scrollTop(0);
			}
		}

	};

	SEMICOLON.isMobile = {
		Android: function() {
			return navigator.userAgent.match(/Android/i);
		},
		BlackBerry: function() {
			return navigator.userAgent.match(/BlackBerry/i);
		},
		iOS: function() {
			return navigator.userAgent.match(/iPhone|iPad|iPod/i);
		},
		Opera: function() {
			return navigator.userAgent.match(/Opera Mini/i);
		},
		Windows: function() {
			return navigator.userAgent.match(/IEMobile/i);
		},
		any: function() {
			return (SEMICOLON.isMobile.Android() || SEMICOLON.isMobile.BlackBerry() || SEMICOLON.isMobile.iOS() || SEMICOLON.isMobile.Opera() || SEMICOLON.isMobile.Windows());
		}
	};

	// Add your Custom JS Codes here
	SEMICOLON.customization = {

		onReady: function(){

			// Add JS Codes here to Run on Document Ready

		},

		onLoad: function(){

			// Add JS Codes here to Run on Window Load

		},

		onResize: function(){

			// Add JS Codes here to Run on Window Resize

		}

	}

	SEMICOLON.documentOnResize = {

		init: function(){

			SEMICOLON.header.menufunctions();
			SEMICOLON.header.fullWidthMenu();
			SEMICOLON.header.stickyMenu();
			SEMICOLON.header.logo();
			SEMICOLON.initialize.dataResponsiveHeights();
			SEMICOLON.initialize.stickFooterOnSmall();
			SEMICOLON.slider.sliderDimensions();
			SEMICOLON.slider.sliderParallax();
			SEMICOLON.widget.html5Video();
			SEMICOLON.widget.masonryThumbs();
			SEMICOLON.initialize.dataResponsiveClasses();
			SEMICOLON.customization.onResize();

			windowWidth = $window.width();

			$(window).trigger( 'scwWindowResize' );

		}

	};

	SEMICOLON.documentOnReady = {

		init: function(){
			SEMICOLON.initialize.init();
			SEMICOLON.header.init();
			if( $slider.length > 0 || $sliderElement.length > 0 ) { SEMICOLON.slider.init(); }
			if( $portfolio.length > 0 ) { SEMICOLON.portfolio.init(); }
			SEMICOLON.widget.init();
			SEMICOLON.documentOnReady.windowscroll();
			SEMICOLON.customization.onReady();
		},

		windowscroll: function(){

			if( $header.length > 0 ) {
				headerOffset = $header.offset().top;
				$headerWrap.addClass('position-absolute');
				headerWrapOffset = $headerWrap.offset().top;
				$headerWrap.removeClass('position-absolute');
			}

			let headerDefinedOffset = $header.attr('data-sticky-offset');
			if( typeof headerDefinedOffset !== 'undefined' ) {
				if( headerDefinedOffset == 'full' ) {
					headerWrapOffset = $window.height();
					let headerOffsetNegative = $header.attr('data-sticky-offset-negative');
					if( typeof headerOffsetNegative !== 'undefined' ) {
						headerWrapOffset = headerWrapOffset - headerOffsetNegative - 1;
					}
				} else {
					headerWrapOffset = Number(headerDefinedOffset);
				}
			} else {
				if( headerWrapOffset === 'undefined' ) {
					headerWrapOffset = headerOffset;
				}
			}

			let pageMenuWrap	= $pagemenu.find('#page-menu-wrap'),
				offset			= $headerWrap.outerHeight(),
				head			= document.head || document.getElementsByTagName('head')[0],
				style			= document.createElement('style'),
				css;

			if( $pagemenu.length > 0 ) {
				$pageMenuClone.css({ 'height': $pagemenu.find('#page-menu-wrap').outerHeight() });
				setTimeout( function(){
					if( $header.length > 0 && !$header.hasClass('no-sticky') ) {
						if( $body.hasClass('device-xl') || $body.hasClass('device-lg') || mobileSticky == 'true' ) {
							pageMenuOffset = $pagemenu.offset().top - $headerWrap.outerHeight();
							head.appendChild(style);
							css = '#page-menu.sticky-page-menu:not(.dots-menu) #page-menu-wrap { top: '+ offset +'px; }';

							style.type = 'text/css';
							style.appendChild(document.createTextNode(css));
						} else {
							pageMenuOffset = $pagemenu.offset().top;
						}
					} else {
						pageMenuOffset = $pagemenu.offset().top;
					}
				}, 1000);
			}

			SEMICOLON.header.stickyMenu( headerWrapOffset );
			SEMICOLON.header.stickyPageMenu( pageMenuOffset );

			window.addEventListener( 'scroll', function(){

				SEMICOLON.initialize.goToTopScroll();
				$('body.open-header.close-header-on-scroll').removeClass("side-header-open");
				SEMICOLON.header.stickyMenu( headerWrapOffset );
				SEMICOLON.header.stickyPageMenu( pageMenuOffset );
				SEMICOLON.header.logo();

			}, { passive: true });

			window.addEventListener( 'DOMContentLoaded', onScrollSliderParallax, false );

			$window.scrollEnd( function(){
				let headerHeight = $headerWrap.outerHeight();
				if( $pagemenu.length > 0 && $header.length > 0 && !$header.hasClass('no-sticky') ) {
					if( $body.hasClass('device-xl') || $body.hasClass('device-lg') ) {
						$pagemenu.filter('.sticky-page-menu:not(.dots-menu,.no-sticky)').find( $pageMenuWrap ).css({ 'top': headerHeight +'px' });
					}
				}
			}, 500 );

		}

	};

	SEMICOLON.documentOnLoad = {

		init: function(){
			SEMICOLON.slider.swiperSliderMenu(true);
			SEMICOLON.slider.revolutionSliderMenu(true);
			SEMICOLON.initialize.stickFooterOnSmall();
			SEMICOLON.widget.gridInit();
			let isoCheckInt = setInterval( function(){
				if( 'pluginIsotopeReady' in scwEvents ) {
					SEMICOLON.widget.filterInit();
					SEMICOLON.widget.masonryThumbs();
					clearInterval( isoCheckInt );
				}
			}, 1000 );
			SEMICOLON.widget.parallax();
			SEMICOLON.widget.loadFlexSlider();
			SEMICOLON.widget.html5Video();
			SEMICOLON.widget.ticker();
			SEMICOLON.header.responsiveMenuClass();
			SEMICOLON.initialize.modal();
			SEMICOLON.customization.onLoad();

		}

	};

	let $window = $(window),
		windowScrT,
		$body = $('body'),
		$wrapper = $('#wrapper'),
		$header = $('#header'),
		$headerWrap = $('#header-wrap'),
		$headerInc = $('.include-header'),
		defLogoH	= $header.attr('data-logo-height') || 100,
		stickyLogoH = $header.attr('data-sticky-logo-height') || 60,
		mobileSticky = $header.attr('data-mobile-sticky') || 'false',
		mobileLogoH = $header.attr('data-mobile-logo-height') || Number( defLogoH ),
		mobileStickyLogoH = $header.attr('data-mobile-sticky-logo-height') || Number( stickyLogoH ),
		defMenuP	= $header.attr('data-menu-padding') || 39,
		stickyMenuP = $header.attr('data-sticky-menu-padding') || 19,
		headerSizeCustom = !$header.hasClass('header-size-lg') && !$header.hasClass('header-size-md') && !$header.hasClass('header-size-sm') && !$header.hasClass('header-size-custom'),
		stickyShrink = $header.attr('data-sticky-shrink') || 'true',
		stickyShrinkOffset = $header.attr('data-sticky-shrink-offset') || 300,
		primaryMenu = $('.primary-menu'),
		primaryMenuMainItems = primaryMenu.find('.menu-container:not(mobile-primary-menu):not(.custom-spacing)').children('.menu-item').children('.menu-link'),
		$headerWrapClone = '',
		initialHeaderWrapHeight = $headerWrap.outerHeight(),
		$headerRow = $headerWrap.find('.header-row:eq(0)'),
		$content = $('#content'),
		$footer = $('#footer'),
		windowWidth = $window.width(),
		oldHeaderClasses = $header.attr('class'),
		oldHeaderWrapClasses = $headerWrap.attr('class'),
		stickyMenuClasses = $header.attr('data-sticky-class'),
		responsiveMenuClasses = $header.attr('data-responsive-class'),
		logo = $('#logo'),
		defaultLogo = logo.find('.standard-logo'),
		defaultLogoWidth = defaultLogo.find('img').outerWidth(),
		retinaLogo = logo.find('.retina-logo'),
		defaultLogoImg = defaultLogo.find('img').attr('src'),
		retinaLogoImg = retinaLogo.find('img').attr('src'),
		defaultDarkLogo = defaultLogo.attr('data-dark-logo'),
		retinaDarkLogo = retinaLogo.attr('data-dark-logo'),
		defaultStickyLogo = defaultLogo.attr('data-sticky-logo'),
		retinaStickyLogo = retinaLogo.attr('data-sticky-logo'),
		defaultMobileLogo = defaultLogo.attr('data-mobile-logo'),
		retinaMobileLogo = retinaLogo.attr('data-mobile-logo'),
		topSearchTimeOut,
		$pagemenu = $('#page-menu'),
		$pageMenuClone = '',
		$pageMenuWrap = $pagemenu.find('#page-menu-wrap'),
		$onePageMenuEl = $('.one-page-menu'),
		$portfolio = $('.portfolio'),
		$shop = $('.shop'),
		$slider = $('#slider'),
		$sliderParallaxEl = $('.slider-parallax'),
		$sliderElement = $('.slider-element'),
		swiperSlider = '',
		$pageTitle = $('#page-title'),
		$topSearch = $('.top-search-form'),
		$topCart = $('#top-cart'),
		$topSocialEl = $('#top-social').find('li'),
		$goToTopEl = $('#gotoTop'),
		googleMapsAPI = 'YOUR-API-KEY',
		xScrollPosition,
		yScrollPosition,
		sliderParallaxEl = document.querySelector('.slider-parallax'),
		sliderParallaxElCaption = document.querySelector('.slider-parallax .slider-caption'),
		sliderParallaxElInner = document.querySelector('.slider-inner'),
		initHeaderHeight,
		headerOffset = 0,
		headerWrapOffset = 0,
		pageMenuOffset = 0,
		resizeTimer;

	$(document).ready( SEMICOLON.documentOnReady.init );

	$window.on( 'load', SEMICOLON.documentOnLoad.init );

	$window.on( 'resize', function() {
		let thisWindow = $(this);
		clearTimeout(resizeTimer);
		resizeTimer = setTimeout(function() {
			if ( thisWindow.width() !== windowWidth ) {
				SEMICOLON.documentOnResize.init();
			}
		}, 250);
	});

})(jQuery);