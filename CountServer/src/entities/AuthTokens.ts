import {
    Entity,
    PrimaryGeneratedColumn,
    Column
} from "typeorm";


@Entity({ name: "auth_tokens" })
export class AuthTokens {
    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column({ type: "varchar", unique: true })
    token!: string;

    @Column({ type: "datetime" })
    createdAt!: Date;
}
