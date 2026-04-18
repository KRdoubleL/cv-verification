import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { uploadPDF } from '../services/api'

export default function UploadPage() {
  const navigate = useNavigate()
  const fileRef = useRef()
  const [batchName, setBatchName] = useState('')
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped?.type === 'application/pdf') { setFile(dropped); setError('') }
    else setError('Only PDF files are accepted')
  }

  const handleSubmit = async () => {
    if (!file) return setError('Please select a PDF file')
    if (!batchName.trim()) return setError('Please enter a batch name')
    setLoading(true)
    setError('')
    try {
      const result = await uploadPDF(file, batchName.trim())
      navigate(`/candidate/${result.candidate_id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="max-w-xl mx-auto space-y-6">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Upload CV</h1>
          <p className="text-sm text-gray-500 mt-1">Upload a PDF resume. We'll extract and structure the data automatically.</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Batch name</label>
            <input type="text" value={batchName} onChange={e => setBatchName(e.target.value)}
              placeholder="e.g. Senior Developer - April 2026"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div onDragOver={e => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)} onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
              dragging ? 'border-blue-400 bg-blue-50' : file ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-gray-400'}`}>
            <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={e => { setFile(e.target.files[0]); setError('') }} />
            {file ? (
              <div className="space-y-1">
                <div className="text-green-600 font-medium text-sm">{file.name}</div>
                <div className="text-gray-400 text-xs">{(file.size / 1024).toFixed(0)} KB</div>
                <button onClick={e => { e.stopPropagation(); setFile(null) }} className="text-xs text-red-500 hover:underline mt-2">Remove</button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-gray-400 text-sm">Drag and drop a PDF here</div>
                <div className="text-gray-300 text-xs">or click to browse</div>
              </div>
            )}
          </div>
          {error && <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</div>}
          <div className="flex gap-3">
            <button onClick={() => navigate('/dashboard')}
              className="flex-1 border border-gray-300 text-gray-700 text-sm px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">Cancel</button>
            <button onClick={handleSubmit} disabled={loading || !file}
              className="flex-1 bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
              {loading ? 'Processing...' : 'Upload & Parse'}
            </button>
          </div>
        </div>
        {loading && <div className="text-center text-sm text-gray-500">Extracting CV data with AI - this takes a few seconds...</div>}
      </div>
    </Layout>
  )
}