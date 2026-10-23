# 新建入库单提交时报错

| 字段 | 内容 |
|---|---|
| 所属模块 | 采购管理 |
| 严重程度 | S2（严重） |
| 环境 | 未提供 |

## 复现步骤

1. 点击采购管理模块
2. 进入新建入库单页面
3. 填写入库单相关信息
4. 点击提交按钮
5. 弹出错误提示：class com.comtech.procurement.bean.entity.purchase.storage.TStorageApprovalDetail cannot be cast to class com.comtech.procurement.bean.vo.purchase.storage.TStorageApprovalDetailVO

## 预期结果

新建入库单成功提交

## 实际结果

弹出错误提示：class com.comtech.procurement.bean.entity.purchase.storage.TStorageApprovalDetail cannot be cast to class com.comtech.procurement.bean.vo.purchase.storage.TStorageApprovalDetailVO

## 原始描述

> 新建入库单提交时报错class com.comtech.procurement.bean.entity.purchase.storage.TStorageApprovalDetail cannot be cast to class com.comtech.procurement.bean.vo.purchase.storage.TStorageApprovalDetailVO
