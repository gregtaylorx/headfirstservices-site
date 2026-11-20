// Invite links: /tripgear/invite/?ref=<code>. The code rides to Play as the
// install referrer (referrer=ref%3D<code>); the app reads it on first launch.
(function () {
  var m = /[?&]ref=([A-Za-z0-9]{4,16})/.exec(location.search);
  var play = 'https://play.google.com/store/apps/details?id=com.digitalnomadessentials.packlite';
  if (m) play += '&referrer=' + encodeURIComponent('ref=' + m[1].toLowerCase());
  document.getElementById('play').href = play;
  var ua = navigator.userAgent || '';
  if (/Android/i.test(ua)) { location.replace(play); }
})();
