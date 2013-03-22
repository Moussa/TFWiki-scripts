//API documentation is at http://www.mediawiki.org/wiki/Api
//JsMwApi documentation is at http://en.wiktionary.org/wiki/User_talk:Conrad.Irwin/Api.js
//Basic usage for the impatient: JsMwApi()({action:'query',prop:'meta'},function(res){alert(res)});
 
/* A Javascript wrapper to the MediaWiki API
 *
 * @param {String} url  The url of api.php 
 *  (default: wgScriptPath + '/api.php')
 * @param {"local"|"remote"}  "local" causes AJAX POST requests, and "remote" Javascript callback style request.
 *  (default: if url starts with http:// or https:// then "remote" else "local")
 */
function JsMwApi (api_url, request_type) {
 
    if (!api_url) 
    {
        if (typeof(wgEnableAPI) === 'undefined' || wgEnableAPI == false)
            throw "Local API is not usable.";
 
        api_url = wgScriptPath + "/api.php";
    }
 
    if (!request_type)
    {
        if (api_url.indexOf('http://') == 0 || api_url.indexOf('https://') == 0)
            request_type = "remote";
        else
            request_type = "local";
    }
 
    /* The function returned by JsMwApi()
     *
     * @param{Parameters} query   An object to be encoded, a string to use directly, or nested arrays of the above
     * @param{Function(res)} callback   The function that will be called with the parsed result from the API.
     */
    function call_api (query, callback)
    {
        if(!query || !callback)
            throw "Insufficient parameters for API call";
 
        query = serialise_query(query);
 
        if(request_type == "remote")
            request_remote(api_url, query, callback, call_api.on_error || default_on_error);
        else
            request_local(api_url, query, callback, call_api.on_error || default_on_error);
 
    }
 
    /* The default error handler, can be overwritten by setting call_api.on_error
     *
     * @param {XmlHttpRequest|null}  The request object used for this call, or null for a remote request
     * @param {Function(res)}  The callback that would have been called on success.
     * @param {res}  The parsed result from the API (or null).
     */
    var default_on_error = JsMwApi.prototype.on_error || function (xhr, callback, res)
    {
        if (typeof(console) != 'undefined')
            console.log([xhr, res]);
 
        callback(null);
    }
 
    /* Try to get a new XmlHttpRequest
     *
     * @return {XmlHttpRequest}
     * @throws "Could not create an XmlHttpRequest"
     */
    function get_xhr () 
    {
        try{
            return new XMLHttpRequest();
        }catch(e){ try {
            return new ActiveXObject("Msxml2.XMLHTTP");
        }catch(e){ try {
            return new ActiveXObject("Microsoft.XMLHTTP");
        }catch(e){
            throw "Could not create an XmlHttpRequest";
        }}}
    }
 
    /* Make an AJAX request to a local api.php
     *
     * @param {String} the URI of api.php
     * @param {String} the (URIencoded) query
     * @param {Function(res)} the callback
     * @throws "Could not create an XmlHttpRequest"
     */
    function request_local (url, query, callback, on_error)
    {
        var xhr = get_xhr();
 
        xhr.open('POST', url + '?format=json', true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");                  
        xhr.send(query);
        xhr.onreadystatechange = function ()
        {
            if (xhr.readyState == 4)
            {
                var res;
                if (xhr.status != 200)
                    res = {error: {
                        code: '_badresponse', 
                        info: xhr.status + " " + xhr.statusText
                    }};
                else
                {
                    try
                    {
                        res = JSON.parse("("+xhr.responseText+")");
                    }
                    catch(e)
                    {
                        res = {error: {
                            code: '_badresult',
                            info: "The server returned an incorrectly formatted response"
                        }};
                    }
                }
                if (!res || res.error || res.warnings)
                    on_error(xhr, callback, res);
                else
                    callback(res);
            }
        }
    }
 
    /* Make a callback request to a remote api.php. Restricted as per api.php documentation.
     *
     * @param {Url}  The URI of api.php
     * @param {String}  A (URIencoded) request string.
     * @param {Function(res)}  The callback
     */
    function request_remote (url, query, callback, on_error)
    {
        if(! window.__JsMwApi__counter)
            window.__JsMwApi__counter = 0;
 
        var cbname = '__JsMwApi__callback' + window.__JsMwApi__counter++; 
 
        window[cbname] = function (res)
        {
            if (res.error || res.warnings)
                on_error(null, callback, res);
            else
                callback(res);
        }
 
        var script = document.createElement('script');
        script.setAttribute('type', 'text/javascript');
        script.setAttribute('src', url + '?format=json&callback=window.' + cbname + '&' + query);
        document.getElementsByTagName('head')[0].appendChild(script);
    }
 
    /* Convert an input object into a URI-encoded query string.
     *
     * @param {Parameters}  Either:
     *   A String (returned unchanged)
     *   An Object (each key value pair is encoded and then joined with &s)
     *     A boolean true causes the key to inserted with no value
     *     A boolean false causes the key to be missed out completely
     *     An array as a key is joined with "|" before encoding
     *   An Array (each item is recursively encoded and the result joined together)
     *     Note that parameters set in later parts of the array will obscure parameters
     *     with the same name set from earlier parts.
     *
     * @return {String}  A string that can be fed to the api over HTTP
     */
    function serialise_query (obj)
    {
        var amp = "";
        var out = "";
        if (String(obj) === obj)
        {
            out = obj;
        }
        else if (obj instanceof Array)
        {
            for (var i=0; i < obj.length; i++)
            {
                out += amp + serialise_query(obj[i]);
                amp = (out == '' || out.charAt(out.length-1) == '&') ? '' : '&';
            }
        }
        else if (obj instanceof Object)
        {
            for (var k in obj)
            {
                if (obj[k] === true)
                    out += amp + encodeURIComponent(k) + '=1';
                else if (obj[k] === false)
                    continue;
                else if (obj[k] instanceof Array)
                    out += amp + encodeURIComponent(k) + '=' + encodeURIComponent(obj[k].join('|'));
                else if (obj[k] instanceof Object)
                    throw "API parameters may not be objects";
                else
                    out += amp + encodeURIComponent(k) + '=' + encodeURIComponent(obj[k]);
                amp = '&';
            }
        }
        else if (typeof(obj) !== 'undefined' && obj !== null)
        {
            throw "An API query can only be a string or an object";
        }
        return out;
    }
 
    // Make JSON.parse work
    var JSON = (typeof JSON == 'undefined' ? new Object() : JSON);
 
    if (typeof JSON.parse != 'function')
        JSON.parse = function (json) { return eval('(' + json + ')'); };
 
    // Allow .prototype. extensions
    if (JsMwApi.prototype)
    {
        for (var i in JsMwApi.prototype)
        {
            call_api[i] = JsMwApi.prototype[i];
        }
    }
    return call_api;
}
 
JsMwApi.prototype.page = function (title) {
 
    /* The function returned by JsMwApi().page("foo")
     * 
     * Overrides the title= and titles= parameters of the query given to it.
     *
     * @param{Parameters}
     * @param{Function(res)}
     */
    function call_with_page (params, callback)
    {
        call_with_page.api([params, {title: title, titles: title}], callback);
    }
 
    /* Access to this pages JsMwApi() object, can be used to set on_error */
    call_with_page.api = this;
 
    /* A function to initiate the editing cycle.
     *
     * @param {Parameters} (optional)
     * @param {Function(text, save_function, res)}
     *   text: The current text of the page,
     *   page: A function to save the result of this edit
     *   res:  The raw API result
     */
    call_with_page.edit = function (params, edit_function)
    {
        if (typeof(params) == 'function')
        {
            edit_function = params;
            params = null;
        }
        params = [params, {
            action: "query", 
            prop: ["info", "revisions"], 
            intoken: "edit", 
            rvprop: ["content", "timestamp"]
        }];
 
        call_with_page(params, function (res)
        {
            if (!res || !res.query || !res.query.pages)
                return edit_function(null);
 
            // Get the first (and only) page from res.query.pages
            for (var pageid in res.query.pages) break;
            var page = res.query.pages[pageid];
 
            var text = page.revisions ? page.revisions[0]['*'] : '';
 
            /* Save the given text to the page, will only work if the edit function has previously been called.
             *
             * @param {String} ntext  The new text to save, if it is the same as the old text, or blank, this method will not save
             * @param {Parameters}    Extra parameters for the edit {summary: "blah", minor: true} 
             * @param {Function(res)} A callback once save has completed
             */
            function save_function (ntext, params, post_save)
            {
                if (typeof(params) == 'function')
                {
                    post_save = params;
                    params = null;
                }
                params = [params, {
                    action: "edit",
                    text: ntext,
                    token: page.edittoken,
                    starttimestamp: page.starttimestamp,
                    basetimestamp: (page.revisions ? page.revisions[0].timestamp : false)
                }];
 
                call_with_page(params, post_save);
            }
 
            // Give control back to the outside world
            edit_function(text, save_function, res);
 
        });
    }
 
    /* A thin wrapper around the API's parse function. Set's the pst flag to
     * make subst: work, and returns all parse information
     *
     * @param {String} params  The text to parse, if this is omitted or null,
     *     then the page itself will be used
     * @param {Function(text, res)} callback
     */
    call_with_page.parse = function (to_parse, callback)
    {
        if (typeof to_parse == "function")
        {
            callback = to_parse;
            to_parse = null;
        }
        var params = (to_parse == null ? {page: title} : {title: title, text: to_parse});
 
        call_with_page.api([{action: "parse", pst: true}, params], function (res)
        {
            if (!res || !res.parse || !res.parse.text)
                callback(null, res);
            else
                callback(res.parse.text['*'], res);
        })
    }
 
    /* A thin wrapper around .parse that forces the text to be parsed without
     * any <p> tags that might otherwise get added.
     * @param {String} params  The text to parse 
     *  NOTE This function is only useful for tiny fragments, anything ill-formed or with block-level elements is likely to fail.
     * @param {Function(text, res)}  callback called with output and original parse query result
     */
    call_with_page.parseFragment = function (to_parse, callback)
    {
        call_with_page.parse("<div>\n" + to_parse + "</div>", function (parsed, res)
        {
            callback(parsed ? parsed.replace(/^<div>\n?/,'').replace(/(\s*\n)?<\/div>\n*(<!--[^>]*-->\s*)?$/,'') : parsed, res);
        })
    }
 
    return call_with_page;
}

//// START SPAMBOT KILLER ///
var nearbyApi = JsMwApi("/w/api.php");

function deletePage(title){
    nearbyApi({action: "query", prop: "info", intoken: 'delete', titles: title}, function (res){
        for (var key in res.query.pages){
            var title = res.query.pages[key].title
            var deletetoken = res.query.pages[key].deletetoken;
            nearbyApi({action: "delete", title: title, reason: 'Spam', token: deletetoken}, function (res){ 
                console.log('Deleted ' + title);
            });
        }
    });
}

function killContribs(user){
    nearbyApi({action: "query", list: "usercontribs", ucuser: user}, function (res){
        for(var edit in res.query.usercontribs){
            if ('new' in res.query.usercontribs[edit]){
                deletePage(res.query.usercontribs[edit].title);
            }
        }
    });
}

function blockUser(user){
    nearbyApi({action: "query", prop: "info", intoken: 'block', titles: 'User:' + user}, function (res){
        for (var key in res.query.pages){
            var blocktoken = res.query.pages[key].blocktoken;
            nearbyApi({action: "block", user: user, expiry: 'never', nocreate: '', autoblock: '', reason: 'Spamming links to external sites', token: deletetoken}, function (res){ 
                console.log('Blocked ' + user);
            });
        }
    });
}

function keel(user){
    nearbyApi({action: "query", list: "users", ususers: user, usprop: "registration"}, function (res){ 
        var regdate = Date.parse(res.query.users[0].registration);
        if (new Date().getTime() - regdate < 86400000){
            blockUser(user);
            killContribs(user);
        }
        else{
            alert('Nope.avi - User:' + user + ' has existed for more than 1 day.');
        }
    });
}

function pootSecretSauce(){
    $('.firstrevisionheader .mw-usertoollinks').append(' <a href="#" id="secretsauce">secretsauce</a>');
    $("#secretsauce").click(function(){
        var user = $('.firstrevisionheader .mw-userlink').attr('title').replace('User:', '');
        keel(user);
        alert('User:' + user + ' has been terminated. Good day');
    });
}
addOnloadHook(pootSecretSauce);
/// END SPAMBOT KILLER ///
