# AI-vs-我们 对照实验模板

日期：`2026-04-20`

这份模板用于验证：

> 我们是否真的比通用 AI 更有顺序、更可信、更适合上线前判断。

## 实验目标

不要只证明“我们也能回答”。

要验证：

- 我们是不是更适合真实决策场景
- 我们是否只是“另一个 AI 包装层”
- 我们相对 AI 的真实差异点是什么

## 实验设计

每个项目做两版输出：

### A 版：通用 AI 输出

输入来源：

- README
- docs
- 少量公开 issue / discussion

输出要求：

- deployment / security advice

### B 版：我们的方法输出

输出格式建议固定为：

- `go / no-go`
- `why`
- `top risks`
- `first 5 steps`
- `what can wait`
- `what evidence this judgment relies on`

## 记录表头

```csv
date_tested,project_name,project_url,project_type,test_scenario,ai_model,ai_prompt_summary,ai_output_link_or_note,our_output_link_or_note,blind_reviewer,which_is_better_for_real_use,which_has_better_ordering,which_feels_more_trustworthy,which_is_more_reusable,which_is_more_worth_paying_for,main_reason,notes
```

## 盲评问题

让目标用户只看输出，不先告诉他们哪份是谁写的。

至少问：

1. 哪一份更适合你真正上线前使用？
2. 哪一份更有顺序感？
3. 哪一份更像你敢照着做的判断？
4. 哪一份更适合收藏或发给同事？
5. 如果要花钱，你更愿意为哪一份付费？

## 最低完成标准

- `10-20` 个真实项目样本
- 至少 `5` 个盲评人
- 每个样本至少完成：
  - 一份 AI 输出
  - 一份我们的输出
  - 一次盲评结果

## 结果判读

如果大多数盲评结果显示：

- 只是措辞不同，但实质差不多

那么说明：

- 目前差异化还不够强

如果大多数盲评结果显示：

- 我们明显更有顺序
- 更像可承担后果的判断
- 更适合真实上线前场景

那么说明：

- 这条线有机会成立

## 推荐补充观察项

特别记录下面这些高频差异：

- AI 太泛
- AI 没项目上下文
- AI 不敢给 go / no-go
- AI 没有优先级
- 我们更适合作为 SOP / 团队复用材料
