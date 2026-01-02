var merged = '';
var i = 0;
var xhr = new XMLHttpRequest();
while(true) {
  xhr.open('GET', '?m=' + i, false);
  xhr.send(null);
  if(!xhr.responseText) break;
  merged += xhr.responseText;
  i++;
}
console.log(merged);