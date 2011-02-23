(function() {
if (navigator.userAgent.indexOf("Mobile") != -1) {
    $('#new-capture-div').remove();
    $('#applet-container-outer').remove();
    return;
}
if (!deployJava.versionCheck("1.6")) {
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
    $("#new-capture").attr('disabled', true);
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
        $("#applet-container-outer").slideDown('fast');

        if ($("#new-capture-input").val() != data.name)
            $("#new-capture-input").val(data.name);

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
        }, 'json');
    }, function(xhr) {
        throb(false);
        alert("Unable to request upload information, error: " + xhr.status);
    });
}

function resetapplet() {
    $('#applet-container-outer').slideUp('fast');
    $('#applet').remove();
    $("#new-capture-reset").css('visibility', 'hidden');
    $("#new-capture-input").removeAttr("disabled");
    $("#new-capture-input").removeAttr("readonly");
    $("#new-capture").removeAttr("disabled");
}


$("#new-capture").click(onaction);
$("#new-capture-input").keydown(function(e) {
    if (e.keyCode == 10 || e.keyCode == 13)
        onaction();
});

$("#new-capture-reset").click(resetapplet);
$(window).unload(resetapplet);
})();
