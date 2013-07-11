$(document).ready ->


  $(".reject").click ->
    houseId = $(@).attr 'house_id'
    if confirm("Are you sure to reject " + houseId + "?")
      $.post '/j/reject/' + houseId + '/', -> location.reload()
      
        


  $("#update-memo").click ->

    data = 
      memo: $("#memo-input").val()
      _csrf_token: window._csrf_token

    houseId = $("#house-id").val()
    
    $.post '/j/memo/' + houseId + '/', data

