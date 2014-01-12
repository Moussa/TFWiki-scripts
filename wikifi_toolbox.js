// Inserts a Wiki-Fi link to the page title when viewing userpages

function AddWikiFiLinkToUser() {
    if (wgPageName.substring(0, 4) != 'User') {
        return;
    }
    
    var link = ' <span style="font-size:12px">(<a href="http://stats.wiki.tf/user/tf/' + wgTitle + '" target="_blank">stats</a>)</span>'
    $("#firstHeading span").append(link);
}

addOnloadHook(AddWikiFiLinkToUser);
