async function extractText(selector) {
    return await page.$eval(selector, (el) => el.innerText);
}
