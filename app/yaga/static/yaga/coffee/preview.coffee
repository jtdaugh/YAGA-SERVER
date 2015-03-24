'use strict'

(($) ->
  $(document).ready ->

    $('button[rel="popover"]').popover(
      html: true
      trigger: 'manual'
      placement: 'left'
      title: $(this).attr('data-title')
      content: ->
        return '<img class="img-responsive img-thumbnail" src="' + $(this).attr('data-url') + '" />'
    ).click (e) ->
      self = this
      $('button[rel="popover"]').each ->
        if self != this
          $(this).popover 'hide'

          return

      $(this).popover 'toggle'
      e.stopPropagation()

      return

    $(document).on 'click', (e) ->
      if !$(e.target).closest('.popover').length
        $('.popover').each ->
          $(@previousSibling).popover 'hide'

          return

      return

    return

  return
) jQuery
