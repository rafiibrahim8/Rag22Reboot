import { Server } from "socket.io"
import { DefaultEventsMap } from "socket.io/dist/typed-events"
import { AuthDevices } from "../entities/AuthDevices";
import { AppDataSource } from "./datasource";
import { getSellCountAndSum } from "./pg-database";

const parseCookie = (str: string | undefined) => {
    if (!str) return {};
    let cookes: any = {};
    str.split(';').forEach((cookie) => {
        const [key, value] = cookie.split('=');
        cookes[decodeURIComponent(key.trim())] = decodeURIComponent(value.trim());
    });
    return cookes;
};

let io: Server<DefaultEventsMap, DefaultEventsMap, DefaultEventsMap, any>;

export function setServer(server: any) {
    io = new Server(server);
    io.use(async (socket, next) => {

        const cookie = parseCookie(socket.handshake.headers.cookie).auth;
        if (!cookie) {
            next(new Error('No cookie'));
            return;
        }
        const authDevice = await AppDataSource.getRepository(AuthDevices).findOne({ where: { cookie } });
        if (!authDevice) {
            next(new Error('No auth'));
            return;
        }
        next();
    });

    io.on('connection', async (socket) => {
        io.emit('info', await getSellCountAndSum());
    });
}

export async function emitCount() {
    io.emit('info', await getSellCountAndSum());
}
