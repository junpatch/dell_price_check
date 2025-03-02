document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("dataForm");
    const trendListDiv = document.getElementById("trendListDiv");
    const chartCanvas = document.getElementById("priceTrendChart");

    if (!chartCanvas) {
        console.error("priceTrendChart 要素が見つかりません。");
        return;
    }
    const ctx = chartCanvas.getContext("2d");

    let chartInstance = null;

    // フォームが送信されたときの処理
    form.addEventListener("submit", async function (event) {
        // デフォルトのフォーム送信動作をキャンセル
        event.preventDefault();

        //前回のチャートを破棄
        if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null; // 必ず初期化
        }

        // フォームデータを取得
        const name = document.getElementById("name").value;
        const model = document.getElementById("model").value;

        try {
            const response = await fetch("/api/get_price_trend", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({name, model}) // JSON形式で送信
            });

            const data = await response.json();

            if (data.prices && data.prices.length > 0) {
                // 日付と価格のデータを分離
                const labels = data.prices.map(entry => entry.date); // 日付データ (x軸ラベル用)
                const prices = data.prices.map(entry => entry.price); // 価格データ (y軸データ用)

                chartInstance = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: '価格推移',
                            data: prices,
                            borderColor: 'rgba(75, 192, 192, 1)', // 線の色
                            backgroundColor: 'rgba(75, 192, 192, 0.2)', // 塗りつぶしの色
                            borderWidth: 2 // 線の太さ
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            },
                            tooltip: {
                                enabled: true
                            }
                        },
                        scales: {
                            x: {
                                type: 'time',
                                time: {
                                    unit: 'day',
                                    tooltipFormat: 'YYYY-MM-DD'
                                },
                                title: {
                                    display: true,
                                    text: '日付'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: '価格(¥)'
                                },
                                beginAtZero: false
                            }
                        }
                    }
                });
            } else {
                trendListDiv.innerHTML = "<p>価格推移のデータがありません。</p>";
            }
        } catch (error) {
            // データの取得に失敗したとき
            console.error(error);
            trendListDiv.innerHTML = "<p class='error'>価格推移を取得できませんでした。: ${error.message}</p>";
        }
    });

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

            priceOutput.innerHTML = `<p>response: ${response.ok}</p><p>data: ${data.stderr}</p>`;
        } catch (error) {
            priceOutput.innerHTML = `<p class="error">エラー: ${error.message}</p>`;
        }
    });
});