import type { Request, Response } from "express"
import crypto from 'node:crypto';
import { DownloadTokens } from "../entities/DownloadTokens";
import { AppDataSource } from "../utils/datasource";
import { genarateSellReport } from "../utils/pg-database";

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
    const token = await AppDataSource.getRepository(DownloadTokens).findOne({where: {token: req.params.token}});
    const deleted = await AppDataSource.getRepository(DownloadTokens).delete({ token: req.params.token });
    if (!deleted.affected) {
        res.status(403).end();
        return;
    }
    const sold_only = token?.sold_only;
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
export {
    getReportURL,
    getReport
}
