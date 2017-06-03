/**
 * Created by user on 2017-06-03.
 */
function showFlashPrompt(message) {
    var template = "<div class='container container-alert-flash-prompt'>" +
        "<div class='col-sm-3 col-sm-offset-8'>" +
        "<div class='alert alert-success' role='alert'>" +
        "<button type='button' class='close' data-dismiss='alert' aria-label='Close'>" +
        "<span aria-hidden='true'>&times;</span></button>"+ message +"</div></div></div>";
    $("body").append(template);
    setTimeout(function () {
        $(".container-alert-flash-prompt").remove();
    }, 1700);
}