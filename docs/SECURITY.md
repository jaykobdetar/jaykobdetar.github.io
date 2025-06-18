# Security Implementation Guide

This project implements a comprehensive, multi-layered security approach using **trusted, industry-standard libraries** and security best practices.

## 🛡️ Security Layers

### 1. Server-Side Security (Python)

#### Trusted Libraries Used
- **bleach** (>= 6.0.0) - Industry-standard HTML sanitization, used by Mozilla, GitHub
- **html5lib** (>= 1.1) - Secure HTML parsing and validation
- **defusedxml** (>= 0.7.1) - Secure XML parsing (prevents XXE attacks)
- **cryptography** (>= 41.0.0) - Industry-standard cryptographic operations

#### Implementation
- `src/utils/trusted_security.py` - Main security module
- `src/utils/security_middleware.py` - Security headers and CSP
- All user input validated and sanitized using trusted libraries
- No custom sanitization - only proven, battle-tested libraries

### 2. Client-Side Security (JavaScript)

#### Trusted Libraries Used
- **DOMPurify** (3.0.5) - Industry-standard client-side HTML sanitization
- Loaded from JSDelivr CDN with integrity verification
- Used by major companies including Google, Microsoft, GitHub

#### Implementation
- `assets/js/trusted-sanitizer.js` - Client-side security wrapper
- Replaces all custom `escapeHtml` functions
- Automatic fallback if DOMPurify not available

### 3. Content Security Policy (CSP)

#### Strict CSP Headers
```
default-src 'self';
script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
img-src 'self' data: https: blob:;
font-src 'self' https://fonts.gstatic.com;
connect-src 'self';
media-src 'self';
object-src 'none';
frame-src 'none';
base-uri 'self';
form-action 'self';
frame-ancestors 'none';
upgrade-insecure-requests
```

#### Additional Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), location=()`

### 4. Input Validation

#### Comprehensive Validation
- Search queries: Length limits, dangerous pattern detection
- Pagination: Bounds checking, integer validation
- Content types: Whitelist validation
- URLs: Protocol validation, dangerous URL blocking
- Email: RFC-compliant validation
- Slugs: URL-safe character validation

## 🚀 Installation & Setup

### 1. Install Security Dependencies

```bash
pip install -r requirements-security.txt
```

### 2. Web Server Configuration

#### Apache (.htaccess)
```apache
# Include security headers
Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https: blob:; font-src 'self' https://fonts.gstatic.com; connect-src 'self'; media-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests"
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "DENY"
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
```

#### Nginx
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https: blob:; font-src 'self' https://fonts.gstatic.com; connect-src 'self'; media-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### 3. Verify Installation

```bash
# Test security modules
python3 -c "from src.utils.trusted_security import trusted_sanitizer; print('✅ Security modules loaded')"

# Test DOMPurify loading
# Open any page and check browser console for DOMPurify availability
```

## 🔍 Security Features

### HTML Sanitization
- **Server-side**: bleach with secure configuration
- **Client-side**: DOMPurify with strict settings
- **Allowed tags**: Only safe HTML elements
- **Allowed attributes**: Whitelisted safe attributes only
- **URL validation**: Blocks javascript:, data:, vbscript: protocols

### SQL Injection Prevention
- **Parameterized queries**: All database queries use parameters
- **Input validation**: Pattern detection for SQL injection attempts
- **Logging**: Suspicious patterns are logged for monitoring

### XSS Prevention
- **Output encoding**: All dynamic content is sanitized
- **CSP headers**: Browser-level XSS protection
- **Input validation**: Dangerous patterns blocked at input
- **No eval()**: No dynamic code execution

### CSRF Protection
- **Same-origin policy**: Enforced via CSP
- **Form validation**: All forms validated server-side
- **Referrer checking**: Strict referrer policy

## 🔧 Development Guidelines

### For Developers

1. **Always use trusted sanitization**:
   ```python
   # ✅ Correct - Use trusted sanitizer
   from utils.trusted_security import trusted_sanitizer
   clean_html = trusted_sanitizer.sanitize_html(user_input)
   
   # ❌ Wrong - Don't create custom sanitization
   clean_html = user_input.replace('<script>', '')
   ```

2. **Validate all input**:
   ```python
   # ✅ Correct - Use trusted validator
   from utils.trusted_security import trusted_validator
   email = trusted_validator.validate_email(user_email)
   
   # ❌ Wrong - Don't trust user input
   email = user_email
   ```

3. **Use secure HTML generation**:
   ```python
   # ✅ Correct - Use base integrator methods
   html = self.get_secure_html_head(title, description)
   
   # ❌ Wrong - Don't create HTML manually
   html = f"<title>{title}</title>"
   ```

### For Content Creators

1. **HTML in content**: Limited to safe tags only
2. **Links**: Only http:, https:, mailto:, tel: protocols allowed
3. **Images**: Validated for safe sources
4. **Scripts**: Not allowed in content

## 🚨 Security Monitoring

### Log Files to Monitor
- Search query validation failures
- Content sanitization warnings
- SQL injection attempt detection
- XSS attempt detection

### Security Alerts
- Multiple validation failures from same IP
- Attempts to bypass input validation
- Unusual query patterns

## 🔒 Production Checklist

### Before Deployment
- [ ] Install security dependencies (`pip install -r requirements-security.txt`)
- [ ] Configure web server security headers
- [ ] Test DOMPurify loading on all pages
- [ ] Verify CSP is not blocking legitimate resources
- [ ] Test input validation on all forms
- [ ] Review log files for security warnings

### Regular Maintenance
- [ ] Update security libraries monthly
- [ ] Monitor security logs weekly
- [ ] Review CSP violations
- [ ] Test XSS protection
- [ ] Audit input validation rules

## 📚 Security Resources

### Libraries Used
- [bleach](https://bleach.readthedocs.io/) - HTML sanitization
- [DOMPurify](https://github.com/cure53/DOMPurify) - Client-side sanitization
- [html5lib](https://html5lib.readthedocs.io/) - HTML parsing
- [defusedxml](https://pypi.org/project/defusedxml/) - XML security

### Security References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CSP Reference](https://content-security-policy.com/)
- [Mozilla Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)

## 🆘 Security Issues

If you discover a security vulnerability, please:
1. **Do NOT** create a public issue
2. Email security concerns privately
3. Include detailed reproduction steps
4. Allow 90 days for fix before disclosure

---

## Summary

This implementation provides **enterprise-grade security** using only **trusted, industry-standard libraries**:

- ✅ **No custom sanitization** - Only proven libraries
- ✅ **Multi-layered protection** - Defense in depth
- ✅ **Industry standards** - Following OWASP guidelines
- ✅ **Comprehensive validation** - All input validated
- ✅ **Security headers** - Browser-level protection
- ✅ **Monitoring ready** - Logging and alerting

The security implementation is designed to be **bulletproof** while maintaining usability and performance.