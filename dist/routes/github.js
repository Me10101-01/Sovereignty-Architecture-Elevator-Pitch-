import crypto from "crypto";
function sigOk(secret, raw, sig) {
    const h = crypto.createHmac("sha256", secret).update(raw).digest("hex");
    return `sha256=${h}` === sig;
}
export function githubRoutes(rest, channelIds, secret) {
    return async (req, res) => {
        const sig = req.get("X-Hub-Signature-256") || "";
        const raw = req.rawBody;
        if (!sigOk(secret, raw, sig))
            return res.status(401).send("bad sig");
        const ev = req.get("X-GitHub-Event");
        const payload = req.body;
        const send = async (channelId, title, desc) => {
            await rest.post(`/channels/${channelId}/messages`, {
                body: { embeds: [{ title, description: desc, color: 3099199 }] }
            });
        };
        if (ev === "pull_request") {
            const a = payload.action;
            const pr = payload.pull_request;
            await send(channelIds.prs, `PR ${a}: #${pr.number} ${pr.title}`, `${pr.user.login} → ${pr.base.repo.full_name}\n${pr.html_url}`);
        }
        else if (ev === "check_suite") {
            const cs = payload.check_suite;
            await send(channelIds.deployments, `Checks ${cs.status}`, `${cs.app.name} → ${cs.conclusion || "pending"}`);
        }
        else if (ev === "push") {
            await send(channelIds.deployments, `Push: ${payload.ref}`, `${payload.repository.full_name}\n${payload.compare}`);
        }
        res.send("ok");
    };
}
