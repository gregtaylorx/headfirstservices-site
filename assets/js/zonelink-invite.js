// Invite links: /zonelink/invite/?ref=<code> (code = 4-16 letters/digits).
// Android: Play with the code as the install referrer (referrer=ref%3D<code>);
// the app reads it on first launch. iPhone/iPad: App Store. Anything else:
// this page, with both badges (Play badge carries the referrer too).
(function () {
  var PLAY = 'https://play.google.com/store/apps/details?id=com.digitalnomadessentials.zonelink';
  var IOS = 'https://apps.apple.com/app/id6794818466';
  var m = /[?&]ref=([A-Za-z0-9]{4,16})(?:&|$)/.exec(location.search);
  var play = m ? PLAY + '&referrer=' + encodeURIComponent('ref=' + m[1].toLowerCase()) : PLAY;
  document.getElementById('play').href = play;
  document.getElementById('ios').href = IOS;
  var ua = navigator.userAgent || '';
  var isIOS = /iPhone|iPad|iPod/i.test(ua) || (/Macintosh/i.test(ua) && navigator.maxTouchPoints > 1);
  if (/Android/i.test(ua)) { location.replace(play); }
  else if (isIOS) { location.replace(IOS); }
})();
