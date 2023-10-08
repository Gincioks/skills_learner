async function scrollPage(x, y) {
    await page.evaluate(
        (x, y) => {
            window.scrollBy(x, y);
        },
        x,
        y
    );
}
