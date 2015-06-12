(function() {
var isChrome = navigator.userAgent.includes("Chrome");
var pasteURL = null;

function onPaste(e) {
    var data = new FormData();
    data.append("file", null);
    if (pasteURL == null) {
        $("#applet-container").text("Not ready for pasting");
        return;
    }

    if (e.clipboardData && e.clipboardData.items) {
      var item = null;
      for (var i = 0; i < e.clipboardData.items.length && item == null; i++) {
        var it = e.clipboardData.items[i];
        if (it.type == "image/png")
          item = it;
      }
      if (item == null) {
        $("#applet-container").text("No image available for pasting");
        return
      } else {
        //var filedata = atob(this.result.substr(this.result.indexOf(",") + 1));
        //data.append("file", new Blob(filedata, { type: "image/png" }));
        data.append("file", item.getAsFile());
        var req = new XMLHttpRequest();
        req.open("POST", pasteURL, true);
        req.send(data);
        throb();
        $("#applet-container").text("Uploading your image");
        req.onload = function(r) {
            window.location.href = req.responseURL;
            throb(false);
        };
        req.onerror = function(e) {
            console.log("ERROR: " + e);
            throb(false);
        };
      }
    } else {
        $("#applet-container").text("No image available for pasting");
        return;
    }
    document.removeEventListener("paste", onPaste, false);
}

if (navigator.userAgent.indexOf("Mobile") != -1) {
    $('#new-capture-div').remove();
    $('#applet-container-outer').remove();
    return;
}
if (!deployJava.versionCheck("1.6+") && !isChrome) {
    $('#no-applet-support').show();
    $('#new-capture-div').remove();
    $('#applet-container-outer').remove();
    return;
}
$('#no-applet-support').remove();
$("#new-capture").button();
$("#new-capture-reset").button();
var defaultValue =
        "Set a name for your new capture or leave blank for a default";

$("#new-capture-input").focus(function() {
    if ($("#new-capture-input").val() == defaultValue) {
        $("#new-capture-input").val("");
    }
    $("#new-capture-input").removeClass("blank");
});

function onblur() {
    if ($.trim($("#new-capture-input").val()) == "") {
        $("#new-capture-input").val(defaultValue);
        $("#new-capture-input").addClass("blank");
    }
}

$("#new-capture-input").blur(onblur);

$("#new-capture-input").val(defaultValue);
$("#new-capture-input").addClass("blank");

function onaction() {
    onblur();
    $("#new-capture-input").attr('readonly', true);
    $("#new-capture-input").attr('disabled', true);
    $("#new-capture").button('option', 'disabled', true);
    $("#new-capture-reset").css("visibility", "visible");

    var name = $("#new-capture-input").val();
    if (name == defaultValue) {
        name = "";
        $("#new-capture-input").val(name);
        $("#new-capture-input").removeClass("blank");
    }
    throb();

    GET("/uploadinfo/" + escape(name) + "?r=" + (new Date().getTime()),
    function(data) {
        throb(false);
        if (isChrome) {
            document.addEventListener("paste", onPaste, false);
            pasteURL = data.url;
        }
        $("#applet-container-outer").slideDown('fast');

        if ($("#new-capture-input").val() != data.name)
            $("#new-capture-input").val(data.name);

        if (!isChrome) {
            runApplet(document.getElementById('applet-container'), {
                id: 'applet',
                codebase: '/applet',
                code: 'com.hanhuy.screenshot.applet.Main',
                name: 'Screen Capturer',
                archive: 'screenshot.jar',
                mayscript: 'mayscript'
            }, {
                'url': data.url,
                'bgcolor': '#ffffff',
                'fgcolor': '#666666'
            }, 'json')
        };
    }, function(xhr) {
        throb(false);
        alert("Unable to request upload information, error: " + xhr.status);
    });
    if (isChrome) {
        $("#drop-title").text("Paste your image into the box below");
        $("#applet-text").remove();
    }
}

function resetapplet() {
    $('#applet-container-outer').slideUp('fast');
    $('#applet').remove();
    $("#new-capture-reset").css('visibility', 'hidden');
    $("#new-capture-input").removeAttr("disabled");
    $("#new-capture-input").removeAttr("readonly");
    $("#new-capture").button('option', 'disabled', false);
    document.removeEventListener("paste", onPaste, false);
    pasteURL = null;
}


$("#new-capture").click(onaction);
$("#new-capture-input").keydown(function(e) {
    if (e.keyCode == 10 || e.keyCode == 13)
        onaction();
});

$("#new-capture-reset").click(resetapplet);
$(window).unload(resetapplet);
})();
