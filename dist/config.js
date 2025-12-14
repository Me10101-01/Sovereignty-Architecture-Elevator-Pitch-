import fs from "fs";
import yaml from "js-yaml";
export function loadConfig() {
    const doc = yaml.load(fs.readFileSync("discovery.yml", "utf8"));
    return doc;
}
export const env = (k, req = true) => {
    const v = process.env[k];
    if (!v && req)
        throw new Error(`Missing env ${k}`);
    return v || "";
};
