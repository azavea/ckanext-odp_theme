// Based on http://www.bootply.com/62742

$('#vizcarousel').carousel({
    interval: 0 // remove interval for manual sliding
});

// when the carousel slides, load the ajax content
$('#vizcarousel').on('slid.bs.carousel', function (e) {
    // get index of currently active item
    var idx = $('#vizcarousel .item.active').index();
    var url = $('.item.active').data('url');
    $('.item').removeClass('in');
    // ajax load from data-url
        $('.item.active').load(url,function(result){
            $(this).addClass('in');
        });
});

$('.carousel-inner').hover(
    function (){
        $('#vizcarousel .vizcarousel-desc').addClass('active');
    },
    function () {
        $('#vizcarousel .vizcarousel-desc').removeClass('active');
    }
);

if ($('#vizcarousel').length) {
    $('[data-slide-number=0]').load($('[data-slide-number=0]').data('url'),function(result){
        $('#vizcarousel').carousel(0);
    });
}