# 每日瓜分奖池分账 —— 修复说明

## 1. 会出错的输入

- 输入：`pool_cents = 100`，`weights = [1, 1, 1]`
- 当前代码返回值：`[33, 33, 33]`
- 实际的和：`99`
- 应有的和：`100`

原因：`100 * 1 / 3 = 33.333…`，`round()` 得到 `33`，三个人各 `33`，合计 `99`，
比池子少 1 分，违反了「总和必须正好等于池子总额」的硬规则。

（另外 `pool_cents = 1, weights = [1, 1]` 也会出错：`1/2 = 0.5`，Python 的
`round` 采用「银行家舍入」`round(0.5) == 0`，两人各 0，合计 0，同样少发。）

## 2. 修复方法

改用「最大余数法」（largest remainder method）：

1. 一次遍历，用 `divmod(pool_cents * w, total)` 同时得到商（保底金额）和余数
   （小数部分）；
2. 商先向下取整，保证不会多发；`sum(quotients) <= pool_cents`；
3. 需补 1 分的人数 `extra = sum(remainders) // total`（`sum(remainders)` 必是
   `total` 的整数倍，整除无误差，范围在 0 ~ 人数-1）；
4. 按余数从大到小排序，给前 `extra` 人各补 1 分。`sorted` 稳定，余数相同时
   下标小者优先，结果确定。

这样每人只可能拿到 `floor` 或 `floor + 1`，且总和恒等于 `pool_cents`。

边界与校验：
- `weights` 全为 0 且 `pool_cents == 0` 时返回全 0；
- `weights` 全为 0 且 `pool_cents > 0` 时抛 `ValueError`（无法分账）；
- 金额或权重为负时抛 `ValueError`（业务上不可能为负）。

## 3. 测试与两次运行输出

测试文件：`test_pool_split.py`，断言 `sum(split_pool(pool, weights)) == pool`。

### 未修改代码的运行输出（失败）

```
[FAIL] pool=100 weights=[1, 1, 1] -> [33, 33, 33] (sum=99, expect=100)
[FAIL] pool=1 weights=[1, 1] -> [0, 0] (sum=0, expect=1)
[FAIL] pool=7 weights=[1, 1, 1] -> [2, 2, 2] (sum=6, expect=7)
[PASS] pool=10 weights=[3, 3, 4] -> [3, 3, 4] (sum=10, expect=10)
[PASS] pool=100 weights=[2, 1, 1] -> [50, 25, 25] (sum=100, expect=100)
[PASS] pool=10000 weights=[1, 2, 3, 4] -> [1000, 2000, 3000, 4000] (sum=10000, expect=10000)

SOME CASES FAILED
```

### 修改后代码的运行输出（通过）

```
[PASS] pool=100 weights=[1, 1, 1] -> [34, 33, 33] (sum=100, expect=100)
[PASS] pool=1 weights=[1, 1] -> [1, 0] (sum=1, expect=1)
[PASS] pool=7 weights=[1, 1, 1] -> [3, 2, 2] (sum=7, expect=7)
[PASS] pool=10 weights=[3, 3, 4] -> [3, 3, 4] (sum=10, expect=10)
[PASS] pool=100 weights=[2, 1, 1] -> [50, 25, 25] (sum=100, expect=100)
[PASS] pool=10000 weights=[1, 2, 3, 4] -> [1000, 2000, 3000, 4000] (sum=10000, expect=10000)
[PASS] pool=0 weights=[0, 0] -> [0, 0] (sum=0, expect=0)
[PASS] pool=5 weights=[0, 0] -> ValueError (invalid input rejected)

random property test: 20000 cases checked

ALL PASS
```

## 4. AI 的使用情况

- 提出的问题：如何让按权重分配整数的结果总和恒等于池子总额。
- 得到的回答：采用「最大余数法」——先 floor 取整，再按小数部分从大到小补零头。
- 是否直接采用：是，采用了该算法思路。
- 如何确认正确：除题目给的样例外，还在 `test_pool_split.py` 中固化了固定种子的
  随机 property 测试（20,000 组随机输入：`pool_cents ∈ [0, 10000]`，人数 1~20，
  权重 1~100）断言 `sum == pool_cents`，全部通过，未出现任何偏差。
