import express from 'express';
import router from './routers';
import { errorHandler, getLoggerMiddlewares } from './utils';

const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(errorHandler);
app.use(getLoggerMiddlewares());
app.use(router)

export default app;
