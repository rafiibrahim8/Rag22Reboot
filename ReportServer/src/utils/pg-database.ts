import xlsx, { IJsonSheet, ISettings } from "json-as-xlsx";
import { Client } from "pg";
import dotenv from "dotenv";

dotenv.config();

const client = new Client({
    user: process.env.PG_USER,
    password: process.env.PG_PASSWORD,
    host: process.env.PG_HOST,
    keepAlive: true
});

export let isPgConnected = false;

async function connectDB() {
    await client.connect();
    await client.query("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY;");
    isPgConnected = true;
}

connectDB();

export async function genarateSellReport(soldOnly = false) {
    if (!isPgConnected) {
        throw new Error("Postgres is not connected");
    }
    let soldOnlyStr = ' ';
    if (soldOnly) {
        soldOnlyStr = ' WHERE is_sold=true ';
    }
    let query = `SELECT qr_sl, is_sold, datetime, buyer_name, buyer_phone, amount, seller, editor, edits, total_edits, epoch FROM sell_info${soldOnlyStr}ORDER BY qr_sl;`;
    let res = (await client.query(query)).rows;
    res = res.map((row) => {
        row.datetime = row.datetime? new Date(row.datetime).toLocaleString('en-UK', { timeZone: 'Asia/Dhaka' }) : row.datetime;
        return row;
    });

    const data: IJsonSheet[] = [{
        sheet: "Sell Report",
        columns: [
            { label: "qr_sl", value: "qr_sl" },
            { label: "is_sold", value: "is_sold" },
            { label: "datetime", value: "datetime" },
            { label: "buyer_name", value: "buyer_name" },
            { label: "buyer_phone", value: "buyer_phone" },
            { label: "amount", value: "amount" },
            { label: "seller", value: "seller" },
            { label: "editor", value: "editor" },
            { label: "edits", value: "edits" },
            { label: "total_edits", value: "total_edits" },
            { label: "epoch", value: "epoch" },
        ],
        content: res
    }];
    const settings: ISettings = {
        writeOptions: {
            type: "buffer",
            bookType: "xlsx",
        },
    }
    const buffer = await xlsx(data, settings);
    return buffer;
}

