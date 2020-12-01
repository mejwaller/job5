var user = "Mikle McGrath,000456";
var expiry = new Date();

expiry.setTime(expiry.getTime() + (7*24*60*60*1000));

window.document.cookie="cookiedata="+escape(user)+";"+"expires=" + expiry.toGMTString()+";";

if(window.document.cookie)
{
	var cookiedata=unescape(window.document.cookie);
	var userdata=cookiedata.split("=");
	
	if(userdata[0]=="cookiedata")
	{
		var data = userdata[1].split(",");
		var user=data[0];
		var acct=data[1];
		
		alert("Welcome "+user+"\nAccount number: " + acct);
	}
}