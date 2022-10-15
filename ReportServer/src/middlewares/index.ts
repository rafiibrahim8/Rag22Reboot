import type { Request, Response, NextFunction } from "express";
import { AuthDevices } from "../entities/AuthDevices";
import { AppDataSource } from "../utils/datasource";

export const authMiddleware =  async (req: Request, res: Response, next: NextFunction) => {
    const cookie = req.cookies['auth'];
    if(!cookie) {
        res.status(403).end();
        return;
    }
    const authDevice = await AppDataSource.getRepository(AuthDevices).findOne({ where: { cookie } });
    if(!authDevice) {
        res.status(403).end();
        return;
    }
    next();
};
