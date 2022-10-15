import crypto from 'node:crypto';
import { AppDataSource } from '../utils/datasource';
import dotenv from 'dotenv';
import { AuthTokens } from '../entities/AuthTokens';
import { waitUntilDBInitialized } from '../utils';

dotenv.config();

async function authDevice() {
    await waitUntilDBInitialized(1000);
    const token = await AppDataSource.getRepository(AuthTokens).save({
        token: crypto.randomBytes(48).toString('base64url'),
        createdAt: new Date(),
    });
    console.log(`Go to: ${process.env.HOST_URL}/auth/${token.token}`);
}

Promise.resolve(authDevice()).catch((err) => {
    console.error(err);
    process.exit(1);
});
