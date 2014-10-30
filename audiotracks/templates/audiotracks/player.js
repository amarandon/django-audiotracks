$(document).ready(function() {
  "use strict";

  function playNext(domObj) {
    var next_audio_elem = $(domObj).parents('.js-audiotracks-container')
                                   .next().find('audio').get(0);
    if (next_audio_elem) {
      var player = next_audio_elem.player;
      // FIXME
      // Only way to make play() work on Firefox is to wrap it in a
      // setTimeout. Weird...
      setTimeout($.proxy(player, 'play'), 0);
    } else {
      var pagination = $('.pagination');
      var current = pagination.find('.active');
      var next = current.next();
      if (next.size()) {
        var url = next.find('a').attr('href');
        window.location = url + '?autoplay=true';
      }
    }
  }

  function setPlayingTitle(domObj) {
    var parents = $(domObj).parents('.js-audiotracks-container'),
        title = parents.find('.js-audiotracks-title').text();
    $('title').html('&#9654; ' + title);
  }

  var oldTitle = $('title').html();

  function revertTitle() {
    $('title').html(oldTitle);
  }

  $('audio').mediaelementplayer({
    audioWidth: '100%', 
    pluginPath: '{{ STATIC_URL }}mediaelement-2.8.2/',
    error: function(domObj) {
        $(domObj).bind('play', function() { playNext(domObj); });
    },
    success: function(me, domObj) {
      var container = $(domObj).parents('.player-container');
      container.next().find('.audio-type').html( me.pluginType );

      $(me).bind('play', function() { setPlayingTitle(domObj); });
      $(me).bind('pause', revertTitle);
      $(me).bind('ended', function() { playNext(domObj); });

      var firstPlayer = mejs.players[0];
      if (me === firstPlayer.media && location.search.indexOf('autoplay=true') !== -1) {
        firstPlayer.play();
      }
    }
  });


});
