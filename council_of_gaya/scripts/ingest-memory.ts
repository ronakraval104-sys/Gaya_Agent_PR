import { ingestMemoryDir } from "../lib/knowledge/ingest";
import { ingestOmniGayaMemory } from "../lib/knowledge/omni-parser";
import { ingestObsidianVault } from "../lib/knowledge/obsidian-ingest";
import { replaceAll } from "../lib/knowledge/repo";

async function main() {
  const overrideDir = process.argv[2];

  console.log("[ingest] scanning memory dir...");
  const { records: fileRecords, report } = await ingestMemoryDir({ memoryDir: overrideDir });
  console.log(`[ingest] memory dir: parsed ${report.parsedRecords}/${report.scannedFiles} files in ${report.durationMs}ms`);

  console.log("[ingest] parsing OMNI_GAYA_MEMORY.md sections...");
  const omniRecords = await ingestOmniGayaMemory();
  console.log(`[ingest] omni-gaya: ${omniRecords.length} records extracted`);
  const omniBreakdown: Record<string, number> = {};
  for (const r of omniRecords) omniBreakdown[r.type] = (omniBreakdown[r.type] ?? 0) + 1;
  console.log("[ingest] omni-gaya breakdown:", omniBreakdown);

  console.log("[ingest] walking Obsidian vault...");
  const { records: obsidianRecords, report: obsidianReport } = await ingestObsidianVault();
  console.log(`[ingest] obsidian: ${obsidianRecords.length}/${obsidianReport.scannedFiles} files in ${obsidianReport.durationMs}ms`);
  console.log("[ingest] obsidian breakdown:", obsidianReport.countsByType);
  if (obsidianReport.skipped.length) {
    console.log(`[ingest] obsidian skipped ${obsidianReport.skipped.length}:`);
    for (const s of obsidianReport.skipped.slice(0, 5)) console.log(`  ${s.path} — ${s.reason}`);
  }

  const allRecords = [...fileRecords, ...omniRecords, ...obsidianRecords];

  console.log("[ingest] combined countsByType:", combinedCounts(allRecords, "type"));
  console.log("[ingest] combined countsByPersona:", combinedCounts(allRecords, "persona"));
  console.log("[ingest] combined countsByPriority:", combinedCounts(allRecords, "priority"));

  console.log(`[ingest] boulder rules: ${report.boulderRules.length + allRecords.filter((r) => r.priority === "boulder" && r.source.origin === "omni-gaya").length}`);
  for (const b of report.boulderRules) console.log(`  🚨 ${b} (memory-dir)`);
  for (const r of allRecords.filter((r) => r.priority === "boulder" && r.source.origin === "omni-gaya")) {
    console.log(`  🚨 ${r.slug} (omni-gaya)`);
  }

  if (report.brokenLinks.length) {
    console.log(`[ingest] ${report.brokenLinks.length} broken wiki-links remain (top 10):`);
    for (const bl of report.brokenLinks.slice(0, 10)) {
      console.log(`  ${bl.fromSlug} -> [[${bl.toSlug}]]`);
    }
  } else {
    console.log("[ingest] link graph clean ✓");
  }

  if (report.skipped.length) {
    console.log(`[ingest] skipped ${report.skipped.length}:`);
    for (const s of report.skipped) console.log(`  ${s.path} — ${s.reason}`);
  }

  const combinedReport = {
    ...report,
    omniRecordsAdded: omniRecords.length,
    omniBreakdown,
    obsidianRecordsAdded: obsidianRecords.length,
    obsidianBreakdown: obsidianReport.countsByType,
    totalRecords: allRecords.length
  };
  await replaceAll(allRecords, combinedReport);
  console.log(`[ingest] wrote ${allRecords.length} total records to knowledge.json`);
}

function combinedCounts(records: any[], field: string): Record<string, number> {
  const out: Record<string, number> = {};
  for (const r of records) out[r[field]] = (out[r[field]] ?? 0) + 1;
  return out;
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
