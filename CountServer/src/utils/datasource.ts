import { DataSource } from "typeorm";
import { AuthDevices } from "../entities/AuthDevices";
import { AuthTokens } from "../entities/AuthTokens";
import { KeyValuePairs } from "../entities/KeyValuePairs";

export const AppDataSource = new DataSource({
    type: "sqlite",
    database: "database.sqlite",
    entities: [KeyValuePairs, AuthDevices, AuthTokens],
    synchronize: true,
    logging: false,
});

AppDataSource.initialize().catch((error) => {
    console.error("Failed to initialize database");
    console.error(error);
    process.exit(1);
});
