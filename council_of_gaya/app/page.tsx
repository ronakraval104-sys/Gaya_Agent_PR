import { OperatorConsoleShell } from "@/components/OperatorConsoleShell";
import { PersonaMorph } from "@/components/PersonaMorph";
import { RadialGraph } from "@/components/RadialGraph";
import { RecordDetail } from "@/components/RecordDetail";
import { SeatBrief } from "@/components/SeatBrief";
import { SessionChronicle } from "@/components/SessionChronicle";
import { Sidebar } from "@/components/Sidebar";
import { SlashConsole } from "@/components/SlashConsole";
import { StatusBar } from "@/components/StatusBar";
import { ThreadsBoard } from "@/components/ThreadsBoard";
import { Topbar } from "@/components/Topbar";
import { SettingsModal } from "@/components/SettingsModal";

export default function Home() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 min-w-0 flex flex-col">
        <Topbar />
        <div className="flex-1 pb-16">
          <OperatorConsoleShell />

          {/* Council + knowledge graph — the reactor now houses the live network */}
          <div className="px-6 max-w-[1600px] mx-auto">
            <div className="flex items-center justify-center py-4">
              <RadialGraph size={700} />
            </div>
          </div>

          {/* Threads Board — daily-driver "what's on my plate" surface */}
          <ThreadsBoard />
        </div>
      </main>

      {/* floating layers — unchanged, still on top */}
      <SeatBrief />
      <SessionChronicle />
      <SlashConsole />
      <RecordDetail />
      <PersonaMorph />
      <SettingsModal />
      <StatusBar />
    </div>
  );
}
