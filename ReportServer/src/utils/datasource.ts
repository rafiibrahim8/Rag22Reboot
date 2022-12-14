import { DataSource } from "typeorm";
import { DownloadTokens } from "../entities/DownloadTokens";
import { KeyValuePairs } from "../entities/KeyValuePairs";

export const AppDataSource = new DataSource({
    type: "sqlite",
    database: "database.sqlite",
    entities: [KeyValuePairs, DownloadTokens],
    synchronize: true,
    logging: false,
});

AppDataSource.initialize().catch((error) => {
    console.error("Failed to initialize database");
    console.error(error);
    process.exit(1);
});
