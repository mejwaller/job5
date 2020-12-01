var browser = navigator.appName;
var desc = navigator.userAgent;
var plat = navigator.platform;
var appcode = navigator.appCodeName;
var appver = navigator.appVersion;

var plugins = "";
/*for(var i = 0; i < navigator.plugins.length; i++)
{`
	plugins += navigator.plugins[i].name + "\n";
}*/

alert("Browser: " + browser + "\n"
+ "Browser description: " + desc + "\n"
+ "Platform: " + plat + "\n"
+ "Code name: " + appcode + "\n"
+ "version: " + appver + "\n"
+ "Plugins: " + plugins);


