import {
    Entity,
    PrimaryGeneratedColumn,
    Column
} from "typeorm";


@Entity({ name: "download_tokens" })
export class DownloadTokens {
    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column({ type: "varchar", unique: true })
    token!: string;

    @Column({ type: "boolean"})
    sold_only!: boolean;

    @Column({ type: "datetime" })
    createdAt!: Date;
}
