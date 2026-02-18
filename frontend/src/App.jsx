import React, { useState, useEffect } from 'react'
import { io } from 'socket.io-client'
import { FileText, Download, RefreshCw, FolderOpen, HardDrive, FileTextIcon } from 'lucide-react'
import StatsCard from './components/StatsCard'
import FileCard from './components/FileCard'
import Header from './components/Header'
import FileUpload from './components/FileUpload'
import TransferProgress from './components/TransferProgress'

function App() {
  const [files, setFiles] = useState([])
  const [stats, setStats] = useState({ total_files: 0, total_size: 0, total_lines: 0 })
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [socket, setSocket] = useState(null)
  const [transfers, setTransfers] = useState([])

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io('http://localhost:5001')
    setSocket(newSocket)

    // Initial data fetch
    fetchFiles()

    // Socket event listeners
    newSocket.on('files_update', (data) => {
      setFiles(data.files)
      setLoading(false)
    })

    newSocket.on('stats_update', (data) => {
      setStats(data)
    })

    // Transfer progress events
    newSocket.on('transfer_start', (data) => {
      const newTransfer = {
        id: Date.now(),
        filename: data.filename,
        size: data.size,
        progress: 0,
        status: 'uploading',
        message: 'Starting transfer...'
      }
      setTransfers(prev => [...prev, newTransfer])
    })

    newSocket.on('transfer_progress', (data) => {
      setTransfers(prev => prev.map(transfer => 
        transfer.filename === data.filename 
          ? { ...transfer, progress: data.progress, message: data.message }
          : transfer
      ))
    })

    newSocket.on('transfer_complete', (data) => {
      setTransfers(prev => prev.map(transfer => 
        transfer.filename === data.filename 
          ? { ...transfer, progress: 100, status: 'completed', message: data.message }
          : transfer
      ))
      
      // Remove completed transfers after 3 seconds
      setTimeout(() => {
        setTransfers(prev => prev.filter(transfer => 
          !(transfer.filename === data.filename && transfer.status === 'completed')
        ))
      }, 3000)
    })

    newSocket.on('transfer_error', (data) => {
      setTransfers(prev => prev.map(transfer => 
        transfer.filename === data.filename 
          ? { ...transfer, status: 'error', error: data.error }
          : transfer
      ))
    })

    newSocket.on('connect', () => {
      console.log('Connected to server')
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server')
    })

    return () => newSocket.close()
  }, [])

  const fetchFiles = async () => {
    try {
      const response = await fetch('/api/files')
      const data = await response.json()
      setFiles(data.files)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching files:', error)
      setLoading(false)
    }
  }

  const downloadFile = (filename) => {
    window.open(`/api/download/${filename}`, '_blank')
  }

  const handleFileUpload = async (file) => {
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()
      
      if (!result.success) {
        console.error('Transfer failed:', result.error)
        alert(`Transfer failed: ${result.error}`)
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const removeTransfer = (transferId) => {
    setTransfers(prev => prev.filter(transfer => transfer.id !== transferId))
  }

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header onRefresh={fetchFiles} loading={loading} />
      
      <main className="container mx-auto px-4 py-8">
        {/* File Upload Section */}
        <FileUpload onUpload={handleFileUpload} loading={uploading} />
        
        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 mt-8">
          <StatsCard
            title="Total Files"
            value={stats.total_files}
            icon={<FolderOpen className="w-6 h-6" />}
            color="blue"
          />
          <StatsCard
            title="Total Size"
            value={formatBytes(stats.total_size)}
            icon={<HardDrive className="w-6 h-6" />}
            color="green"
          />
          <StatsCard
            title="Total Lines"
            value={stats.total_lines.toLocaleString()}
            icon={<FileTextIcon className="w-6 h-6" />}
            color="purple"
          />
        </div>

        {/* Files Section */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <FileText className="w-6 h-6" />
              Received Files
            </h2>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              {socket?.connected ? (
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  Live
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                  Offline
                </span>
              )}
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Loading files...</span>
            </div>
          ) : files.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No files received yet</h3>
              <p className="text-gray-500">Upload a file above to see results here</p>
            </div>
          ) : (
            <div className="space-y-4 max-w-4xl mx-auto">
              {files.map((file) => (
                <FileCard
                  key={file.id}
                  file={file}
                  onDownload={downloadFile}
                  formatBytes={formatBytes}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Transfer Progress Notifications */}
      <TransferProgress transfers={transfers} onRemove={removeTransfer} />
    </div>
  )
}

export default App
