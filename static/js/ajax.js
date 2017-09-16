
/*
* do an ajax request (get|post) and apply callback function to server response
* */

function request(url, method, data, callback){

    var x = (window.XMLHttpRequest)
        ? new XMLHttpRequest() // IE7+, Firefox, Chrome, Opera, Safari
        : new ActiveXObject("Microsoft.XMLHTTP"); // IE6, IE5
    
    x.onreadystatechange = function() {
        if (x.readyState==4){
            if(x.status==200) {
                callback(x.response);
            }
            else {
                console.log("Network error (" + x.status + ")");
            }
        }
    };

    if (method.toUpperCase()=='GET') url += "?" + data;
    
    x.open(method,url,true);

    if (method.toUpperCase()=="POST") x.setRequestHeader('Content-type','application/x-www-form-urlencoded');

    x.send(data);
}
