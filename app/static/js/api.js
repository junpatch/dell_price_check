document.addEventListener("DOMContentLoaded", async () => {
  const productNameSelect = document.getElementById("productNameSelect");
  const productModelSelect = document.getElementById("productModelSelect");

  // 共通の option 要素作成関数
  function createOptionElement(value, textContent) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = textContent;
    return option;
  }

  productNameSelect.addEventListener("change", async (event) => {
    const selectedName = event.target.value;

    // 初期状態のオプションを設定
    productModelSelect.innerHTML = "";
    productModelSelect.appendChild(createOptionElement("", "--model名を選択--"));
    productModelSelect.disabled = true;

    if (!selectedName) return;

    try {
      const response = await fetch(`/api/get_model/${encodeURIComponent(selectedName)}`);
      const modelList = await response.json();

      if (modelList.length > 0) {
        modelList.forEach((item) => {
          productModelSelect.appendChild(createOptionElement(item.model, item.model));
        });
        productModelSelect.disabled = false;
      }
    } catch (error) {
      console.error("モデルリストの取得に失敗しました:", error);
    }
  });

  // チャートの描画
  const productLink = document.getElementById("productLink")
  const productSelectionForm = document.getElementById("productSelectionForm");
  const priceTrendCanvas = document.getElementById("priceTrendChart");

  if (!priceTrendCanvas) {
    console.error("priceTrendChart 要素が見つかりません。");
    return;
  }

  const ctx = priceTrendCanvas.getContext("2d");
  let chartInstance = null;

    productSelectionForm.addEventListener("submit", async (event) => {
    event.preventDefault();

        // 前回のチャートを破棄
        if (chartInstance) chartInstance.destroy();

        const name = productNameSelect.value;
        const model = productModelSelect.value;

        try {
            const response = await fetch("/api/get_price_trend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, model }),
            });

            const data = await response.json();

            if (data.prices?.length > 0) {
            const labels = data.prices.map((entry) => entry.date); // 日付データ
            const prices = data.prices.map((entry) => entry.price); // 価格データ

            chartInstance = new Chart(ctx, {
                type: "line",
                data: {
                labels,
                datasets: [
                    {
                    label: "価格推移",
                    data: prices,
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    borderWidth: 2,
                    },
                ],
                },
                options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: `${name} - ${model}`},
                    legend: { display: true, position: "top" },
                    tooltip: { enabled: true },
                },
                scales: {
                    x: {
                    type: "time",
                    time: { unit: "day", tooltipFormat: "YYYY-MM-DD" },
                    title: { display: true, text: "日付" },
                    },
                },
                },
            });

            productLink.innerHTML = `<p><a href=${data.url}>＞リンク</a><p>`

            } else {
            trendOutputDiv.innerHTML = "<p>価格推移のデータがありません。</p>";
            }
        } catch (error) {
            console.error("価格データの取得に失敗しました:", error);
            trendOutputDiv.innerHTML = "<p class='error'>価格推移を取得できませんでした。</p>";
        }
    });
    //グラフ描画ここまで

    // 価格データ取得（いずれ消す）
    const btnGetLatest = document.getElementById("getLatest");
    const priceOutput = document.getElementById("priceOutput");

    btnGetLatest.addEventListener("click", async (event) =>{
        event.preventDefault(); // デフォルト動作を防ぐ（URL遷移しない）

        priceOutput.innerHTML = `<p>読み込み中...</p>`;

        try {
            // APIから価格データを取得
            const response = await fetch("/api/check_price");
            if (!response.ok) {
                throw new Error("データの取得に失敗しました");
              }
            const data = await response.json();

            priceOutput.innerHTML = `<p>response: ${response.ok}</p>`;
        } catch (error) {
            priceOutput.innerHTML = `<p class="error">エラー: ${error.message}</p>`;
        }
    });

    // 通知テスト（いずれ消す）
    const btnNotificationTest = document.getElementById("notificationTest");
    const notificationOutput = document.getElementById("notificationOutput");

    btnNotificationTest.addEventListener("click", async (event) =>{
        event.preventDefault(); // デフォルト動作を防ぐ（URL遷移しない）

        notificationOutput.innerHTML = `<p>読み込み中...</p>`;

        try {
            // APIから価格データを取得
            const response = await fetch("/api/notification_test");
            if (!response.ok) {
                throw new Error("データの取得に失敗しました");
              }
            const data = await response.json();

            notificationOutput.innerHTML = `<p>response: ${response.ok}</p>`;
        } catch (error) {
            notificationOutput.innerHTML = `<p class="error">エラー: ${error.message}</p>`;
        }
    });
});