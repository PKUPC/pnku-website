"""
货币计算相关工具

increase_policy 的形式如下：
[(timestamp_min, increase_per_min), ...]
"""


def calc_balance(
    increase_policy: list[tuple[int, int]], timestamp_s: int, begin_timestamp_s: int = 0, base: int = 0
) -> int:
    """
    计算货币余额，从 begin_timestamp_s 开始，到 timestamp_s 结束，基础值为 base
    其中 begin_timestamp_s 和 base 是可选项，默认为 0。
    """
    if len(increase_policy) == 0:
        return base
    if begin_timestamp_s < 0:
        return base

    target_min = timestamp_s // 60
    begin_min = begin_timestamp_s // 60

    if target_min <= begin_min:
        return base

    balance = base

    # 遍历增长策略，计算在时间范围内的增长
    for i in range(len(increase_policy) - 1):
        policy_start_min = increase_policy[i][0]
        policy_end_min = increase_policy[i + 1][0]
        increase_per_min = increase_policy[i][1]

        # 如果当前策略的开始时间晚于目标时间，停止计算
        if policy_start_min >= target_min:
            break

        # 如果当前策略的开始时间晚于开始时间
        if policy_start_min >= begin_min:
            # 计算在当前策略时间段内的增长
            if target_min > policy_end_min:
                # 目标时间超过当前策略结束时间，获取整个策略时间段的增长
                balance += (policy_end_min - policy_start_min) * increase_per_min
            else:
                # 目标时间在当前策略时间段内，计算部分增长
                balance += (target_min - policy_start_min) * increase_per_min
                break
        else:
            # 当前策略的开始时间早于开始时间
            if begin_min < policy_end_min:
                # 开始时间在当前策略时间段内
                if target_min > policy_end_min:
                    # 目标时间超过当前策略结束时间
                    balance += (policy_end_min - begin_min) * increase_per_min
                else:
                    # 目标时间在当前策略时间段内
                    balance += (target_min - begin_min) * increase_per_min
                    break

    # 处理最后一个策略（没有下一个策略）
    if len(increase_policy) > 0:
        last_policy_start_min = increase_policy[-1][0]
        last_increase_per_min = increase_policy[-1][1]

        if target_min > last_policy_start_min:
            if begin_min < last_policy_start_min:
                # 开始时间早于最后一个策略开始时间
                balance += (target_min - last_policy_start_min) * last_increase_per_min
            else:
                # 开始时间晚于或等于最后一个策略开始时间
                balance += (target_min - begin_min) * last_increase_per_min

    return balance


def truncate_increase_policy(increase_policy: list[tuple[int, int]], begin_timestamp_s: int) -> list[tuple[int, int]]:
    """
    将 increase_policy 截断到从 begin_timestamp_s 开始
    """
    if len(increase_policy) == 0:
        return [(0, 0)]

    if begin_timestamp_s < 0:
        return [(0, 0)]

    begin_min = begin_timestamp_s // 60
    if begin_min <= increase_policy[0][0]:
        return increase_policy
    elif len(increase_policy) == 1:
        return [(begin_min, increase_policy[0][1])]
    else:
        assert len(increase_policy) >= 2 and begin_min > increase_policy[0][0]
        start_idx = 0
        for i in range(1, len(increase_policy)):
            if begin_min > increase_policy[i][0]:
                start_idx = i
            else:
                break
        # start_idx 是要换掉的
        rst = [(begin_min, increase_policy[start_idx][1])]
        if start_idx < len(increase_policy) - 1:
            for i in range(start_idx + 1, len(increase_policy)):
                rst.append(increase_policy[i])
        return rst
