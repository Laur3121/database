// https://zenn.dev/sdkfz181tiger/articles/096dfb74d485db

const codes = [];

window.onload = (e) => {

	let video  = document.createElement("video");
	let canvas = document.getElementById("canvas");
	let ctx    = canvas.getContext("2d");
	let msg    = document.getElementById("msg");

	const userMedia = {video: {facingMode: "environment"}};
	navigator.mediaDevices.getUserMedia(userMedia).then((stream)=>{
		video.srcObject = stream;
		video.setAttribute("playsinline", true);
		video.play();
		startTick();
	});

    function startTick() {
		msg.innerText = "Loading video...";
		if(video.readyState === video.HAVE_ENOUGH_DATA){
			canvas.height = video.videoHeight;
			canvas.width = video.videoWidth;
			ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
			// let img = ctx.getImageData(0, 0, canvas.width, canvas.height);

         while(true) {
            let img = ctx.getImageData(0, 0, canvas.width, canvas.height);
             code = jsQR(img.data, img.width, img.height, { inversionAttempts: "dontInvert" })
             
                console.log(code)
                if (!code) break;
             // if(code){
			 if (!codes.includes(code.data)) {
				 codes.push(code.data);
				 get_data(code.data)
}
            //  codes.push(code.data)
                    drawRect(code.location);
                    //  }
                }
                // msg.innerText =codes
          
            

		}
		setTimeout(startTick, 10);
	}

	
      document.getElementById('resetButton').addEventListener('click', () => {
            // クリック時に実行する処理
		  console.log("リセット")
		   codes = []
        });



	function drawRect(location){
        	ctx.beginPath();
        ctx.moveTo(location.topLeftCorner.x, location.topLeftCorner.y);
        ctx.lineTo(  location.topRightCorner.x,   location.topRightCorner.y);
          ctx.lineTo(  location.bottomRightCorner.x,   location.bottomRightCorner.y);
        ctx.lineTo(location.bottomLeftCorner.x, location.bottomLeftCorner.y);
          ctx.lineTo(location.bottomLeftCorner.x, location.bottomLeftCorner.y);
  ctx.fillStyle = "red";
  ctx.fill();
        // ctx.stroke();
		// drawLine(location.topLeftCorner,     location.topRightCorner);
		// drawLine(location.topRightCorner,    location.bottomRightCorner);
		// drawLine(location.bottomRightCorner, location.bottomLeftCorner);
		// drawLine(location.bottomLeftCorner,  location.topLeftCorner);
	}

	function drawLine(begin, end){
		ctx.lineWidth = 4;
		ctx.strokeStyle = "#FF3B58";
		ctx.beginPath();
		ctx.moveTo(begin.x, begin.y);
		ctx.lineTo(end.x, end.y);
        ctx.fillStyle = "blue";
        // ctx.stroke();
        // ctx.fill();
	}


	function get_data(id) {
		console.log( JSON.stringify(id),"を問い合わせ")
		   fetch('/api/get_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(id)
            })
            .then(response => response.json())
			   .then(data => {
				   console.log("帰ってきた", data)
				   msg += data;
				   msg += "\n";
                // document.getElementById('result').innerText = 'サーバーからの返答: ' + JSON.stringify(data);
            })
            .catch(error => console.error('Error:', error));
	}
}