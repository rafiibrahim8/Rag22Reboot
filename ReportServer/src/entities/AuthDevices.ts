import {
    Entity,
    PrimaryGeneratedColumn,
    Column
} from "typeorm";


@Entity({ name: "auth_devices" })
export class AuthDevices {
    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column({ type: "varchar", unique: true })
    cookie!: string;

    @Column({ type: "datetime" })
    createdAt!: Date;
}
