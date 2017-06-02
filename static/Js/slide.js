/**
 * Created by c0hb1rd on 2017/3/10.
 */
jQuery(document).ready(function($){
    //open popup
    var yes = $("#yes");
    var no = $("#no");
    var cdPopup = $('.cd-popup');

    no.on("click", function() {
        cdPopup.removeClass('is-visible');
    });

    $('.ctrl-delete').on('click', function(event){

        yes.on("click", function() {
            location.href = event.target.href;

            return false;
        });
        cdPopup.addClass('is-visible');

        return false;
    });

    //close popup
    cdPopup.on('click', function(event){
        if( $(event.target).is('.cd-popup-close') || $(event.target).is('.cd-popup') ) {
            event.preventDefault();
            $(this).removeClass('is-visible');
        }
    });
    //close popup when clicking the esc keyboard button
    $(document).keyup(function(event){
        if(event.which=='27'){
            $('.cd-popup').removeClass('is-visible');
        }
    });
});
