import Fastify from "fastify";
import { connect } from "./lib/database.js";

const app = Fastify();
const db = await connect(process.env.DATABASE_URL ?? "");

app.get("/boards", async () => db.listBoards());

await app.listen({ port: Number(process.env.PORT ?? 3000) });
