import type { Request, Response } from "express"
import crypto from 'node:crypto';
import { AuthDevices } from "../entities/AuthDevices";
import { AuthTokens } from "../entities/AuthTokens";
import { COOKIE_MAX_AGE } from "../utils";
import { AppDataSource } from "../utils/datasource";
import { emitCount } from "../utils/socket";

const home = async (req: Request, res: Response) => {
    res.render('index');
}

const authDevice = async (req: Request, res: Response) => {
    const token = await AppDataSource.getRepository(AuthTokens).delete({ token: req.params.token });
    if (!token.affected) {
        res.status(403).end();
        return;
    }
    const cookie = await AppDataSource.getRepository(AuthDevices).save({
        cookie: crypto.randomBytes(48).toString('base64url'),
        createdAt: new Date()
    });
    res.cookie('auth', cookie.cookie, { maxAge: COOKIE_MAX_AGE, httpOnly: true }).redirect('/');
}

const newSell = async (req: Request, res: Response) => {
    if(req.query.token !== process.env.PING_TOKEN) {
        res.status(403).end();
        return;
    }
    emitCount();
    res.end('ok');
}

export {
    home,
    authDevice,
    newSell
}
