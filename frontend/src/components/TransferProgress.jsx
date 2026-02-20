import React from 'react'
import { X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import clsx from 'clsx'

const TransferProgress = ({ transfers, onRemove }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      default:
        return <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'uploading':
        return 'border-blue-200 bg-blue-50'
      case 'completed':
        return 'border-green-200 bg-green-50'
      case 'error':
        return 'border-red-200 bg-red-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  const getProtocolBadgeClasses = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-200'
      case 'active':
        return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'error':
        return 'bg-red-100 text-red-700 border-red-200'
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200'
    }
  }

  if (transfers.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 max-w-md space-y-2 z-50">
      {transfers.map((transfer) => (
        <div
          key={transfer.id}
          className={clsx(
            'rounded-lg border p-4 shadow-lg transition-all duration-300',
            getStatusColor(transfer.status)
          )}
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              {getStatusIcon(transfer.status)}
              <span className="text-sm font-medium text-gray-900 truncate">
                {transfer.filename}
              </span>
            </div>
            
            <button
              onClick={() => onRemove(transfer.id)}
              className="p-1 text-gray-500 hover:text-gray-700 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {transfer.status === 'uploading' && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-gray-600">
                <span>{transfer.stage ? `Stage: ${transfer.stage}` : 'Uploading...'}</span>
                <span>{Math.round(transfer.progress || 0)}%</span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className="h-full bg-blue-600 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${transfer.progress || 0}%` }}
                />
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <div className="rounded border border-gray-200 bg-white p-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[11px] font-semibold text-gray-700">UDP Discovery</span>
                    <span className={clsx(
                      'text-[10px] px-2 py-0.5 rounded border',
                      getProtocolBadgeClasses(transfer.udpStatus)
                    )}>
                      {transfer.udpStatus || 'pending'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full bg-cyan-500 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${transfer.udpProgress || 0}%` }}
                    />
                  </div>
                </div>

                <div className="rounded border border-gray-200 bg-white p-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[11px] font-semibold text-gray-700">TCP Upload</span>
                    <span className={clsx(
                      'text-[10px] px-2 py-0.5 rounded border',
                      getProtocolBadgeClasses(transfer.tcpStatus)
                    )}>
                      {transfer.tcpStatus || 'pending'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full bg-blue-600 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${transfer.tcpProgress || 0}%` }}
                    />
                  </div>
                </div>
              </div>
              
              {transfer.message && (
                <p className="text-xs text-gray-500 truncate">
                  {transfer.message}
                </p>
              )}
            </div>
          )}

          {transfer.status === 'completed' && (
            <div className="text-xs text-green-700">
              Transfer completed successfully!
            </div>
          )}

          {transfer.status === 'error' && (
            <div className="text-xs text-red-700">
              {transfer.error || 'Transfer failed'}
            </div>
          )}

          <div className="text-xs text-gray-500 mt-1">
            {transfer.size && `${(transfer.size / 1024).toFixed(1)} KB`}
          </div>
        </div>
      ))}
    </div>
  )
}

export default TransferProgress
