# Render Deployment Guide for Schedulo

## 🚀 Quick Deployment Steps

### 1. Environment Variables Setup
In your Render dashboard, set these environment variables:

```bash
# Required for Django
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=0
ALLOWED_HOSTS=yourapp.onrender.com,portal.delaala.co.uk
CSRF_TRUSTED_ORIGINS=https://yourapp.onrender.com,https://portal.delaala.co.uk

# Database (Render PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database
USE_SQLITE=0

# Delaala Domain Lock (if using custom domain)
DELAALA_DOMAIN=portal.delaala.co.uk
DELAALA_ORG_NAME=Delaala Company Limited

# Email (optional - configure if needed)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Schedulo <noreply@yourdomain.com>
```

### 2. Build & Start Commands
In Render service settings:

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

**Start Command:**
```bash
gunicorn Schedulo_app.wsgi:application
```

### 3. After First Deployment
Run this command in Render shell to set up initial data:

```bash
python manage.py setup_production_data --admin-password YourSecurePassword123
```

This will create:
- ✅ Delaala Company Limited organization
- ✅ Admin user (admin/YourSecurePassword123)
- ✅ 2 Sample employees (john.doe & jane.smith, password: employee123)
- ✅ Proper organization memberships for ID card creation

### 4. Adding More Employees
To add additional employees after deployment:

```bash
python manage.py add_employee \
  --username new.employee \
  --email employee@delaala.co.uk \
  --first-name "New" \
  --last-name "Employee" \
  --job-title "Position Title" \
  --password "employee123"
```

### 5. Troubleshooting "No Employees" Issue
If no employees show in the ID card dropdown:

1. **Check if users have organization memberships:**
   ```bash
   python manage.py shell
   >>> from accounts.models import OrgMembership
   >>> OrgMembership.objects.all().count()
   ```

2. **List all organization members:**
   ```bash
   python manage.py shell
   >>> from accounts.models import User
   >>> from core.models import Organization
   >>> org = Organization.objects.first()
   >>> users = User.objects.filter(org_memberships__organization=org)
   >>> for u in users: print(f"{u.username} - {u.first_name} {u.last_name}")
   ```

3. **Add organization membership manually:**
   ```bash
   python manage.py shell
   >>> from accounts.models import User, OrgMembership
   >>> from core.models import Organization
   >>> user = User.objects.get(username='username')
   >>> org = Organization.objects.first()
   >>> OrgMembership.objects.create(user=user, organization=org, role='staff')
   ```

### 4. Custom Domain Setup (Optional)
If using portal.delaala.co.uk:
1. Add domain in Render dashboard
2. Update DNS records
3. Set DELAALA_DOMAIN and DELAALA_ORG_NAME environment variables

## 🆔 ID Card System Features

After deployment, you'll have:

- ✅ **Admin Dashboard** for managing ID cards
- ✅ **Employee Self-Service** to view their own cards
- ✅ **Professional Print Layout** for physical cards
- ✅ **Auto-Generated Employee IDs** (ORG-YEAR-XXXX format)
- ✅ **Multi-Tenant Support** with organization filtering
- ✅ **Domain Lock** for Delaala company portal

## 📱 Login Information

After running setup_production_data:
- **Username:** admin
- **Password:** YourSecurePassword123 (or what you set)
- **Email:** admin@delaala.co.uk

**⚠️ IMPORTANT:** Change the admin password immediately after first login!

## 🔧 Adding Employees

1. Login as admin
2. Go to Admin → Users
3. Create new user accounts
4. Assign them to "Delaala Company Limited" organization
5. Go to ID Cards → Create New ID Card
6. Select employee and fill in details

## 🖨️ Printing ID Cards

1. Navigate to ID Cards → List
2. Click on any employee's card
3. Click "Print ID Card" button
4. Use browser print function (optimized for standard ID card size)

## 🔐 Security Features

- Domain lock for portal.delaala.co.uk
- Multi-tenant data isolation
- Role-based access control
- Secure password requirements
- CSRF protection
- HTTPS enforcement in production

## 📞 Support

The system includes:
- Emergency contact information
- Blood type and medical alerts
- Access level management
- Employee photos from profiles
- Expiry date tracking
