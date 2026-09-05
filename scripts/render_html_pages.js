async (page) => {
  const encodedJobs = await page.evaluate(() => location.hash.slice(1));
  const jobs = JSON.parse(decodeURIComponent(encodedJobs));
  const rendered = [];

  for (const job of jobs) {
    const failures = [];
    const onConsole = message => {
      if (message.type() === "error") failures.push(`console: ${message.text()}`);
    };
    const onRequestFailed = request => {
      const detail = request.failure();
      failures.push(`request: ${request.url()} ${detail ? detail.errorText : ""}`);
    };
    page.on("console", onConsole);
    page.on("requestfailed", onRequestFailed);

    try {
      await page.goto(job.url, { waitUntil: "networkidle" });
      await page.evaluate(async () => {
        if (document.fonts && document.fonts.ready) await document.fonts.ready;
        await Promise.all([...document.images].map(image => {
          if (image.complete && image.naturalWidth > 0) return Promise.resolve();
          return image.decode().catch(() => {
            throw new Error(`image decode failed: ${image.currentSrc || image.src}`);
          });
        }));
      });

      const readyMarker = page.locator("[data-render-ready]");
      if (await readyMarker.count()) {
        await page.locator('[data-render-ready="true"]').first().waitFor({
          state: "attached",
          timeout: 5000,
        });
      }

      const metrics = await page.evaluate(() => ({
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,
        scrollWidth: Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0),
        scrollHeight: Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0),
      }));
      if (metrics.scrollWidth > metrics.viewportWidth || metrics.scrollHeight > metrics.viewportHeight) {
        throw new Error(`${job.name} canvas overflow: ${JSON.stringify(metrics)}`);
      }
      if (failures.length) throw new Error(`${job.name}\n${failures.join("\n")}`);

      await page.screenshot({ path: job.output, animations: "disabled" });
      rendered.push(job.name);
    } finally {
      page.off("console", onConsole);
      page.off("requestfailed", onRequestFailed);
    }
  }

  return rendered;
}
