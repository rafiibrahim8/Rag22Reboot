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

export async function getSellCountAndSum() {
    if (!isPgConnected) {
        throw new Error("Postgres is not connected");
    }
    const res = await client.query('SELECT count(is_sold), sum(amount) FROM sell_info where is_sold=true;')
    return {
        count: res.rows[0].count as number,
        sum: res.rows[0].sum as number
    };
}
