import { OperatorConsoleShell } from "@/components/OperatorConsoleShell";
import { CouncilOrbitalNexus } from "@/components/CouncilOrbitalNexus";
import { GayaCompanionDeck } from "@/components/GayaCompanionDeck";
import { ProjectsBoard } from "@/components/ProjectsBoard";
import { PersonaMorph } from "@/components/PersonaMorph";
import { RecordDetail } from "@/components/RecordDetail";
import { SeatBrief } from "@/components/SeatBrief";
import { SessionChronicle } from "@/components/SessionChronicle";
import { Sidebar } from "@/components/Sidebar";
import { SlashConsole } from "@/components/SlashConsole";
import { StatusBar } from "@/components/StatusBar";
import { Topbar } from "@/components/Topbar";
import { SettingsModal } from "@/components/SettingsModal";

export default function Home() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 min-w-0 flex flex-col">
        <Topbar />

        {/* Infinite Scroll Cockpit Viewport */}
        <div className="flex-1 pb-24 space-y-4">
          {/* Act 1: Grand Council Orbital Nexus */}
          <section className="px-6 pt-4 max-w-[1600px] mx-auto w-full">
            <CouncilOrbitalNexus />
          </section>

          {/* Act 2: Mini Gaya Real-Time Audio & Scale Companion Deck */}
          <section>
            <GayaCompanionDeck />
          </section>

          {/* Act 3: Live Operator Stream & System Console */}
          <section>
            <OperatorConsoleShell />
          </section>

          {/* Act 4: Our Projects Command Board (Replacing Threads Board) */}
          <section>
            <ProjectsBoard />
          </section>
        </div>
      </main>

      {/* Floating System Modals */}
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

