function popup()
{
	var popwindow = window.open("","","top=40,left=30,width=250,height=125");
	popwindow.document.open();
	
	popwindow.document.write("<title>Pop-up</title>");
	popwindow.document.write("Dynamic Pop-up Page<br/>");
	popwindow.document.write("img src='dex.gif'>");
	popwindow.document.close();
}
window.onload=popup;