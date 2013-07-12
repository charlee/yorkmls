$(document).ready ->


  $(".reject").click ->
    houseId = $(@).attr 'house_id'
    $.post '/j/reject/' + houseId + '/', -> location.reload()
      

  $(".restore").click ->
    houseId = $(@).attr 'house_id'
    $.post '/j/restore/' + houseId + '/', -> location.reload()

  $(".reparse").click ->
    houseId = $(@).attr 'house_id'
    $.post '/j/reparse/' + houseId + '/', -> location.reload()


  $(".want-view").click ->
    houseId = $(@).attr 'house_id'
    $.post '/j/wantview/' + houseId + '/', -> location.reload()

  $(".cancel-view").click ->
    houseId = $(@).attr 'house_id'
    $.post '/j/cancelview/' + houseId + '/', -> location.reload()

  $("#update-memo").click ->

    data = 
      memo: $("#memo-input").val()
      _csrf_token: window._csrf_token

    houseId = $("#house-id").val()
    
    $.post '/j/memo/' + houseId + '/', data


  $(".houselink").click ->
    $(@).closest("table").find("tr").removeClass("info")
    $(@).closest("tr").addClass("info")
