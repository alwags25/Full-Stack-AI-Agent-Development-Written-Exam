"""
test_pool_split.py —— 校验 split_pool 是否满足「分账总和恒等于池子总额」的硬规则。

直接运行：python test_pool_split.py
"""

import random

from pool_split import split_pool


def check_case(pool_cents, weights):
    """返回 (是否通过, 实际总和, 分配结果)。"""
    result = split_pool(pool_cents, weights)
    actual = sum(result)
    return actual == pool_cents, actual, result


def main():
    # 覆盖不同规模/权重的样例，其中第一组即第 1 问找到的出错输入。
    cases = [
        (100, [1, 1, 1]),       # 找到的出错输入：实际 99，应有 100
        (1, [1, 1]),            # 每人 0.5 分，round 银行家舍入到 0
        (7, [1, 1, 1]),         # 7 / 3 除不尽
        (10, [3, 3, 4]),        # 权重不完全相同
        (100, [2, 1, 1]),       # 权重不对称
        (10000, [1, 2, 3, 4]),  # 较大金额
        (0, [0, 0]),            # 零奖池、零权重边界
    ]

    all_ok = True
    for pool, weights in cases:
        ok, actual, result = check_case(pool, weights)
        if not ok:
            all_ok = False
        print(f"[{'PASS' if ok else 'FAIL'}] "
              f"pool={pool} weights={weights} -> {result} (sum={actual}, expect={pool})")

    # 非法输入（total == 0 且 pool > 0）应显式抛错，而不是返回错误结果。
    try:
        split_pool(5, [0, 0])
        print("[FAIL] pool=5 weights=[0, 0] should raise ValueError, but it did not")
        all_ok = False
    except ValueError:
        print("[PASS] pool=5 weights=[0, 0] -> ValueError (invalid input rejected)")

    # 随机 property 测试：用固定种子保证可复现，广泛覆盖比手写样例更不易漏问题。
    # 权重取正整数，保证 total > 0，聚焦于「总和恒等于池子」的核心规则。
    rng = random.Random(20261114)
    n_random = 20000
    for _ in range(n_random):
        pool = rng.randint(0, 10000)
        n = rng.randint(1, 20)
        weights = [rng.randint(1, 100) for _ in range(n)]
        ok, actual, result = check_case(pool, weights)
        if not ok:
            all_ok = False
            print(f"[FAIL] pool={pool} weights={weights} -> {result} (sum={actual}, expect={pool})")
            break
    print(f"random property test: {n_random} cases checked")

    print()
    print("ALL PASS" if all_ok else "SOME CASES FAILED")


if __name__ == "__main__":
    main()
