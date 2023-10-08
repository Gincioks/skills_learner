async function waitForElement(selector) {
    await page.waitForSelector(selector);
}
