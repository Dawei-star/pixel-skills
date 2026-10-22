# 常用 UI 组件模板库

网页复刻专用的即用型 HTML/CSS 模板。根据目标截图调整颜色、间距和尺寸。

## 目录

- [导航栏](#导航栏)
- [主视觉区域](#主视觉区域)
- [特性卡片网格](#特性卡片网格)
- [定价卡片](#定价卡片)
- [用户评价](#用户评价)
- [行动号召区域](#行动号召区域)
- [页脚](#页脚)
- [表单样式](#表单样式)
- [按钮变体](#按钮变体)
- [徽章 / 标签 / 胶囊](#徽章--标签--胶囊)
- [数据表格](#数据表格)
- [侧边栏布局](#侧边栏布局)
- [弹窗 / 对话框](#弹窗--对话框)

---

## 导航栏

### 顶部导航栏（居中 Logo，链接在右侧）

```html
<header class="navbar">
  <div class="navbar__container">
    <a href="#" class="navbar__logo">
      <!-- SVG 图标或文字 Logo -->
      <span>品牌名</span>
    </a>
    <nav class="navbar__nav">
      <a href="#" class="navbar__link">功能</a>
      <a href="#" class="navbar__link">定价</a>
      <a href="#" class="navbar__link">关于</a>
      <a href="#" class="navbar__link">联系我们</a>
    </nav>
    <div class="navbar__actions">
      <a href="#" class="btn btn--ghost">登录</a>
      <a href="#" class="btn btn--primary">注册</a>
    </div>
    <button class="navbar__toggle" aria-label="菜单">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
```

```css
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: blur(12px);
  background: rgba(255,255,255,0.8);
}
.navbar__container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.navbar__logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
}
.navbar__nav {
  display: flex;
  gap: 32px;
}
.navbar__link {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.2s;
}
.navbar__link:hover { color: var(--color-text); }
.navbar__toggle { display: none; }

@media (max-width: 768px) {
  .navbar__nav, .navbar__actions { display: none; }
  .navbar__toggle { display: flex; flex-direction: column; gap: 4px; background: none; border: none; cursor: pointer; }
  .navbar__toggle span { display: block; width: 24px; height: 2px; background: var(--color-text); border-radius: 2px; }
}
```

### 透明导航栏（覆盖在主视觉图上）

```css
.navbar--transparent {
  background: transparent;
  border-bottom: none;
}
.navbar--transparent .navbar__link { color: rgba(255,255,255,0.8); }
.navbar--transparent .navbar__link:hover { color: #fff; }
.navbar--transparent .navbar__logo { color: #fff; }
```

---

## 主视觉区域

### 居中文本主视觉

```html
<section class="hero">
  <div class="hero__container">
    <span class="badge">新功能</span>
    <h1 class="hero__title">今天开始<br>创造非凡</h1>
    <p class="hero__subtitle">一段简短的描述，用一两句话解释核心价值主张。</p>
    <div class="hero__actions">
      <a href="#" class="btn btn--primary btn--lg">立即开始</a>
      <a href="#" class="btn btn--outline btn--lg">了解更多</a>
    </div>
  </div>
</section>
```

```css
.hero {
  padding: 128px 24px 80px;
  text-align: center;
  background: var(--color-bg-hero, var(--color-bg));
}
.hero__container {
  max-width: 800px;
  margin: 0 auto;
}
.hero__title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin: 24px 0;
  color: var(--color-text);
}
.hero__subtitle {
  font-size: 1.25rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}
.hero__actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}
```

### 分栏主视觉（文字 + 图片并排）

```html
<section class="hero-split">
  <div class="hero-split__container">
    <div class="hero-split__content">
      <span class="badge">全新 v2.0</span>
      <h1>管理你的工作流的最佳方式</h1>
      <p>描述文字，突出关键优势。</p>
      <div class="hero-split__actions">
        <a href="#" class="btn btn--primary btn--lg">免费试用</a>
      </div>
    </div>
    <div class="hero-split__image">
      <img src="https://picsum.photos/600/400" alt="产品截图" />
    </div>
  </div>
</section>
```

```css
.hero-split__container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
}
.hero-split__content h1 {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.1;
  margin: 16px 0 24px;
}
.hero-split__image img {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15);
}
@media (max-width: 768px) {
  .hero-split__container { grid-template-columns: 1fr; text-align: center; }
}
```

---

## 特性卡片网格

```html
<section class="features">
  <div class="features__container">
    <div class="section-header">
      <h2>核心功能</h2>
      <p>你需要的一切，开箱即用。</p>
    </div>
    <div class="features__grid">
      <div class="feature-card">
        <div class="feature-card__icon"><!-- SVG --></div>
        <h3>功能一</h3>
        <p>该功能的描述及其带来的好处。</p>
      </div>
      <div class="feature-card">
        <div class="feature-card__icon"><!-- SVG --></div>
        <h3>功能二</h3>
        <p>该功能的描述及其带来的好处。</p>
      </div>
      <div class="feature-card">
        <div class="feature-card__icon"><!-- SVG --></div>
        <h3>功能三</h3>
        <p>该功能的描述及其带来的好处。</p>
      </div>
    </div>
  </div>
</section>
```

```css
.features { padding: 96px 24px; background: var(--color-bg-alt, #f9fafb); }
.features__container { max-width: 1200px; margin: 0 auto; }
.section-header { text-align: center; margin-bottom: 64px; }
.section-header h2 { font-size: 2.25rem; font-weight: 700; margin-bottom: 16px; }
.section-header p { font-size: 1.125rem; color: var(--color-text-muted); max-width: 600px; margin: 0 auto; }
.features__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}
.feature-card {
  background: var(--color-white);
  padding: 32px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  transition: box-shadow 0.3s, transform 0.3s;
}
.feature-card:hover {
  box-shadow: 0 10px 40px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.feature-card__icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  background: var(--color-primary-light, #eff6ff);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px;
  color: var(--color-primary);
}
.feature-card h3 { font-size: 1.125rem; font-weight: 600; margin-bottom: 8px; }
.feature-card p { font-size: 0.9375rem; color: var(--color-text-muted); line-height: 1.6; }
@media (max-width: 768px) { .features__grid { grid-template-columns: 1fr; } }
@media (min-width: 769px) and (max-width: 1024px) { .features__grid { grid-template-columns: repeat(2, 1fr); } }
```

---

## 定价卡片

```html
<section class="pricing">
  <div class="pricing__container">
    <div class="section-header">
      <h2>定价方案</h2>
      <p>简单透明的价格。</p>
    </div>
    <div class="pricing__grid">
      <div class="pricing-card">
        <h3>入门版</h3>
        <div class="pricing-card__price">¥9<span>/月</span></div>
        <p>适合个人用户入门</p>
        <ul>
          <li>功能 1</li><li>功能 2</li><li>功能 3</li>
        </ul>
        <a href="#" class="btn btn--outline btn--block">立即开始</a>
      </div>
      <div class="pricing-card pricing-card--featured">
        <span class="badge">最受欢迎</span>
        <h3>专业版</h3>
        <div class="pricing-card__price">¥29<span>/月</span></div>
        <p>适合成长中的团队</p>
        <ul>
          <li>入门版全部功能</li><li>功能 4</li><li>功能 5</li>
        </ul>
        <a href="#" class="btn btn--primary btn--block">立即开始</a>
      </div>
      <div class="pricing-card">
        <h3>企业版</h3>
        <div class="pricing-card__price">¥99<span>/月</span></div>
        <p>适合大型组织</p>
        <ul>
          <li>专业版全部功能</li><li>功能 6</li><li>功能 7</li>
        </ul>
        <a href="#" class="btn btn--outline btn--block">联系销售</a>
      </div>
    </div>
  </div>
</section>
```

```css
.pricing { padding: 96px 24px; }
.pricing__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
  align-items: start;
}
.pricing-card {
  padding: 32px;
  border-radius: 16px;
  border: 1px solid var(--color-border);
  text-align: center;
}
.pricing-card--featured {
  border: 2px solid var(--color-primary);
  box-shadow: 0 20px 60px rgba(var(--color-primary-rgb, 0,0,0), 0.15);
  transform: scale(1.05);
}
.pricing-card h3 { font-size: 1.25rem; font-weight: 600; margin-bottom: 8px; }
.pricing-card__price { font-size: 3rem; font-weight: 800; margin: 16px 0; }
.pricing-card__price span { font-size: 1rem; font-weight: 400; color: var(--color-text-muted); }
.pricing-card ul { list-style: none; padding: 0; margin: 24px 0; text-align: left; }
.pricing-card li { padding: 8px 0; font-size: 0.9375rem; color: var(--color-text-muted); border-bottom: 1px solid var(--color-border); }
.pricing-card li::before { content: "✓"; color: var(--color-primary); margin-right: 8px; font-weight: 700; }
.btn--block { display: block; width: 100%; text-align: center; }
@media (max-width: 768px) {
  .pricing__grid { grid-template-columns: 1fr; max-width: 400px; }
  .pricing-card--featured { transform: none; }
}
```

---

## 用户评价

```html
<section class="testimonials">
  <div class="testimonials__container">
    <div class="section-header"><h2>用户怎么说</h2></div>
    <div class="testimonials__grid">
      <div class="testimonial-card">
        <div class="testimonial-card__stars">★★★★★</div>
        <p>"用户关于使用体验的评价引用。"</p>
        <div class="testimonial-card__author">
          <img src="https://picsum.photos/48/48" alt="头像" />
          <div><strong>姓名</strong><span>职位，公司</span></div>
        </div>
      </div>
    </div>
  </div>
</section>
```

```css
.testimonials { padding: 96px 24px; background: var(--color-bg-alt); }
.testimonials__grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; max-width: 1200px; margin: 0 auto; }
.testimonial-card { background: var(--color-white); padding: 32px; border-radius: 12px; border: 1px solid var(--color-border); }
.testimonial-card__stars { color: #f59e0b; margin-bottom: 16px; }
.testimonial-card p { font-size: 0.9375rem; line-height: 1.7; color: var(--color-text-muted); margin-bottom: 24px; }
.testimonial-card__author { display: flex; align-items: center; gap: 12px; }
.testimonial-card__author img { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
.testimonial-card__author strong { display: block; font-size: 0.875rem; }
.testimonial-card__author span { font-size: 0.8125rem; color: var(--color-text-muted); }
@media (max-width: 768px) { .testimonials__grid { grid-template-columns: 1fr; } }
```

---

## 行动号召区域

```html
<section class="cta">
  <div class="cta__container">
    <h2>准备好开始了吗？</h2>
    <p>加入数千名正在创造非凡的用户。</p>
    <div class="cta__actions">
      <a href="#" class="btn btn--white btn--lg">免费试用</a>
      <a href="#" class="btn btn--outline-white btn--lg">联系销售</a>
    </div>
  </div>
</section>
```

```css
.cta {
  padding: 96px 24px;
  background: var(--color-primary);
  text-align: center;
  border-radius: 24px;
  margin: 0 24px 96px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}
.cta h2 { font-size: 2.5rem; font-weight: 800; color: #fff; margin-bottom: 16px; }
.cta p { font-size: 1.125rem; color: rgba(255,255,255,0.8); margin-bottom: 32px; }
.btn--white { background: #fff; color: var(--color-primary); }
.btn--outline-white { border: 2px solid rgba(255,255,255,0.3); color: #fff; background: transparent; }
```

---

## 页脚

```html
<footer class="footer">
  <div class="footer__container">
    <div class="footer__grid">
      <div class="footer__brand">
        <span class="footer__logo">品牌名</span>
        <p>公司简介描述。</p>
      </div>
      <div class="footer__col">
        <h4>产品</h4>
        <a href="#">功能</a><a href="#">定价</a><a href="#">更新日志</a>
      </div>
      <div class="footer__col">
        <h4>公司</h4>
        <a href="#">关于我们</a><a href="#">博客</a><a href="#">招聘</a>
      </div>
      <div class="footer__col">
        <h4>法律</h4>
        <a href="#">隐私政策</a><a href="#">服务条款</a>
      </div>
    </div>
    <div class="footer__bottom">
      <p>&copy; 2026 品牌名. 保留所有权利.</p>
    </div>
  </div>
</footer>
```

```css
.footer { padding: 64px 24px 32px; background: var(--color-bg-dark, #111827); color: rgba(255,255,255,0.6); }
.footer__grid { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 48px; margin-bottom: 48px; }
.footer__logo { font-size: 1.5rem; font-weight: 700; color: #fff; display: block; margin-bottom: 12px; }
.footer__brand p { font-size: 0.875rem; line-height: 1.6; max-width: 280px; }
.footer__col h4 { color: #fff; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px; }
.footer__col a { display: block; font-size: 0.875rem; color: rgba(255,255,255,0.6); text-decoration: none; padding: 4px 0; transition: color 0.2s; }
.footer__col a:hover { color: #fff; }
.footer__bottom { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px; text-align: center; font-size: 0.8125rem; max-width: 1200px; margin: 0 auto; }
@media (max-width: 768px) { .footer__grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 480px) { .footer__grid { grid-template-columns: 1fr; } }
```

---

## 表单样式

```html
<form class="form">
  <div class="form__group">
    <label class="form__label">邮箱</label>
    <input type="email" class="form__input" placeholder="you@example.com" />
  </div>
  <div class="form__group">
    <label class="form__label">密码</label>
    <input type="password" class="form__input" placeholder="••••••••" />
  </div>
  <div class="form__group">
    <label class="form__label">留言</label>
    <textarea class="form__textarea" rows="4" placeholder="请输入您的留言..."></textarea>
  </div>
  <button type="submit" class="btn btn--primary btn--block">提交</button>
</form>
```

```css
.form { max-width: 480px; }
.form__group { margin-bottom: 20px; }
.form__label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 6px; color: var(--color-text); }
.form__input, .form__textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.9375rem;
  background: var(--color-white);
  color: var(--color-text);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form__input:focus, .form__textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}
.form__textarea { resize: vertical; min-height: 100px; }
```

---

## 按钮变体

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
  line-height: 1.4;
}
.btn--lg { padding: 14px 28px; font-size: 1rem; border-radius: 10px; }
.btn--sm { padding: 6px 14px; font-size: 0.8125rem; border-radius: 6px; }

/* 主要按钮 */
.btn--primary {
  background: var(--color-primary);
  color: #fff;
}
.btn--primary:hover { background: var(--color-primary-dark); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.3); }

/* 次要按钮 */
.btn--secondary {
  background: var(--color-secondary, #f3f4f6);
  color: var(--color-text);
}
.btn--secondary:hover { background: var(--color-secondary-dark, #e5e7eb); }

/* 描边按钮 */
.btn--outline {
  background: transparent;
  border: 1.5px solid var(--color-border);
  color: var(--color-text);
}
.btn--outline:hover { border-color: var(--color-primary); color: var(--color-primary); }

/* 幽灵按钮 */
.btn--ghost {
  background: transparent;
  color: var(--color-text-muted);
}
.btn--ghost:hover { color: var(--color-text); background: var(--color-bg-alt); }

/* 危险按钮 */
.btn--danger { background: #ef4444; color: #fff; }
.btn--danger:hover { background: #dc2626; }
```

---

## 徽章 / 标签 / 胶囊

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
  background: var(--color-primary-light, #eff6ff);
  color: var(--color-primary);
}
.badge--success { background: #ecfdf5; color: #059669; }
.badge--warning { background: #fffbeb; color: #d97706; }
.badge--danger { background: #fef2f2; color: #dc2626; }
.badge--dark { background: #f3f4f6; color: #374151; }
```

---

## 数据表格

```html
<div class="table-wrapper">
  <table class="data-table">
    <thead>
      <tr><th>名称</th><th>状态</th><th>金额</th><th>日期</th></tr>
    </thead>
    <tbody>
      <tr><td>项目 1</td><td><span class="badge badge--success">活跃</span></td><td>¥120</td><td>2026-01-15</td></tr>
      <tr><td>项目 2</td><td><span class="badge badge--warning">待处理</span></td><td>¥85</td><td>2026-01-14</td></tr>
    </tbody>
  </table>
</div>
```

```css
.table-wrapper { overflow-x: auto; border: 1px solid var(--color-border); border-radius: 12px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.data-table th { text-align: left; padding: 12px 16px; background: var(--color-bg-alt); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-muted); }
.data-table td { padding: 12px 16px; border-top: 1px solid var(--color-border); }
.data-table tbody tr:hover { background: var(--color-bg-alt); }
```

---

## 侧边栏布局

```html
<div class="layout">
  <aside class="sidebar">
    <div class="sidebar__header">
      <span class="sidebar__logo">品牌名</span>
    </div>
    <nav class="sidebar__nav">
      <a href="#" class="sidebar__link sidebar__link--active">
        <span class="sidebar__icon"><!-- 图标 --></span> 仪表盘
      </a>
      <a href="#" class="sidebar__link">
        <span class="sidebar__icon"><!-- 图标 --></span> 数据分析
      </a>
      <a href="#" class="sidebar__link">
        <span class="sidebar__icon"><!-- 图标 --></span> 设置
      </a>
    </nav>
  </aside>
  <main class="main-content">
    <div class="main-content__header">
      <h1>仪表盘</h1>
    </div>
    <div class="main-content__body">
      <!-- 页面内容 -->
    </div>
  </main>
</div>
```

```css
.layout { display: flex; min-height: 100vh; }
.sidebar {
  width: 260px;
  background: var(--color-bg-dark, #111827);
  color: rgba(255,255,255,0.7);
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
}
.sidebar__logo { font-size: 1.25rem; font-weight: 700; color: #fff; padding: 0 8px 24px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 24px; }
.sidebar__nav { display: flex; flex-direction: column; gap: 4px; }
.sidebar__link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 0.875rem;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  transition: all 0.2s;
}
.sidebar__link:hover { background: rgba(255,255,255,0.08); color: #fff; }
.sidebar__link--active { background: rgba(255,255,255,0.12); color: #fff; font-weight: 500; }
.main-content { flex: 1; margin-left: 260px; padding: 32px; background: var(--color-bg-alt); }
.main-content__header { margin-bottom: 32px; }
@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); }
  .main-content { margin-left: 0; }
}
```

---

## 弹窗 / 对话框

```html
<div class="modal-overlay" id="modal">
  <div class="modal">
    <div class="modal__header">
      <h3>弹窗标题</h3>
      <button class="modal__close">&times;</button>
    </div>
    <div class="modal__body">
      <p>弹窗内容放在这里。</p>
    </div>
    <div class="modal__footer">
      <button class="btn btn--ghost">取消</button>
      <button class="btn btn--primary">确认</button>
    </div>
  </div>
</div>
```

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}
.modal {
  background: var(--color-white);
  border-radius: 16px;
  width: 90%;
  max-width: 480px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.25);
}
.modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 0;
}
.modal__header h3 { font-size: 1.125rem; font-weight: 600; }
.modal__close { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--color-text-muted); padding: 4px; }
.modal__body { padding: 24px; }
.modal__footer { padding: 0 24px 24px; display: flex; gap: 12px; justify-content: flex-end; }
```
