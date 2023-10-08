async function captureScreenshot(filename) {
    await page.screenshot({ path: filename });
}
