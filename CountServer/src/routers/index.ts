import { Router } from "express";
import { authDevice, home, newSell} from "../controllers";
import { authMiddleware } from "../middlewares";
import { fourOhFourHandler } from "../utils";

const router = Router();

router.route("/").get(authMiddleware, home);
router.route("/auth/:token").get(authDevice);

router.route("/new").get(newSell);

router.route("*").all(fourOhFourHandler);

export default router;
