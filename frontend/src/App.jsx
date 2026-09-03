import { useEffect, useMemo, useState } from "react";
import AnalysisModal from "./AnalysisModal";
import ResultsModal from "./ResultsModal";

const API_URL = "http://127.0.0.1:8001";

const NAV_ITEMS = [
  ["Overview", "⌂"],
  ["Evidence", "◈"],
  ["Timeline", "◷"],
  ["Theories", "◇"],
  ["Red Team", "⚠"],
  ["Investigation Graph", "⌘"],
];

/* ============================================================= */
/* APP */
/* ============================================================= */

function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState("");
  const [caseFile, setCaseFile] = useState(null);
  const [caseText, setCaseText] = useState("");
  const [fileInputKey, setFileInputKey] = useState(0);

  // holds the real backend response while the AnalysisModal's
  // scripted terminal log is still playing out
  const [pendingResult, setPendingResult] = useState(null);
  const [apiReady, setApiReady] = useState(false);

  const theories = result?.theories || [];
  const evidence = result?.evidence || [];
  const timeline = result?.timeline || [];
  const redTeam = result?.red_team;
  const nextEvidence = result?.next_best_evidence;

  /* ========================================================= */
  /* FILE UPLOAD — .txt / .md read locally, .pdf / .docx go     */
  /* through the backend extractor at /api/files/extract        */
  /* ========================================================= */

  async function handleFileUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setError("");
    setResult(null);

    const allowed = [".txt", ".md", ".pdf", ".docx"];
    const ext = "." + file.name.split(".").pop().toLowerCase();

    if (!allowed.includes(ext)) {
      setError("LUNA accepts .txt, .md, .pdf, or .docx case files.");
      setCaseFile(null);
      setCaseText("");
      return;
    }

    try {
      let text = "";

      if (ext === ".txt" || ext === ".md") {
        text = await file.text();
      } else {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_URL}/api/files/extract`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
          throw new Error(
            data?.detail || "LUNA could not read this file."
          );
        }

        text = data?.text || "";
      }

      if (!text.trim()) {
        setError("The uploaded case file is empty.");
        setCaseFile(null);
        setCaseText("");
        return;
      }

      setCaseFile(file);
      setCaseText(text);
      setActivePage("Overview");
    } catch (err) {
      console.error(err);
      setError(
        err?.message || "LUNA could not read the uploaded case file."
      );
    }
  }

  /* ========================================================= */
  /* ANALYZE CASE                                               */
  /* ========================================================= */

  async function analyzeCase() {
    if (!caseText.trim()) {
      setError("Upload a case file before starting the investigation.");
      return;
    }

    setError("");
    setResult(null);
    setShowResults(false);
    setPendingResult(null);
    setApiReady(false);
    setActivePage("Overview");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/investigate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ case_text: caseText }),
      });

      let data = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        throw new Error(
          data?.detail || `LUNA backend returned HTTP ${response.status}.`
        );
      }

      if (!data) {
        throw new Error("LUNA returned an empty investigation result.");
      }

      // Real data is here -- but we let AnalysisModal's own log
      // animation finish before unlocking "VIEW RESULTS".
      setPendingResult(data);
      setApiReady(true);
    } catch (err) {
      console.error("LUNA investigation error:", err);

      setError(
        err?.message || "Unable to connect to the LUNA reasoning engine."
      );

      // Abort the popup immediately on a hard failure -- no point
      // making the user watch the animation play out for nothing.
      setLoading(false);
      setPendingResult(null);
      setApiReady(false);
    }
  }

  /* ========================================================= */
  /* Called when the user dismisses the AnalysisModal           */
  /* ========================================================= */

  function handleAnalysisComplete() {
    setResult(pendingResult);
    setLoading(false);
    setShowResults(true);
  }

  /* ========================================================= */
  /* CLEAR CASE                                                 */
  /* ========================================================= */

  function clearCase() {
    setCaseFile(null);
    setCaseText("");
    setResult(null);
    setShowResults(false);
    setPendingResult(null);
    setApiReady(false);
    setError("");
    setLoading(false);
    setActivePage("Overview");

    setFileInputKey((value) => value + 1);
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#030303] text-white selection:bg-red-500/30">
      <Background />

      <div className="relative z-10 flex min-h-screen">

        {/* ===================================================== */}
        {/* SIDEBAR */}
        {/* ===================================================== */}

        <aside className="hidden w-[275px] shrink-0 border-r border-red-500/[0.09] bg-[#040404]/90 backdrop-blur-2xl lg:flex lg:flex-col">

          <div className="relative border-b border-red-500/[0.09] p-6">
            <CornerBrackets />

            <Logo />

            <div className="mt-7 flex items-center justify-between font-mono text-[8px] uppercase tracking-[0.25em]">
              <span className="text-neutral-800">LUNA NETWORK</span>
              <span className="text-red-500/50">01.0</span>
            </div>
          </div>

          <div className="px-4 py-7">
            <div className="mb-4 flex items-center justify-between px-3">
              <div className="text-[8px] font-bold uppercase tracking-[0.35em] text-neutral-700">
                Investigation
              </div>

              <div className="font-mono text-[8px] text-red-500/40">
                06 MODULES
              </div>
            </div>

            <div className="space-y-1.5">
              {NAV_ITEMS.map(([name, icon], index) => (
                <button
                  key={name}
                  onClick={() => setActivePage(name)}
                  className={`group relative flex w-full items-center gap-3 overflow-hidden rounded-xl border px-3 py-3.5 text-left text-sm transition-all duration-300 ${
                    activePage === name
                      ? "border-red-500/20 bg-red-500/[0.065] text-red-400 shadow-[inset_2px_0_0_rgba(239,68,68,.9)]"
                      : "border-transparent text-neutral-600 hover:border-red-500/[0.08] hover:bg-white/[0.02] hover:text-neutral-300"
                  }`}
                >
                  {activePage === name && (
                    <span className="absolute right-0 top-0 h-full w-20 bg-gradient-to-l from-red-500/[0.06] to-transparent" />
                  )}

                  <span className="w-5 font-mono text-[11px] text-neutral-700">
                    0{index + 1}
                  </span>

                  <span
                    className={`relative flex h-7 w-7 items-center justify-center rounded-lg border text-sm transition ${
                      activePage === name
                        ? "border-red-500/20 bg-red-500/[0.08] text-red-400"
                        : "border-white/[0.04] text-neutral-700 group-hover:border-red-500/10 group-hover:text-red-500"
                    }`}
                  >
                    {icon}
                  </span>

                  <span className="relative">{name}</span>

                  {activePage === name && (
                    <span className="relative ml-auto h-1.5 w-1.5 rounded-full bg-red-500 shadow-[0_0_12px_rgba(239,68,68,.9)]" />
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-auto space-y-4 p-5">
            <Telemetry />
            <SystemStatus />
          </div>
        </aside>

        {/* ===================================================== */}
        {/* MAIN */}
        {/* ===================================================== */}

        <main className="min-w-0 flex-1">

          <header className="sticky top-0 z-30 flex h-[76px] items-center justify-between border-b border-red-500/[0.08] bg-[#030303]/80 px-6 backdrop-blur-2xl md:px-10">

            <div className="flex items-center gap-5">
              <div className="hidden h-8 w-px bg-red-500/20 sm:block" />

              <div>
                <div className="flex items-center gap-2 text-[8px] uppercase tracking-[0.35em] text-neutral-700">
                  <span className="h-1 w-1 rounded-full bg-red-500" />
                  Active Investigation
                </div>

                <div className="mt-1.5 flex items-center gap-3">
                  <span className="font-mono text-xs tracking-wider text-neutral-300">
                    {result?.case_id || "CASE-LUNA-001"}
                  </span>

                  <span className="rounded-sm border border-red-500/15 bg-red-500/[0.03] px-2 py-0.5 text-[7px] font-bold uppercase tracking-[0.2em] text-red-500/70">
                    CLASSIFIED
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">

              <div className="hidden text-right md:block">
                <div className="font-mono text-[7px] uppercase tracking-[0.3em] text-neutral-800">
                  Reasoning Engine
                </div>

                <div className="mt-1 text-[10px] text-neutral-600">
                  GEMINI / LUNA CORE
                </div>
              </div>

              <div className="h-7 w-px bg-white/[0.05]" />

              <div className="flex items-center gap-2 rounded-full border border-red-500/15 bg-red-500/[0.035] px-3.5 py-2">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,.8)]" />
                <span className="text-[8px] font-bold tracking-[0.2em] text-red-400">
                  ONLINE
                </span>
              </div>
            </div>
          </header>

          <div className="mx-auto max-w-[1600px] px-5 py-8 md:px-10 md:py-10">

            <PageHeader activePage={activePage} result={result} />

            {/* CASE INPUT */}

            {activePage === "Overview" && !loading && (
              <CaseInput
                caseFile={caseFile}
                caseText={caseText}
                fileInputKey={fileInputKey}
                onUpload={handleFileUpload}
                onAnalyze={analyzeCase}
                onClear={clearCase}
                disabled={loading}
              />
            )}

            {/* OVERVIEW */}

            {!loading && activePage === "Overview" && (
              <Overview
                result={result}
                theories={theories}
                redTeam={redTeam}
                nextEvidence={nextEvidence}
                evidence={evidence}
                error={error}
                runInvestigation={analyzeCase}
                onReopenResults={() => setShowResults(true)}
              />
            )}

            {/* EVIDENCE */}

            {!loading && activePage === "Evidence" && (
              <EvidenceView evidence={evidence} />
            )}

            {/* TIMELINE */}

            {!loading && activePage === "Timeline" && (
              <TimelineView timeline={timeline} />
            )}

            {/* THEORIES */}

            {!loading && activePage === "Theories" && (
              <TheoriesView theories={theories} />
            )}

            {/* RED TEAM */}

            {!loading && activePage === "Red Team" && (
              <RedTeamView redTeam={redTeam} />
            )}

            {/* GRAPH */}

            {!loading && activePage === "Investigation Graph" && (
              <GraphView
                theories={theories}
                redTeam={redTeam}
                nextEvidence={nextEvidence}
              />
            )}

          </div>
        </main>
      </div>

      {/* ===================================================== */}
      {/* ANALYSIS POPUP -- shown the moment "Analyze Case" fires */}
      {/* ===================================================== */}

      {loading && (
        <AnalysisModal
          fileName={caseFile?.name}
          charCount={caseText.length}
          ready={apiReady}
          onComplete={handleAnalysisComplete}
        />
      )}

      {/* ===================================================== */}
      {/* RESULTS POPUP -- opens automatically once analysis     */}
      {/* completes; can be reopened from the Overview page      */}
      {/* ===================================================== */}

      {showResults && result && (
        <ResultsModal
          open={showResults}
          result={result}
          onClose={() => setShowResults(false)}
        />
      )}
    </div>
  );
}

/* ============================================================= */
/* CASE INPUT */
/* ============================================================= */

function CaseInput({
  caseFile,
  caseText,
  fileInputKey,
  onUpload,
  onAnalyze,
  onClear,
  disabled,
}) {
  return (
    <section className="relative mb-6 overflow-hidden rounded-3xl border border-red-500/[0.12] bg-[#060606] shadow-[0_0_80px_rgba(100,0,0,.05)]">

      <CornerBrackets />

      <div className="relative p-6 md:p-7">

        <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">

          <div>
            <div className="flex items-center gap-2 text-[8px] font-bold uppercase tracking-[0.35em] text-red-500/70">
              <span className="h-px w-5 bg-red-500/40" />
              Case Ingestion
            </div>

            <h2 className="mt-2 text-xl font-black">
              Upload Case File
            </h2>

            <p className="mt-1 text-[9px] text-neutral-700">
              Supply a case file (.txt, .md, .pdf, .docx) and LUNA will reconstruct and investigate it.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">

            <label className="group relative flex cursor-pointer items-center gap-3 overflow-hidden rounded-xl border border-red-500/20 bg-red-500/[0.055] px-5 py-3 text-[10px] font-black tracking-wider text-red-400 transition hover:border-red-500/35 hover:bg-red-500/[0.09]">

              <input
                key={fileInputKey}
                type="file"
                accept=".txt,.md,.pdf,.docx,text/plain,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="hidden"
                onChange={onUpload}
                disabled={disabled}
              />

              <span>↑</span>

              <span>{caseFile ? "CHANGE CASE" : "UPLOAD CASE"}</span>

            </label>

            {caseFile && (
              <button
                onClick={onClear}
                disabled={disabled}
                className="rounded-xl border border-white/[0.07] bg-white/[0.018] px-5 py-3 text-[10px] font-bold tracking-wider text-neutral-500 transition hover:border-red-500/20 hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-40"
              >
                CLEAR
              </button>
            )}

          </div>
        </div>

        {caseFile && (
          <div className="mt-5 flex flex-col gap-4 rounded-2xl border border-white/[0.06] bg-black/30 p-5 md:flex-row md:items-center md:justify-between">

            <div className="min-w-0">

              <div className="font-mono text-[8px] uppercase tracking-[0.25em] text-neutral-800">
                Loaded Case File
              </div>

              <div className="mt-2 truncate text-sm font-bold text-neutral-300">
                {caseFile.name}
              </div>

              <div className="mt-1 font-mono text-[8px] text-neutral-700">
                {caseText.length.toLocaleString()} CHARACTERS
              </div>

            </div>

            <button
              onClick={onAnalyze}
              disabled={disabled || !caseText.trim()}
              className="group relative flex shrink-0 items-center justify-center gap-3 overflow-hidden rounded-xl bg-red-600 px-7 py-3.5 text-[10px] font-black tracking-wider text-white shadow-[0_0_30px_rgba(180,0,0,.18)] transition hover:bg-red-500 hover:shadow-[0_0_45px_rgba(220,20,20,.25)] disabled:cursor-not-allowed disabled:opacity-40"
            >
              <span className="relative">▶</span>
              <span className="relative">ANALYZE CASE</span>
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

/* ============================================================= */
/* BACKGROUND */
/* ============================================================= */

function Background() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div className="absolute left-[-20%] top-[-25%] h-[900px] w-[900px] rounded-full bg-red-700/[0.035] blur-[180px]" />
      <div className="absolute bottom-[-25%] right-[-20%] h-[900px] w-[900px] rounded-full bg-red-900/[0.045] blur-[180px]" />

      <div
        className="absolute inset-0 opacity-[0.032]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,.7) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.7) 1px, transparent 1px)
          `,
          backgroundSize: "48px 48px",
        }}
      />

      <div
        className="absolute inset-0 opacity-[0.018]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(239,68,68,.7) 1px, transparent 1px),
            linear-gradient(90deg, rgba(239,68,68,.7) 1px, transparent 1px)
          `,
          backgroundSize: "12px 12px",
        }}
      />

      <div
        className="absolute inset-0 opacity-[0.025]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(255,255,255,.4) 4px)",
        }}
      />

      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_30%,rgba(0,0,0,.58)_100%)]" />
      <div className="absolute left-0 right-0 top-0 h-px bg-gradient-to-r from-transparent via-red-500/30 to-transparent" />
    </div>
  );
}

/* ============================================================= */
/* CORNER BRACKETS */
/* ============================================================= */

function CornerBrackets() {
  return (
    <>
      <span className="pointer-events-none absolute left-0 top-0 h-3 w-3 border-l border-t border-red-500/30" />
      <span className="pointer-events-none absolute right-0 top-0 h-3 w-3 border-r border-t border-red-500/30" />
      <span className="pointer-events-none absolute bottom-0 left-0 h-3 w-3 border-b border-l border-red-500/30" />
      <span className="pointer-events-none absolute bottom-0 right-0 h-3 w-3 border-b border-r border-red-500/30" />
    </>
  );
}

/* ============================================================= */
/* LOGO */
/* ============================================================= */

function Logo() {
  return (
    <div className="group relative flex items-center gap-4">
      <div className="relative flex h-12 w-12 items-center justify-center">
        <div className="absolute inset-0 rounded-xl border border-red-500/30" />
        <div className="absolute inset-[4px] rounded-lg border border-red-500/10" />
        <span className="absolute left-0 top-0 h-2 w-2 border-l border-t border-red-500" />
        <span className="absolute right-0 top-0 h-2 w-2 border-r border-t border-red-500" />
        <span className="absolute bottom-0 left-0 h-2 w-2 border-b border-l border-red-500" />
        <span className="absolute bottom-0 right-0 h-2 w-2 border-b border-r border-red-500" />
        <span className="text-lg font-black text-red-400">L</span>
        <span className="absolute right-0 top-0 h-1.5 w-1.5 rounded-full bg-red-500 shadow-[0_0_12px_rgba(239,68,68,.9)]" />
      </div>

      <div>
        <div className="flex items-center gap-2">
          <span
            className="text-xl font-black tracking-[0.25em] luna-glitch"
            data-text="LUNA"
          >
            LUNA
          </span>
          <span className="font-mono text-[7px] text-red-500/50">AI</span>
        </div>

        <div className="mt-1 text-[7px] uppercase tracking-[0.3em] text-neutral-700">
          Investigative Reasoning
        </div>
      </div>
    </div>
  );
}

/* ============================================================= */
/* TELEMETRY */
/* ============================================================= */

function Telemetry() {
  return (
    <div className="rounded-xl border border-white/[0.05] bg-white/[0.012] p-4">
      <div className="mb-4 flex items-center justify-between">
        <span className="font-mono text-[7px] uppercase tracking-[0.25em] text-neutral-800">
          Core Telemetry
        </span>
        <span className="font-mono text-[7px] text-red-500/40">LIVE</span>
      </div>

      <div className="space-y-3">
        {[
          ["NEURAL", "98.4%", 98],
          ["MEMORY", "72.1%", 72],
          ["SIGNAL", "91.8%", 92],
        ].map(([label, value, width]) => (
          <div key={label}>
            <div className="mb-1.5 flex justify-between font-mono text-[7px]">
              <span className="text-neutral-700">{label}</span>
              <span className="text-neutral-600">{value}</span>
            </div>

            <div className="h-[2px] overflow-hidden bg-white/[0.04]">
              <div
                className="h-full bg-red-500/60 transition-all duration-1000"
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============================================================= */
/* SYSTEM STATUS */
/* ============================================================= */

function SystemStatus() {
  return (
    <div className="relative overflow-hidden rounded-xl border border-red-500/[0.08] bg-red-500/[0.025] p-4">
      <CornerBrackets />

      <div className="flex items-center justify-between">
        <span className="text-[8px] uppercase tracking-[0.25em] text-neutral-700">
          Core Status
        </span>
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,.8)]" />
      </div>

      <div className="mt-3 text-[10px] font-semibold tracking-wide text-red-400">
        ALL SYSTEMS OPERATIONAL
      </div>

      <div className="mt-2 font-mono text-[8px] text-neutral-800">
        LUNA CORE / 1.0.0
      </div>
    </div>
  );
}

/* ============================================================= */
/* PAGE HEADER */
/* ============================================================= */

function PageHeader({ activePage, result }) {
  return (
    <div className="mb-8 flex items-end justify-between">
      <div>
        <div className="flex items-center gap-2 text-[8px] font-bold uppercase tracking-[0.35em] text-red-500/70">
          <span className="h-px w-5 bg-red-500/40" />
          LUNA / {activePage.toUpperCase()}
        </div>

        <h1 className="mt-3 text-3xl font-black tracking-tight md:text-4xl">
          {activePage}
        </h1>

        <p className="mt-2 text-[11px] text-neutral-700">
          {result?.incident || "Investigative intelligence workspace."}
        </p>
      </div>

      <div className="hidden text-right md:block">
        <div className="font-mono text-[7px] uppercase tracking-[0.3em] text-neutral-800">
          SYSTEM TIME
        </div>
        <div className="mt-1 font-mono text-[10px] text-neutral-600">
          {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

/* ============================================================= */
/* OVERVIEW */
/* ============================================================= */

function Overview({
  result,
  theories,
  redTeam,
  nextEvidence,
  evidence,
  error,
  runInvestigation,
  onReopenResults,
}) {
  return (
    <div>

      <section className="relative overflow-hidden rounded-[30px] border border-red-500/[0.12] bg-[#060606] shadow-[0_0_120px_rgba(100,0,0,.07)]">

        <CornerBrackets />

        <div className="absolute right-[-8%] top-[-45%] h-[600px] w-[600px] rounded-full bg-red-700/[0.055] blur-[120px]" />

        <div className="relative p-8 md:p-14">

          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,.9)]" />
            <span className="text-[8px] font-bold uppercase tracking-[0.35em] text-red-400">
              Investigation Intelligence
            </span>
          </div>

          <h2 className="mt-7 max-w-6xl text-4xl font-black leading-[0.91] tracking-tight md:text-[76px]">
            Evidence is
            <span className="text-neutral-700"> fragmented.</span>
            <br />
            <span className="text-red-500">Reasoning isn't.</span>
          </h2>

          <p className="mt-8 max-w-2xl text-[13px] leading-7 text-neutral-600">
            LUNA reconstructs incidents from fragmented evidence, generates
            competing explanations, attacks them with adversarial reasoning,
            and determines what evidence should be pursued next.
          </p>

          <div className="mt-10 flex flex-wrap gap-3">

            {!result && (
              <button
                onClick={runInvestigation}
                disabled={!evidence.length}
                className="flex items-center gap-3 rounded-xl bg-red-600 px-6 py-3.5 text-[11px] font-black tracking-wider text-white shadow-[0_0_35px_rgba(180,0,0,.2)] transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <span>▶</span>
                <span>RUN INVESTIGATION</span>
              </button>
            )}

            {result && (
              <button
                onClick={onReopenResults}
                className="flex items-center gap-3 rounded-xl bg-red-600 px-6 py-3.5 text-[11px] font-black tracking-wider text-white shadow-[0_0_35px_rgba(180,0,0,.2)] transition hover:bg-red-500"
              >
                <span>⤢</span>
                <span>REOPEN RESULTS</span>
              </button>
            )}

            <div className="flex items-center rounded-xl border border-white/[0.07] bg-white/[0.018] px-5 py-3">
              <span className="text-[8px] uppercase tracking-widest text-neutral-800">
                Pipeline
              </span>
              <span className="ml-3 text-[9px] text-neutral-500">
                Evidence → Theory → Attack → Action
              </span>
            </div>

          </div>

          <div className="mt-12 grid max-w-3xl grid-cols-3 gap-3">
            {[
              ["01", "FRAGMENTED", "Evidence"],
              ["02", "ADVERSARIAL", "Reasoning"],
              ["03", "ACTIONABLE", "Decision"],
            ].map(([num, title, sub]) => (
              <div key={num} className="border-l border-red-500/20 pl-4">
                <div className="font-mono text-[8px] text-red-500/50">{num}</div>
                <div className="mt-2 text-[8px] font-bold tracking-[0.18em] text-neutral-500">
                  {title}
                </div>
                <div className="mt-1 text-[8px] text-neutral-800">{sub}</div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {error && (
        <div className="relative mt-6 overflow-hidden rounded-2xl border border-red-500/20 bg-red-500/[0.04] p-5">
          <CornerBrackets />
          <div className="text-[10px] font-bold tracking-widest text-red-400">
            LUNA CORE ERROR
          </div>
          <div className="mt-2 text-[10px] leading-6 text-red-300/60">
            {error}
          </div>
        </div>
      )}

      <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">
        <Metric label="Evidence Items" value={evidence.length || "—"} />
        <Metric label="Competing Theories" value={theories.length || "—"} />
        <Metric
          label="Evidence Gaps"
          value={redTeam?.evidence_gaps?.length || "—"}
        />
        <Metric
          label="Investigation State"
          value={result ? "COMPLETE" : "READY"}
          accent
        />
      </div>

      {result ? (
        <div className="mt-10 space-y-10">

          <section>
            <SectionTitle
              number="01"
              title="Competing Case Theories"
              description="Alternative explanations ranked by evidentiary fit."
            />

            <div className="grid gap-5 lg:grid-cols-3">
              {theories.length ? (
                theories.map((theory) => (
                  <TheoryCard key={theory.id || theory.title} theory={theory} />
                ))
              ) : (
                <EmptyState
                  title="No theories returned"
                  text="The reasoning engine did not return theory objects."
                />
              )}
            </div>
          </section>

          {nextEvidence && <NextEvidence data={nextEvidence} />}

          {redTeam && <RedTeamView redTeam={redTeam} compact />}

        </div>
      ) : (
        <EmptyState
          title="Investigation Core Ready"
          text="Upload a case file and initialize an investigation to construct competing theories, challenge assumptions, and identify the next evidence worth pursuing."
        />
      )}

    </div>
  );
}

/* ============================================================= */
/* EVIDENCE */
/* ============================================================= */

function EvidenceView({ evidence }) {
  return (
    <div>
      <SectionTitle
        number="E1"
        title="Evidence Explorer"
        description="Fragmented observations available to the investigation."
      />

      {!evidence.length ? (
        <EmptyState
          title="No evidence loaded"
          text="Evidence objects will appear here once a case is analyzed."
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {evidence.map((item, index) => (
            <div
              key={item.id || index}
              className="group relative overflow-hidden rounded-2xl border border-white/[0.07] bg-[#070707] p-6 transition duration-300 hover:-translate-y-1 hover:border-red-500/20"
            >
              <CornerBrackets />

              <div className="relative flex justify-between">
                <span className="font-mono text-xs text-red-400">
                  {item.id || `E${String(index + 1).padStart(2, "0")}`}
                </span>
                <span className="text-[8px] uppercase tracking-[0.2em] text-neutral-800">
                  EVIDENCE
                </span>
              </div>

              <p className="relative mt-5 text-[11px] leading-7 text-neutral-500">
                {item.description || item.text || JSON.stringify(item)}
              </p>

              <div className="mt-6 border-t border-white/[0.05] pt-4 font-mono text-[7px] text-neutral-800">
                SOURCE / ANALYZED OBJECT
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ============================================================= */
/* TIMELINE */
/* ============================================================= */

function TimelineView({ timeline }) {
  return (
    <div>
      <SectionTitle
        number="T1"
        title="Incident Timeline"
        description="Chronological reconstruction of observed events."
      />

      {!timeline.length ? (
        <EmptyState
          title="Timeline unavailable"
          text="Timeline events will appear when the case is analyzed."
        />
      ) : (
        <div className="relative ml-5 border-l border-red-500/20 pl-8">
          {timeline.map((event, index) => (
            <div key={index} className="relative mb-8">
              <span className="absolute -left-[41px] top-1 h-3 w-3 rounded-full border-2 border-red-500 bg-[#030303] shadow-[0_0_15px_rgba(239,68,68,.5)]" />

              <div className="group relative overflow-hidden rounded-2xl border border-white/[0.07] bg-[#070707] p-5 transition hover:border-red-500/20">
                <CornerBrackets />

                <div className="font-mono text-[9px] text-red-400">
                  {event.timestamp ||
                    event.time ||
                    `EVENT ${String(index + 1).padStart(2, "0")}`}
                </div>

                <p className="mt-3 text-[11px] leading-7 text-neutral-500">
                  {event.event ||
                    event.description ||
                    event.text ||
                    JSON.stringify(event)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ============================================================= */
/* THEORIES */
/* ============================================================= */

function TheoriesView({ theories }) {
  return (
    <div>
      <SectionTitle
        number="T1"
        title="Competing Case Theories"
        description="LUNA refuses to collapse uncertainty into a single explanation."
      />

      {theories.length ? (
        <div className="grid gap-5 lg:grid-cols-3">
          {theories.map((theory, index) => (
            <TheoryCard key={theory.id || index} theory={theory} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No theories generated"
          text="Analyze a case to construct competing explanations."
        />
      )}
    </div>
  );
}

/* ============================================================= */
/* RED TEAM */
/* ============================================================= */

function RedTeamView({ redTeam, compact = false }) {
  if (!redTeam) {
    return (
      <EmptyState
        title="Red Team inactive"
        text="Analyze a case to activate adversarial reasoning."
      />
    );
  }

  const panels = [
    ["Unsupported Claims", redTeam.unsupported_claims],
    ["Assumptions", redTeam.assumptions],
    ["Alternative Explanations", redTeam.alternative_explanations],
    ["Critical Questions", redTeam.critical_questions],
    ["Evidence Gaps", redTeam.evidence_gaps],
  ];

  return (
    <section>
      {!compact && (
        <SectionTitle
          number="R1"
          title="Red Team Analysis"
          description="Adversarial reasoning designed to break the leading explanation."
        />
      )}

      <div className="relative overflow-hidden rounded-3xl border border-red-500/15 bg-red-500/[0.018]">
        <CornerBrackets />

        <div className="flex items-center justify-between border-b border-red-500/10 p-6">
          <div>
            <div className="flex items-center gap-2 text-[8px] font-bold uppercase tracking-[0.35em] text-red-500">
              <span className="h-1 w-1 rounded-full bg-red-500" />
              Devil's Advocate
            </div>
            <h2 className="mt-2 text-xl font-black">Theory Stress Test</h2>
          </div>

          <div className="rounded-full border border-red-500/20 bg-red-500/10 px-4 py-2 text-[9px] font-black tracking-widest text-red-400">
            {redTeam.verdict || "ANALYSIS"}
          </div>
        </div>

        <div className="grid md:grid-cols-2">
          {panels.map(([title, items]) => (
            <RedPanel key={title} title={title} items={items} />
          ))}
        </div>
      </div>
    </section>
  );
}

/* ============================================================= */
/* GRAPH */
/* ============================================================= */

function GraphView({ theories, redTeam, nextEvidence }) {
  const nodes = useMemo(
    () => [
      { title: "EVIDENCE", subtitle: "Observed fragments", position: "left-[6%] top-[18%]" },
      {
        title: theories[0]?.id || "THEORY-01",
        subtitle: theories[0]?.title || "Primary explanation",
        position: "left-[30%] top-[9%]",
      },
      {
        title: "LUNA CORE",
        subtitle: "Reasoning engine",
        position: "left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2",
        accent: true,
      },
      {
        title: theories[1]?.id || "THEORY-02",
        subtitle: theories[1]?.title || "Alternative explanation",
        position: "right-[30%] top-[9%]",
      },
      { title: "RED TEAM", subtitle: redTeam?.verdict || "Stress testing", position: "right-[6%] top-[18%]", danger: true },
      { title: "EVIDENCE GAP", subtitle: "Unknown / missing", position: "left-[14%] bottom-[12%]" },
      {
        title: "NEXT ACTION",
        subtitle: nextEvidence?.priority || "Awaiting",
        position: "right-[14%] bottom-[12%]",
        accent: true,
      },
    ],
    [theories, redTeam, nextEvidence]
  );

  return (
    <div>
      <SectionTitle
        number="G1"
        title="Investigation Graph"
        description="A live relationship map connecting evidence, theories, attacks and investigative action."
      />

      <div className="relative min-h-[650px] overflow-hidden rounded-3xl border border-red-500/[0.1] bg-[#050505] shadow-[0_0_100px_rgba(100,0,0,.05)]">
        <CornerBrackets />

        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,.5) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,.5) 1px, transparent 1px)
            `,
            backgroundSize: "42px 42px",
          }}
        />

        <div className="absolute left-5 top-5 font-mono text-[7px] tracking-[0.25em] text-neutral-800">
          GRAPH://LIVE
        </div>

        <div className="absolute right-5 top-5 flex items-center gap-2 font-mono text-[7px] text-red-500/40">
          <span className="h-1 w-1 animate-pulse rounded-full bg-red-500" />
          NODE NETWORK ACTIVE
        </div>

        <div className="absolute left-1/2 top-1/2 h-[260px] w-[260px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-red-500/[0.04]" />
        <div className="absolute left-1/2 top-1/2 h-[180px] w-[180px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-red-500/[0.06]" />
        <div className="absolute left-1/2 top-1/2 h-[100px] w-[100px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-red-500/[0.08]" />

        <GraphLine className="left-[15%] top-[29%] w-[28%] rotate-[20deg]" />
        <GraphLine className="left-[38%] top-[28%] w-[15%] rotate-[45deg]" />
        <GraphLine className="right-[15%] top-[29%] w-[28%] -rotate-[20deg]" />
        <GraphLine className="right-[38%] top-[28%] w-[15%] -rotate-[45deg]" />
        <GraphLine className="left-[17%] bottom-[27%] w-[28%] -rotate-[20deg]" />
        <GraphLine className="right-[17%] bottom-[27%] w-[28%] rotate-[20deg]" />

        {nodes.map((node, index) => (
          <GraphNode key={index} {...node} />
        ))}

        <div className="absolute bottom-5 left-5 font-mono text-[7px] text-neutral-800">
          RELATIONSHIP MATRIX / 07 NODES
        </div>
      </div>
    </div>
  );
}

function GraphLine({ className }) {
  return (
    <div className={`absolute h-px bg-gradient-to-r from-transparent via-red-500/30 to-transparent ${className}`} />
  );
}

function GraphNode({ title, subtitle, position, accent = false, danger = false }) {
  return (
    <div
      className={`absolute w-48 rounded-2xl border p-4 backdrop-blur-xl transition duration-300 hover:scale-[1.03] ${
        danger
          ? "border-red-500/25 bg-red-500/[0.055] shadow-[0_0_30px_rgba(180,0,0,.08)]"
          : accent
          ? "border-red-500/30 bg-red-500/[0.06] shadow-[0_0_45px_rgba(180,0,0,.12)]"
          : "border-white/[0.08] bg-[#080808]/90"
      } ${position}`}
    >
      <CornerBrackets />

      <div className="flex items-center justify-between">
        <span
          className={`text-[8px] font-black uppercase tracking-[0.18em] ${
            danger || accent ? "text-red-400" : "text-neutral-600"
          }`}
        >
          {title}
        </span>

        <span
          className={`h-1.5 w-1.5 ${
            danger || accent
              ? "animate-pulse rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,.7)]"
              : "rounded-full bg-neutral-700"
          }`}
        />
      </div>

      <div className="mt-2 text-[10px] font-bold leading-5 text-neutral-400">
        {subtitle}
      </div>
    </div>
  );
}

/* ============================================================= */
/* NEXT BEST EVIDENCE */
/* ============================================================= */

function NextEvidence({ data }) {
  const item = Array.isArray(data) ? data[0] : data;
  if (!item) return null;

  const recommendation = item.recommendation || item.action || "No recommendation returned.";
  const score = item.discrimination_score ?? item.estimated_information_gain ?? null;

  return (
    <section className="relative overflow-hidden rounded-3xl border border-red-500/20 bg-red-500/[0.025] p-7 shadow-[0_0_80px_rgba(120,0,0,.07)]">
      <CornerBrackets />

      <div className="relative flex items-start justify-between gap-5">
        <div>
          <div className="text-[8px] font-bold uppercase tracking-[0.35em] text-red-500">
            03 / Decision Support
          </div>
          <h2 className="mt-2 text-2xl font-black">Next Best Evidence</h2>
          <p className="mt-1 text-[9px] text-neutral-700">
            Highest-value investigative action currently identified.
          </p>
        </div>

        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-right">
          <div className="text-[7px] uppercase tracking-widest text-red-500/60">
            Priority
          </div>
          <div className="mt-1 text-lg font-black text-red-400">
            {item.priority || "HIGH"}
          </div>
        </div>
      </div>

      <div className="relative mt-7 grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-white/[0.06] bg-black/30 p-5 md:col-span-2">
          <div className="text-[7px] uppercase tracking-[0.2em] text-neutral-700">
            Recommended Action
          </div>
          <div className="mt-3 text-sm font-bold leading-7 text-neutral-300">
            {recommendation}
          </div>
        </div>

        <div className="rounded-2xl border border-white/[0.06] bg-black/30 p-5">
          <div className="text-[7px] uppercase tracking-[0.2em] text-neutral-700">
            Evidence Value
          </div>
          <div className="mt-3 font-mono text-3xl font-black text-red-400">
            {score != null ? Number(score).toFixed(2) : "—"}
          </div>

          <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.05]">
            <div
              className="h-full rounded-full bg-red-500"
              style={{ width: `${Math.min(Number(score || 0) * 100, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {item.reason && (
        <div className="relative mt-4 rounded-2xl border border-red-500/10 bg-red-500/[0.025] p-5">
          <div className="text-[7px] uppercase tracking-[0.2em] text-red-500/60">
            Why
          </div>
          <div className="mt-2 text-[11px] leading-6 text-neutral-400">
            {item.reason}
          </div>
        </div>
      )}
    </section>
  );
}

/* ============================================================= */
/* THEORY CARD */
/* ============================================================= */

function TheoryCard({ theory }) {
  const score = Number(theory.score || 0);

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-white/[0.07] bg-[#070707] p-6 transition duration-300 hover:-translate-y-1 hover:border-red-500/20">
      <CornerBrackets />

      <div className="relative">
        <div className="flex items-center justify-between">
          <span className="rounded-lg border border-red-500/10 bg-red-500/[0.04] px-3 py-1 font-mono text-[9px] text-red-400">
            {theory.id || "THEORY"}
          </span>
          <span className="font-mono text-sm text-neutral-500">
            {score.toFixed(2)}
          </span>
        </div>

        <h3 className="mt-5 text-lg font-black">
          {theory.title || "Unnamed Theory"}
        </h3>

        <p className="mt-3 text-[10px] leading-6 text-neutral-600">
          {theory.explanation || theory.description || "No explanation returned."}
        </p>

        <div className="mt-6">
          <div className="mb-2 flex justify-between">
            <span className="text-[7px] uppercase tracking-[0.2em] text-neutral-800">
              Evidentiary Fit
            </span>
            <span className="font-mono text-[8px] text-neutral-700">
              {Math.round(score * 100)}%
            </span>
          </div>

          <div className="relative h-1 overflow-hidden rounded-full bg-white/[0.05]">
            <div
              className="h-full rounded-full bg-red-500 transition-all duration-1000"
              style={{ width: `${Math.min(score * 100, 100)}%` }}
            />
          </div>
        </div>

        <div className="mt-5 flex justify-between border-t border-white/[0.05] pt-4">
          <span className="text-[7px] uppercase tracking-[0.2em] text-neutral-800">
            Confidence
          </span>
          <span className="text-[8px] font-bold text-neutral-500">
            {theory.confidence || "UNKNOWN"}
          </span>
        </div>
      </div>
    </div>
  );
}

/* ============================================================= */
/* RED PANEL */
/* ============================================================= */

function RedPanel({ title, items }) {
  if (!items?.length) return null;

  return (
    <div className="border-b border-r border-red-500/[0.06] bg-[#080808]/70 p-6 transition hover:bg-red-500/[0.012]">
      <div className="mb-4 flex items-center gap-2">
        <span className="h-1 w-1 rounded-full bg-red-500 shadow-[0_0_7px_rgba(239,68,68,.6)]" />
        <span className="text-[8px] font-bold uppercase tracking-[0.2em] text-neutral-600">
          {title}
        </span>
      </div>

      <div className="space-y-3">
        {items.map((item, index) => (
          <div
            key={index}
            className="group flex gap-3 rounded-xl border border-white/[0.05] bg-white/[0.015] p-4 transition hover:border-red-500/10 hover:bg-red-500/[0.02]"
          >
            <span className="font-mono text-[8px] text-red-500/60">
              {String(index + 1).padStart(2, "0")}
            </span>

            <p className="text-[10px] leading-6 text-neutral-500">
              {typeof item === "string"
                ? item
                : item?.text || item?.description || JSON.stringify(item)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============================================================= */
/* SECTION TITLE */
/* ============================================================= */

function SectionTitle({ number, title, description }) {
  return (
    <div className="mb-6 flex items-end justify-between">
      <div>
        <div className="flex items-center gap-2 text-[8px] font-bold uppercase tracking-[0.35em] text-red-500/70">
          <span className="h-px w-5 bg-red-500/40" />
          {number} / LUNA CORE
        </div>

        <h2 className="mt-2 text-2xl font-black">{title}</h2>
        <p className="mt-1 text-[9px] text-neutral-700">{description}</p>
      </div>

      <div className="hidden font-mono text-[7px] text-neutral-800 md:block">
        MODULE://ACTIVE
      </div>
    </div>
  );
}

/* ============================================================= */
/* METRIC */
/* ============================================================= */

function Metric({ label, value, accent }) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-white/[0.06] bg-[#070707] p-5 transition hover:border-red-500/15">
      <CornerBrackets />

      <div className="flex justify-between">
        <span className="text-[8px] uppercase tracking-[0.2em] text-neutral-700">
          {label}
        </span>
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            accent ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,.7)]" : "bg-neutral-800"
          }`}
        />
      </div>

      <div className={`mt-5 text-2xl font-black ${accent ? "text-red-400" : "text-neutral-300"}`}>
        {value}
      </div>

      <div className="mt-3 font-mono text-[7px] text-neutral-800">
        LUNA / METRIC
      </div>
    </div>
  );
}

/* ============================================================= */
/* EMPTY STATE */
/* ============================================================= */

function EmptyState({ title, text }) {
  return (
    <section className="relative mt-6 flex min-h-[380px] items-center justify-center overflow-hidden rounded-3xl border border-dashed border-red-500/[0.08] bg-white/[0.01]">
      <CornerBrackets />

      <div className="absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full border border-red-500/[0.025]" />
      <div className="absolute left-1/2 top-1/2 h-44 w-44 -translate-x-1/2 -translate-y-1/2 rounded-full border border-red-500/[0.04]" />

      <div className="relative max-w-md text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-red-500/20 bg-red-500/[0.035] text-xl text-red-400">
          ◈
        </div>

        <div className="mt-6 text-[8px] font-bold uppercase tracking-[0.35em] text-red-500/70">
          LUNA CORE
        </div>

        <h2 className="mt-3 text-2xl font-black">{title}</h2>

        <p className="mx-auto mt-3 text-[10px] leading-6 text-neutral-700">
          {text}
        </p>

        <div className="mt-6 font-mono text-[7px] tracking-[0.2em] text-neutral-800">
          SYS://AWAITING_INPUT
        </div>
      </div>
    </section>
  );
}

export default App;
