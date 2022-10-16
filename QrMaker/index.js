const { PDFDocument, StandardFonts } = require('pdf-lib');
const cliProgress = require('cli-progress');
const QRCode = require('qrcode');
const fs = require('fs');
const crypto = require('crypto');

const TOTAL_GENARATE = 9000;
const TEMPLATE_FILE_NAME = 'template0.pdf'
const PAGE_PER_PDF = 100;

const qrCoor = JSON.parse(fs.readFileSync('resources/img-coor.json').toString('utf-8'));
const slCoor = JSON.parse(fs.readFileSync('resources/sl-coor.json').toString('utf-8'))

async function addImage(qr_codes3, blank_pdf){
    let pdf = await PDFDocument.load(fs.readFileSync(`resources/${TEMPLATE_FILE_NAME}`));
    let slFont = await pdf.embedFont(StandardFonts.CourierBold);
    let page0 = pdf.getPage(0);
    for(let i=0; i<3; i++){
        let qrBuffer = await QRCode.toBuffer(qr_codes3[i], {
            errorCorrectionLevel: 'H', margin: 1, scale: 6
        });
        let pngImage = await pdf.embedPng(qrBuffer);
        page0.drawImage(pngImage, qrCoor[i]);
        page0.drawText(qr_codes3[i].split(':')[2], {
            x: slCoor[i][0].x,
            y: slCoor[i][0].y,
            font: slFont,
            size: 10
        });
        page0.drawText(qr_codes3[i].split(':')[2], {
            x: slCoor[i][1].x,
            y: slCoor[i][1].y,
            font: slFont,
            size: 10
        });

    }
    
    let [newPage] = await blank_pdf.copyPages(pdf, [0]);
    blank_pdf.addPage(newPage);
}

async function buildPDF(qrTexts){
    if(qrTexts.length % (3*PAGE_PER_PDF) != 0){
        console.log('Number of QR codes is not divisible by 3*PAGE_PER_PDF');
        return;
    }
    console.log('Number of QR codes: ', qrTexts.length);
    console.log('Number of PDFs: ', qrTexts.length/3/PAGE_PER_PDF);

    let progressBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
    progressBar.start(qrTexts.length, 0);

    let n = qrTexts.length / (3*PAGE_PER_PDF);
    for(let i=0; i<n; i++){
        let blank_pdf = await PDFDocument.create();
        for(let j=0; j<PAGE_PER_PDF; j++){
            let a = qrTexts[(i*3+0)*PAGE_PER_PDF+j];
            let b = qrTexts[(i*3+1)*PAGE_PER_PDF+j];
            let c = qrTexts[(i*3+2)*PAGE_PER_PDF+j];

            let tqrs = [a, b, c];
            await addImage(tqrs, blank_pdf);
            progressBar.increment(3);
        }

        let start_index = (i*PAGE_PER_PDF*3 + 1).toString().padStart(5, '0');
        let end_index = ((i+1)*PAGE_PER_PDF*3).toString().padStart(5, '0');
        fs.writeFileSync(`receipt/receipt_Q${start_index}-Q${end_index}.pdf`, await blank_pdf.save());
    }
    progressBar.stop();
}

async function genarateCodes(){
    if(!TOTAL_GENARATE){
        throw new Error('TOTAL_GENARATE cannot be 0');
    }
    if(TOTAL_GENARATE % (3*PAGE_PER_PDF) != 0){
        throw new Error('TOTAL_GENARATE is not divisible by (3*PAGE_PER_PDF)');
    }

    let qrTexts = [];
    for(let i=1; i<=TOTAL_GENARATE; i++){
        let randomStr = crypto.randomBytes(14).toString('base64url').substring(0, 18);
        let sl = i.toString().padStart(5, '0');
        qrTexts.push(`rag22r:${randomStr}:Q${sl}`);
    }
    
    fs.writeFileSync('receipt/qrs.json', JSON.stringify(qrTexts, null, 4));
    return qrTexts;
}

async function run(){
    let qrTexts = await genarateCodes();
    await buildPDF(qrTexts);
}

run().then(_ =>{
    console.log('Done');
});
