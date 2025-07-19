# app.py
import os
import bisect
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Mapping khối -> chỉ số cột điểm quy đổi
COL_MAP = {
    'A00': 4,
    'A01': 5,
    'B00': 6,
    'B08': 7,
    'C00': 8,
    'D01': 9,
    'D07': 10
}

# -----------------------------
# Đọc file khối
# -----------------------------
def load_block(block_name: str):
    path = os.path.join('data', f'{block_name}.txt')
    if not os.path.isfile(path):
        raise FileNotFoundError(f'Không tìm thấy {path}')
    data = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            row = parts[0].split('\t') if '\t' in parts[0] else parts
            # loại bỏ dấu % rồi ép float
            row = [float(x.rstrip('%')) for x in row]
            data.append(row)
    return data

# Cache 7 khối khi khởi động server
pool = {k: load_block(k) for k in COL_MAP}

# -----------------------------
# Route giao diện
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------------
# API
# -----------------------------
@app.route('/api/rank', methods=['POST'])
def rank():
    payload = request.get_json(silent=True) or {}
    block = str(payload.get('block', '')).upper()
    score = payload.get('score')

    # validate
    if block not in pool:
        return jsonify({'error': 'Khối không hợp lệ'}), 400
    try:
        score = float(score)
    except (TypeError, ValueError):
        return jsonify({'error': 'Điểm không hợp lệ'}), 400

    data = pool[block]
    scores = [row[0] for row in data]

    # tìm dòng >= điểm nhập
    pos = bisect.bisect_left(scores, score)
    if pos == len(scores):
        pos = len(scores) - 1
    row = data[pos]

    count_above = int(row[1])
    total = int(row[2])
    percent = round(count_above / total * 100, 2)

    # điểm quy đổi
    equivalents = {}
    for k in COL_MAP:
        try:
            val = row[COL_MAP[k]]
            equivalents[k] = round(val, 2)
        except IndexError:
            equivalents[k] = None

    return jsonify({
        'block': block,
        'score': score,
        'count_above': count_above,
        'total': total,
        'percent': percent,
        'equivalents': equivalents
    })

# -----------------------------
# Chạy server
# -----------------------------
import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
