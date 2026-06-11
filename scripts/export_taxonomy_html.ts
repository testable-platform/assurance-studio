/**
 * Build the same HTML taxonomy report the Confidence Engine download button saves.
 *
 * Usage (from ai-testable-platform frontend):
 *   npx tsx --tsconfig tsconfig.json D:/Metric_evaluation/scripts/export_taxonomy_html.ts [batch_dir]
 */
import * as fs from "node:fs";
import * as path from "node:path";
import type { RunSummaryResponse, TaxonomyGateResponse } from "@/src/lib/api/types";
import { buildTaxonomyGateHtmlReport } from "@/src/lib/confidence-engine/taxonomy-gate-html-export";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..");
const DEFAULT_BATCH = path.join(ROOT, "taxonomy_reports", "20260611T103648Z");
const REPO_NAME = process.env.REPOSITORY_MATCH || "Mohammed-shihaf/Metric_eveluation";

function readJson<T>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, "utf-8")) as T;
}

function branchDirs(batchDir: string): string[] {
  return fs
    .readdirSync(batchDir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => path.join(batchDir, d.name))
    .filter((dir) => fs.existsSync(path.join(dir, "taxonomy-gate.json")));
}

function main(): void {
  const batchDir = process.argv[2] ? path.resolve(process.argv[2]) : DEFAULT_BATCH;
  if (!fs.existsSync(batchDir)) {
    console.error("Batch directory not found:", batchDir);
    process.exit(1);
  }

  let count = 0;
  for (const branchDir of branchDirs(batchDir)) {
    const branchName = path.basename(branchDir);
    const taxonomy = readJson<TaxonomyGateResponse>(path.join(branchDir, "taxonomy-gate.json"));
    const summaryPath = path.join(branchDir, "run_summary.json");
    const summary = fs.existsSync(summaryPath)
      ? readJson<RunSummaryResponse>(summaryPath)
      : null;

    const html = buildTaxonomyGateHtmlReport(
      taxonomy,
      { trustRunCompleted: true },
      {
        repo_name: REPO_NAME,
        branch_name: summary?.branch_name ?? branchName,
        commit_id: summary?.commit_sha ?? null,
      },
    );

    const outName = `taxonomy-gate-${taxonomy.run_id}.html`;
    const outPath = path.join(branchDir, outName);
    fs.writeFileSync(outPath, html, "utf-8");
    console.log("  %s -> %s" , branchName, outName);
    count += 1;
  }

  console.log("Done: %d HTML report(s) in %s", count, batchDir);
}

main();
