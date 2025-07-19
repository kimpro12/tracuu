from flask import Flask, request, jsonify, render_template
import os
from typing import Dict, List

app = Flask(__name__)

# --- Hàm đọc file (giữ nguyên logic cũ) ---
def load_scores() -> Dict[str, List[str]]:
    files = ['toan', 'van', 'ly', 'hoa', 'sinh', 'su', 'dia', 'anh', 'mamon']
    data = {}
    for f in files:
        with open(f"{f}.txt", encoding='utf-8') as fp:
            data[f] = [line.strip() for line in fp]
    return data

def calculate_blocks(data: Dict[str, List[str]]) -> Dict[str, List[float]]:
    toan  = data['toan']
    van   = data['van']
    ly    = data['ly']
    hoa   = data['hoa']
    sinh  = data['sinh']
    su    = data['su']
    dia   = data['dia']
    anh   = data['anh']
    mamon = data['mamon']

    A00, A01, B00, B08, C00, D01, D07 = [], [], [], [], [], [], []

    for i in range(len(toan)):
        if toan[i] and ly[i] and hoa[i]:
            A00.append(float(toan[i]) + float(ly[i]) + float(hoa[i]))

        if toan[i] and ly[i] and anh[i] and mamon[i] == "N1":
            A01.append(float(toan[i]) + float(ly[i]) + float(anh[i]))

        if toan[i] and hoa[i] and sinh[i]:
            B00.append(float(toan[i]) + float(hoa[i]) + float(sinh[i]))

        if toan[i] and sinh[i] and anh[i] and mamon[i] == "N1":
            B08.append(float(toan[i]) + float(sinh[i]) + float(anh[i]))

        if van[i] and su[i] and dia[i]:
            C00.append(float(van[i]) + float(su[i]) + float(dia[i]))

        if toan[i] and van[i] and anh[i] and mamon[i] == "N1":
            D01.append(float(toan[i]) + float(van[i]) + float(anh[i]))

        if toan[i] and hoa[i] and anh[i] and mamon[i] == "N1":
            D07.append(float(toan[i]) + float(hoa[i]) + float(anh[i]))

    # Giảm dần
    for arr in [A00, A01, B00, B08, C00, D01, D07]:
        arr.sort(reverse=True)

    return {
        'A00': A00,
        'A01': A01,
        'B00': B00,
        'B08': B08,
        'C00': C00,
        'D01': D01,
        'D07': D07
    }

# --- Flask routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rank', methods=['POST'])
def rank():
    data = request.get_json()
    khoi_chon = data['block'].upper()
    diem_cua_ban = float(data['score'])

    pool = calculate_blocks(load_scores())

    if khoi_chon not in pool:
        return jsonify({'error': 'Khối không hợp lệ!'}), 400

    lst = pool[khoi_chon]
    n = len(lst)
    if n == 0:
        return jsonify({'error': 'Khối này chưa có dữ liệu.'}), 400

    so_ngon_hon = sum(1 for d in lst if d >= diem_cua_ban)
    phan_tram = so_ngon_hon / n

    # Quy ra các khối khác
    equivalents = {}
    for ten, arr in pool.items():
        if not arr:
            equivalents[ten] = None
        else:
            idx = max(0, min(int(round(phan_tram * len(arr))) - 1, len(arr) - 1))
            equivalents[ten] = round(arr[idx], 2)

    return jsonify({
        'block': khoi_chon,
        'score': diem_cua_ban,
        'count_above': so_ngon_hon,
        'total': n,
        'percent': round(phan_tram * 100, 2),
        'equivalents': equivalents
    })

import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
