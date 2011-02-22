function POST(url, data, success, error, datatype) {
  $.ajax({
      type: 'POST',
      url: url,
      data: data,
      success: success,
      error: error,
      dataType: datatype
  });
}
function GET(url, success, error, datatype) {
  $.ajax({
      type: 'GET',
      url: url,
      success: success,
      error: error,
      dataType: datatype
  });
}

var _throbberCount = 0;
function throb(start) {
    if (start === undefined || start) {
        _throbberCount++;
        $('#throbber').show('fast');
    } else {
        _throbberCount--;
        if (!_throbberCount)
            $('#throbber').hide('fast');
    }
}

function runApplet(e, attributes, parameters) {
    var intercepted = '';
    var dw = document.write;
    document.write = function(s) { intercepted += s; }
    deployJava.runApplet(attributes, parameters, '1.6');
    document.write = dw;
    e.innerHTML = intercepted;
}