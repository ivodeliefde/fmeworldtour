function callFME(usr,pwd){
		$.post("/callFME", {usr: usr, pwd: pwd}, function(data, status){
        alert("Data: " + data + "\nStatus: " + status);
    });
}
