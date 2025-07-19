async function calculate() {
    const block = document.getElementById('block').value.toUpperCase();
    const score = parseFloat(document.getElementById('score').value);
    const result = document.getElementById('result');

    if (isNaN(score)) {
        result.textContent = "Vui lòng nhập điểm hợp lệ!";
        return;
    }

    try {
        const res = await fetch('/api/rank', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({block, score})
        });
        const data = await res.json();
        if (!res.ok) {
            result.textContent = data.error || "Lỗi không xác định";
            return;
        }

        let text = `Điểm ${data.block} ${data.score} nằm trên ${data.count_above}/${data.total} thí sinh.\n`;
        text += `Tức top ${data.percent}% của khối ${data.block}.\n\n`;
        text += "Điểm tương ứng ở các khối khác:\n";
        for (const [k, v] of Object.entries(data.equivalents)) {
            text += `${k}: ${v === null ? 'Không có dữ liệu' : v}\n`;
        }
        result.textContent = text;
    } catch (err) {
        result.textContent = "Lỗi kết nối: " + err.message;
    }
}