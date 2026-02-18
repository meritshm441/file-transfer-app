import React, { useState } from 'react'
import { Download, Eye, EyeOff, Calendar, FileText, HardDrive } from 'lucide-react'
import clsx from 'clsx'

const FileCard = ({ file, onDownload, formatBytes }) => {
  const [showFullContent, setShowFullContent] = useState(false)

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="glass-card p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 w-full max-w-4xl">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center gap-2 truncate">
            <FileText className="w-5 h-5 text-blue-600 flex-shrink-0" />
            <span className="truncate">{file.name}</span>
          </h3>
          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <span className="flex items-center gap-1">
              <HardDrive className="w-4 h-4 flex-shrink-0" />
              {formatBytes(file.size)}
            </span>
            <span className="flex items-center gap-1">
              <FileText className="w-4 h-4 flex-shrink-0" />
              {file.lines} lines
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-4 h-4 flex-shrink-0" />
              {formatDate(file.modified)}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2 ml-4 flex-shrink-0">
          <button
            onClick={() => setShowFullContent(!showFullContent)}
            className="btn-secondary flex items-center gap-1 text-sm whitespace-nowrap"
          >
            {showFullContent ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            {showFullContent ? 'Hide' : 'Show'}
          </button>
          <button
            onClick={() => onDownload(file.name)}
            className="btn-primary flex items-center gap-1 text-sm whitespace-nowrap"
          >
            <Download className="w-4 h-4" />
            Download
          </button>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-mono text-gray-700 bg-white rounded border border-gray-300">
            <div className={clsx(
              'p-3 overflow-auto',
              showFullContent ? 'max-h-96' : 'max-h-24'
            )}>
              <pre className="whitespace-pre font-mono text-sm leading-relaxed m-0">
                {showFullContent ? file.content : file.preview}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FileCard
