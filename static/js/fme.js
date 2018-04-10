function callFME(usr,pwd,aoi){
		console.log("AOI : "+aoi.toString())
		$.post("/callFME", {usr: usr, pwd: pwd, aoi:aoi}).done(function(data, status){
	        alert("Data: " + data + "\nStatus: " + status);
					var parsedData = JSON.parse(data)
					console.log(parsedData);
					var downloads = '';
					for (var key in parsedData) {
							console.log("Response: "+key+" "+parsedData[key]);
			        downloads += '<a href="/download/'+parsedData[key]+'" target="_blank"><p><div class="col-sm-4 bg-2"><center>'+key+'</center></div></p>\n</a>\n';
					}
					console.log(downloads);
					$("#download-panel").html(downloads);
				}).fail(function(xhr, textStatus, errorThrown){
					$("#download-panel").html('<div class="col-sm-4 bg-3"><center>FME Failure...</center></div>');
				});
};
