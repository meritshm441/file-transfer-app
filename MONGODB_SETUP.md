# MongoDB Setup Guide for File Transfer App

## 🎯 Target Database: `file_transfer_app`

## Option 1: Install MongoDB Community Server

### Windows Installation:
```bash
# Download and install MongoDB
winget install MongoDB.Server

# Or download from: https://www.mongodb.com/try/download/community
```

### Start MongoDB Service:
```bash
# Start MongoDB daemon
mongod

# Or install as Windows service
net start MongoDB
```

## Option 2: Use MongoDB Atlas (Cloud)

### Update Connection String:
Edit `.env` file:
```env
MONGODB_URI=mongodb+srv://meritshm9:Defence%4021@cluster0.8ofq6ud.mongodb.net/file_transfer_app?appName=Cluster0
DB_NAME=file_transfer_app
```

## Option 3: Use Docker (Recommended for Development)

```bash
# Pull and run MongoDB container
docker run --name mongodb -p 27017:27017 -d mongo:latest

# With persistent data
docker run --name mongodb -p 27017:27017 -v mongodb_data:/data/db -d mongo:latest
```

## 🔄 Switch to MongoDB

After MongoDB is running, use the switcher script:

```bash
python switch_to_mongodb.py
```

Or manually update the imports:

### In `api.py`:
```python
# Try to import MongoDB database, fallback to simple file-based storage
try:
    from database import get_database
    print("[API] Using MongoDB database")
    db = get_database()
except ImportError as e:
    print(f"[API] MongoDB import failed: {e}")
    print("[API] Falling back to simple file-based storage")
    from simple_db import get_database
    db = get_database()
```

### In `server.py`:
```python
# Try to import MongoDB database, fallback to simple file-based storage
try:
    from database import get_database
    print("[Server] Using MongoDB database")
    db = get_database()
except ImportError as e:
    print(f"[Server] MongoDB import failed: {e}")
    print("[Server] Falling back to simple file-based storage")
    from simple_db import get_database
    db = get_database()
```

## 🧪 Test MongoDB Connection

```bash
# Test database connection and initialization
python init_db.py
```

## 🚀 Start Application

```bash
# Start API server
python api.py

# Start frontend (in another terminal)
cd frontend && npm run dev
```

## 📊 Database Collections

MongoDB will create these collections in `file_transfer_app` database:

- `files` - Store file metadata and content
- `transfers` - Store transfer history and statistics

## 🔍 MongoDB Compass (GUI Tool)

Install MongoDB Compass to view your database:
```bash
winget install MongoDB.Compass.Full
```

Connect to: `mongodb://localhost:27017/file_transfer_app`

## 📝 Current Status

- ✅ **File-based storage**: Working (data/files.json, data/transfers.json)
- ⏳ **MongoDB**: Ready to use after installation
- 🔄 **Switching**: Use `switch_to_mongodb.py` script

## 🎯 Benefits of MongoDB

- **Scalability**: Handle large amounts of file data
- **Performance**: Faster queries with indexes
- **Features**: Aggregation pipelines for advanced analytics
- **Production Ready**: Cloud deployment with Atlas

## 🚨 Troubleshooting

### MongoDB not starting:
```bash
# Check if MongoDB is installed
mongod --version

# Start with custom data directory
mongod --dbpath C:\data\db
```

### Connection issues:
```bash
# Check if MongoDB is running
netstat -an | findstr 27017

# Test connection
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('Connected!' if client.admin.command('ping') else 'Failed')"
```

### Port conflicts:
```bash
# Kill process using port 27017
netstat -ano | findstr :27017
taskkill /PID <PID> /F
```
