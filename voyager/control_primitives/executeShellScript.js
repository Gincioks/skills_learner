async function executeShellScript(script) {
    try {
        const { stdout, stderr } = await exec(script, {
            cwd: "../env/browser/workspace",
        });
        console.log("stdout:", stdout);
        console.error("stderr:", stderr);
    } catch (error) {
        console.error(error);
    }
}
