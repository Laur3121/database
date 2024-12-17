// https://zenn.dev/sdkfz181tiger/articles/096dfb74d485db

const codes = [];  //呼んだURLをここにためる

//これの中で書かないとHTML要素が生成される前に実行されてgetEleentが死ぬ
window.onload = (e) => {

	//要素を取得
	let video  = document.createElement("video");
	let canvas = document.getElementById("canvas");
	let ctx    = canvas.getContext("2d");
	let msg    = document.getElementById("msg");

	//カメラの準備が出来たらスタート
	const userMedia = {video: {facingMode: "environment"}};
	navigator.mediaDevices.getUserMedia(userMedia).then((stream)=>{
		video.srcObject = stream;
		video.setAttribute("playsinline", true);
		video.play();
		startTick();
	});

    function startTick() {
		/* msg.innerText = "Loading video..."; */
		if(video.readyState === video.HAVE_ENOUGH_DATA){
			canvas.height = video.videoHeight;
			canvas.width = video.videoWidth;
			ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
			// let img = ctx.getImageData(0, 0, canvas.width, canvas.height);

			while (true) {

			 //canvasからコピーしてjsqrに渡す
            let img = ctx.getImageData(0, 0, canvas.width, canvas.height);
             code = jsQR(img.data, img.width, img.height, { inversionAttempts: "dontInvert" })
             
			 console.log(code)
			 
			 //無限ループだがコードを読める場所がなくなったらそのフレームを終了
                if (!code) break;
			 // if(code){
			 //前呼んだ奴は聞かないように
			 if (!codes.includes(code.data)) {
				 codes.push(code.data);
				 get_data(code.data)
}
            //  codes.push(code.data)
			//前QRコードを詠んだ場所を読まないように塗りつぶし
                    drawRect(code.location);
                    //  }
                }
                // msg.innerText =codes
          
            

		}
		//10ms待ってこの関数を読んでつぎフレームへ
		setTimeout(startTick, 10);
	}

	//リセットボタン
      document.getElementById('resetButton').addEventListener('click', () => {
         
		  console.log("リセット")
		 codes.length = 0; 
		   msg ="";
           const table = document.getElementById('data-table').getElementsByTagName('tbody')[0];

table.innerHTML = '';
        });


//前QRコードを詠んだ場所を読まないように塗りつぶし
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
//没
	// function drawLine(begin, end){
	// 	ctx.lineWidth = 4;
	// 	ctx.strokeStyle = "#FF3B58";
	// 	ctx.beginPath();
	// 	ctx.moveTo(begin.x, begin.y);
	// 	ctx.lineTo(end.x, end.y);
    //     ctx.fillStyle = "blue";
    //     // ctx.stroke();
    //     // ctx.fill();
	// }


// fetchでURLを問い合わせる
function get_data(id) {
    console.log(JSON.stringify(id), "を問い合わせ");
    fetch('/api/get_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(id)
    })
    .then(response => response.json())
    .then(data => {
        console.log("帰ってきた", data);

        // データを表に追加
        addRowToTable(data);

        /* // msgにもデバッグ用に追記
        msg.innerText += JSON.stringify(data, null, 2) + "\n"; */
    })
    .catch(error => console.error('Error:', error));
}

// 表に行を追加する関数(わかんなくなったらhtmlの方見る)
function addRowToTable(data) {
    const table = document.getElementById('data-table').getElementsByTagName('tbody')[0];
    
    // 新しい行を作成用
    const newRow = table.insertRow();

    // 各セルを作成し、データを埋め込むやつ
    const cellId = newRow.insertCell(0);
    const cellProductName = newRow.insertCell(1);
    const cellManufacturer = newRow.insertCell(2);
    const cellDescription = newRow.insertCell(3);
    const cellPurchaseDate = newRow.insertCell(4);

    cellId.textContent = data.id || "N/A"; //ない場合はN/Aになる
    cellProductName.textContent = data.product_name || "N/A";
    cellManufacturer.textContent = data.manufacturer || "N/A";
    cellDescription.textContent = data.description || "N/A";
    cellPurchaseDate.textContent = data.purchase_date || "N/A";
}


	
};
