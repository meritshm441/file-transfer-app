# File Transfer Dashboard

A modern, real-time file transfer monitoring application built with React, Vite, and Flask.

## Architecture

### Backend (Flask + Socket.IO)
- **REST API**: `/api/files`, `/api/stats`, `/api/download/:filename`
- **Real-time updates**: WebSocket connections for live file monitoring
- **File monitoring**: Automatic detection of new `received_*.txt` files

### Frontend (React + Vite + TailwindCSS)
- **Modern React**: Hooks, components, real-time updates
- **Styling**: TailwindCSS with custom components
- **Build system**: Vite for fast development and optimized builds
- **Icons**: Lucide React for consistent iconography

## Quick Start

### Prerequisites
- Python 3.12.4
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Activate virtual environment**
   ```bash
   .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the API server**
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
- **Statistics**: Total files, size, and line counts
- **WebSocket connection**: Live status indicator

### File Management
- **File cards**: Modern card-based UI for each received file
- **Content preview**: Toggle between preview and full content
- **Download functionality**: Direct file downloads
- **Metadata display**: Size, lines, and modification timestamps

### Modern UI/UX
- **Responsive design**: Works on desktop and mobile
- **Glass morphism**: Modern translucent card effects
- **Smooth animations**: Hover effects and transitions
- **Loading states**: Professional loading indicators

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
# Test file transfer functionality
python test.py

# Test API endpoints
curl http://localhost:5001/api/files
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

## Technology Stack

### Backend
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-SocketIO**: WebSocket support
- **Python 3.12.4**: Runtime environment

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
