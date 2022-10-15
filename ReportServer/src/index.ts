import dotenv from 'dotenv';
import app from "./app";

dotenv.config();
const port = parseInt(process.env.PORT || '3000');
const bind = process.env.BIND_TO || '127.0.0.1'

app.listen(port, bind, () => {
    console.log(`Binded to ${bind}:${port}`);
});
