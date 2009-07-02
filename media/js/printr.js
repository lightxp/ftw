function printr_show(val) {
	Okienko=window.open('','','scrollbars=yes,resizable=yes,width=400,height=400,left=100,top=50');
	Okienko.document.open();
	Okienko.document.write ("<HTML><HEAD><TITLE>printr</TITLE></HEAD><BODY TOPMARGIN='10' LEFTMARTIN='0'>"+val+"</BODY></HTML>");
	Okienko.document.close();
	Okienko.focus();		
}

function printr(val) {
	switch (typeof val) {
        case ("object"):
			if (val.lenght) {
				var o=array2String(val,0);
			} else {
				var o=object2String(val,0);
			}
			printr_show(o);
            break;
        default:
			printr_show(val);
	}	
}	

function ftab(i){
	var temp = '';
	for (var j=1;j<=i;j++) temp += "&nbsp;&nbsp;&nbsp;&nbsp;";	
	return temp;
}

function object2String(obj,j) {
    var val, output = "";
	++j;
    if (obj) {    
        output += "<b>object{</b><br>";
		var tab = ftab(j);
        for (var i in obj) {
			val = obj[i];
			if (val != null){
				switch (typeof val) {
	                case ("object"):
						if (val.lenght) {
							output += tab + i + " => " + array2String(val,j) + "<br>";
	                    } else {
	                        output += tab + i + " => " + object2String(val,j) + "<br>";
	                    }
	                    break;
	                case ("string"):
	                    output += tab + i + " => '" + escape(val) + "'<br>";
	                    break;
	                default:
	                    output += tab + i + " => " + val + "<br>";
	            }
			} else {
				break;
			}
        }
        output = output.substring(0, output.length) + tab + "<b>}</b>";
    }
    return output;
}

function array2String(array,k) {
    var output = "";
	++k;
    if (array) {
        output += "<b>array[</b><br>";
		var tab = ftab(k);
        for (var i in array) {
            val = array[i];
            switch (typeof val) {
                case ("object"):
                    if (val[0]) {
                        output += tab + array2String(val,k) + "<br>";
                    } else {
                        output += tab + object2String(val,k) + "<br>";
                    }
                    break;
                case ("string"):
                    output += tab+"'" + escape(val) + "'<br>";
                    break;
                default:
                    output += tab + val + "<br>";
            }
        }
        output = output.substring(0, output.length) + tab + "<b>]</b>";
    }
    return output;
}


function string2Object(string) {
    eval("var result = " + string);
    return result;
}

function string2Array(string) {
    eval("var result = " + string);
    return result;
}
