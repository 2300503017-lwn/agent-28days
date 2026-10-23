# 审批流启动报错

| 字段 | 内容 |
|---|---|
| 所属模块 | PR管理 |
| 严重程度 | S3（一般） |
| 环境 | 未提供 |

## 复现步骤

1. 点击PR管理模块
2. 点击新建PR按钮
3. 选择BUFFER采购类型
4. 填写PR相关信息
5. 点击提交按钮
6. 审批流启动报错，显示错误信息：Function not found: containsIgnoreCase
7. 审批流状态显示为：未开始

## 预期结果

审批流应正常启动，状态显示为：已开始

## 实际结果

审批流启动报错，状态显示为：未开始

## 原始描述

> 【PR管理-新建PR-BUFFER采购】PR提交后审批流启动报错"Function not found: containsIgnoreCase"，审批流状态"未开始"
