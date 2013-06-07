// Inserts a Wiki-Fi link in the toolbox on the left sidebar when viewing userpages

function AddWikiFiLinkToToolbox() {
    if (wgPageName.substring(0, 4) != 'User') {
        return;
    }

    var name = 'Wiki-Fi stats';
    var link = 'http://stats.wiki.tf/user/tf/' + wgTitle;

    var node = document.getElementById('p-tb').getElementsByTagName('div')[0].getElementsByTagName('ul')[0];
    
    var aNode = document.createElement('a');
    var liNode = document.createElement('li');
    
    aNode.appendChild(document.createTextNode(name));
    aNode.setAttribute('href', link);
    liNode.appendChild(aNode);
    liNode.className = 'plainlinks';
    node.appendChild(liNode);
}

addOnloadHook(AddWikiFiLinkToToolbox);
