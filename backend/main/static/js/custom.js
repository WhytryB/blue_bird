(function($){
    $(document).ready(function(){

        $(".side-nav .has-sub > a").click(function(event){
            event.preventDefault();
            $(this).toggleClass("menu-open");
            $(this).next(".submenu").slideToggle();
        });

        $(".toggle-bar").click(function(event){
            event.preventDefault();
            $(".wrapper").toggleClass("sidebar-off");
        });

      });
}(jQuery))