(async function () {
    // ─── CONFIG ──────────────────────────────────────────────────────────────────
    const MAX_URLS = 10;             // total URLs to download in this session
    const BATCH_SIZE = 1;            // URLs per batch
    const COOLDOWN_BETWEEN_BATCHES = 30_000; // ms (30 s) between batches
    const MIN_DELAY_BETWEEN_URLS = 4_000;  // ms
    const MAX_DELAY_BETWEEN_URLS = 8_000;  // ms
    const POLL_INTERVAL = 2_000;      // ms between checks for page load
    const PAGE_LOAD_TIMEOUT = 45_000; // max ms to wait for a single page
    // ────────────────────────────────────────────────────────────────────────────

    const urls = [
        "https://www.linkedin.com/company/axtria/insights/",
        "https://www.linkedin.com/company/infosys/insights/",
        "https://www.linkedin.com/company/accenture/insights/",
        "https://www.linkedin.com/company/cognizant/insights/",
        "https://www.linkedin.com/company/nagarro/insights/",
        "https://www.linkedin.com/company/american-express/insights/",
        "https://www.linkedin.com/company/gspann-technologies-inc/insights/",
        "https://www.linkedin.com/company/ibm/insights/",
        "https://www.linkedin.com/company/zs-associates/insights/",
        "https://www.linkedin.com/company/tata-consultancy-services/insights/",
        "https://www.linkedin.com/company/hcltech/insights/",
        "https://www.linkedin.com/company/kpmgindia/insights/",
        "https://www.linkedin.com/company/pwc/insights/",
        "https://www.linkedin.com/company/lumentechnologies/insights/",
        "https://www.linkedin.com/company/techpinnacle-bit-solutions/insights/",
        "https://www.linkedin.com/company/genpact/insights/",
        "https://www.linkedin.com/company/google/insights/",
        "https://www.linkedin.com/company/amazon/insights/",
        "https://www.linkedin.com/company/procore-technologies/insights/",
        "https://www.linkedin.com/company/siemens-energy/insights/",
        "https://www.linkedin.com/company/dentsuglobalservices/insights/",
        "https://www.linkedin.com/company/statusneo/insights/",
        "https://www.linkedin.com/company/tredence/insights/",
        "https://www.linkedin.com/company/capgemini/insights/",
        "https://www.linkedin.com/company/hmh-india/insights/",
        "https://www.linkedin.com/company/chegg-inc-/insights/",
        "https://www.linkedin.com/school/khan-academy/insights/",
        "https://www.linkedin.com/company/bounteous-accolite/insights/",
        "https://www.linkedin.com/company/boston-consulting-group/insights/",
        "https://www.linkedin.com/company/spglobal/insights/",
        "https://www.linkedin.com/company/mindlance/insights/",
        "https://www.linkedin.com/company/exl-service/insights/",
        "https://www.linkedin.com/company/optum/insights/",
        "https://www.linkedin.com/company/altimetrik/insights/",
        "https://www.linkedin.com/company/deeplearningai/insights/",
        "https://www.linkedin.com/company/magic-edtech/insights/",
        "https://www.linkedin.com/company/the-webplant-pvt-ltd-/insights/",
        "https://www.linkedin.com/company/techahead/insights/",
        "https://www.linkedin.com/company/mobileum/insights/",
        "https://www.linkedin.com/company/virtusa/insights/",
        "https://www.linkedin.com/company/sutherland-global/insights/",
        "https://www.linkedin.com/company/bain-and-company/insights/",
        "https://www.linkedin.com/company/ernstandyoung/insights/",
        "https://www.linkedin.com/company/publicissapient/insights/",
        "https://www.linkedin.com/company/persistent-systems/insights/",
        "https://www.linkedin.com/company/flocareer/insights/",
        "https://www.linkedin.com/company/quantlytix-pvt-ltd/insights/",
        "https://www.linkedin.com/company/eduedge-global/",
        "https://www.linkedin.com/company/eduedge-global/insights/",
        "https://www.linkedin.com/company/zoneitsolutions/insights/",
        "https://www.linkedin.com/company/fractal-analytics/insights/",
        "https://www.linkedin.com/company/birlasoft/insights/",
        "https://www.linkedin.com/company/hexaware-technologies/insights/",
        "https://www.linkedin.com/company/citi/insights/",
        "https://www.linkedin.com/company/aisinfo/insights/",
        "https://www.linkedin.com/company/microsoft/insights/",
        "https://www.linkedin.com/company/codingal/insights/",
        "https://www.linkedin.com/company/fico/insights/",
        "https://www.linkedin.com/company/chetu-inc-/insights/",
        "https://www.linkedin.com/company/sabre-corporation/insights/",
        "https://www.linkedin.com/company/dxctechnology/insights/",
        "https://www.linkedin.com/company/luxoft/insights/",
        "https://www.linkedin.com/company/webveda/insights/",
        "https://www.linkedin.com/company/miraclesoft/insights/"
    ];

    // ─── Helpers ────────────────────────────────────────────────────────────────
    const sleep = ms => new Promise(r => setTimeout(r, ms));

    function randomBetween(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function deriveFilename(url) {
        // e.g. "https://www.linkedin.com/company/axtria/insights/" → "axtria_insights.html"
        const parts = url.split('/').filter(Boolean);
        // parts = ["https:", "www.linkedin.com", "company", "axtria", "insights"]
        const company = parts[3] || 'unknown';
        const page = parts[4] || 'page';
        return `${company}_${page}.html`;
    }

    function downloadBlob(html, filename) {
        const blob = new Blob([html], { type: 'text/html' });
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        a.click();
        // Revoke after a short delay to let the browser start the download
        setTimeout(() => URL.revokeObjectURL(blobUrl), 5000);
    }

    //   async function waitForPageLoad(tab, url, timeout) {
    //     const start = Date.now();
    //     while (Date.now() - start < timeout) {
    //       try {
    //         if (tab.document && tab.document.body && tab.document.body.classList.contains('boot-complete')) {
    //           return true;
    //         }
    //       } catch (_) { /* cross-origin before load */ }
    //       await sleep(POLL_INTERVAL);
    //     }
    //     return false;
    //   }


    async function waitForPageLoad(tab, url, timeout) {
        const start = Date.now();

        // Phase 1: wait for boot-complete
        while (Date.now() - start < timeout) {
            try {
                if (tab.document?.body?.classList.contains('boot-complete')) break;
            } catch (_) { }
            await sleep(POLL_INTERVAL);
        }

        // Phase 2: wait for stats to actually render
        while (Date.now() - start < timeout) {
            try {
                // Look for the employee-count element (LinkedIn's insights page)
                const stats = tab.document.querySelector('[data-tracking-control-name="public_insights_employee-count"]')
                    || tab.document.querySelector('h2')?.textContent?.match(/\d[\d,]*\s*(employees|followers)/i);
                if (stats) return true;
            } catch (_) { }
            await sleep(POLL_INTERVAL);
        }

        return false;
    }

    // ─── Pop-up blocker check ───────────────────────────────────────────────────
    const testTab = window.open('about:blank', '_blank');
    if (!testTab) {
        alert(
            '🚫 Pop-up blocked!\n\n' +
            'Please click "Always allow pop-ups from LinkedIn" in the address bar,\n' +
            'then reload this page and run the script again.'
        );
        console.error('Pop-ups are blocked. Allow them and retry.');
        return;
    }
    testTab.close();
    console.log('✅ Pop-ups are allowed. Starting…');
    await sleep(1000);

    // ─── Cap URLs for this session ─────────────────────────────────────────────
    const urlsToProcess = urls.slice(0, MAX_URLS);
    const totalUrlsAvailable = urls.length;
    console.log(`ℹ️  Limiting to ${MAX_URLS} of ${totalUrlsAvailable} available URLs.`);

    // ─── Batch processor ────────────────────────────────────────────────────────
    let successCount = 0;
    let failCount = 0;
    const total = urlsToProcess.length;

    for (let i = 0; i < urlsToProcess.length; i += BATCH_SIZE) {
        const batch = urlsToProcess.slice(i, i + BATCH_SIZE);
        const batchNum = Math.floor(i / BATCH_SIZE) + 1;
        const totalBatches = Math.ceil(urlsToProcess.length / BATCH_SIZE);
        console.log(`\n📦 Batch ${batchNum}/${totalBatches} (${batch.length} URLs)`);

        for (let j = 0; j < batch.length; j++) {
            const url = batch[j];
            const globalIdx = i + j + 1;
            console.log(`  [${globalIdx}/${total}] Opening: ${url}`);

            const newTab = window.open(url, '_blank');

            // ── Fix 1: Pop-up blocked detection ──────────────────────────────────
            if (!newTab) {
                console.warn(`  ⚠️  Pop-up blocked for: ${url} — skipping`);
                failCount++;
                continue;
            }

            // ── Fix 2 & 3: Wait for page load with timeout ───────────────────────
            const loaded = await waitForPageLoad(newTab, url, PAGE_LOAD_TIMEOUT);

            if (loaded) {
                try {
                    const fileName = deriveFilename(url);
                    downloadBlob(newTab.document.documentElement.outerHTML, fileName);
                    successCount++;
                    console.log(`  ✅ Saved: ${fileName}`);
                } catch (err) {
                    failCount++;
                    console.warn(`  ❌ Error saving ${url}: ${err.message}`);
                }
            } else {
                failCount++;
                console.warn(`  ⏰ Timed out waiting for: ${url}`);
            }

            // Close tab
            try { newTab.close(); } catch (_) { /* already closed */ }

            // ── Fix 2: Randomized delay between URLs ─────────────────────────────
            if (j < batch.length - 1 || i + BATCH_SIZE < urlsToProcess.length) {
                const delay = randomBetween(MIN_DELAY_BETWEEN_URLS, MAX_DELAY_BETWEEN_URLS);
                console.log(`  ⏳ Waiting ${(delay / 1000).toFixed(1)}s before next URL...`);
                await sleep(delay);
            }
        }

        // ── Fix 3: Cooldown between batches ────────────────────────────────────
        if (i + BATCH_SIZE < urlsToProcess.length) {
            console.log(`\n🛑 Batch ${batchNum} complete. Cooling down for ${(COOLDOWN_BETWEEN_BATCHES / 1000).toFixed(0)}s...`);
            console.log(`   Progress: ${successCount} succeeded, ${failCount} failed, ${total - successCount - failCount} remaining`);
            await sleep(COOLDOWN_BETWEEN_BATCHES);
        }
    }

    console.log(`\n🎉 DONE! ${successCount} succeeded, ${failCount} failed out of ${total} total.`);
})();
