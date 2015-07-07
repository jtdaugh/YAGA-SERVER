'use strict'

(($) ->
  $(document).ready ->

    $('.approve').click ->
        self = this
        $self = $ self

        BootstrapDialog.confirm
            title: gettext 'Approve?'
            message: gettext 'Are You sure want to approve this post?'
            type: BootstrapDialog.TYPE_WARNING
            closable: true
            draggable: true
            btnCancelLabel: gettext 'No'
            btnOKLabel: gettext 'Yes!'
            btnOKClass: 'btn-warning'
            callback: (result) ->
                if result
                    $.ajax
                      type: 'POST'
                      url: APPROVE_ENDPOINT,
                      data:
                        'pk': $self.attr('data-pk')
                      success: ->
                        $self.remove()

                        return

                return

        return

    return

  return
) jQuery
