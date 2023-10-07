async function searchGoogle(query) {
    await navigateToGoogle();
    await typeText("#APjFqb", query);
    await page.keyboard.press("Enter");
    await page.waitForSelector("div[id=result-stats]");
    const searchResults = await page.evaluate(() => {
        const anchors = Array.from(document.querySelectorAll("a"));
        return anchors.map((anchor) => {
            const title = anchor.textContent;
            const url = anchor.href;
            return `${title} - ${url}`;
        });
    });

    return searchResults;
}
