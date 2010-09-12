function handleHelpTooltipMouseOver(event) {
  var el = document.createElement('div');
  el.id = 'helpTooltip';
  el.innerHTML = event.toElement.getElementsByTagName('div')[0].innerHTML;
  el.style.top = 0;
  el.style.left = 0;
  el.style.visibility = 'hidden';
  document.body.appendChild(el);
 
  var width = el.offsetWidth;
  var height = el.offsetHeight;
 
  if (event.pageX - width - 50 + document.body.scrollLeft >= 0 ) {
    el.style.left = (event.pageX - width - 20) + 'px';
  } else {
    el.style.left = (event.pageX + 20) + 'px';
  }
 
 
  if (event.pageY - height - 50 + document.body.scrollTop >= 0) {
    el.style.top = (event.pageY - height - 20) + 'px';
  } else {
    el.style.top = (event.pageY + 20) + 'px';
  }
 
  el.style.visibility = 'visible';
}
 
function handleHelpTooltipMouseOut(event) {
  var el = document.getElementById('helpTooltip');
  el.parentNode.removeChild(el);
}
 
function enableHelpTooltips() {
  var helpEls = document.getElementsByClassName('help');
 
  for (var i = 0, helpEl; helpEl = helpEls[i]; i++) {
    helpEl.onmouseover = handleHelpTooltipMouseOver;
    helpEl.onmouseout = handleHelpTooltipMouseOut;
  }
}
