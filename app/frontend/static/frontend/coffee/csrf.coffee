(($) ->
  $(document).ready ->
    csrfSafeMethod = (method) ->
      return /^(GET|HEAD|OPTIONS|TRACE)$/.test method

    $.ajaxSetup beforeSend: (xhr, settings) ->
      if !csrfSafeMethod(settings.type) and !@crossDomain
        xhr.setRequestHeader 'X-CSRFToken', $('meta[name="csrf-token"]').attr 'content'
      return

  return
) jQuery
