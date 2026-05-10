import sys
import time
import resource

DELTA = 30

ALPHA = {
    'A': {'A': 0, 'C': 110, 'G': 48, 'T': 94},
    'C': {'A': 110, 'C': 0, 'G': 118, 'T': 48},
    'G': {'A': 48, 'C': 118, 'G': 0, 'T': 110},
    'T': {'A': 94, 'C': 48, 'G': 110, 'T': 0},
}


def parse_input(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    s0 = lines[0]
    j = int(lines[1])
    ops1 = list(map(int, lines[2:2 + j]))

    t0_index = 2 + j
    t0 = lines[t0_index]
    k = int(lines[t0_index + 1])
    ops2 = list(map(int, lines[t0_index + 2:t0_index + 2 + k]))

    return s0, ops1, t0, ops2


def generate_string(base, ops):
    s = base
    for idx in ops:
        insert_pos = idx + 1
        s = s[:insert_pos] + s + s[insert_pos:]
    return s


def mismatch_cost(a, b):
    return ALPHA[a][b]


def align_basic(x, y):
    m, n = len(x), len(y)

    dp = [[0] * (n + 1) for _ in range(m + 1)]
    prev = [[None] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        dp[i][0] = i * DELTA
        prev[i][0] = 'U'
    for j in range(1, n + 1):
        dp[0][j] = j * DELTA
        prev[0][j] = 'L'

    for i in range(1, m + 1):
        xi = x[i - 1]
        for j in range(1, n + 1):
            diag = dp[i - 1][j - 1] + mismatch_cost(xi, y[j - 1])
            up = dp[i - 1][j] + DELTA
            left = dp[i][j - 1] + DELTA

            best = min(diag, up, left)
            dp[i][j] = best

            # Any optimal tie-breaking is acceptable.
            if best == diag:
                prev[i][j] = 'D'
            elif best == up:
                prev[i][j] = 'U'
            else:
                prev[i][j] = 'L'

    aligned_x = []
    aligned_y = []
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0 and prev[i][j] == 'D':
            aligned_x.append(x[i - 1])
            aligned_y.append(y[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or prev[i][j] == 'U'):
            aligned_x.append(x[i - 1])
            aligned_y.append('_')
            i -= 1
        else:
            aligned_x.append('_')
            aligned_y.append(y[j - 1])
            j -= 1

    aligned_x.reverse()
    aligned_y.reverse()
    return dp[m][n], ''.join(aligned_x), ''.join(aligned_y)


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: python3 basic.py <input_file> <output_file>')

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    s0, ops1, t0, ops2 = parse_input(input_path)
    x = generate_string(s0, ops1)
    y = generate_string(t0, ops2)

    before_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    start_time = time.perf_counter()
    cost, aligned_x, aligned_y = align_basic(x, y)
    end_time = time.perf_counter()
    after_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    total_time_ms = (end_time - start_time) * 1000.0
    total_mem_kb = float(max(0, after_mem - before_mem))

    with open(output_path, 'w') as f:
        f.write(f'{cost}\n')
        f.write(f'{aligned_x}\n')
        f.write(f'{aligned_y}\n')
        f.write(f'{total_time_ms:.2f}\n')
        f.write(f'{total_mem_kb:.2f}\n')


if __name__ == '__main__':
    main()
