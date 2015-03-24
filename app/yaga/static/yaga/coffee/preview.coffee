'use strict'

(($) ->
  $(document).ready ->

    $('button[rel="popover"]').popover(
      html: true
      trigger: 'manual'
      placement: 'left'
      title: $(this).attr('data-title')
      content: ->
        '<img class="img-responsive img-thumbnail" src="' + $(this).attr('data-url') + '" />'
    ).click (e) ->
      $(this).popover 'toggle'
      e.stopPropagation()

      return

    $('html').click (e) ->
      $('button[rel="popover"]').popover 'hide'

      return

    return

  return
) jQuery
