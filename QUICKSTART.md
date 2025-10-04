# LedgerFlow Quick Start Guide

Get LedgerFlow up and running in 5 minutes!

## Prerequisites
- Docker and Docker Compose installed
- OR Node.js 18+ and Python 3.11+ for local development

## Option 1: Docker (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/Sabvl67/LedgerFlow.git
cd LedgerFlow
```

### 2. Configure Environment Variables
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env if you have AWS credentials

# Frontend
cp frontend/.env.local.example frontend/.env.local
```

### 3. Start All Services
```bash
docker-compose up -d
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 5. Create Your First Account
1. Navigate to http://localhost:3000/register
2. Enter your details and select a role (user, approver, or admin)
3. Login with your credentials

### 6. Upload Your First Invoice
1. Click "Upload Invoice"
2. Select invoice type (AP or AR)
3. Upload a PDF or image file
4. Review the OCR-extracted data
5. Edit and validate the information
6. Submit for approval

That's it! You're ready to use LedgerFlow.

## Option 2: Local Development

### 1. Set Up Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start the server
DATABASE_URL=sqlite:///./ledgerflow.db uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### 2. Set Up Frontend (New Terminal)
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local

# Start the dev server
npm run dev
```

Frontend will be available at http://localhost:3000

### 3. Test the Synthetic Data Generator
```bash
cd backend
python scripts/generate_synthetic_data.py
```

This will generate sample invoices and demonstrate >90% extraction accuracy.

## Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Test the API
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## Common Tasks

### Upload an Invoice via API
```bash
# Register a user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password","full_name":"User","role":"user"}'

# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password" | \
  python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Upload invoice
curl -X POST http://localhost:8000/api/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@invoice.pdf" \
  -F "invoice_type=accounts_payable"
```

### Generate Synthetic Test Data
```bash
cd backend
python scripts/generate_synthetic_data.py
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify DATABASE_URL in .env
- Install email-validator: `pip install email-validator`

### Frontend won't start
- Check if port 3000 is available
- Delete `node_modules` and run `npm install` again
- Verify NEXT_PUBLIC_API_URL in .env.local

### Database issues
- Delete database file: `rm backend/test.db` or `rm backend/ledgerflow.db`
- Restart the backend to create fresh tables

### Docker issues
- Stop containers: `docker-compose down`
- Remove volumes: `docker-compose down -v`
- Rebuild: `docker-compose up --build`

## Configuration

### AWS Textract (Optional)
If you want to use real AWS Textract instead of mock OCR:

1. Create AWS account and enable Textract
2. Get AWS credentials
3. Update backend/.env:
```
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
```

### QuickBooks (Optional)
If you want to enable QuickBooks sync:

1. Create QuickBooks Developer account
2. Create an app
3. Update backend/.env:
```
QUICKBOOKS_CLIENT_ID=your-client-id
QUICKBOOKS_CLIENT_SECRET=your-secret
QUICKBOOKS_REDIRECT_URI=http://localhost:3000/api/quickbooks/callback
```

## Next Steps

1. **Explore the UI**: Try uploading different invoice types
2. **Test Approvals**: Create approver accounts and test the workflow
3. **Check API Docs**: Visit http://localhost:8000/docs for interactive API documentation
4. **Run Tests**: Execute `pytest` to verify everything works
5. **Customize**: Modify the code to fit your specific needs

## Support

- Issues: https://github.com/Sabvl67/LedgerFlow/issues
- Documentation: See README.md and IMPLEMENTATION.md
- API Docs: http://localhost:8000/docs

## Key Features to Try

1. **Invoice Upload**: Upload a PDF/image and see OCR in action
2. **Validation**: Edit OCR-extracted data before approval
3. **Approvals**: Test the role-based approval workflow
4. **Accuracy**: Check the >90% extraction confidence scores
5. **Real-time**: Notice how fast invoice processing happens

Happy using LedgerFlow! 🎉
