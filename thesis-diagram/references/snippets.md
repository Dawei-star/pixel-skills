# 可粘贴片段

"两端半圆""空心三角"这类描述会被脑补出偏差。下面每段都验证过，改数值即可，不要重新发明。

---

## 箭头 marker

```svg
<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5"
        markerWidth="7" markerHeight="7" orient="auto-start-reverse">
  <path d="M1 1 L9 5 L1 9 Z" fill="#2C2C2A"/>
</marker>
```

开放箭头把 path 换成折线：`<path d="M1.5 1.5 L9 5 L1.5 8.5" fill="none" stroke="#2C2C2A" stroke-width="1.4" stroke-linecap="round"/>`

**`refX="9"` 表示路径终点即箭尖**。因此线的终点必须给目标图元的边界坐标，留 2px 余量就会露缝。

---

## 终止符（GB 1526 跑道形）

```svg
<rect x="0" y="0" width="84" height="28" rx="14" fill="#fff" stroke="#2C2C2A" stroke-width="1.3"/>
```

`rx` 必须等于 `height/2`。写 `rx="6"` 就退化成圆角矩形，是两套规范都不认的形状。

---

## UML 初始 / 终止节点

```svg
<circle cx="0" cy="0" r="8" fill="#2C2C2A"/>
```

```svg
<circle cx="0" cy="0" r="12" fill="none" stroke="#2C2C2A" stroke-width="1.4"/>
<circle cx="0" cy="0" r="8" fill="#2C2C2A"/>
```

第一个是初始节点，后两行叠起来是终止节点。**都不写文字**，写了就变成动作框。

---

## 类图关系端点

聚合（空心菱形，贴整体端）：

```svg
<polygon points="0,0 10,-6 20,0 10,6" fill="#fff" stroke="#2C2C2A" stroke-width="1.1"/>
```

组合把 `fill` 改成 `#2C2C2A`。菱形放在**整体**那一端，不是部分。

泛化 / 实现（空心三角，指向父类）：

```svg
<marker id="tri" viewBox="0 0 12 12" refX="10.5" refY="6"
        markerWidth="11" markerHeight="11" orient="auto">
  <path d="M1.5 1.5 L10.5 6 L1.5 10.5 Z" fill="#FFFFFF" stroke="#2C2C2A" stroke-width="1.1"/>
</marker>
```

实现线加 `stroke-dasharray="5 3"`。

---

## 活动图分叉 / 汇合

```svg
<line x1="80" y1="104" x2="240" y2="104" stroke="#2C2C2A" stroke-width="3.5"/>
```

一条粗横线，不是菱形。菱形只表示"几选一"。

---

## PlantUML 活动图判断节点（必加，否则有三大硬伤）

PlantUML 新版 activity 语法的默认画法有三个问题：① 条件文字顶破菱形边框；
② if/endif 汇合处自动画一个**空心小菱形**（UML 合并节点，教材流程图里看着像画错）；
③ 连线为绕进空心菱形而产生拐弯。统一样式里必须加：

```plantuml
' 条件文字写在菱形内，菱形随文字自动撑大
skinparam ConditionStyle Inside
' 分支汇合处：用水平线代替默认的空心合并菱形
skinparam ConditionEndStyle hline
```

注意 `ConditionStyle Diamond` 是"空菱形 + 文字挂在外面"，不符合教材惯例，不要用。
分支本身以 `stop` 结束时不存在汇合，`hline` 不生效也无需处理。

---

## 椭圆上的交点

从 `(x0,y0)` 指向椭圆 `(cx,cy,rx,ry)`，取靠近起点的交点：

```python
import math
dx, dy = cx - x0, cy - y0
a = (dx / rx) ** 2 + (dy / ry) ** 2
s = 1 - math.sqrt(1 / a)
return x0 + dx * s, y0 + dy * s
```

不要目测。参与者引出多条关联线时，统一从**手臂末端**出发，落点用这个公式算。

---

## 时序图激活条

```svg
<rect x="164" y="66" width="12" height="132" fill="#fff" stroke="#2C2C2A" stroke-width="1.2"/>
```

消息箭头的端点对齐激活条的左右边缘，不指向生命线。

---

## 用例图布局骨架

```
参与者(左中) ─┬─→ 主用例1 ──«include»→ 次用例A (右列,偏上)
              ├─→ 主用例2 ──«include»→ 次用例B (右列,偏下)
              └─→ 主用例3 ──«extend»── 次用例C (右列,同行)
```

主用例一列，被依赖用例右移一列并上下错开。参考尺寸：画布 400×360，主用例 `cx=168 rx=60`，次用例 `cx=318 rx=46`，垂直间距 ≥ 75。

### PlantUML 样板（关联必须带箭头）

```
@startuml
left to right direction
skinparam monochrome true
skinparam shadowing false
skinparam packageStyle rectangle

' 线型：禁用默认样条曲线，长距离 include 会画出 S 弯、跨边界关联会绕大弧线
skinparam linetype ortho
' 线宽：PlantUML 默认椭圆 0.5 / 连线 1.0 / actor 0.5，同图粗细不一，全部拉齐到 1
skinparam usecaseBorderThickness 1.0
skinparam actorBorderThickness 1.0
skinparam rectangleBorderThickness 1.0
skinparam classBorderThickness 1.0
skinparam activityBorderThickness 1.0
skinparam stateBorderThickness 1.0
' 时序图：参与者边框拉齐；生命线 0.5 细虚线是 UML 惯例，保留
skinparam sequenceParticipantBorderThickness 1.0
skinparam sequenceActorBorderThickness 1.0

actor 用户 as U
rectangle 在线订单管理系统 {
  usecase "提交订单" as UC1
  usecase "查看订单记录" as UC2
  usecase "申请退款" as UC3
  usecase "计算优惠" as UC4
}

U --> UC1
U --> UC2
U --> UC3
UC1 ..> UC4 : <<include>>
@enduml
```

`-->` 才有箭头，`--` 出来是光杆线，别用。`..>` 给 include / extend，箭头指向被依赖方。`left to right direction` 让参与者落左侧、系统边界在右，比默认的上下布局更接近教材版式。

手写 SVG 时，每条关联线的 `<line>` 都要带 `marker-end="url(#ar)"`，终点取椭圆边界交点：

```
t = 1 / sqrt((dx/rx)² + (dy/ry)²)      // (dx,dy) 为椭圆中心 → 连线起点（参与者）的向量
交点 = (cx + dx·t, cy + dy·t)
```

箭尖再沿连线方向外扩 1px 贴住边界，留给 marker 的 `refX` 吃掉。
