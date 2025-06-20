import os
import gzip
import shutil
import subprocess
from config import conf

def decompress_gz(gz_path):
    crx_path = gz_path[:-3] if gz_path.endswith('.gz') else gz_path
    if os.path.exists(crx_path):
        print(f"[INFO] Уже распаковано: {crx_path}")
        return crx_path
    print(f"[INFO] Распаковка {gz_path} -> {crx_path}")
    with gzip.open(gz_path, 'rb') as f_in, open(crx_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"[OK] Файл готов: {crx_path}")
    return crx_path

def update_kinematic_conf(crx_path, conf_file_path):
    with open(conf_file_path, "r", encoding="utf-8") as fin:
        lines = fin.readlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith("inpstr2-path"):
            new_lines.append(f"inpstr2-path    = {crx_path}\n")
        elif line.strip().startswith("inpstr3-path"):
            new_lines.append(f"inpstr3-path    = {crx_path}\n")
        else:
            new_lines.append(line)
    with open(conf_file_path, "w", encoding="utf-8") as fout:
        fout.writelines(new_lines)
    print(f"[INFO] kinematic.conf обновлён с путём: {crx_path}")

def run_rtk_rnx2rtkp(rover_crx, base_crx, nav_crx, out_dir, conf):
    out_pos = os.path.join(out_dir, 'solution.pos')
    rnx2rtkp_path = conf.RTKLIB_BIN
    if not os.path.exists(rnx2rtkp_path):
        raise FileNotFoundError(f"Не найден RTKLIB: {rnx2rtkp_path}")
    cmd = [
        rnx2rtkp_path,
        '-k', conf.RTK_CONF,
        '-o', out_pos,
        rover_crx,
        base_crx,
        nav_crx
    ]
    print(f"[INFO] Запуск RTKLIB: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("[RTKLIB OUT]:", res.stdout)
    if res.returncode != 0:
        print("[ERROR] rnx2rtkp failed:\n", res.stderr)
    else:
        print(f"[OK] RTK решение сохранено: {out_pos}")
    return out_pos

def analyze_2d_accuracy(pos_file):
    from math import sqrt
    fix_count = all_count = 0
    sum2d_fix = sum2d_all = 0.0
    print("\n[INFO] Анализ 2D точности по .pos:")
    with open(pos_file) as f:
        for line in f:
            if line.startswith('%') or len(line) < 60:
                continue
            parts = line.split()
            q = int(parts[5])
            e = float(parts[7])
            n = float(parts[8])
            r2d = sqrt(e**2 + n**2)
            all_count += 1
            sum2d_all += r2d
            if q == 1:
                fix_count += 1
                sum2d_fix += r2d
    if all_count == 0:
        print("  Нет решений в файле!")
        return
    print(f"  Всего эпох: {all_count}")
    print(f"  FIX эпох (Q=1): {fix_count}")
    if fix_count > 0:
        print(f"  RMS 2D по FIX: {sum2d_fix/fix_count:.4f} м")
    print(f"  RMS 2D по всем: {sum2d_all/all_count:.4f} м")

def main():
    os.makedirs(conf.OUT_DIR, exist_ok=True)
    rover_crx = decompress_gz(conf.ROVER_FILE)
    base_crx  = decompress_gz(conf.BASE_FILE)
    nav_crx   = decompress_gz(conf.NAV_FILE)
    update_kinematic_conf(rover_crx, conf.RTK_CONF)
    pos_file = run_rtk_rnx2rtkp(rover_crx, base_crx, nav_crx, conf.OUT_DIR, conf)
    analyze_2d_accuracy(pos_file)
    print("[OK] Pipeline RTK завершён!")

if __name__ == "__main__":
    main()
