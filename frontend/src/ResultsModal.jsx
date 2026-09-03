import React, { useMemo } from "react";

export default function ResultsModal({ open = true, result, onClose }) {
  if (!open) return null;

  // ============================================================
  // SAFE DATA NORMALIZATION
  // ============================================================

  const theories = Array.isArray(result?.theories)
    ? result.theories
    : [];

  const evidence = Array.isArray(result?.evidence)
    ? result.evidence
    : [];

  const timeline = Array.isArray(result?.timeline)
    ? result.timeline
    : [];

  const redTeam = result?.red_team || {};

  const nextBestEvidence =
    result?.next_best_evidence ||
    result?.nextBestEvidence ||
    {};

  const contradictions =
    Array.isArray(result?.contradictions)
      ? result.contradictions
      : [];

  const gaps =
    Array.isArray(result?.gaps)
      ? result.gaps
      : Array.isArray(redTeam?.evidence_gaps)
        ? redTeam.evidence_gaps
        : [];

  // ============================================================
  // HELPERS
  // ============================================================

  const getText = (value, fallback = "No information available.") => {
    if (value === null || value === undefined) return fallback;

    if (typeof value === "string") return value;

    if (typeof value === "number" || typeof value === "boolean") {
      return String(value);
    }

    return JSON.stringify(value);
  };

  const scorePercent = (value) => {
    let number = Number(value);

    if (Number.isNaN(number)) return 0;

    // Supports both 0.72 and 72
    if (number <= 1) {
      number *= 100;
    }

    return Math.max(0, Math.min(100, Math.round(number)));
  };

  const theoryScore = (theory) => {
    return (
      theory?.score ??
      theory?.confidence ??
      theory?.probability ??
      theory?.fit ??
      0
    );
  };

  const theoryTitle = (theory, index) => {
    return (
      theory?.title ||
      theory?.name ||
      theory?.theory ||
      theory?.explanation ||
      `Theory ${String(index + 1).padStart(2, "0")}`
    );
  };

  const theoryDescription = (theory) => {
    return (
      theory?.description ||
      theory?.reasoning ||
      theory?.summary ||
      theory?.explanation ||
      "No supporting explanation was provided."
    );
  };

  // ============================================================
  // LEADING THEORY
  // ============================================================

  const sortedTheories = useMemo(() => {
    return [...theories].sort(
      (a, b) =>
        Number(theoryScore(b)) -
        Number(theoryScore(a))
    );
  }, [theories]);

  const leadingTheory =
    sortedTheories[0] || null;

  const leadingScore = leadingTheory
    ? scorePercent(theoryScore(leadingTheory))
    : 0;

  const verdict =
    result?.verdict ||
    result?.summary ||
    result?.conclusion ||
    (leadingTheory
      ? theoryTitle(leadingTheory, 0)
      : "Insufficient evidence for a leading explanation");

  const verdictDescription =
    result?.verdict_explanation ||
    result?.verdict_reasoning ||
    result?.summary_text ||
    result?.conclusion_reasoning ||
    (leadingTheory
      ? theoryDescription(leadingTheory)
      : "LUNA could not establish a sufficiently supported explanation from the available evidence.");

  // ============================================================
  // METADATA
  // ============================================================

  const caseId =
    result?.case_id ||
    result?.caseId ||
    "LUNA-CASE";

  const incident =
    result?.incident ||
    result?.case_title ||
    result?.title ||
    "Uploaded investigation case";

  const date =
    result?.date ||
    result?.incident_date ||
    result?.case_date ||
    "";

  const identityLock =
    result?.identity_lock ||
    result?.identityLock ||
    {};

  // ============================================================
  // RED TEAM
  // ============================================================

  const redTeamVerdict =
    redTeam?.verdict ||
    redTeam?.conclusion ||
    redTeam?.status ||
    "NOT PROVEN";

  const unsupportedClaims =
    Array.isArray(redTeam?.unsupported_claims)
      ? redTeam.unsupported_claims
      : [];

  const assumptions =
    Array.isArray(redTeam?.assumptions)
      ? redTeam.assumptions
      : [];

  const alternativeExplanations =
    Array.isArray(redTeam?.alternative_explanations)
      ? redTeam.alternative_explanations
      : [];

  const redTeamItems = [
    ...unsupportedClaims.map((item) => ({
      type: "UNSUPPORTED",
      text: getText(item),
    })),
    ...assumptions.map((item) => ({
      type: "ASSUMPTION",
      text: getText(item),
    })),
    ...alternativeExplanations.map((item) => ({
      type: "ALTERNATIVE",
      text: getText(item),
    })),
  ];

  // ============================================================
  // NEXT BEST EVIDENCE
  // ============================================================

  const nextEvidenceTitle =
    nextBestEvidence?.action ||
    nextBestEvidence?.title ||
    nextBestEvidence?.recommendation ||
    nextBestEvidence?.description ||
    "Obtain additional evidence surrounding the critical incident window.";

  const nextEvidenceReason =
    nextBestEvidence?.reason ||
    nextBestEvidence?.why ||
    nextBestEvidence?.rationale ||
    "What additional evidence can independently confirm or contradict the current reconstruction?";

  const nextPriority =
    nextBestEvidence?.priority ||
    "HIGH";

  const nextValue =
    nextBestEvidence?.discrimination_score ??
    nextBestEvidence?.estimated_information_gain ??
    null;

  // ============================================================
  // STATS
  // ============================================================

  const evidenceCount =
    result?.metrics?.evidence_count ??
    evidence.length;

  const theoryCount =
    result?.metrics?.theory_count ??
    theories.length;

  const timelineCount =
    result?.metrics?.timeline_events ??
    timeline.length;

  const gapCount =
    result?.metrics?.evidence_gaps ??
    gaps.length;

  // ============================================================
  // INVESTIGATION GRAPH CHAIN (06)
  // ============================================================

  const graphChain = [
    "EVIDENCE",
    "EVENTS",
    "OBJECTS",
    "THEORIES",
    "RED TEAM",
    "GAPS",
    "NEXT ACTION",
  ];

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black text-white font-mono selection:bg-red-900 selection:text-white">

      {/* Background Grid */}
      <div
        className="fixed inset-0 pointer-events-none opacity-10"
        style={{
          backgroundImage:
            "linear-gradient(to right, #333 1px, transparent 1px), linear-gradient(to bottom, #333 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      <div className="relative max-w-[1400px] mx-auto p-6 md:p-10 space-y-8">

        {/* ======================================================
            HEADER
        ====================================================== */}

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-red-950/60 pb-6">

          <div>

            <div className="flex items-center gap-3 text-xs tracking-widest text-red-500 font-semibold uppercase mb-1">
              <span>LUNA CORE</span>
              <span>//</span>
              <span>INVESTIGATION RESULT</span>
            </div>

            <div className="flex items-center gap-3 flex-wrap">

              <h1 className="text-3xl md:text-5xl font-black tracking-tight uppercase text-white">
                CASE SOLVED — WITH CONDITIONS
              </h1>

              <span className="bg-red-950/80 border border-red-600 text-red-500 text-xs px-2.5 py-0.5 font-bold uppercase tracking-wider rounded-sm">
                ACTIVE
              </span>

            </div>

            <p className="text-xs text-neutral-500 tracking-wider mt-2 uppercase">
              {caseId}
              &nbsp;//&nbsp;
              {incident}
              {date ? <>&nbsp;|&nbsp;{date}</> : null}
            </p>

          </div>

          <button
            onClick={onClose}
            className="flex items-center gap-2 border border-red-800/60 hover:border-red-500 bg-red-950/30 hover:bg-red-900/40 text-red-400 hover:text-red-200 px-5 py-2.5 text-xs font-bold tracking-widest uppercase transition-all duration-150 rounded-sm"
          >
            <span>CLOSE</span>
            <span className="text-sm">×</span>
          </button>

        </div>

        {/* ======================================================
            TOP SUMMARY
        ====================================================== */}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <div className="lg:col-span-7 bg-neutral-950 border border-neutral-800/80 p-6 relative flex flex-col justify-between">

            <div className="space-y-4">

              <div className="text-xs tracking-widest text-neutral-400 uppercase font-bold">
                LUNA VERDICT
              </div>

              <h2 className="text-2xl md:text-4xl font-extrabold tracking-tight leading-tight text-white">
                {getText(verdict)}
              </h2>

              <p className="text-sm text-neutral-400 leading-relaxed max-w-2xl">
                {getText(verdictDescription)}
              </p>

            </div>

            <div className="mt-8 pt-4 border-t border-neutral-900 flex items-end gap-4">

              <div>

                <div className="text-[10px] tracking-wider text-red-500 font-bold uppercase mb-1">
                  CONFIDENCE
                </div>

                <div className="text-4xl font-extrabold text-red-500 tracking-tight">
                  {leadingScore}%
                </div>

              </div>

              <span className="text-[10px] tracking-widest text-neutral-500 uppercase pb-1">
                EVIDENTIARY FIT
              </span>

            </div>

          </div>

          <div className="lg:col-span-5 grid grid-cols-2 gap-4">

            <StatCard
              label="EVIDENCE"
              value={evidenceCount}
            />

            <StatCard
              label="THEORIES"
              value={theoryCount}
            />

            <StatCard
              label="TIMELINE EVENTS"
              value={timelineCount}
            />

            <StatCard
              label="EVIDENCE GAPS"
              value={gapCount}
            />

          </div>

        </div>

        {/* ======================================================
            01 / RECONSTRUCTION  +  02 / COMPETING THEORIES
        ====================================================== */}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <div className="lg:col-span-6 bg-neutral-950 border border-neutral-800/80 p-6">

            <SectionHeader
              number="01 /"
              title="RECONSTRUCTION"
              subtitle="What LUNA believes the available evidence supports."
            />

            <div className="space-y-3 max-h-[420px] overflow-y-auto pr-2 custom-scrollbar">

              {timeline.length > 0 ? (

                timeline.map((event, index) => {

                  const eventText =
                    event?.description ||
                    event?.event ||
                    event?.summary ||
                    event?.text ||
                    event?.action ||
                    getText(event);

                  const eventTime =
                    event?.timestamp ||
                    event?.time ||
                    event?.datetime ||
                    "";

                  return (
                    <div
                      key={index}
                      className="flex gap-4 p-3 bg-neutral-900/40 border border-neutral-800/50 rounded-sm text-xs"
                    >

                      <span className="text-red-500 font-bold shrink-0">
                        {`EVENT ${String(index + 1).padStart(2, "0")}`}
                      </span>

                      <p className="text-neutral-300 leading-relaxed">
                        {eventTime ? `${eventTime} — ` : ""}
                        {getText(eventText)}
                      </p>

                    </div>
                  );
                })

              ) : (

                <EmptyState text="No timeline reconstruction was returned." />

              )}

            </div>

          </div>

          {/* ====================================================
              02 / THEORIES
          ==================================================== */}

          <div className="lg:col-span-6 bg-neutral-950 border border-neutral-800/80 p-6">

            <SectionHeader
              number="02 /"
              title="COMPETING THEORIES"
              subtitle="LUNA keeps alternatives alive instead of forcing one answer."
            />

            <div className="space-y-4">

              {sortedTheories.length > 0 ? (

                sortedTheories.map((theory, index) => {

                  const score =
                    scorePercent(
                      theoryScore(theory)
                    );

                  return (
                    <div
                      key={index}
                      className="p-4 bg-neutral-900/30 border border-neutral-800/60"
                    >

                      <div className="flex justify-between items-start mb-2">

                        <div className="flex items-center gap-2">

                          <span className="text-xs font-bold text-red-500">
                            THEORY-
                            {String(index + 1).padStart(2, "0")}
                          </span>

                          {index === 0 && (
                            <span className="bg-red-950 border border-red-800 text-red-400 text-[10px] px-1.5 py-0.5 font-bold uppercase tracking-wider">
                              LEADING
                            </span>
                          )}

                        </div>

                        <span className="text-sm font-extrabold text-white">
                          {score}%
                        </span>

                      </div>

                      <h4 className="text-sm font-bold text-white mb-2">
                        {getText(
                          theoryTitle(theory, index)
                        )}
                      </h4>

                      <p className="text-xs text-neutral-400 leading-relaxed">
                        {getText(
                          theoryDescription(theory)
                        )}
                      </p>

                      <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.05]">
                        <div
                          className="h-full rounded-full bg-red-500"
                          style={{ width: `${score}%` }}
                        />
                      </div>

                    </div>
                  );
                })

              ) : (

                <EmptyState text="No competing theories were returned." />

              )}

            </div>

          </div>

        </div>

        {/* ======================================================
            03 / RED TEAM  +  04 / CONTRADICTIONS & GAPS
        ====================================================== */}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <div className="lg:col-span-6 bg-neutral-950 border border-neutral-800/80 p-6">

            <SectionHeader
              number="03 /"
              title="RED TEAM"
              subtitle="LUNA actively tries to break its own leading explanation."
            />

            <div className="mb-6 p-4 bg-red-950/20 border border-red-900/40 text-center">

              <div className="text-[10px] tracking-widest text-red-500 font-bold uppercase mb-1">
                VERDICT
              </div>

              <div className="text-xl font-black tracking-wider text-red-500 uppercase">
                {getText(redTeamVerdict)}
              </div>

            </div>

            <div className="space-y-3 text-xs text-neutral-300">

              {redTeamItems.length > 0 ? (

                redTeamItems.map((item, index) => (

                  <div
                    key={index}
                    className="flex gap-3 p-3 bg-neutral-900/30 border border-neutral-800/50"
                  >

                    <span className="text-red-500 font-bold shrink-0">
                      •
                    </span>

                    <div>

                      <span className="text-[9px] text-red-500 font-bold uppercase tracking-wider">
                        {item.type}
                      </span>

                      <p className="text-neutral-300 leading-relaxed mt-1">
                        {item.text}
                      </p>

                    </div>

                  </div>

                ))

              ) : (

                <>

                  <p>
                    • No unsupported claims were returned.
                  </p>

                  <p>
                    • No explicit assumptions were returned.
                  </p>

                  <p>
                    • The leading explanation should remain subject to verification.
                  </p>

                </>

              )}

            </div>

          </div>

          {/* ====================================================
              04 / CONTRADICTIONS & GAPS
          ==================================================== */}

          <div className="lg:col-span-6 bg-neutral-950 border border-neutral-800/80 p-6">

            <SectionHeader
              number="04 /"
              title="CONTRADICTIONS & GAPS"
              subtitle="What could weaken the current reconstruction or change the outcome."
            />

            <div className="space-y-2.5">

              {contradictions.length > 0 || gaps.length > 0 ? (

                <>
                  {contradictions.map((item, index) => (

                    <GapItem
                      key={`c-${index}`}
                      type="CHECK"
                      text={getText(
                        item?.description ||
                        item?.text ||
                        item?.reason ||
                        item
                      )}
                    />

                  ))}

                  {gaps.map((item, index) => (

                    <GapItem
                      key={`g-${index}`}
                      type="GAP"
                      text={getText(
                        item?.description ||
                        item?.text ||
                        item?.reason ||
                        item
                      )}
                    />

                  ))}
                </>

              ) : (

                <EmptyState text="No explicit contradictions or evidence gaps were returned." />

              )}

            </div>

          </div>

        </div>

        {/* ======================================================
            05 / NEXT BEST EVIDENCE
        ====================================================== */}

        <div className="bg-neutral-950 border border-neutral-800/80 p-6">

          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">

            <div>

              <div className="flex items-baseline gap-2 mb-1">

                <span className="text-xs font-bold text-red-500">
                  05 /
                </span>

                <h3 className="text-xs font-bold tracking-widest text-white uppercase">
                  NEXT BEST EVIDENCE
                </h3>

              </div>

              <h2 className="text-lg md:text-2xl font-bold text-white leading-snug max-w-4xl">
                {getText(nextEvidenceTitle)}
              </h2>

              {nextEvidenceReason && (
                <p className="text-xs text-neutral-400 mt-3 max-w-3xl leading-relaxed">
                  {getText(nextEvidenceReason)}
                </p>
              )}

            </div>

            <div className="text-center border border-red-900/50 bg-red-950/20 px-6 py-4 shrink-0">

              <div className="text-[10px] text-red-500 font-bold uppercase tracking-widest">
                PRIORITY
              </div>

              <div className="text-2xl font-black text-red-500 uppercase mt-1">
                {getText(nextPriority)}
              </div>

              {nextValue != null && (
                <div className="text-[10px] text-neutral-500 uppercase tracking-widest mt-2">
                  VALUE {Math.round(Number(nextValue) * (Number(nextValue) <= 1 ? 100 : 1))}%
                </div>
              )}

            </div>

          </div>

        </div>

        {/* ======================================================
            06 / INVESTIGATION GRAPH   +   07 / IDENTITY-LOCK
        ====================================================== */}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <div className="lg:col-span-6 bg-neutral-950 border border-neutral-800/80 p-6">

            <SectionHeader
              number="06 /"
              title="INVESTIGATION GRAPH"
              subtitle="The reasoning chain behind the result."
            />

            <div className="flex flex-wrap items-center gap-3">
              {graphChain.map((node, index) => (
                <React.Fragment key={node}>
                  <span
                    className={`px-4 py-2 text-[10px] font-bold uppercase tracking-wider rounded-sm border ${
                      node === "RED TEAM"
                        ? "border-red-600 bg-red-950/60 text-red-400"
                        : "border-neutral-800 bg-neutral-900/40 text-neutral-400"
                    }`}
                  >
                    {node}
                  </span>
                  {index < graphChain.length - 1 && node !== "NEXT ACTION" && (
                    <span className="text-neutral-700 text-xs">→</span>
                  )}
                </React.Fragment>
              ))}
            </div>

          </div>

          <div className="lg:col-span-6 bg-neutral-950 border border-neutral-800/80 p-6">

            <SectionHeader
              number="07 /"
              title="IDENTITY-LOCK"
              subtitle="Reason first. Identify only when authorized and necessary."
            />

            <div className="flex items-center gap-4 bg-neutral-900/30 border border-neutral-800/50 p-4">

              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-sm border border-red-800 bg-red-950/60">
                <span className="h-2.5 w-2.5 rounded-full bg-red-500" />
              </span>

              <div>
                <div className="text-sm font-black uppercase tracking-wide text-white">
                  {identityLock?.revealed
                    ? "IDENTITY AUTHORIZED"
                    : "IDENTITIES REMAIN ANONYMOUS"}
                </div>

                <p className="text-xs text-neutral-500 mt-1 leading-relaxed">
                  {identityLock?.reason ||
                    "LUNA's conclusion is based on behavior, evidence and relationships—not unnecessary identity exposure."}
                </p>
              </div>

            </div>

          </div>

        </div>

        {/* ======================================================
            PHILOSOPHY
        ====================================================== */}

        <div className="border border-red-950/50 bg-red-950/10 p-6">

          <div className="text-[10px] text-red-500 font-bold tracking-[0.25em] uppercase mb-3">
            LUNA INVESTIGATION PRINCIPLE
          </div>

          <div className="text-xl md:text-2xl font-black uppercase tracking-tight">
            What would change our mind?
          </div>

          <p className="text-xs text-neutral-500 mt-2 max-w-3xl">
            LUNA does not treat its leading explanation as truth.
            Every explanation remains challengeable by contradictory
            evidence, missing information, and competing scenarios.
          </p>

        </div>

        {/* ======================================================
            FOOTER
        ====================================================== */}

        <div className="flex justify-end pt-4">

          <button
            onClick={onClose}
            className="bg-red-600 hover:bg-red-500 text-black font-extrabold px-8 py-3 text-xs tracking-widest uppercase transition-colors"
          >
            RETURN TO CASE
          </button>

        </div>

      </div>
    </div>
  );
}


// ============================================================
// COMPONENTS
// ============================================================

function StatCard({ label, value }) {
  return (
    <div className="bg-neutral-950 border border-neutral-800/80 p-5 flex flex-col justify-between">

      <span className="text-[11px] tracking-widest text-neutral-400 font-bold uppercase">
        {label}
      </span>

      <span className="text-5xl font-black text-white mt-4">
        {value}
      </span>

    </div>
  );
}


function SectionHeader({
  number,
  title,
  subtitle,
}) {
  return (
    <>
      <div className="flex items-baseline gap-2 mb-1">

        <span className="text-xs font-bold text-red-500">
          {number}
        </span>

        <h3 className="text-xs font-bold tracking-widest text-white uppercase">
          {title}
        </h3>

      </div>

      <p className="text-[11px] text-neutral-500 mb-6">
        {subtitle}
      </p>
    </>
  );
}


function GapItem({ type, text }) {
  return (
    <div className="flex items-start gap-3 p-3 bg-neutral-900/30 border border-neutral-800/50 text-xs">

      <span
        className={`px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider rounded-sm shrink-0 ${
          type === "CONTR" || type === "CHECK"
            ? "bg-red-950 text-red-500 border border-red-800"
            : "bg-neutral-800 text-neutral-300"
        }`}
      >
        {type}
      </span>

      <span className="text-neutral-300 leading-relaxed">
        {text}
      </span>

    </div>
  );
}


function EmptyState({ text }) {
  return (
    <div className="p-4 border border-neutral-800/50 bg-neutral-900/20 text-xs text-neutral-500">
      {text}
    </div>
  );
}
