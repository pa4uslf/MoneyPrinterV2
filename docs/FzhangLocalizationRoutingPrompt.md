# 给另一个 AI 的站点语言路由改造提示词

> Historical note:
> this prompt has already been used and the locale-routing implementation has landed in `fzhang.dev`.
> Keep this file as an archive / reusable brief, not as an open task by default.

你现在要修改 `fzhang.dev` 的语言切换机制，不要只做表层翻译插件。

目标是让站点、清单、后续通知邮件都能根据访问者语言自动进入合适的语言版本。

## 目标

1. 当访问者系统语言 / 浏览器语言是英文时，自动展示英文版页面、英文版清单承接、英文版后续通知
2. 当访问者系统语言 / 浏览器语言是中文时，继续展示中文版本
3. 不要让用户自己先翻译再填写邮箱，也不要让 Google Translate 这种翻译层拦截表单
4. 不要让“网站可读”和“转化可完成”脱节

## 当前已知问题

- 中文清单页面在新标签页打开后，英文访问者不一定看得懂
- Google Translate 这类方案会拦截表单，出现 `This form cannot be supported`
- checklist、post-submit、邮件通知如果只给中文，英文访问者容易高跳出或退订

## 你要实现的方向

### 1. 语言检测与路由

实现一个轻量的语言检测和路由层：

- 优先读取 `navigator.language` / 浏览器语言
- 允许用户手动切换语言
- 保存语言偏好到 cookie 或 localStorage
- 不要每次刷新都反复重置用户选择

### 2. 页面语言版本

至少保证这些区域有语言版本：

- 首页
- 公共文章
- checklist landing page
- checklist / markdown 阅读页
- post-submit page
- subscribe / 邮件订阅页
- Buttondown 发送的资源交付和 follow-up 邮件

### 3. 转化关键页的要求

不要只翻译 UI 文案。

要让英文访问者在这些页面上仍然能完成动作：

- 领取清单
- 理解清单用途
- 理解后续邮件是什么
- 理解下一步应该做什么

### 4. 邮件语言切换

根据订阅者语言偏好或来源语言，给邮件使用对应语言：

- 英文订阅者 -> 英文交付邮件、英文 welcome、英文 follow-up
- 中文订阅者 -> 中文交付邮件、中文 welcome、中文 follow-up

如果需要打标签，建议同步写入：

- `locale-en`
- `locale-zh`

### 5. 尽量保持轻量

优先考虑：

- 现有站点结构上的 locale 分流
- 两套最小内容版本
- 少量模板切换

不要做：

- 重型 CMS 重构
- 不必要的整站国际化迁移
- 为了翻译而翻译的多语言工程

## 你要输出的结果

1. 语言路由方案
2. 页面与邮件需要修改的文件列表
3. 如何检测并保存语言偏好
4. checklist / post-submit / email 如何做到同语种承接
5. 验证清单

## 验证清单

至少验证：

- 中文系统语言访问者看到中文版本
- 英文系统语言访问者看到英文版本
- 英文访问者能直接填邮箱，不再被翻译层打断
- checklist、post-submit、邮件内容语言一致
- 语言切换不会破坏移动端体验

如果你发现“整站翻译插件”不足以满足这个目标，请明确提出替代方案，不要硬套翻译插件。
