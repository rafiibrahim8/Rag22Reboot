let socket = io();
const formatter = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'BDT',
    minimumFractionDigits: 0
});
socket.on('info', (data)=>{
    console.log(data.count);
    document.getElementById('count').innerHTML = `${data.count}`;
    document.getElementById('sum').innerHTML = `${formatter.format(data.sum).replace('BDT', '৳')}`;
});
