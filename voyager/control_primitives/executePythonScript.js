async function executePythonScript(script) {
    return new Promise((resolve, reject) => {
        exec(`python -c "${script}"`, (error, stdout, stderr) => {
            if (error) {
                reject(error);
            } else if (stderr) {
                reject(new Error(stderr));
            } else {
                resolve(stdout);
            }
        });
    });
}
