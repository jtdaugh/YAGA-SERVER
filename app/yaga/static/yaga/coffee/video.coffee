'use strict'


bindVideo = ->
  $(document).ready ->

    attachment = videojs('attachment', {
      'techOrder': [
        'html5'
        'flash'
      ]
      'flash': 'swf': VIDEOJS_SWF
      'controls': true
      'autoplay': false
      'preload': 'none'
      'loop': 'true'
      'width': 640
      'height': 640
    }, ->

      return
    )

    return

  return
