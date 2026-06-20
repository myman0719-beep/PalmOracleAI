import PalmScanner from "../components/PalmScanner";

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-black">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(88,28,135,0.35),transparent_40%),radial-gradient(circle_at_bottom,rgba(14,165,233,0.15),transparent_35%),linear-gradient(to_bottom,#020617,#000)]" />
      <div className="absolute inset-0 opacity-40 bg-[radial-gradient(white_1px,transparent_1px)] [background-size:24px_24px]" />

      <div className="relative z-10">
        <header className="mx-auto max-w-7xl px-4 pt-10 text-center text-white md:px-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-purple-400/20 bg-white/5 px-4 py-2 text-sm text-purple-100 backdrop-blur-md">
            🔮 Palm Oracle AI
          </div>

          <h1 className="mt-5 text-4xl font-bold tracking-tight text-white md:text-6xl">
            Pháp Sư Bói Chỉ Tay AI
          </h1>

          <p className="mx-auto mt-4 max-w-2xl text-sm text-purple-100/80 md:text-base">
            Camera tự mở, AI tự nhận diện bàn tay, tự chụp khi đúng vị trí và trả về phân tích chi tiết theo phong cách huyền bí.
          </p>
        </header>

        <div className="mx-auto max-w-7xl px-4 pb-10 md:px-8">
          <PalmScanner />
        </div>
      </div>
    </main>
  );
}