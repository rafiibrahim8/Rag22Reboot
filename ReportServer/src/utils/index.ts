import { Request, Response, NextFunction } from "express";
import morgan from "morgan";
import fs from 'node:fs';
import { AppDataSource } from "./datasource";

export const COOKIE_MAX_AGE = 30 * 24 * 60 * 60 * 1000;

export const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
export const waitUntilDBInitialized =  async (msMaxWait: number, msCoolDown=80) => {
    for (let i = 0; i < msMaxWait; i += 10) {
        if (AppDataSource.isInitialized) {
            await sleep(msCoolDown);
            return true;
        }
        await sleep(10);
    }
    return false;
}
export const errorHandler = async (err:any , req: Request, res: Response, next: NextFunction) => {
    console.log(err);
    res.status(err.status || 500).end();
};

export const fourOhFourHandler = async (req: Request, res: Response, next: NextFunction) => {
    res.status(404).end();
}

export const getRemoteAddress = (req: Request): string => {
    const address = req.headers['cf-connecting-ip'] || req.headers['x-real-ip'] || req.headers['x-forwarded-for'] || req.connection.remoteAddress || 'Failed to get IP';
    return Array.isArray(address) ? address[0] : address;
}

export const getLoggerMiddlewares = () => {
    morgan.token('remote-addr', (req: Request, res: Response) => getRemoteAddress(req));
    const logFormat = `:remote-addr [:date[iso]] :method :url :status ":user-agent"`;
    const logStream = fs.createWriteStream('app.log', { flags: 'a' })
    return [
        morgan(logFormat, { stream: logStream }),
        morgan(logFormat)
    ]
}
