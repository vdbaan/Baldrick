var page = require('webpage').create(), system = require('system');

page.viewportSize = {width:1024, height:768};
page.clipRect = {top:0, left:0, width:1024, height:768};
page.settings.resourceTimeout = 30000;
page.onResourceTimeout = function(e){
    console.log(e.errorCode);   // it'll probably be 408 
    console.log(e.errorString); // it'll probably be 'Network timeout on resource'
    console.log(e.url);         // the url whose request timed out
    phantom.exit(1);
};
webpage = system.args[1];
output = system.args[2];
page.open(webpage, function() {
    page.render(output);
    console.log('Done creating: ' + output);
    phantom.exit();
});