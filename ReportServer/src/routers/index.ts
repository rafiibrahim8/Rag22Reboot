import { Router } from "express";
import { getReportURL, getReport } from "../controllers";
import { fourOhFourHandler } from "../utils";

const router = Router();

router.route("/report").get(getReportURL);
router.route("/report/:token").get(getReport);

router.route("*").all(fourOhFourHandler);

export default router;
