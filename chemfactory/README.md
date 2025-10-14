# ChemFactory MES/ERP System

A comprehensive Manufacturing Execution System (MES) and Enterprise Resource Planning (ERP) solution designed specifically for chemical detergents manufacturing companies. Built with FastAPI backend and Next.js frontend, supporting both English and Arabic languages.

## 🌟 Features

### Core Manufacturing
- **Product Management**: Raw materials, intermediates, and finished goods with multilingual support
- **Bill of Materials (BOM)**: Versioned formulations with percentage and weight-based calculations
- **Manufacturing Orders**: Production planning and execution tracking
- **Batch Management**: Complete batch lifecycle from creation to completion
- **Quality Control**: In-process and final quality checks with pass/fail criteria
- **Traceability**: Full lot tracking from materials to finished products

### Inventory & Logistics
- **Multi-warehouse Support**: Multiple warehouses with location-based inventory
- **Lot & Expiry Management**: FEFO (First Expiry, First Out) inventory rotation
- **Inventory Movements**: Receive, putaway, pick, move, adjust, and scrap operations
- **Purchasing**: Supplier management, RFQs, purchase orders, and receipts
- **Sales & Dispatch**: Customer orders, shipments, and delivery management

### Quality & Safety
- **Quality Checks**: Configurable test parameters with tolerance ranges
- **MSDS Management**: Safety data sheet storage and access
- **Hazard Classification**: GHS hazard symbols and safety information
- **COA Generation**: Certificate of Analysis PDF generation

### Accounting
- **Chart of Accounts**: Flexible account structure
- **Journal Entries**: Double-entry bookkeeping
- **Cost Tracking**: Material and labor cost allocation
- **Tax Management**: VAT calculation and reporting

### Human Resources
- **Employee Management**: Staff records and role assignments
- **Skills & Training**: Competency tracking and training records
- **Shift Management**: Work schedule and attendance tracking

### CRM
- **Lead Management**: Sales opportunity tracking
- **Customer Relations**: Account and contact management
- **Activity Tracking**: Communication and interaction history

## 🚀 Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy 2.x**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic v2**: Data validation using Python type annotations
- **JWT Authentication**: Secure token-based authentication
- **PostgreSQL/SQLite**: Database support

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **next-intl**: Internationalization for Arabic/English support
- **TanStack Query**: Data fetching and caching
- **React Hook Form**: Form handling with validation
- **Zod**: Schema validation

## 📁 Project Structure

```
chemfactory/
├── backend/
│   ├── app/
│   │   ├── core/           # Settings, security, dependencies
│   │   ├── db/             # Models, schemas, database
│   │   ├── api/            # API routers
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access layer
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── app/                # Next.js App Router
│   │   ├── [locale]/       # Internationalized routes
│   │   ├── _components/    # Reusable components
│   │   ├── _hooks/         # Custom React hooks
│   │   └── _lib/           # Utility functions
│   ├── messages/           # Translation files
│   └── package.json
├── docs/                   # Documentation
├── .replit                 # Replit configuration
├── replit.nix             # Nix package configuration
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite for development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chemfactory
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Initialize Alembic
   alembic init alembic
   
   # Create initial migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migrations
   alembic upgrade head
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run the Application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

### Replit Deployment

1. **Import to Replit**
   - Import this repository to Replit
   - The `.replit` file will automatically configure the environment

2. **Run the Application**
   - Click the "Run" button in Replit
   - Both backend and frontend will start automatically
   - Backend will be available at `https://your-repl-url.replit.dev:8000`
   - Frontend will be available at `https://your-repl-url.replit.dev`

## 🌐 Internationalization

The system supports both English and Arabic languages:

- **English**: Default language with LTR layout
- **Arabic**: RTL layout with proper Arabic font support
- **Language Switching**: Users can switch between languages
- **RTL Support**: Complete right-to-left layout support for Arabic

### Adding New Languages

1. Add language code to `frontend/i18n.ts`
2. Create translation file in `frontend/messages/[language].json`
3. Update locale validation in layout files

## 🔐 Authentication & Authorization

### Roles
- **ADMIN**: Full system access
- **PRODUCTION_MANAGER**: Manufacturing and production oversight
- **OPERATOR**: Production execution and batch management
- **WAREHOUSE**: Inventory and logistics management
- **QA**: Quality control and testing
- **FINANCE**: Accounting and financial operations
- **SALES**: Customer relations and sales
- **HR**: Human resources management
- **VIEWER**: Read-only access

### Security Features
- JWT-based authentication with access and refresh tokens
- Role-based access control (RBAC)
- Row-level security for data access
- Password hashing with bcrypt
- CORS protection
- Input validation and sanitization

## 📊 Key Business Flows

### 1. Product Creation
1. Create raw materials, intermediates, and finished goods
2. Define product specifications and safety information
3. Set up storage requirements and shelf life

### 2. Formulation Management
1. Create BOM with ingredients and percentages
2. Define tolerance ranges for quality control
3. Version control for formulation changes
4. Release approved formulations for production

### 3. Manufacturing Process
1. Create manufacturing orders based on demand
2. Reserve materials and plan production schedule
3. Execute batches with actual vs. target tracking
4. Perform quality checks at each stage
5. Complete batches and update inventory

### 4. Quality Control
1. Define test parameters and acceptance criteria
2. Record test results during production
3. Block release for failed quality checks
4. Generate certificates of analysis (COA)

### 5. Inventory Management
1. Receive materials and finished goods
2. Track lot numbers and expiry dates
3. Implement FEFO rotation
4. Manage quarantine and hold status

## 🧪 Demo Data

The system includes seed data for demonstration:

### Sample Products
- **Raw Materials**: SLES 70%, CAPB, Fragrance X, Dye Blue 15, Water, Preservative
- **Finished Goods**: "Dishwash Lemon 1L", "Floor Cleaner Pine 4L"

### Sample BOM
- Complete formulation for "Dishwash Lemon 1L" with percentages and tolerances

### Sample QC Tests
- pH testing
- Viscosity measurement
- Active matter percentage
- Appearance inspection

## 📈 Reports & Analytics

- **Batch Genealogy**: Complete traceability from materials to finished products
- **Stock Valuation**: Current inventory value by location
- **Quality Reports**: Pass/fail rates and trend analysis
- **Production Reports**: Efficiency and throughput metrics
- **Financial Reports**: Cost analysis and profitability

## 🔧 API Documentation

- **Swagger UI**: Available at `/docs` when running the backend
- **ReDoc**: Available at `/redoc` for alternative documentation
- **OpenAPI Schema**: Machine-readable API specification

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the API documentation at `/docs`

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core manufacturing functionality
- ✅ Basic inventory management
- ✅ Quality control system
- ✅ Multilingual support

### Phase 2 (Planned)
- 🔄 Barcode scanning integration
- 🔄 Advanced reporting dashboard
- 🔄 Mobile application
- 🔄 Real-time notifications

### Phase 3 (Future)
- 📋 Advanced MRP planning
- 📋 Integration with external systems
- 📋 Machine learning for predictive maintenance
- 📋 IoT sensor integration

---

**ChemFactory MES/ERP** - Empowering chemical manufacturing with modern technology and multilingual support.
