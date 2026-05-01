import "./server.js";
import { getLoginUrl } from "./auth/upstoxAuth.js";

console.log("Execution Service Started");
console.log("Login here:");
console.log(getLoginUrl());