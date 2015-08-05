/*global $:false, jQuery:false */

(function() {
    'use strict';

    
    function getURLParameter(name) {
        return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,''])[1].replace(/\+/g, '%20'))||null;
    }
    

    jQuery.fn.extend({
        disable: function(state) {
            return this.each(function() {
                var $this = $(this);
                $this.toggleClass('disabled', state);
            });
        }
    });

    String.prototype.toNum = function(){
        return parseInt(this, 10);
    };


    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
    }
});

})();

