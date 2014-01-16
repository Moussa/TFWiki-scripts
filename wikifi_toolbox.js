// Inserts a Wiki-Fi link to the page title when viewing userpages

function AddWikiFiLinkToUser() {
    if (wgCanonicalNamespace == 'User') {
        var link = ' <span style="font-size:12px">(<a href="http://stats.wiki.tf/user/tf/' + wgTitle.split("/")[0] + '" target="_blank">stats</a>)</span>'
        $("#firstHeading span").append(link);
    }
}

addOnloadHook(AddWikiFiLinkToUser);
