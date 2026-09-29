"use client";

import { useEffect, useMemo, useState } from "react";
import type {
  ChangeEvent,
  KeyboardEvent,
  ReactNode,
} from "react";

import {
  Activity,
  AlertCircle,
  BarChart3,
  Bot,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Database,
  FileText,
  Lightbulb,
  MessageSquare,
  RefreshCw,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Upload,
  XCircle,
} from "lucide-react";

import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";


// ============================================================
// CONFIGURATION
// ============================================================

const API_URL = "https://reviewlens-api-260925.azurewebsites.net";


// ============================================================
// TYPES
// ============================================================

type Review = {
  id: string;
  review_hash: string;
  review_text: string;
  redacted_text: string;
  sentiment: string;
  positive_score: number;
  neutral_score: number;
  negative_score: number;
  created_at: string;
};

type Insight = {
  id: number;
  type: string;
  title: string;
  description: string | null;
  created_at: string;
};

type Evidence = {
  id: number;
  insight_id: number;
  review_id: string;
  reason: string | null;
  search_score: number | null;
};

type Validation = {
  id: number;
  sample_size: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  created_at: string;
};

type Drift = {
  id: number;
  current_period: string;
  baseline_period: string;
  baseline_negative_rate: number;
  current_negative_rate: number;
  negative_rate_change: number;
  drift_detected: boolean;
  created_at: string;
};

type AssistantSource = {
  id: string;
  review_text: string;
  redacted_text: string;
  sentiment: string;
  positive_score?: number;
  neutral_score?: number;
  negative_score?: number;
  review_hash?: string;
  score?: number;
};


// ============================================================
// AI RESPONSE CLEANING
// ============================================================

function sanitizeAIAnswer(
  answer: unknown
): string {
  if (typeof answer !== "string") {
    return "";
  }

  return answer
    .replace(/&#x20;/gi, " ")
    .replace(/&#32;/gi, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/\\\*/g, "*")
    .replace(/\\\./g, ".")
    .replace(/\\_/g, "_")
    .replace(/\\#/g, "#")
    .replace(/\\-/g, "-")
    .replace(/\\`/g, "`")
    .replace(/\*\*/g, "")
    .replace(
      /(^|[\s])\*([^*\n]+)\*(?=\s|$)/g,
      "$1$2"
    )
    .replace(/`/g, "")
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}


// ============================================================
// MAIN COMPONENT
// ============================================================

export default function Home() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [validation, setValidation] =
    useState<Validation | null>(null);

  const [drift, setDrift] =
    useState<Drift | null>(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [question, setQuestion] = useState("");
  const [assistantAnswer, setAssistantAnswer] =
    useState("");
  const [assistantSources, setAssistantSources] =
    useState<AssistantSource[]>([]);
  const [assistantLoading, setAssistantLoading] =
    useState(false);

  const [uploading, setUploading] =
    useState(false);
  const [uploadMessage, setUploadMessage] =
    useState("");


// ============================================================
// LOAD DASHBOARD
// ============================================================

  const loadDashboard = async () => {
    try {
      setRefreshing(true);

      const [
        reviewsResponse,
        insightsResponse,
        evidenceResponse,
        validationResponse,
        driftResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/reviews`),
        fetch(`${API_URL}/insights`),
        fetch(`${API_URL}/evidence`),
        fetch(`${API_URL}/validation`),
        fetch(`${API_URL}/drift`),
      ]);

      if (!reviewsResponse.ok) {
        throw new Error(
          "Unable to load reviews."
        );
      }

      if (!insightsResponse.ok) {
        throw new Error(
          "Unable to load insights."
        );
      }

      if (!evidenceResponse.ok) {
        throw new Error(
          "Unable to load evidence."
        );
      }

      if (!validationResponse.ok) {
        throw new Error(
          "Unable to load validation."
        );
      }

      if (!driftResponse.ok) {
        throw new Error(
          "Unable to load drift monitoring."
        );
      }

      const reviewsData =
        await reviewsResponse.json();

      const insightsData =
        await insightsResponse.json();

      const evidenceData =
        await evidenceResponse.json();

      const validationData =
        await validationResponse.json();

      const driftData =
        await driftResponse.json();

      setReviews(
        Array.isArray(reviewsData?.reviews)
          ? reviewsData.reviews
          : []
      );

      setInsights(
        Array.isArray(insightsData?.insights)
          ? insightsData.insights
          : []
      );

      setEvidence(
        Array.isArray(evidenceData?.evidence)
          ? evidenceData.evidence
          : []
      );

      setValidation(
        validationData?.validation ?? null
      );

      setDrift(
        driftData?.drift ?? null
      );

    } catch (error) {
      console.error(
        "Dashboard loading failed:",
        error
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };


// ============================================================
// INITIAL LOAD
// ============================================================

  useEffect(() => {
    loadDashboard();
  }, []);


// ============================================================
// SENTIMENT COUNTS
// ============================================================

  const sentimentCounts = useMemo(() => {
    const positive = reviews.filter(
      (review) =>
        review.sentiment?.toLowerCase() ===
        "positive"
    ).length;

    const neutral = reviews.filter(
      (review) =>
        review.sentiment?.toLowerCase() ===
        "neutral"
    ).length;

    const negative = reviews.filter(
      (review) =>
        review.sentiment?.toLowerCase() ===
        "negative"
    ).length;

    return {
      positive,
      neutral,
      negative,
    };
  }, [reviews]);


  const sentimentData = [
    {
      name: "Positive",
      value: sentimentCounts.positive,
    },
    {
      name: "Neutral",
      value: sentimentCounts.neutral,
    },
    {
      name: "Negative",
      value: sentimentCounts.negative,
    },
  ];


  const positivePercentage =
    reviews.length > 0
      ? Math.round(
          (sentimentCounts.positive /
            reviews.length) *
            100
        )
      : 0;


  const negativePercentage =
    reviews.length > 0
      ? Math.round(
          (sentimentCounts.negative /
            reviews.length) *
            100
        )
      : 0;


// ============================================================
// COMPLAINTS
// ============================================================

  const complaintInsights = useMemo(() => {
    return insights.filter((insight) => {
      return (
        insight.type?.toLowerCase() ===
        "complaint"
      );
    });
  }, [insights]);


// ============================================================
// ASK ASSISTANT
// ============================================================

  const askAssistant = async () => {
    const trimmedQuestion =
      question.trim();

    if (!trimmedQuestion) {
      return;
    }

    setAssistantLoading(true);
    setAssistantAnswer("");
    setAssistantSources([]);

    try {
      const response = await fetch(
        `${API_URL}/assistant`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            question: trimmedQuestion,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Assistant request failed."
        );
      }

      const cleanedAnswer =
        sanitizeAIAnswer(data?.answer);

      setAssistantAnswer(
        cleanedAnswer ||
          "No answer was returned."
      );

      setAssistantSources(
        Array.isArray(data?.sources)
          ? data.sources
          : []
      );

    } catch (error) {
      console.error(
        "Assistant request failed:",
        error
      );

      setAssistantAnswer(
        "Unable to generate an answer. Please try again."
      );

      setAssistantSources([]);

    } finally {
      setAssistantLoading(false);
    }
  };


// ============================================================
// ENTER KEY
// ============================================================

  const handleQuestionKeyDown = (
    event: KeyboardEvent<HTMLInputElement>
  ) => {
    if (
      event.key === "Enter" &&
      !assistantLoading
    ) {
      event.preventDefault();
      askAssistant();
    }
  };


// ============================================================
// UPLOAD CSV
// ============================================================

  const handleUpload = async (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploading(true);
    setUploadMessage("");

    try {
      const formData =
        new FormData();

      formData.append(
        "file",
        file
      );

      const response =
        await fetch(
          `${API_URL}/reviews/upload`,
          {
            method: "POST",
            body: formData,
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Upload failed."
        );
      }

      setUploadMessage(
        `${file.name} uploaded successfully.`
      );

      await loadDashboard();

    } catch (error) {
      console.error(
        "Upload failed:",
        error
      );

      setUploadMessage(
        "Upload failed. Please try again."
      );

    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };


// ============================================================
// LOADING
// ============================================================

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="flex items-center gap-3 text-slate-600">
          <RefreshCw className="h-5 w-5 animate-spin" />

          <span className="text-sm">
            Loading ReviewLens AI...
          </span>
        </div>
      </main>
    );
  }


// ============================================================
// DASHBOARD
// ============================================================

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">

      <div className="flex min-h-screen">


        {/* ==================================================
            SIDEBAR
        ================================================== */}

        <aside className="hidden w-64 flex-col border-r border-slate-200 bg-white lg:flex">

          <div className="border-b border-slate-200 p-6">

            <div className="flex items-center gap-3">

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900">

                <Activity className="h-5 w-5 text-white" />

              </div>

              <div>

                <h1 className="text-lg font-bold">
                  ReviewLens AI
                </h1>

                <p className="text-xs text-slate-500">
                  Review Intelligence
                </p>

              </div>

            </div>

          </div>


          <nav className="flex-1 p-4">

            <div className="space-y-1">

              <a
                href="#overview"
                className="flex items-center gap-3 rounded-xl bg-slate-900 px-4 py-3 text-sm font-medium text-white"
              >
                <BarChart3 className="h-4 w-4" />
                Overview
              </a>


              <a
                href="#insights"
                className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-600 hover:bg-slate-50"
              >
                <Lightbulb className="h-4 w-4" />
                AI Insights
              </a>


              <a
                href="#reviews"
                className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-600 hover:bg-slate-50"
              >
                <MessageSquare className="h-4 w-4" />
                Reviews
              </a>


              <a
                href="#validation"
                className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-600 hover:bg-slate-50"
              >
                <CheckCircle2 className="h-4 w-4" />
                Sentiment Validation
              </a>


              <a
                href="#drift"
                className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-600 hover:bg-slate-50"
              >
                <Activity className="h-4 w-4" />
                Drift Monitoring
              </a>


              <a
                href="#assistant"
                className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-600 hover:bg-slate-50"
              >
                <Bot className="h-4 w-4" />
                AI Assistant
              </a>

            </div>

          </nav>


          <div className="border-t border-slate-200 p-4">

            <div className="rounded-xl bg-slate-50 p-4">

              <div className="mb-2 flex items-center gap-2">

                <ShieldCheck className="h-4 w-4 text-emerald-600" />

                <span className="text-xs font-semibold">
                  System Status
                </span>

              </div>

              <div className="flex items-center gap-2">

                <span className="h-2 w-2 rounded-full bg-emerald-500" />

                <span className="text-xs text-slate-500">
                  All systems operational
                </span>

              </div>

            </div>

          </div>

        </aside>


        {/* ==================================================
            MAIN
        ================================================== */}

        <div className="flex-1">


          {/* HEADER */}

          <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">

            <div className="flex items-center justify-between px-5 py-4 lg:px-8">

              <div>

                <h2 className="text-xl font-bold">
                  Review Intelligence
                </h2>

                <p className="text-sm text-slate-500">
                  AI-powered analysis of your customer feedback.
                </p>

              </div>


              <div className="flex items-center gap-3">

                <button
                  onClick={loadDashboard}
                  disabled={refreshing}
                  className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                >

                  <RefreshCw
                    className={`h-4 w-4 ${
                      refreshing
                        ? "animate-spin"
                        : ""
                    }`}
                  />

                  Refresh

                </button>


                <label className="flex cursor-pointer items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800">

                  <Upload className="h-4 w-4" />

                  {uploading
                    ? "Uploading..."
                    : "Upload Reviews"}

                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleUpload}
                    disabled={uploading}
                    className="hidden"
                  />

                </label>

              </div>

            </div>

          </header>


          <div className="space-y-6 p-5 lg:p-8">


            {/* ==================================================
                UPLOAD MESSAGE
            ================================================== */}

            {uploadMessage && (

              <div className="flex items-center justify-between rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">

                <div className="flex items-center gap-2">

                  <CheckCircle2 className="h-4 w-4" />

                  {uploadMessage}

                </div>


                <button
                  onClick={() =>
                    setUploadMessage("")
                  }
                  aria-label="Close message"
                >

                  <XCircle className="h-4 w-4" />

                </button>

              </div>

            )}


            {/* ==================================================
                OVERVIEW CARDS
            ================================================== */}

            <section
              id="overview"
              className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
            >

              <StatCard
                title="Total Reviews"
                value={reviews.length}
                icon={
                  <FileText className="h-5 w-5" />
                }
                subtitle="Processed reviews"
              />


              <StatCard
                title="Positive"
                value={
                  sentimentCounts.positive
                }
                icon={
                  <ThumbsUp className="h-5 w-5" />
                }
                subtitle={`${positivePercentage}% positive sentiment`}
              />


              <StatCard
                title="Neutral"
                value={
                  sentimentCounts.neutral
                }
                icon={
                  <Activity className="h-5 w-5" />
                }
                subtitle="Neutral sentiment"
              />


              <StatCard
                title="Negative"
                value={
                  sentimentCounts.negative
                }
                icon={
                  <ThumbsDown className="h-5 w-5" />
                }
                subtitle={`${negativePercentage}% negative sentiment`}
              />

            </section>


            {/* ==================================================
                SENTIMENT + AI INSIGHTS
            ================================================== */}

            <section className="grid gap-6 xl:grid-cols-3">


              {/* SENTIMENT */}

              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

                <div className="mb-4">

                  <h2 className="font-semibold">
                    Sentiment Distribution
                  </h2>

                  <p className="text-sm text-slate-500">
                    Overall customer sentiment
                  </p>

                </div>


                <div className="h-64">

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <PieChart>

                      <Pie
                        data={sentimentData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={65}
                        outerRadius={95}
                        paddingAngle={3}
                      >

                        <Cell fill="#10b981" />
                        <Cell fill="#94a3b8" />
                        <Cell fill="#ef4444" />

                      </Pie>

                      <Tooltip />

                    </PieChart>

                  </ResponsiveContainer>

                </div>


                <div className="space-y-3">

                  <LegendRow
                    label="Positive"
                    value={
                      sentimentCounts.positive
                    }
                    dotClass="bg-emerald-500"
                  />

                  <LegendRow
                    label="Neutral"
                    value={
                      sentimentCounts.neutral
                    }
                    dotClass="bg-slate-400"
                  />

                  <LegendRow
                    label="Negative"
                    value={
                      sentimentCounts.negative
                    }
                    dotClass="bg-red-500"
                  />

                </div>

              </div>


              {/* AI INSIGHTS */}

              <div
                id="insights"
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm xl:col-span-2"
              >

                <div className="mb-5 flex items-start justify-between">

                  <div>

                    <div className="flex items-center gap-2">

                      <Sparkles className="h-5 w-5" />

                      <h2 className="font-semibold">
                        AI Insights
                      </h2>

                    </div>

                    <p className="mt-1 text-sm text-slate-500">
                      Patterns extracted from customer feedback
                    </p>

                  </div>


                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                    {insights.length} insights
                  </span>

                </div>


                {insights.length > 0 ? (

                  <div className="grid gap-3 md:grid-cols-2">

                    {insights
                      .slice(0, 6)
                      .map((insight) => (

                        <div
                          key={insight.id}
                          className="rounded-xl border border-slate-200 p-4"
                        >

                          <div className="mb-2 flex items-center justify-between">

                            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                              {insight.type}
                            </span>

                            <ChevronRight className="h-4 w-4 text-slate-400" />

                          </div>


                          <h3 className="font-medium text-slate-900">
                            {insight.title}
                          </h3>


                          {insight.description && (

                            <p className="mt-2 text-sm leading-5 text-slate-500">
                              {insight.description}
                            </p>

                          )}

                        </div>

                      ))}

                  </div>

                ) : (

                  <div className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
                    No insights available.
                  </div>

                )}

              </div>

            </section>


            {/* ==================================================
                SENTIMENT VALIDATION
            ================================================== */}

            <section
              id="validation"
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >

              <div className="mb-5 flex items-start justify-between">

                <div>

                  <div className="flex items-center gap-2">

                    <ShieldCheck className="h-5 w-5 text-emerald-600" />

                    <h2 className="font-semibold">
                      Sentiment Validation
                    </h2>

                  </div>

                  <p className="mt-1 text-sm text-slate-500">
                    Performance against the labelled validation sample
                  </p>

                </div>


                {validation && (

                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
                    Validation Complete
                  </span>

                )}

              </div>


              {validation ? (

                <>

                  {/* SAMPLE SIZE */}

                  <div className="mb-5 rounded-xl bg-slate-50 p-5">

                    <div className="flex items-center justify-between">

                      <div>

                        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                          Validation Sample
                        </p>

                        <p className="mt-1 text-3xl font-bold text-slate-900">
                          {validation.sample_size}
                        </p>

                        <p className="text-sm text-slate-500">
                          labelled reviews
                        </p>

                      </div>


                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50">

                        <CheckCircle2 className="h-6 w-6 text-emerald-600" />

                      </div>

                    </div>

                  </div>


                  {/* METRICS */}

                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                    <MetricCard
                      title="Accuracy"
                      value={`${(
                        validation.accuracy * 100
                      ).toFixed(2)}%`}
                    />


                    <MetricCard
                      title="Precision"
                      value={`${(
                        validation.precision * 100
                      ).toFixed(2)}%`}
                    />


                    <MetricCard
                      title="Recall"
                      value={`${(
                        validation.recall * 100
                      ).toFixed(2)}%`}
                    />


                    <MetricCard
                      title="F1 Score"
                      value={`${(
                        validation.f1 * 100
                      ).toFixed(2)}%`}
                    />

                  </div>

                </>

              ) : (

                <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

                  <div className="flex items-center gap-3">

                    <AlertCircle className="h-5 w-5 text-slate-400" />

                    <div>

                      <p className="text-sm font-medium text-slate-700">
                        No validation results available.
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Run the sentiment validation pipeline and refresh the dashboard.
                      </p>

                    </div>

                  </div>

                </div>

              )}

            </section>


            {/* ==================================================
                DRIFT MONITORING
            ================================================== */}

            <section
              id="drift"
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div className="mb-5 flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-slate-700" />
                    <h2 className="font-semibold">
                      Drift Monitoring
                    </h2>
                  </div>

                  <p className="mt-1 text-sm text-slate-500">
                    Monitors changes in the negative sentiment rate
                    between baseline and current review periods.
                  </p>
                </div>

                {drift && (
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${
                      drift.drift_detected
                        ? "bg-red-50 text-red-700"
                        : "bg-emerald-50 text-emerald-700"
                    }`}
                  >
                    {drift.drift_detected
                      ? "Drift Detected"
                      : "No Drift Detected"}
                  </span>
                )}
              </div>

              {drift ? (
                <>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <MetricCard
                      title="Baseline Negative Rate"
                      value={`${(
                        drift.baseline_negative_rate * 100
                      ).toFixed(1)}%`}
                    />

                    <MetricCard
                      title="Current Negative Rate"
                      value={`${(
                        drift.current_negative_rate * 100
                      ).toFixed(1)}%`}
                    />

                    <MetricCard
                      title="Rate Change"
                      value={`${(
                        drift.negative_rate_change * 100
                      ).toFixed(1)}%`}
                    />
                  </div>

                  <div className="mt-5 grid gap-4 md:grid-cols-2">
                    <div className="rounded-xl bg-slate-50 p-4">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                        Baseline Period
                      </p>

                      <p className="mt-2 break-words text-sm leading-6 text-slate-700">
                        {drift.baseline_period}
                      </p>
                    </div>

                    <div className="rounded-xl bg-slate-50 p-4">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                        Current Period
                      </p>

                      <p className="mt-2 break-words text-sm leading-6 text-slate-700">
                        {drift.current_period}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 rounded-xl border border-slate-200 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-slate-900">
                          Drift Threshold
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          Drift is flagged when the negative sentiment
                          rate changes by at least 20%.
                        </p>
                      </div>

                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                        20%
                      </span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
                  <div className="flex items-center gap-3">
                    <AlertCircle className="h-5 w-5 text-slate-400" />

                    <div>
                      <p className="text-sm font-medium text-slate-700">
                        No drift monitoring results available.
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Run the drift monitoring pipeline and refresh
                        the dashboard.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </section>


            {/* ==================================================
                COMMON COMPLAINTS + EVIDENCE
            ================================================== */}

            <section className="grid gap-6 lg:grid-cols-2">


              {/* COMMON COMPLAINTS */}

              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

                <div className="mb-5">

                  <h2 className="font-semibold">
                    Common Complaints
                  </h2>

                  <p className="text-sm text-slate-500">
                    Issues identified from customer reviews
                  </p>

                </div>


                <div className="space-y-3">

                  {complaintInsights.length >
                  0 ? (

                    complaintInsights.map(
                      (insight) => (

                        <div
                          key={insight.id}
                          className="rounded-xl bg-slate-50 p-4"
                        >

                          <div className="flex items-center justify-between">

                            <div className="flex items-center gap-3">

                              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50">

                                <AlertCircle className="h-4 w-4 text-red-600" />

                              </div>


                              <div>

                                <p className="text-sm font-medium">
                                  {insight.title}
                                </p>

                                <p className="mt-1 text-xs text-slate-500">
                                  {insight.description}
                                </p>

                              </div>

                            </div>


                            <ChevronRight className="h-4 w-4 text-slate-400" />

                          </div>


                          <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">

                            <Database className="h-3.5 w-3.5" />

                            {evidence.filter(
                              (item) =>
                                item.insight_id ===
                                insight.id
                            ).length}{" "}
                            evidence

                          </div>

                        </div>

                      )
                    )

                  ) : (

                    <div className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
                      No complaints available.
                    </div>

                  )}

                </div>

              </div>


              {/* EVIDENCE COVERAGE */}

              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

                <div className="mb-5">

                  <h2 className="font-semibold">
                    Evidence Coverage
                  </h2>

                  <p className="text-sm text-slate-500">
                    Links between insights and source reviews
                  </p>

                </div>


                {insights.length > 0 ? (

                  <div className="space-y-3">

                    {insights.map(
                      (insight) => {

                        const linkedEvidence =
                          evidence.filter(
                            (item) =>
                              item.insight_id ===
                              insight.id
                          );

                        return (

                          <div
                            key={insight.id}
                            className="flex items-center justify-between rounded-xl bg-slate-50 p-4"
                          >

                            <div className="flex items-center gap-3">

                              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white">

                                <FileText className="h-4 w-4 text-slate-600" />

                              </div>


                              <div>

                                <p className="text-sm font-medium">
                                  {insight.title}
                                </p>

                                <p className="text-xs text-slate-500">
                                  {linkedEvidence.length} linked reviews
                                </p>

                              </div>

                            </div>


                            <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-slate-600">
                              {linkedEvidence.length}
                            </span>

                          </div>

                        );

                      }
                    )}

                  </div>

                ) : (

                  <div className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
                    No evidence available.
                  </div>

                )}

              </div>

            </section>


            {/* ==================================================
                AI ASSISTANT
            ================================================== */}

            <section
              id="assistant"
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >

              <div className="mb-5 flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900">

                  <Bot className="h-5 w-5 text-white" />

                </div>


                <div>

                  <h2 className="text-lg font-semibold">
                    Ask ReviewLens AI
                  </h2>

                  <p className="text-sm text-slate-500">
                    Ask questions about your customer reviews
                  </p>

                </div>

              </div>


              <div className="flex flex-col gap-3 sm:flex-row">

                <input
                  type="text"
                  value={question}
                  onChange={(event) =>
                    setQuestion(
                      event.target.value
                    )
                  }
                  onKeyDown={
                    handleQuestionKeyDown
                  }
                  disabled={assistantLoading}
                  placeholder="What are the main complaints from customers?"
                  className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100 disabled:bg-slate-50"
                />


                <button
                  onClick={askAssistant}
                  disabled={
                    assistantLoading ||
                    !question.trim()
                  }
                  className="flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                >

                  {assistantLoading ? (

                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      Analyzing...
                    </>

                  ) : (

                    <>
                      <Send className="h-4 w-4" />
                      Ask AI
                    </>

                  )}

                </button>

              </div>


              {/* AI ANSWER */}

              {assistantAnswer && (

                <div className="mt-6">

                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

                    <div className="mb-3 flex items-center gap-2">

                      <Sparkles className="h-4 w-4" />

                      <h3 className="font-semibold">
                        ReviewLens AI
                      </h3>

                    </div>


                    <div className="whitespace-pre-line text-sm leading-7 text-slate-700">
                      {assistantAnswer}
                    </div>

                  </div>


                  {/* RETRIEVED EVIDENCE */}

                  {assistantSources.length >
                    0 && (

                    <div className="mt-6">

                      <div className="mb-4 flex items-center justify-between">

                        <div>

                          <h3 className="text-sm font-semibold">
                            Retrieved Evidence
                          </h3>

                          <p className="mt-1 text-xs text-slate-500">
                            Reviews used by Qwen3 to generate this answer
                          </p>

                        </div>


                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                          {
                            assistantSources.length
                          }{" "}
                          sources
                        </span>

                      </div>


                      <div className="space-y-3">

                        {assistantSources.map(
                          (
                            source,
                            index
                          ) => {

                            const sentiment =
                              source.sentiment
                                ?.toLowerCase() ||
                              "neutral";


                            return (

                              <div
                                key={
                                  source.id ||
                                  `source-${index}`
                                }
                                className="rounded-xl border border-slate-200 bg-white p-4"
                              >

                                <div className="mb-3 flex items-center justify-between">

                                  <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                    Evidence{" "}
                                    {index + 1}
                                  </span>


                                  <span
                                    className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                                      sentiment ===
                                      "positive"
                                        ? "bg-emerald-50 text-emerald-700"
                                        : sentiment ===
                                            "negative"
                                          ? "bg-red-50 text-red-700"
                                          : "bg-slate-100 text-slate-600"
                                    }`}
                                  >
                                    {source.sentiment ||
                                      "Neutral"}
                                  </span>

                                </div>


                                <p className="text-sm leading-6 text-slate-700">
                                  {
                                    source.redacted_text ||
                                    source.review_text
                                  }
                                </p>


                                {typeof source.score ===
                                  "number" && (

                                  <div className="mt-3 flex items-center gap-2 text-xs text-slate-400">

                                    <Search className="h-3.5 w-3.5" />

                                    Retrieval score:
                                    {" "}
                                    {source.score.toFixed(
                                      3
                                    )}

                                  </div>

                                )}

                              </div>

                            );

                          }
                        )}

                      </div>

                    </div>

                  )}

                </div>

              )}

            </section>


            {/* ==================================================
                RECENT REVIEWS
            ================================================== */}

            <section
              id="reviews"
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >

              <div className="mb-5 flex items-center justify-between">

                <div>

                  <h2 className="font-semibold">
                    Recent Reviews
                  </h2>

                  <p className="text-sm text-slate-500">
                    Latest processed customer feedback
                  </p>

                </div>


                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  {reviews.length} total
                </span>

              </div>


              {reviews.length > 0 ? (

                <div className="space-y-3">

                  {reviews.map(
                    (review) => {

                      const sentiment =
                        review.sentiment
                          ?.toLowerCase() ||
                        "neutral";


                      return (

                        <div
                          key={review.id}
                          className="rounded-xl border border-slate-200 p-4"
                        >

                          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">

                            <div className="flex-1">

                              <div className="mb-2 flex items-center gap-2">

                                {sentiment ===
                                "positive" ? (

                                  <ThumbsUp className="h-4 w-4 text-emerald-600" />

                                ) : sentiment ===
                                  "negative" ? (

                                  <ThumbsDown className="h-4 w-4 text-red-600" />

                                ) : (

                                  <Activity className="h-4 w-4 text-slate-500" />

                                )}


                                <span
                                  className={`text-xs font-semibold uppercase ${
                                    sentiment ===
                                    "positive"
                                      ? "text-emerald-600"
                                      : sentiment ===
                                          "negative"
                                        ? "text-red-600"
                                        : "text-slate-500"
                                  }`}
                                >
                                  {
                                    review.sentiment ||
                                    "Neutral"
                                  }
                                </span>

                              </div>


                              <p className="text-sm leading-6 text-slate-700">
                                {review.redacted_text ||
                                  review.review_text}
                              </p>

                            </div>


                            <div className="flex items-center gap-2 text-xs text-slate-400">

                              <Clock3 className="h-3.5 w-3.5" />

                              {new Date(
                                review.created_at
                              ).toLocaleDateString()}

                            </div>

                          </div>

                        </div>

                      );

                    }
                  )}

                </div>

              ) : (

                <div className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
                  No reviews available.
                </div>

              )}

            </section>


            {/* ==================================================
                FOOTER
            ================================================== */}

            <footer className="flex flex-col items-center justify-between gap-3 border-t border-slate-200 pt-6 text-xs text-slate-400 sm:flex-row">

              <p>
                ReviewLens AI • Customer Review Intelligence
              </p>


              <div className="flex items-center gap-2">

                <ShieldCheck className="h-3.5 w-3.5" />

                PII-aware analysis

              </div>

            </footer>

          </div>

        </div>

      </div>

    </main>
  );
}


// ============================================================
// STAT CARD
// ============================================================

function StatCard({
  title,
  value,
  icon,
  subtitle,
}: {
  title: string;
  value: number;
  icon: ReactNode;
  subtitle: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm text-slate-500">
            {title}
          </p>

          <p className="mt-2 text-3xl font-bold">
            {value}
          </p>

        </div>


        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
          {icon}
        </div>

      </div>


      <p className="mt-3 text-xs text-slate-400">
        {subtitle}
      </p>

    </div>
  );
}


// ============================================================
// SENTIMENT LEGEND
// ============================================================

function LegendRow({
  label,
  value,
  dotClass,
}: {
  label: string;
  value: number;
  dotClass: string;
}) {
  return (
    <div className="flex items-center justify-between">

      <div className="flex items-center gap-2">

        <span
          className={`h-2.5 w-2.5 rounded-full ${dotClass}`}
        />

        <span className="text-sm text-slate-600">
          {label}
        </span>

      </div>


      <span className="text-sm font-semibold">
        {value}
      </span>

    </div>
  );
}


// ============================================================
// VALIDATION METRIC CARD
// ============================================================

function MetricCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">

      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {title}
      </p>

      <p className="mt-2 text-2xl font-bold text-slate-900">
        {value}
      </p>

    </div>
  );
}

