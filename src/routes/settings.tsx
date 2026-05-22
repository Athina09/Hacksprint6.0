import { createFileRoute } from "@tanstack/react-router";
import { Shell } from "@/components/aegis/Shell";
import { SecurityPanel } from "@/components/aegis/SecurityPanel";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [{ title: "Settings — AEGIS" }, { name: "description", content: "AEGIS platform settings." }] }),
  component: () => (
    <Shell>
      <div className="p-5 space-y-4">
        <h1 className="text-xl font-semibold text-gradient">Settings</h1>
        <SecurityPanel />
        <div className="glass max-w-xl rounded-xl p-4 text-sm text-muted-foreground">
          Theme, AI sensitivity, district scoping and audit logs — coming soon.
        </div>
      </div>
    </Shell>
  ),
});
