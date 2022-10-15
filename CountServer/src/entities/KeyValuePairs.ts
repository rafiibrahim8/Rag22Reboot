import {
    Entity,
    PrimaryGeneratedColumn,
    Column
} from "typeorm";


@Entity({ name: "key_value_pairs" })
export class KeyValuePairs {
    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column({ type: "varchar", unique: true })
    key!: string;

    @Column({ type: "simple-json" })
    value!: object;
}
