# File Transfer Dashboard

A modern, real-time file transfer monitoring application built with React, Vite, and Flask.

## Architecture

### Backend (Flask + Socket.IO + MongoDB)
- **REST API**: `/api/files`, `/api/stats`, `/api/download/:filename`
- **Real-time updates**: WebSocket connections for live file monitoring
- **MongoDB Database**: Persistent storage for files and transfer metadata
- **File monitoring**: Automatic detection of new `received_*.txt` files

### Frontend (React + Vite + TailwindCSS)
- **Modern React**: Hooks, components, real-time updates
- **Styling**: TailwindCSS with custom components
- **Build system**: Vite for fast development and optimized builds
- **Icons**: Lucide React for consistent iconography

### Database (MongoDB)
- **Files Collection**: Store file metadata and content
- **Transfers Collection**: Track transfer history and statistics
- **Indexes**: Optimized queries for performance

## Quick Start

### Prerequisites
- Python 3.12.4
- Node.js 18+
- npm or yarn
- MongoDB 6.0+ (local installation or MongoDB Atlas)

### Backend Setup

1. **Install and start MongoDB**
   ```bash
   # For local MongoDB
   mongod
   
   # Or use MongoDB Atlas (cloud)
   # Get connection string and add to .env file
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection string
   ```

3. **Initialize database**
   ```bash
   python init_db.py
   ```

4. **Activate virtual environment**
   ```bash
   .venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Start the API server**
   ```bash
   python api.py
   ```
   Server runs on: `http://localhost:5001`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   Frontend runs on: `http://localhost:3000`

## Features

### Real-time Dashboard
- **Live file monitoring**: Automatic updates when new files arrive
- **Enhanced statistics**: File metrics, transfer analytics, success rates
- **WebSocket connection**: Live status indicator
- **MongoDB persistence**: Data survives server restarts

### File Management
- **Database storage**: Files stored in MongoDB with metadata
- **Advanced search**: Filter by file type, client, date range
- **Content preview**: Toggle between preview and full content
- **Download functionality**: Direct file downloads
- **Transfer tracking**: Complete transfer history with performance metrics

### Modern UI/UX
- **Responsive design**: Works on desktop and mobile
- **Glass morphism**: Modern translucent card effects
- **Smooth animations**: Hover effects and transitions
- **Loading states**: Professional loading indicators
- **Enhanced stats**: 6 comprehensive metrics cards

## API Endpoints

### Files
- `GET /api/files` - List all received files
- `GET /api/files/:filename` - Get detailed file information
- `GET /api/download/:filename` - Download a file

### Statistics
- `GET /api/stats` - Get transfer statistics

### WebSocket Events
- `files_update` - Emitted when files change
- `stats_update` - Emitted when statistics change

## Development

### Running Tests
```bash
# Initialize database first
python init_db.py

# Test file transfer functionality
python test.py

# Test API endpoints
curl http://localhost:5001/api/files

# Test database operations
python -c "from database import db; print('Database connection:', db.client.admin.command('ping'))"
```

### Building for Production
```bash
cd frontend
npm run build
```

### Project Structure
```
file-transfer-app/
├── api.py                 # Flask API server
├── server.py              # Original file transfer server
├── database.py            # MongoDB models and connection
├── init_db.py            # Database initialization script
├── .env.example          # Environment variables template
├── src/client.py          # File transfer client
├── test.py                # Test script
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.jsx       # Main app component
│   │   └── main.jsx      # Entry point
│   ├── public/           # Static assets
│   └── package.json      # Dependencies
├── templates/            # Legacy Flask templates
└── requirements.txt      # Python dependencies
```

### Technology Stack

### Backend
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-SocketIO**: WebSocket support
- **PyMongo**: MongoDB driver
- **Python 3.12.4**: Runtime environment

### Database
- **MongoDB**: NoSQL document database
- **Indexes**: Optimized query performance
- **Aggregation**: Advanced statistics and analytics

### Frontend
- **React 18**: UI library
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Lucide React**: Icon library
- **Socket.IO Client**: Real-time communication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for learning and development.
