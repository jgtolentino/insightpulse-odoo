# INSIGHTPULSE AI - UNIFIED DESIGN SYSTEM
**Brand Identity & Theme Specification**
**Version:** 1.0.0
**Last Updated:** 2025-11-08
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Visual Identity](#visual-identity)
2. [Component Library](#component-library)
3. [Login Page Template](#login-page-template)
4. [Brand Assets](#brand-assets)
5. [Usage Guidelines](#usage-guidelines)
6. [Accessibility](#accessibility)
7. [Implementation Checklist](#implementation-checklist)

---

## VISUAL IDENTITY

### Color Palette (Extracted from Mattermost)

**Primary Colors:**
```css
--primary-blue: #2F5BFF;        /* Main brand color - buttons, links */
--primary-blue-hover: #1E44E0;  /* Hover state */
--primary-blue-light: #E8EEFF;  /* Light backgrounds */
```

**Neutral Colors:**
```css
--white: #FFFFFF;
--gray-50: #F8F9FA;             /* Page backgrounds */
--gray-100: #F1F3F5;            /* Card backgrounds */
--gray-200: #E9ECEF;            /* Borders */
--gray-300: #DEE2E6;            /* Disabled states */
--gray-400: #CED4DA;            /* Input borders */
--gray-500: #ADB5BD;            /* Placeholder text */
--gray-600: #6C757D;            /* Secondary text */
--gray-700: #495057;            /* Body text */
--gray-800: #343A40;            /* Headings */
--gray-900: #212529;            /* Dark text */
```

**Semantic Colors:**
```css
--success: #28A745;             /* Success messages */
--warning: #FFC107;             /* Warnings */
--error: #DC3545;               /* Errors */
--info: #17A2B8;                /* Info messages */
```

**Text Colors:**
```css
--text-primary: #212529;
--text-secondary: #6C757D;
--text-muted: #ADB5BD;
--text-link: #2F5BFF;
--text-link-hover: #1E44E0;
```

### Typography

**Font Family:**
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
--font-monospace: 'JetBrains Mono', 'Fira Code', monospace;
```

**Font Sizes:**
```css
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */
--text-5xl: 3rem;        /* 48px */
```

**Font Weights:**
```css
--font-light: 300;
--font-regular: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

**Line Heights:**
```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

### Spacing Scale

```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### Border Radius

```css
--radius-sm: 0.25rem;   /* 4px */
--radius-md: 0.375rem;  /* 6px */
--radius-lg: 0.5rem;    /* 8px */
--radius-xl: 0.75rem;   /* 12px */
--radius-2xl: 1rem;     /* 16px */
--radius-full: 9999px;
```

### Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

---

## COMPONENT LIBRARY

### Buttons

**Primary Button:**
```html
<button class="btn-primary">Sign In</button>
<button class="btn-primary btn-full-width">Sign In</button>
```

**CSS:**
```css
.btn-primary {
    background-color: var(--primary-blue);
    color: var(--white);
    font-weight: var(--font-semibold);
    font-size: var(--text-base);
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-lg);
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-primary:hover {
    background-color: var(--primary-blue-hover);
    box-shadow: var(--shadow-md);
}
```

**Secondary Button:**
```html
<button class="btn-secondary">Cancel</button>
```

**CSS:**
```css
.btn-secondary {
    background-color: var(--white);
    color: var(--primary-blue);
    font-weight: var(--font-semibold);
    font-size: var(--text-base);
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-lg);
    border: 2px solid var(--primary-blue);
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-secondary:hover {
    background-color: var(--primary-blue-light);
}
```

### Input Fields

**Text Input:**
```html
<div class="form-group">
    <label class="input-label" for="email">Email</label>
    <input type="email" id="email" class="input-field" placeholder="you@example.com">
</div>
```

**Password Input:**
```html
<div class="form-group">
    <label class="input-label" for="password">Password</label>
    <div class="password-input-wrapper">
        <input type="password" id="password" class="input-field" placeholder="••••••••">
        <button type="button" class="password-toggle" aria-label="Show password">👁️</button>
    </div>
</div>
```

**CSS:**
```css
.input-field {
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: var(--text-base);
    color: var(--text-primary);
    background-color: var(--white);
    border: 1px solid var(--gray-400);
    border-radius: var(--radius-lg);
    transition: all 0.2s ease;
}

.input-field:focus {
    outline: none;
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 3px var(--primary-blue-light);
}
```

### Cards

**Basic Card:**
```html
<div class="card">
    <h2 class="card-header">Card Title</h2>
    <div class="card-body">
        <p>Card content goes here.</p>
    </div>
</div>
```

**CSS:**
```css
.card {
    background-color: var(--white);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-md);
    padding: var(--space-6);
}
```

### Links

**Basic Link:**
```html
<a href="#" class="link">Forgot your password?</a>
```

**CSS:**
```css
.link {
    color: var(--text-link);
    text-decoration: none;
    font-weight: var(--font-medium);
    transition: color 0.2s ease;
}

.link:hover {
    color: var(--text-link-hover);
    text-decoration: underline;
}
```

---

## LOGIN PAGE TEMPLATE

### Complete HTML

**File:** `portal/login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log in to InsightPulse AI</title>
    <link rel="stylesheet" href="static/css/insightpulse-theme.css">

    <!-- Favicon -->
    <link rel="apple-touch-icon" sizes="180x180" href="/static/favicons/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicons/favicon-16x16.png">
    <link rel="manifest" href="/static/favicons/site.webmanifest">
    <meta name="theme-color" content="#2F5BFF">
</head>
<body class="login-page">
    <div class="login-container">
        <!-- Left Side: Branding -->
        <div class="login-left">
            <div class="brand-logo">
                <img src="/static/insightpulse-logo.svg" alt="InsightPulse AI">
                <span class="brand-tagline">FINANCE SSC AUTOMATION</span>
            </div>
            <h1 class="login-heading">Log in to your account</h1>
            <p class="login-subheading">Collaborate with your team in real-time</p>
        </div>

        <!-- Right Side: Login Form -->
        <div class="login-right">
            <div class="login-card">
                <h2 class="card-header">Log in</h2>

                <form id="loginForm" class="login-form" action="/web/login" method="post">
                    <div class="form-group">
                        <label class="input-label" for="login">Email or Username</label>
                        <input
                            type="text"
                            id="login"
                            name="login"
                            class="input-field"
                            placeholder="Email or Username"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label class="input-label" for="password">Password</label>
                        <div class="password-input-wrapper">
                            <input
                                type="password"
                                id="password"
                                name="password"
                                class="input-field"
                                placeholder="Password"
                                required
                            >
                            <button type="button" class="password-toggle" aria-label="Show password" onclick="togglePassword()">
                                👁️
                            </button>
                        </div>
                    </div>

                    <!-- Database Selection (Odoo-specific) -->
                    <input type="hidden" name="db" value="odoo19">

                    <a href="/web/reset_password" class="link forgot-password-link">Forgot your password?</a>

                    <button type="submit" class="btn-primary btn-full-width">
                        Log in
                    </button>
                </form>

                <div class="signup-prompt">
                    <a href="/web/signup" class="link">Don't have an account?</a>
                </div>
            </div>
        </div>
    </div>

    <footer class="login-footer">
        <p>&copy; 2025 InsightPulse AI. All rights reserved.</p>
        <div class="footer-links">
            <a href="/about" class="link">About</a>
            <a href="/privacy" class="link">Privacy Policy</a>
            <a href="/terms" class="link">Terms</a>
            <a href="/help" class="link">Help</a>
        </div>
    </footer>

    <script>
        function togglePassword() {
            const passwordInput = document.getElementById('password');
            const passwordToggle = document.querySelector('.password-toggle');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                passwordToggle.textContent = '🙈';
            } else {
                passwordInput.type = 'password';
                passwordToggle.textContent = '👁️';
            }
        }
    </script>
</body>
</html>
```

---

## BRAND ASSETS

### Logo Specifications

**Primary Logo:**
- Format: SVG (vector)
- Colors:
  - Main: #2F5BFF (primary blue)
  - Text: #212529 (dark gray)
- Sizes:
  - Large: 200px height
  - Medium: 48px height (navigation)
  - Small: 32px height (favicon)
- Clear space: Minimum 16px on all sides

**Typography Logo:**
- Font: Inter Bold
- Text: "InsightPulse AI"
- Tagline: "Finance SSC Automation" (Inter Medium, 60% opacity)

### Favicon

**Include in all HTML `<head>` sections:**

```html
<link rel="apple-touch-icon" sizes="180x180" href="/static/favicons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/static/favicons/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/static/favicons/favicon-16x16.png">
<link rel="manifest" href="/static/favicons/site.webmanifest">
<meta name="msapplication-TileColor" content="#2F5BFF">
<meta name="theme-color" content="#2F5BFF">
```

**Generate favicon set at:** https://realfavicongenerator.net/

---

## USAGE GUIDELINES

### Do's ✅

- ✅ Use Inter font family for all text
- ✅ Maintain consistent spacing using the spacing scale
- ✅ Use primary blue (#2F5BFF) for CTAs and interactive elements
- ✅ Ensure 4.5:1 color contrast for accessibility (WCAG 2.1 AA)
- ✅ Use rounded corners (8-12px) for cards and inputs
- ✅ Apply subtle shadows for depth
- ✅ Test on mobile devices (responsive design)
- ✅ Include focus states for keyboard navigation

### Don'ts ❌

- ❌ Don't use other blue shades (maintain brand consistency)
- ❌ Don't use Comic Sans or decorative fonts
- ❌ Don't use hard corners (always apply border radius)
- ❌ Don't use red for primary buttons (reserve for errors)
- ❌ Don't use pure black (#000000) - use gray-900 instead
- ❌ Don't mix different shadow styles
- ❌ Don't ignore accessibility requirements

---

## ACCESSIBILITY

### WCAG 2.1 AA Compliance

**Focus States (Keyboard Navigation):**
```css
*:focus-visible {
    outline: 2px solid var(--primary-blue);
    outline-offset: 2px;
}
```

**High Contrast Mode Support:**
```css
@media (prefers-contrast: high) {
    :root {
        --primary-blue: #0033CC;
        --gray-400: #999999;
        --gray-600: #666666;
    }
}
```

**Reduced Motion Support:**
```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### Screen Reader Support

**Always include proper ARIA labels:**

```html
<button aria-label="Show password" class="password-toggle">
    <span aria-hidden="true">👁️</span>
</button>

<nav aria-label="Main navigation">...</nav>
<main aria-label="Main content">...</main>
```

**Semantic HTML:**
- Use `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`
- Proper heading hierarchy (h1 → h2 → h3)
- Form labels associated with inputs

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Core Setup
- [x] Download Inter font from Google Fonts
- [x] Create insightpulse-theme.css file
- [ ] Generate favicon set (use realfavicongenerator.net)
- [ ] Create SVG logo
- [ ] Create brand guidelines PDF

### Phase 2: Service Integration
- [ ] Apply theme to Odoo (custom module)
- [ ] Apply theme to Apache Superset (custom CSS)
- [x] Apply theme to Mattermost (custom theme JSON)
- [ ] Apply theme to n8n (custom CSS)
- [x] Apply theme to unified landing page

### Phase 3: Testing
- [ ] Test on all browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on mobile devices (iOS, Android)
- [ ] Validate accessibility (WAVE, axe DevTools)
- [ ] Test with screen readers (NVDA, JAWS, VoiceOver)
- [ ] Test keyboard navigation
- [ ] Validate color contrast ratios

### Phase 4: Documentation
- [ ] Create component showcase page
- [ ] Document all CSS classes
- [ ] Create style guide for developers
- [ ] Create brand guidelines for marketing
- [ ] Document deployment process

---

## FILES REFERENCE

**Design System Files:**
- `/config/DESIGN_SYSTEM.md` - This file (authoritative specification)
- `/config/branding_theme.json` - Design token specification
- `/config/mattermost_theme.json` - Mattermost custom theme
- `/portal/static/css/insightpulse-theme.css` - Complete CSS implementation
- `/portal/login.html` - Login page template
- `/portal/index.html` - Unified landing page

**Odoo Integration:**
- `/odoo/addons/custom_theme/__manifest__.py` - Theme module manifest
- `/odoo/addons/custom_theme/static/src/css/odoo_custom_theme.css` - Odoo CSS overrides

**Documentation:**
- `/config/BRANDING_README.md` - Installation instructions
- `/portal/DEPLOYMENT.md` - Deployment guide
- `/portal/OAUTH_SETUP.md` - OAuth configuration guide

---

## SERVICES COVERAGE

This design system ensures consistent branding across all InsightPulse services:

1. **Odoo ERP** (erp.insightpulseai.net) - ✅ Configured
2. **Apache Superset** (superset.insightpulseai.net) - ⏳ Pending
3. **Mattermost** (chat.insightpulseai.net) - ✅ Configured
4. **n8n** (n8n.insightpulseai.net) - ⏳ Pending
5. **Unified Portal** (insightpulseai.net) - ✅ Configured

---

## SUPPORT

**Repository:** https://github.com/jgtolentino/insightpulse-odoo
**Documentation:** /docs/
**Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues
**Admin:** jgtolentino_rn@yahoo.com

---

**This design system specification is the authoritative reference for all InsightPulse AI branding and visual design decisions.**
