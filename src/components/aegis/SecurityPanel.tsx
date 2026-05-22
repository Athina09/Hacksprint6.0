import { useQuery } from "@tanstack/react-query";
import { Shield, Lock, Database, AlertTriangle, CheckCircle2 } from "lucide-react";
import { fetchSecurityStatus } from "@/lib/api";

export function SecurityPanel() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["security-status"],
    queryFn: fetchSecurityStatus,
    retry: 1,
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div className="glass max-w-xl rounded-xl p-4 text-sm text-muted-foreground">
        Checking database encryption status…
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="glass max-w-xl rounded-xl border border-amber-500/30 p-4 text-sm">
        <div className="flex items-center gap-2 text-amber-400">
          <AlertTriangle className="h-4 w-4" />
          <span className="font-medium">Backend offline</span>
        </div>
        <p className="mt-2 text-muted-foreground">
          Start the secure API to enable AES-256 protected databases:
        </p>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-black/40 p-3 text-xs text-emerald-300/90">
          cd backend && python3 -m venv .venv{"\n"}
          source .venv/bin/activate{"\n"}
          pip install -r requirements.txt{"\n"}
          cp ../.env.example ../.env{"\n"}
          uvicorn main:app --host 127.0.0.1 --port 8000
        </pre>
      </div>
    );
  }

  const ok = data.encryption_enabled && data.key_configured;

  return (
    <div className="glass max-w-xl rounded-xl p-4">
      <div className="flex items-center gap-2">
        <Shield className="h-5 w-5 text-emerald-400" />
        <h2 className="text-sm font-semibold text-foreground">Database protection</h2>
        {ok ? (
          <span className="ml-auto flex items-center gap-1 rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">
            <CheckCircle2 className="h-3 w-3" /> ACTIVE
          </span>
        ) : (
          <span className="ml-auto rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold text-amber-400">
            KEY MISSING
          </span>
        )}
      </div>

      <dl className="mt-4 space-y-3 text-sm">
        <div className="flex items-start gap-3">
          <Lock className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div>
            <dt className="text-muted-foreground">Algorithm</dt>
            <dd className="font-mono text-foreground">{data.algorithm}</dd>
            <dd className="text-xs text-muted-foreground">{data.key_derivation}</dd>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Database className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div>
            <dt className="text-muted-foreground">Encrypted stores</dt>
            <dd className="text-foreground">
              {data.databases.join(", ")} ({data.files_encrypted} files)
            </dd>
          </div>
        </div>
      </dl>

      <p className="mt-4 text-xs leading-relaxed text-muted-foreground">
        Autopsy, evidence, timeline, and movement data are encrypted at rest before being
        written to disk. Set <code className="text-emerald-400/90">DATABASE_ENCRYPTION_KEY</code> in{" "}
        <code className="text-emerald-400/90">.env</code> — never commit that file.
      </p>
    </div>
  );
}
