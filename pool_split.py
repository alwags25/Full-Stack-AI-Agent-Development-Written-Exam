"""
pool_split.py —— 每日瓜分奖池的分账逻辑

这是我们线上「每日瓜分奖池」的真实代码，为这道题做了简化
（去掉了数据库读写和日期处理，只留下算钱的部分）。

背景：
  平台每天放一个奖池。当天达标的用户，按各自的贡献权重瓜分池子里的钱。

约定：
  · 所有金额都是整数「分」，系统里不存在半分钱。
  · weights 是每个人的贡献权重（线上用的是「合格采集秒数」）。

硬规则（产品定的，不能破）：
  分完之后，所有人拿到的钱加起来必须【正好等于】池子总额。
  多一分 = 平台凭空多发了钱。
  少一分 = 有人的钱卡在系统里没发出去。
"""


def split_pool(pool_cents: int, weights: list[int]) -> list[int]:
    """把 pool_cents 按 weights 的比例分给每个人，返回每人拿到多少分。

    返回列表与 weights 一一对应，且保证 sum(返回值) == pool_cents。

    约定：金额与权重都应为非负整数（分 / 秒）。
    weights 全为 0 时，若 pool_cents 也为 0 则返回全 0，否则无法分账、抛 ValueError。
    """
    if pool_cents < 0:
        raise ValueError("pool_cents 不能为负数")
    if any(w < 0 for w in weights):
        raise ValueError("weights 不能含负数")

    total = sum(weights)
    if total == 0:
        if pool_cents == 0:
            return [0] * len(weights)
        raise ValueError("weights 之和为 0，无法分账")

    # 最大余数法（largest remainder method）：一次遍历同时取
    # 「向下取整的商」（保底金额）和「余数」（代表小数部分，用于分配零头）。
    quotients = []
    remainders = []
    for w in weights:
        q, r = divmod(pool_cents * w, total)
        quotients.append(q)
        remainders.append(r)

    # 需要补 1 分的人数。sum(remainders) 必是 total 的整数倍，整除无误差。
    extra = sum(remainders) // total

    # 按小数部分从大到小补 1 分。sorted 稳定，余数相同时保持原下标顺序
    # （即下标小者优先），结果确定。
    order = sorted(range(len(weights)), key=lambda i: remainders[i], reverse=True)
    for i in order[:extra]:
        quotients[i] += 1

    return quotients


if __name__ == "__main__":
    # 一个跑得通的例子：奖池 100 元，三个人权重相同
    print(split_pool(10000, [1, 1, 1]))
