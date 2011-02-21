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
