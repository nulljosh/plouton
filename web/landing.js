// Landing: reveal on scroll, and the live Home / Status / Messages demo.
document.documentElement.classList.add('js');
document.addEventListener('DOMContentLoaded', function () {
  var io = 'IntersectionObserver' in window && new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(function (el) { io ? io.observe(el) : el.classList.add('in'); });

  var tabs = document.querySelectorAll('.app-tab');
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (o) {
        var on = o === t;
        o.setAttribute('aria-selected', on);
        document.getElementById(o.getAttribute('aria-controls')).hidden = !on;
      });
    });
  });

  // the one action on Home: mark the cheque as landed, like the app's "Paid yet?" toggle
  var paid = document.getElementById('d-paid'), when = document.getElementById('d-when');
  if (paid) paid.addEventListener('click', function () {
    var on = paid.getAttribute('aria-pressed') !== 'true';
    paid.setAttribute('aria-pressed', on);
    paid.textContent = on ? 'Landed. Undo' : 'It landed';
    when.textContent = on ? 'Paid. Next one in 30 days' : 'Wednesday, in 2 days';
  });

  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
});
