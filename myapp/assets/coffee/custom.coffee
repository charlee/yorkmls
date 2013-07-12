$(document).ready ->


  $(".reject").click ->
    houseId = $(@).attr 'house_id'
    $.post '/j/reject/' + houseId + '/', -> location.href = '/'
      

  $(".restore").click ->
    houseId = $(@).attr 'house_id'
    $.post '/j/restore/' + houseId + '/', -> location.reload()


  $("#update-memo").click ->

    data = 
      memo: $("#memo-input").val()
      _csrf_token: window._csrf_token

    houseId = $("#house-id").val()
    
    $.post '/j/memo/' + houseId + '/', data

