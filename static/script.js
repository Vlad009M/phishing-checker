// ===== script.js =====
document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("theme-toggle");
    const body = document.body;

    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-theme");
        themeToggle.checked = true;
    }

    themeToggle?.addEventListener("change", () => {
        body.classList.toggle("dark-theme", themeToggle.checked);
        localStorage.setItem("theme", themeToggle.checked ? "dark" : "light");
    });

    const checkMode = document.getElementById("check-mode");
    const textBlock = document.getElementById("text-check");
    const fileBlock = document.getElementById("file-check");
    const urlBlock = document.getElementById("url-check");
    const mainTitle = document.getElementById("main-title");
    const subtitle = document.getElementById("subtitle");

    function showOnly(blockToShow) {
        [textBlock, fileBlock, urlBlock].forEach(block => block.style.display = "none");
        blockToShow.style.display = "block";
    }

    function updateTitleAndSubtitle(mode) {
        switch (mode) {
            case "text":
                mainTitle.textContent = "Чи безпечний цей текст?";
                subtitle.textContent = "Встав текст, який ви хочете перевірити на фішинг";
                break;
            case "file":
                mainTitle.textContent = "Цей файл безпечний?";
                subtitle.textContent = "Проскануйте файл";
                break;
            case "url":
                mainTitle.textContent = "Чи безпечне це посилання?";
                subtitle.textContent = "Відскануйте URL-адресу, яку ви бажаєте відкрити";
                break;
        }
    }

    checkMode.addEventListener("change", function () {
        const mode = this.value;
        updateTitleAndSubtitle(mode);
        if (mode === "text") showOnly(textBlock);
        else if (mode === "file") showOnly(fileBlock);
        else if (mode === "url") showOnly(urlBlock);
    });

    updateTitleAndSubtitle(checkMode.value);
    showOnly(textBlock);

    document.getElementById("check-btn").addEventListener("click", () => {
        const mode = checkMode.value;
        const result = document.getElementById("result");
        const gptResult = document.getElementById("gpt-result");
        const finalVerdict = document.getElementById("final-verdict");

        result.textContent = "";
        gptResult.textContent = "";
        if (finalVerdict) finalVerdict.textContent = "";

        if (mode === "text") {
            const text = document.getElementById("email-input").value;
            if (!text.trim()) return alert("Введіть текст для перевірки");

            fetch("/predict-text", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text })
            })
            .then(res => {
                if (res.status === 403) throw new Error("Ліміт вичерпано");
                return res.json();
            })
            .then(mlData => {
                result.textContent = `🧪 ML-модель: ймовірність фішингу ${mlData.probability}%`;
                return fetch("/ai-analysis", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: text })
                });
            })
            .then(res => {
                if (res.status === 403) throw new Error("Ліміт вичерпано");
                return res.json();
            })
            .then(aiData => {
                gptResult.textContent = `🤖 AI-аналіз: ${aiData.ai_opinion}`;
                const mlScore = parseFloat(result.textContent.match(/(\d+\.\d+)/)?.[1] || 0);
                const isPhishing = mlScore > 60 || aiData.ai_opinion.includes("фішинг");
                finalVerdict.textContent = isPhishing ? "⚠️ Попередження: повідомлення може бути фішинговим!" : "✅ Повідомлення не виглядає фішинговим.";
            })
            .catch(err => {
                if (err.message.includes("Ліміт")) {
                    alert("Ваш ліміт вичерпано. Придбайте Premium для необмеженого доступу.");
                } else {
                    result.textContent = "❌ Сталася помилка при перевірці тексту";
                }
            });
        }
        else if (mode === "file") {
            const fileInput = document.getElementById("file-input");
            const fileNameDisplay = document.getElementById("selected-file-name");
            if (!fileInput.files.length) return alert("Оберіть файл для перевірки");

            const formData = new FormData();
            formData.append("file", fileInput.files[0]);

            fetch("/check-file", {
                method: "POST",
                body: formData
            })
            .then(res => {
                if (res.status === 403) throw new Error("Ліміт вичерпано");
                return res.json();
            })
            .then(data => {
                result.textContent = `Ймовірність фішингу у файлі: ${data.probability}%`;
            })
            .catch(err => {
                if (err.message.includes("Ліміт")) {
                    alert("Ваш ліміт вичерпано. Придбайте Premium для необмеженого доступу.");
                } else {
                    result.textContent = "❌ Помилка перевірки файлу";
                }
            });
        }
        else if (mode === "url") {
            const url = document.getElementById("url-input").value;
            const isValidUrl = /^https?:\/\/.+/i.test(url);
            if (!isValidUrl) return alert("Введіть коректне URL-посилання");

            const formData = new FormData();
            formData.append("url", url);

            fetch("/check-url", {
                method: "POST",
                body: formData
            })
            .then(res => {
                if (res.status === 403) throw new Error("Ліміт вичерпано");
                return res.json();
            })
            .then(data => {
                result.textContent = `Ймовірність фішингу у посиланні: ${data.probability}%`;
            })
            .catch(err => {
                if (err.message.includes("Ліміт")) {
                    alert("Ваш ліміт вичерпано. Придбайте Premium для необмеженого доступу.");
                } else {
                    result.textContent = "❌ Помилка перевірки URL";
                }
            });
        }
    });

    // Кнопка Premium (тимчасова)
    const upgradeBtn = document.getElementById("upgrade-btn");
    if (upgradeBtn) {
        upgradeBtn.addEventListener("click", () => {
            alert("👉 Функція оновлення до Premium у розробці. Зверніться до адміністратора.");
        });
    }
});
