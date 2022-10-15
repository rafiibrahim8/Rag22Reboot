import type { Request, Response } from "express"
import crypto from 'node:crypto';
import { AuthDevices } from "../entities/AuthDevices";
import { AuthTokens } from "../entities/AuthTokens";
import { DownloadTokens } from "../entities/DownloadTokens";
import { COOKIE_MAX_AGE } from "../utils";
import { AppDataSource } from "../utils/datasource";
import { genarateSellReport } from "../utils/pg-database";
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

const getReportURL = async (req: Request, res: Response) => {
    if (req.query.token !== process.env.REPORT_TOKEN) {
        res.status(403).end();
        return;
    }
    const token = await AppDataSource.getRepository(DownloadTokens).save({
        token: crypto.randomBytes(48).toString('base64url'),
        createdAt: new Date(),
        sold_only: !! parseInt(req.query.sold_only as string)
    });
    res.end(`${process.env.HOST_URL}/report/${token.token}`);
}

const getReport = async (req: Request, res: Response) => {
    const token = await AppDataSource.getRepository(DownloadTokens).delete({ token: req.params.token });
    if (!token.affected) {
        res.status(403).end();
        return;
    }
    const sold_only = token.raw[0].sold_only;
    const buffer = await genarateSellReport(sold_only);
    if(!buffer) {
        res.status(500).end();
        return;
    }
    const filename = `sell-report-${new Date().toLocaleString("en-UK", { timeZone: "Asia/Dhaka" }).replace(/\/|:/g,'-').replace(', ', 'T')}.xlsx`;
    res.writeHead(200, {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename=${filename}`,
    });
    res.end(buffer);
}

const newSell = async (req: Request, res: Response) => {
    if(req.query.token !== process.env.REPORT_TOKEN) {
        res.status(403).end();
        return;
    }
    emitCount();
    res.end('ok');
}

export {
    home,
    authDevice,
    getReportURL,
    getReport,
    newSell
}
