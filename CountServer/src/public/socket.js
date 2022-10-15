let socket = io();
socket.on('count', (data)=>{
    console.log(data.count);
    document.getElementById('count').innerHTML = `${data.count}`;
});

