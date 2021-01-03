 
function updateLabel(lastElement) {
    let element = document.getElementById("db-status")
    if(lastElement) {
        element.innerText = "OK";
        element.style.color = "green";
    } else {
        element.innerText = "DOWN";
        element.style.color = "red";
    }
}


function cleanResponse(data) {
    
    var information = [], labels = []
    for(let i = 0; i < data.length; i++) {   
        let value = data[i][0] ? 0: 1
        information.push(value)
        labels.push(data[i][1].split(" ")[1])
    }

    return [information.reverse(), labels.reverse()]
}


function getDBStatus() { 
    var url, response; 
    url = `http://127.0.0.1:5000/monitor/dashboard`

    response = fetch(url); 
    response.then(res => {
        res.json().then(data => {
            let info = cleanResponse(data["body"]);
            let lastElement = info[0].slice(-1)[0];
            updateLabel(lastElement);
        })
    }).catch(error => {
        console.error(`Error: ${response.status} ${response.statusText} ${error}`)
    })
}

setInterval(getDBStatus, 1000)

function loadBinLogs(rows = 10) {
    var url, response; 

    if(rows > 50000){
        alert("Showing just 1000 rows")
        rows = 50000
    }
    url = `http://127.0.0.1:5000/binlogs`

    response = fetch(url, {method: "POST", body: JSON.stringify({"rows": rows})})

    response.then(res => {
        res.json().then(data => {
            let binlogs = data["body"]
            document.getElementById("logs").innerText = binlogs
        })
    }).catch(error => {
        console.error(`Error: ${response.status} ${response.statusText} ${error}`)
    })
}


loadBinLogs()


document.getElementById("showing-logs").addEventListener("change", ()=>{
    let rowsValue = document.getElementById("showing-logs").value; 
    rowsValue = rowsValue ? rowsValue : 10
    loadBinLogs(rowsValue)
})
