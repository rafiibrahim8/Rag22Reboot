import express from 'express';
import path from 'path';
import cookieParser from 'cookie-parser';
import http from 'http';
import router from './routers';
import { errorHandler, getLoggerMiddlewares } from './utils';
import { setServer } from './utils/socket';

const app = express();
app.set('view engine', 'pug');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(errorHandler);
app.use(getLoggerMiddlewares());
app.use(router)

const server = http.createServer(app);
setServer(server);

export default server;
