import React, { useEffect, useState } from 'react';

const STAGES = [
  { id: '01', name: 'Ingesting Case File' },
  { id: '02', name: 'Reconstructing Timeline' },
  { id: '03', name: 'Generating Competing Theories' },
  { id: '04', name: 'Red-Teaming Leading Theory' },
  { id: '05', name: 'Ranking Next Best Evidence' },
];

function buildLogs(fileName, charCount) {
  return [
    { stage: 0, text: ">> INGESTING CASE FILE <<" },
    { stage: 0, text: `> reading ${fileName || "case_file"}` },
    {
      stage: 0,
      text: `> ${charCount ? charCount.toLocaleString() : "—"} characters loaded`,
    },
    { stage: 1, text: ">> RECONSTRUCTING TIMELINE <<" },
    { stage: 1, text: "> normalizing anonymous identifiers" },
    { stage: 1, text: "> sorting observations by timestamp" },
    { stage: 1, text: "> OK -- evidence stream ready" },
    { stage: 1, text: "> linking evidence to people / objects" },
    { stage: 2, text: ">> GENERATING COMPETING THEORIES <<" },
    { stage: 2, text: "> flagging visibility & access gaps" },
    { stage: 2, text: "> querying LUNA reasoning core" },
    { stage: 2, text: "> OK -- chronology built" },
    { stage: 2, text: "> drafting 2-4 competing explanations" },
    { stage: 3, text: ">> RED-TEAMING LEADING THEORY <<" },
    { stage: 3, text: "> scoring evidentiary fit per theory" },
    { stage: 3, text: "> assuming adversarial posture" },
    { stage: 3, text: "> separating fact from assumption" },
    { stage: 4, text: ">> RANKING NEXT BEST EVIDENCE <<" },
    { stage: 4, text: "> searching for contradictions" },
    { stage: 4, text: "> scoring candidate evidence" },
    { stage: 4, text: "> OK -- verdict reached" },
    { stage: 4, text: "> weighting by theory discrimination" },
    { stage: 4, text: "> selecting highest-value action" },
  ];
}

/**
 * Props:
 *  fileName   - name of the uploaded case file (shown in the log)
 *  charCount  - characters ingested (shown in the log)
 *  ready      - true once the REAL backend response has actually
 *               arrived. The scripted terminal log always plays out
 *               in full, but the modal will not let the user through
 *               to results until this is true -- so a slow Gemini
 *               call never gets cut off mid-animation.
 *  onComplete - called when the user dismisses into the results view
 */
export default function AnalysisModal({ fileName, charCount, ready, onComplete }) {
  const [currentStage, setCurrentStage] = useState(0);
  const [displayedLogs, setDisplayedLogs] = useState([]);

  useEffect(() => {
    const LOGS = buildLogs(fileName, charCount);
    let logIndex = 0;

    const interval = setInterval(() => {
      if (logIndex < LOGS.length) {
        const nextLog = LOGS[logIndex];
        setDisplayedLogs((prev) => [...prev, nextLog.text]);
        setCurrentStage(nextLog.stage);
        logIndex++;
      } else {
        clearInterval(interval);
      }
    }, 250);

    return () => clearInterval(interval);
    // fileName/charCount are fixed for the life of one analysis run
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const animationDone = displayedLogs.length === buildLogs().length;
  const canProceed = animationDone && ready;

  return (
    <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-6 font-mono">
      <div className="w-full max-w-4xl bg-black border border-red-900/60 p-8 relative shadow-2xl">
        {/* Header */}
        <div className="text-[10px] text-red-500 font-bold tracking-widest uppercase mb-1">
          ◆ LUNA CORE // CASE ANALYSIS IN PROGRESS
        </div>
        <h2 className="text-3xl font-black tracking-tight text-red-600 uppercase mb-8">
          ANALYZING EVIDENCE
        </h2>

        {/* Stage Progress Pills */}
        <div className="grid grid-cols-5 gap-2 mb-8">
          {STAGES.map((s, idx) => {
            const isActive = idx === currentStage && !animationDone;
            const isDone = idx < currentStage || animationDone;

            return (
              <div
                key={s.id}
                className={`p-3 border text-center transition-all ${
                  isActive
                    ? 'border-red-600 bg-red-950/40 text-red-400'
                    : isDone
                    ? 'border-red-900/40 bg-red-950/10 text-red-700'
                    : 'border-neutral-800 bg-neutral-950 text-neutral-600'
                }`}
              >
                <div className="text-[10px] font-bold mb-1">
                  {isDone ? '✓' : s.id}
                </div>
                <div className="text-[9px] font-bold leading-tight uppercase">
                  {s.name}
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Terminal Output */}
        <div className="bg-neutral-950 border border-neutral-900 p-6 h-64 overflow-y-auto font-mono text-xs space-y-2 custom-scrollbar">
          {displayedLogs.map((log, i) => (
            <div
              key={i}
              className={
                log.startsWith('>>')
                  ? 'text-red-500 font-bold mt-3'
                  : 'text-neutral-300'
              }
            >
              {log}
            </div>
          ))}

          {animationDone && !ready && (
            <div className="text-amber-500 font-bold mt-3 animate-pulse">
              &gt;&gt; AWAITING LUNA REASONING CORE (GEMINI) &lt;&lt;
            </div>
          )}
        </div>

        {/* Footer Bar */}
        <div className="mt-6 flex justify-between items-center pt-4 border-t border-neutral-900">
          <div className="text-xs text-neutral-500 tracking-wider">
            {canProceed
              ? "ANALYSIS COMPLETE"
              : `STAGE ${currentStage + 1} / ${STAGES.length}`}
          </div>

          {canProceed && (
            <button
              onClick={onComplete}
              className="bg-red-600 hover:bg-red-500 text-white font-black px-6 py-2.5 text-xs tracking-widest uppercase transition-colors"
            >
              VIEW RESULTS ▶
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
