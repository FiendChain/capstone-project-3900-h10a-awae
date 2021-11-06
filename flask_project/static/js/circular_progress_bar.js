/* 
 * Code taken from: https://bootstrapious.com/p/circular-progress-bar
 * Used to create the circular progress bar used in battlepass
 */
$("document").ready(function() {
  $(".battlepass-progress").each(function() {
    var value = $(this).attr('data-value');
    var left = $(this).find('.progress-left .progress-bar');
    var right = $(this).find('.progress-right .progress-bar');

    if (value > 0) {
      if (value <= 50) {
        right.css('transform', 'rotate(' + percentageToDegrees(value) + 'deg)')
      } else {
        right.css('transform', 'rotate(180deg)')
        left.css('transform', 'rotate(' + percentageToDegrees(value - 50) + 'deg)')
      }
    }
  })

  function percentageToDegrees(percentage) {
    return percentage / 100 * 360
  }

});