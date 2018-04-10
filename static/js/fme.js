function callFME(usr,pwd,aoi){
		console.log("AOI : "+aoi.toString())
		$.post("/callFME", {usr: usr, pwd: pwd, aoi:aoi}, function(data, status){
        alert("Data: " + data + "\nStatus: " + status);
				var parsedData = JSON.parse(data)
				console.log(parsedData);
				var downloads = '';
				for (var key in parsedData) {
						console.log("Response: "+key+" "+parsedData[key]);
		        downloads += '<a href="/download/'+parsedData[key]+'" target="_blank">'+key+'</a>\n';
				}
				console.log(downloads);
				$("#download-panel").html(downloads);
    });
}
