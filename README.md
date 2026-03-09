# VPN Backend API

Enterprise-grade VPN management backend built with FastAPI, featuring advanced security, multi-server support, and comprehensive user management.

## 🚀 Features

- **Authentication & Security**
  - JWT-based authentication with refresh tokens
  - 2FA/TOTP support
  - Session management with device tracking
  - Rate limiting and DDoS protection
  - Comprehensive audit logging

- **VPN Management**
  - 40+ country server selection
  - WireGuard protocol support
  - Real-time bandwidth monitoring
  - Connection history tracking
  - Premium server access

- **User Features**
  - Email verification
  - Password reset flow
  - Profile management
  - Referral system
  - API key management
  - GDPR compliance (data export/deletion)

- **Admin Features**
  - User management
  - Server management
  - Premium access control
  - Account suspension
  - Security event monitoring
  - Comprehensive analytics

## 📋 Tech Stack

- **Framework:** FastAPI 0.115+
- **Database:** PostgreSQL (NeonDB)
- **Authentication:** JWT with bcrypt
- **Validation:** Pydantic v2
- **Deployment:** Vercel Serverless
- **Security:** Advanced rate limiting, CSP headers, input validation

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- PostgreSQL database (NeonDB recommended)
- Node.js (for Vercel CLI)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/muhammad62763-sketch/VPN-backend.git
cd VPN-backend
```

2. **Create virtual environment**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
python apply_complete_schema_fix.py
```

6. **Start development server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

7. **Access API documentation**
```
http://localhost:8000/docs
```

## 🚀 Deployment

### Deploy to Vercel

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy**
```bash
vercel --prod
```

4. **Configure environment variables in Vercel Dashboard**

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed instructions.

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user

### VPN Endpoints

- `GET /api/v1/vpn/servers` - List available servers
- `POST /api/v1/vpn/config` - Get VPN configuration
- `DELETE /api/v1/vpn/config/{config_id}` - Revoke configuration
- `GET /api/v1/vpn/stats` - Get connection statistics

### User Endpoints

- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update profile
- `POST /api/v1/users/change-password` - Change password
- `GET /api/v1/users/devices` - List user devices

### Admin Endpoints

- `GET /api/v1/admin/dashboard` - Admin dashboard stats
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users/{user_id}/ban` - Ban user
- `GET /api/v1/admin/audit-logs` - View audit logs

For complete API documentation, visit `/docs` endpoint.

## 🔒 Security Features

- **Input Validation:** Comprehensive validation on all endpoints
- **SQL Injection Prevention:** Parameterized queries with whitelisting
- **XSS Protection:** Input sanitization and CSP headers
- **Rate Limiting:** Adaptive rate limiting with IP blocking
- **Session Management:** Secure session tracking with JTI
- **Audit Logging:** Complete audit trail of all actions
- **2FA Support:** TOTP-based two-factor authentication

## 📊 Database Schema

The application uses PostgreSQL with 19 tables:

- `users` - User accounts
- `refresh_tokens` - JWT refresh tokens
- `vpn_configs` - VPN configurations
- `vpn_servers` - Available VPN servers
- `ip_pool` - IP address allocation
- `audit_logs` - Audit trail
- `security_events` - Security monitoring
- `active_sessions` - Session tracking
- `notifications` - User notifications
- `api_keys` - API key management
- `referral_codes` - Referral system
- `bandwidth_usage` - Bandwidth tracking
- And more...

See [database/schema.sql](database/schema.sql) for complete schema.

## 🧪 Testing

```bash
# Run security scan
bandit -r app/ -ll

# Run tests (if implemented)
pytest

# Check code quality
pylint app/
```

## 📱 Mobile Frontend

See [frontend.md](frontend.md) for React Native mobile app documentation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- **Muhammad** - [@muhammad62763-sketch](https://github.com/muhammad62763-sketch)

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- NeonDB for serverless PostgreSQL
- Vercel for serverless deployment
- WireGuard for VPN protocol

## 📞 Support

For support, email support@yourdomain.com or open an issue on GitHub.

## 🔗 Links

- [API Documentation](https://your-project.vercel.app/docs)
- [Deployment Guide](VERCEL_DEPLOYMENT.md)
- [Frontend Documentation](frontend.md)

---

**Version:** 2.0.0  
**Status:** Production Ready  
**Last Updated:** 2026-03-08
