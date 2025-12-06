# Erika Standalone Application Setup

## Status

The standalone Qt application has been set up with:
- ✅ Database service adapted to use erika library
- ✅ Credentials dialog adapted for standalone use
- ✅ Run script created
- ⚠️ Main Qt app needs to be copied and adapted

## Quick Start

1. **Copy the Qt application**:
   ```bash
   cp /mnt/webapps-nvme/EgoQT/src/ui/erika_standalone_app.py app/main.py
   ```

2. **Adapt the imports** in `app/main.py`:
   - Replace `from database.erika_db_service import` → `from app.database_service import`
   - Replace `from ui.erika_credentials_dialog import` → `from app.credentials_dialog import`
   - Replace `from services.erika_egollama_integration import` → `from erika.services.egollama_gateway import ErikaEgoLlamaGateway as ErikaEgoLlamaIntegration`
   - Remove threat intelligence imports
   - Change token path from `.egoqt` to `.erika`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database** (if using PostgreSQL):
   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ego"
   ```

5. **Run the application**:
   ```bash
   python scripts/run_erika.py
   ```

## Files Created

- `app/database_service.py` - Database service using erika library
- `app/credentials_dialog.py` - Gmail credentials configuration dialog
- `scripts/run_erika.py` - Entry point for running the app
- `requirements.txt` - Updated with PyQt6

## Testing

Once the main app is copied and adapted, test with:
```bash
python scripts/run_erika.py
```

The app should:
1. Start the Qt GUI
2. Allow configuring Gmail credentials
3. Fetch emails from Gmail
4. Display email dashboard with statistics

