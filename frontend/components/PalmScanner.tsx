"use client";

import { CSSProperties, useEffect, useMemo, useRef, useState } from "react";
import { Camera, MoonStar, Sparkles, Wand2 } from "lucide-react";
import { FilesetResolver, HandLandmarker } from "@mediapipe/tasks-vision";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

type DetailItem = {
  name: string;
  icon: string;
  score: number;
  level: string;
  description: string;
};

type AnalysisResponse = {
  success?: boolean;
  summary?: string;
  careers?: string[];
  analysis?: string;
  report?: string;
  scores?: Record<string, number>;
  details?: DetailItem[];
  features?: Record<string, number>;
  error?: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://palmoracleai.onrender.com";

const LABELS: Record<string, string> = {
  logic: "Logic",
  emotion: "Cảm xúc",
  leadership: "Lãnh đạo",
  creativity: "Sáng tạo",
  confidence: "Tự tin",
  social: "Xã hội",
  determination: "Quyết tâm",
  independence: "Độc lập",
};

const FLOATING_TAROTS = [
  { left: "6%", top: "14%", rotate: "-12deg", delay: "0s", scale: 1.0 },
  { left: "84%", top: "16%", rotate: "10deg", delay: "1s", scale: 1.08 },
  { left: "10%", top: "76%", rotate: "8deg", delay: "1.8s", scale: 0.96 },
  { left: "84%", top: "72%", rotate: "-8deg", delay: "2.4s", scale: 1.02 },
];

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

export default function PalmScanner() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const overlayRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const landmarkerRef = useRef<HandLandmarker | null>(null);
  const rafRef = useRef<number | null>(null);
  const stableFramesRef = useRef(0);
  const lastCaptureRef = useRef(0);
  const capturingRef = useRef(false);
  const handVisibleRef = useRef(false);
  const handCenteredRef = useRef(false);

  const [status, setStatus] = useState("Đang mở cánh cổng tri thức...");
  const [cameraReady, setCameraReady] = useState(false);
  const [handVisible, setHandVisible] = useState(false);
  const [handCentered, setHandCentered] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const chartData = useMemo(() => {
    if (!result?.scores) return [];
    return Object.entries(result.scores).map(([key, value]) => ({
      trait: LABELS[key] || key,
      score: Number(value),
    }));
  }, [result]);

  useEffect(() => {
    let cancelled = false;

    const init = async () => {
      try {
        setStatus("Đang xin quyền camera...");
        await startCamera();
        await initHandDetector();

        if (cancelled) return;

        setCameraReady(true);
        setStatus("Đưa bàn tay vào vòng ma thuật...");
        startDetectionLoop();
      } catch (error) {
        console.error(error);
        setStatus("Không thể khởi tạo camera hoặc bộ nhận diện tay.");
      }
    };

    init();

    return () => {
      cancelled = true;
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      streamRef.current?.getTracks().forEach((track) => track.stop());
      landmarkerRef.current?.close?.();
    };
  }, []);

  async function startCamera() {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user",
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      audio: false,
    });

    streamRef.current = stream;

    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
    }

    try {
      const audio = new Audio("/magic.mp3");
      audio.volume = 0.45;
      audio.play().catch(() => {});
    } catch {
      // bỏ qua nếu trình duyệt chặn
    }
  }

  async function initHandDetector() {
    const vision = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
    );

    const detector = await HandLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
      },
      runningMode: "VIDEO",
      numHands: 1,
    });

    landmarkerRef.current = detector;
  }

  function drawOverlay(
    w: number,
    h: number,
    centered: boolean,
    cx: number,
    cy: number,
    radius: number,
    landmarks?: { x: number; y: number }[]
  ) {
    const canvas = overlayRef.current;
    if (!canvas) return;

    canvas.width = w;
    canvas.height = h;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, w, h);

    ctx.fillStyle = "rgba(0,0,0,0.10)";
    ctx.fillRect(0, 0, w, h);

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.strokeStyle = centered ? "rgba(103,232,249,0.95)" : "rgba(196,181,253,0.9)";
    ctx.lineWidth = 4;
    ctx.shadowColor = centered ? "rgba(103,232,249,0.8)" : "rgba(168,85,247,0.7)";
    ctx.shadowBlur = 18;
    ctx.stroke();
    ctx.restore();

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.72, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255,255,255,0.14)";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();

    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx - radius * 1.25, cy);
    ctx.lineTo(cx + radius * 1.25, cy);
    ctx.moveTo(cx, cy - radius * 1.25);
    ctx.lineTo(cx, cy + radius * 1.25);
    ctx.stroke();
    ctx.restore();

    if (landmarks?.length) {
      ctx.save();
      ctx.fillStyle = centered ? "rgba(125,249,255,0.85)" : "rgba(233,213,255,0.8)";
      landmarks.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x * w, p.y * h, 4, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.restore();
    }

    ctx.save();
    ctx.font = "600 16px Inter, system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillStyle = centered ? "rgba(204,251,241,0.95)" : "rgba(240,233,255,0.92)";
    ctx.fillText(
      centered ? "Bàn tay đã vào đúng vị trí" : "Đặt lòng bàn tay vào vòng ma thuật",
      cx,
      cy - radius - 18
    );
    ctx.restore();
  }

  async function beginAutoCapture() {
    if (capturingRef.current || isAnalyzing) return;
    capturingRef.current = true;

    try {
      for (const n of [3, 2, 1]) {
        setCountdown(n);
        setStatus("Đang tiên tri...");
        await sleep(700);
      }
      setCountdown(null);
      await captureAndAnalyze();
    } finally {
      capturingRef.current = false;
    }
  }

  async function captureAndAnalyze() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    setIsAnalyzing(true);
    setStatus("Đang tiên tri vận mệnh...");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      setIsAnalyzing(false);
      return;
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob((b) => resolve(b), "image/jpeg", 0.95)
    );

    if (!blob) {
      setIsAnalyzing(false);
      setStatus("Không thể chụp ảnh từ camera.");
      return;
    }

    const formData = new FormData();
    formData.append("file", blob, "palm.jpg");

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = (await response.json()) as AnalysisResponse;
      setResult(data);
      setStatus("Tiên tri đã hoàn tất.");
      lastCaptureRef.current = Date.now();
    } catch (error) {
      console.error(error);
      setStatus("Không kết nối được backend.");
    } finally {
      setIsAnalyzing(false);
      setCountdown(null);
    }
  }

  function startDetectionLoop() {
    const video = videoRef.current;
    const detector = landmarkerRef.current;
    if (!video || !detector) return;

    const loop = () => {
      const activeVideo = videoRef.current;
      const activeDetector = landmarkerRef.current;

      if (activeVideo && activeDetector && activeVideo.readyState >= 2) {
        const now = performance.now();
        const result = activeDetector.detectForVideo(activeVideo, now);
        const hand = result.landmarks?.[0];

        const rect = activeVideo.getBoundingClientRect();
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const radius = Math.min(rect.width, rect.height) * 0.28;

        let visible = false;
        let centered = false;

        if (hand) {
          visible = true;

          const xs = hand.map((p) => p.x);
          const ys = hand.map((p) => p.y);

          const minX = Math.min(...xs);
          const maxX = Math.max(...xs);
          const minY = Math.min(...ys);
          const maxY = Math.max(...ys);

          const handCx = ((minX + maxX) / 2) * rect.width;
          const handCy = ((minY + maxY) / 2) * rect.height;
          const boxW = (maxX - minX) * rect.width;
          const boxH = (maxY - minY) * rect.height;
          const dist = Math.hypot(handCx - centerX, handCy - centerY);

          const boxOk = boxW > rect.width * 0.12 && boxH > rect.height * 0.12;
          const distOk = dist < radius * 0.55;

          centered = boxOk && distOk;

          drawOverlay(
            Math.round(rect.width),
            Math.round(rect.height),
            centered,
            centerX,
            centerY,
            radius,
            hand
          );
        } else {
          drawOverlay(
            Math.round(rect.width),
            Math.round(rect.height),
            false,
            centerX,
            centerY,
            radius
          );
        }

        if (visible !== handVisibleRef.current) {
          handVisibleRef.current = visible;
          setHandVisible(visible);
        }

        if (centered !== handCenteredRef.current) {
          handCenteredRef.current = centered;
          setHandCentered(centered);
        }

        if (centered) {
          stableFramesRef.current += 1;
          if (
            stableFramesRef.current >= 12 &&
            Date.now() - lastCaptureRef.current > 3500 &&
            !capturingRef.current &&
            !isAnalyzing
          ) {
            stableFramesRef.current = 0;
            beginAutoCapture();
          }
        } else {
          stableFramesRef.current = 0;
        }

        if (!visible) {
          setStatus("Chưa phát hiện bàn tay.");
        } else if (centered) {
          setStatus("Bàn tay đã được khóa... đang tiên tri...");
        } else {
          setStatus("Di chuyển bàn tay vào tâm vòng ma thuật...");
        }
      }

      rafRef.current = requestAnimationFrame(loop);
    };

    rafRef.current = requestAnimationFrame(loop);
  }

  const radarData = useMemo(() => {
    if (!result?.scores) return [];
    return Object.entries(result.scores).map(([key, value]) => ({
      trait: LABELS[key] || key,
      score: Number(value),
    }));
  }, [result]);

  const details = result?.details || [];

  return (
    <main className="relative mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-8 text-white md:px-8">
      {FLOATING_TAROTS.map((card, idx) => {
        const style: CSSProperties = {
          left: card.left,
          top: card.top,
          animation: "floatCard 6s ease-in-out infinite",
          animationDelay: card.delay,
          transform: `rotate(${card.rotate}) scale(${card.scale})`,
        };

        return (
          <div
            key={idx}
            className="pointer-events-none absolute hidden xl:block"
            style={style}
          >
            <div className="h-36 w-24 rounded-2xl border border-purple-400/40 bg-gradient-to-b from-fuchsia-950/90 to-slate-950/90 shadow-2xl shadow-purple-950/50 backdrop-blur-sm">
              <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
                <MoonStar className="h-7 w-7 text-fuchsia-300" />
                <div className="text-xs tracking-[0.35em] text-purple-200/80">TAROT</div>
              </div>
            </div>
          </div>
        );
      })}

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div
          className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/5 p-4 shadow-[0_0_60px_rgba(168,85,247,0.12)] backdrop-blur-xl md:p-6"
          style={{ animation: "auraPulse 6s ease-in-out infinite" }}
        >
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h2 className="text-2xl font-semibold text-white">🔮 Vòng ma thuật camera</h2>
              <p className="text-sm text-zinc-300/80">Đưa lòng bàn tay vào vòng sáng giữa khung hình để tự động chụp.</p>
            </div>

            <div className="flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-400/10 px-4 py-2 text-xs text-cyan-100">
              <Camera className="h-4 w-4" />
              {cameraReady ? "Camera đã mở" : "Đang khởi tạo"}
            </div>
          </div>

          <div className="relative mx-auto aspect-[4/3] w-full max-w-4xl overflow-hidden rounded-[1.75rem] border border-purple-400/30 bg-black/60">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="absolute inset-0 h-full w-full scale-x-[-1] object-cover"
            />

            <canvas
              ref={overlayRef}
              className="pointer-events-none absolute inset-0 h-full w-full scale-x-[-1]"
            />

            <canvas ref={canvasRef} className="hidden" />

            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(168,85,247,0.14),transparent_36%)]" />

            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <div
                className={`rounded-full border transition-all duration-300 ${
                  handCentered ? "border-cyan-300/90" : "border-purple-300/80"
                }`}
                style={{
                  width: "38%",
                  height: "38%",
                  boxShadow: handCentered
                    ? "0 0 0 18px rgba(34,211,238,0.06), 0 0 90px rgba(34,211,238,0.22)"
                    : "0 0 0 18px rgba(168,85,247,0.05), 0 0 90px rgba(168,85,247,0.20)",
                }}
              />
            </div>

            <div className="pointer-events-none absolute left-1/2 top-[13%] -translate-x-1/2 rounded-full border border-white/10 bg-black/35 px-4 py-2 text-sm text-white/90 backdrop-blur-md">
              {status}
            </div>

            {countdown !== null && (
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                <div className="rounded-full border border-cyan-300/50 bg-black/40 px-8 py-6 text-6xl font-bold text-cyan-200 backdrop-blur-md shadow-[0_0_60px_rgba(34,211,238,0.35)]">
                  {countdown}
                </div>
              </div>
            )}

            {!handVisible && cameraReady && (
              <div className="pointer-events-none absolute inset-x-0 bottom-6 mx-auto w-fit rounded-full border border-fuchsia-300/20 bg-black/40 px-5 py-2 text-sm text-fuchsia-100 backdrop-blur-md">
                <span className="inline-block animate-pulse">✦</span> Đưa bàn tay vào khung để đánh thức quả cầu tiên tri
              </div>
            )}
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <InfoChip title="Tự động chụp" value={handCentered ? "Đã khóa" : "Chờ tay vào vị trí"} />
            <InfoChip title="AI Vision" value={handVisible ? "Đang quét" : "Chưa thấy tay"} />
            <InfoChip title="Âm thanh" value={isAnalyzing ? "Đang ngân" : "Sẵn sàng"} />
          </div>
        </div>

        <div className="flex flex-col gap-6">
          <OrbCard />

          <div className="rounded-[2rem] border border-white/10 bg-black/35 p-5 backdrop-blur-xl">
            <div className="flex items-center gap-3 text-lg font-semibold text-white">
              <Wand2 className="h-5 w-5 text-fuchsia-300" />
              Tiến trình tiên tri
            </div>

            <div className="mt-4 space-y-3 text-sm text-zinc-300">
              <ProgressLine label="Mở camera" active={cameraReady} />
              <ProgressLine label="Nhận diện bàn tay" active={handVisible} />
              <ProgressLine label="Khóa vị trí" active={handCentered} />
              <ProgressLine label="Tự động phân tích" active={isAnalyzing} />
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-[2rem] border border-white/10 bg-black/35 p-6 backdrop-blur-xl">
          <h2 className="text-2xl font-semibold text-white">✨ Lời tiên tri</h2>

          <div className="mt-4 min-h-[220px] rounded-3xl border border-purple-500/20 bg-white/5 p-5 text-zinc-200 leading-8">
            {isAnalyzing ? (
              <div className="flex min-h-[220px] flex-col items-center justify-center gap-4 text-center text-purple-100">
                <div className="flex items-center gap-3 text-lg font-medium">
                  <Sparkles className="h-5 w-5 animate-pulse text-cyan-300" />
                  <span>Đang tiên tri...</span>
                </div>
                <div className="text-sm text-zinc-300/80">Vòng sao đang xoay, dữ liệu đang được giải mã.</div>
              </div>
            ) : result?.summary ? (
              <div>
                <div className="text-lg font-semibold text-purple-200">Tóm tắt vận mệnh</div>
                <p className="mt-2 whitespace-pre-wrap">{result.summary}</p>

                {result.careers?.length ? (
                  <div className="mt-5">
                    <div className="text-sm uppercase tracking-[0.25em] text-zinc-400">Nghề nghiệp phù hợp</div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {result.careers.map((career) => (
                        <span
                          key={career}
                          className="rounded-full border border-fuchsia-400/25 bg-fuchsia-500/10 px-3 py-1 text-sm text-fuchsia-100"
                        >
                          {career}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}

                {result.analysis ? (
                  <div className="mt-6">
                    <div className="text-sm uppercase tracking-[0.25em] text-zinc-400">Phân tích mở rộng</div>
                    <pre className="mt-3 whitespace-pre-wrap font-sans">{result.analysis}</pre>
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="flex min-h-[220px] items-center justify-center text-zinc-400">
                Chưa có kết quả. Hãy đặt bàn tay vào vòng ma thuật.
              </div>
            )}
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-black/35 p-6 backdrop-blur-xl">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-2xl font-semibold text-white">📊 Biểu đồ năng lực</h2>
            <div className="text-xs uppercase tracking-[0.3em] text-purple-200/70">Mystic Summary</div>
          </div>

          <div className="mt-4 h-[320px] rounded-3xl border border-purple-500/15 bg-white/5 p-2">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={chartData}>
                  <PolarGrid stroke="rgba(255,255,255,0.18)" />
                  <PolarAngleAxis dataKey="trait" tick={{ fill: "#f5d0fe", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      background: "rgba(10,10,20,0.95)",
                      border: "1px solid rgba(168,85,247,0.45)",
                      borderRadius: 16,
                      color: "#fff",
                    }}
                  />
                  <Radar dataKey="score" stroke="#c084fc" fill="#8b5cf6" fillOpacity={0.35} />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-zinc-400">Chưa có biểu đồ.</div>
            )}
          </div>
        </div>
      </section>

      {details.length ? (
        <section className="mt-10">
          <h2
            className="text-center text-4xl font-bold text-white"
            style={{ animation: "glowText 4s ease-in-out infinite" }}
          >
            🎯 Chi Tiết 8 Chỉ Số
          </h2>
          <p className="mt-3 text-center text-zinc-300">
            Mỗi chỉ số đều có mức điểm, trạng thái và mô tả cụ thể.
          </p>

          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
            {details.map((item, index) => (
              <div
                key={index}
                className="group rounded-[1.8rem] border border-white/10 bg-[#0b0b16]/80 p-6 shadow-[0_0_40px_rgba(168,85,247,0.12)] transition-transform duration-300 hover:-translate-y-1"
              >
                <div className="flex items-center justify-between">
                  <div className="text-3xl">{item.icon}</div>
                  <div className="text-xs font-semibold tracking-[0.25em] text-orange-300">{item.level}</div>
                </div>

                <h3 className="mt-3 text-xl font-semibold text-white">{item.name}</h3>
                <div className="mt-5 text-5xl font-extrabold text-amber-300">{item.score.toFixed(1)}</div>

                <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-fuchsia-500 via-purple-500 to-cyan-400"
                    style={{ width: `${clamp(item.score, 0, 100)}%` }}
                  />
                </div>

                <p className="mt-4 text-sm leading-7 text-zinc-300">{item.description}</p>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {result?.report ? (
        <section className="mt-10 rounded-[2rem] border border-white/10 bg-black/35 p-6 backdrop-blur-xl">
          <h2 className="text-2xl font-semibold text-white">📜 Báo cáo tổng hợp</h2>
          <pre className="mt-4 whitespace-pre-wrap rounded-3xl border border-purple-500/15 bg-white/5 p-5 leading-7 text-zinc-200">
            {result.report}
          </pre>
        </section>
      ) : null}

      <style jsx global>{`
        @keyframes floatCard {
          0%,100% { transform: translateY(0) rotate(var(--rot)); opacity: 0.9; }
          50% { transform: translateY(-16px) rotate(calc(var(--rot) + 3deg)); opacity: 1; }
        }

        @keyframes auraPulse {
          0%,100% { box-shadow: 0 0 30px rgba(168,85,247,.28), 0 0 90px rgba(34,211,238,.12); }
          50% { box-shadow: 0 0 50px rgba(168,85,247,.46), 0 0 130px rgba(34,211,238,.18); }
        }

        @keyframes glowText {
          0%,100% { text-shadow: 0 0 10px rgba(196,181,253,.25), 0 0 30px rgba(168,85,247,.12); }
          50% { text-shadow: 0 0 18px rgba(196,181,253,.6), 0 0 36px rgba(168,85,247,.32); }
        }
      `}</style>
    </main>
  );
}

function InfoChip({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur-md">
      <div className="text-xs uppercase tracking-[0.25em] text-zinc-400">{title}</div>
      <div className="mt-2 text-sm font-semibold text-white">{value}</div>
    </div>
  );
}

function ProgressLine({ label, active }: { label: string; active: boolean }) {
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span>{label}</span>
        <span className={active ? "text-cyan-300" : "text-zinc-500"}>
          {active ? "Hoạt động" : "Chờ"}
        </span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            active ? "w-full bg-gradient-to-r from-fuchsia-500 to-cyan-400" : "w-1/4 bg-white/20"
          }`}
        />
      </div>
    </div>
  );
}

function OrbCard() {
  return (
    <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-[radial-gradient(circle_at_center,rgba(168,85,247,0.22),rgba(0,0,0,0.7)_55%)] p-6 backdrop-blur-xl">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(34,211,238,0.10),transparent_45%)]" />
      <div className="relative flex items-center justify-between gap-4">
        <div>
          <h3 className="text-2xl font-semibold text-white">Quả cầu pha lê</h3>
          <p className="mt-2 max-w-sm text-sm leading-6 text-zinc-300">
            Phát sáng theo nhịp quét tay. Khi bàn tay đúng vị trí, hệ thống sẽ tự động chụp và phân tích.
          </p>
        </div>

        <div className="relative h-28 w-28 animate-[pulse_3.8s_ease-in-out_infinite] rounded-full border border-cyan-300/25 bg-[radial-gradient(circle_at_35%_30%,rgba(255,255,255,0.95),rgba(196,181,253,0.55)_18%,rgba(34,211,238,0.22)_45%,rgba(0,0,0,0.12)_72%)] shadow-[0_0_50px_rgba(34,211,238,0.18)]">
          <div className="absolute inset-2 rounded-full border border-white/10" />
          <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_30%_30%,rgba(255,255,255,0.65),transparent_30%),radial-gradient(circle_at_50%_65%,rgba(168,85,247,0.20),transparent_45%)]" />
        </div>
      </div>
    </div>
  );
}