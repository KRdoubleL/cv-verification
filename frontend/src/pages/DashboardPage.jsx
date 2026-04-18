import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import CandidateCard from '../components/CandidateCard'
import { getBatches, getBatchDetail } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [batches, setBatches] = useState([])
  const [selectedBatch, setSelectedBatch] = useState(null)
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingCandidates, setLoadingCandidates] = useState(false)

  useEffect(() => { loadBatches() }, [])

  const loadBatches = async () => {
    try {
      const data = await getBatches()
      setBatches(data)
      if (data.length > 0) selectBatch(data[0].id)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const selectBatch = async (batchId) => {
    setSelectedBatch(batchId)
    setLoadingCandidates(true)
    try {
      const data = await getBatchDetail(batchId)
      setCandidates(data.candidates || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingCandidates(false)
    }
  }

  const total = candidates.length
  const changed = candidates.filter(c => (c.change_score ?? 100) < 100).length
  const unchanged = candidates.filter(c => (c.change_score ?? 100) === 100).length
  const avg = total > 0 ? Math.round(candidates.reduce((s, c) => s + (c.change_score ?? 100), 0) / total) : 100

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">Candidates</h1>
          {(user?.role === 'recruiter' || user?.role === 'admin') && (
            <button onClick={() => navigate('/upload')}
              className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              Upload CV
            </button>
          )}
        </div>

        {loading ? <div className="text-gray-400 text-sm">Loading...</div>
        : batches.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-gray-400 text-sm">No candidates uploaded yet.</p>
            {(user?.role === 'recruiter' || user?.role === 'admin') && (
              <button onClick={() => navigate('/upload')} className="mt-4 text-blue-600 text-sm hover:underline">
                Upload your first CV
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="flex gap-2 flex-wrap">
              {batches.map(batch => (
                <button key={batch.id} onClick={() => selectBatch(batch.id)}
                  className={`text-sm px-3 py-1.5 rounded-lg border transition-colors ${
                    selectedBatch === batch.id
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'}`}>
                  {batch.batch_name} <span className="ml-1 opacity-70">{batch.total_candidates}</span>
                </button>
              ))}
            </div>

            {!loadingCandidates && total > 0 && (
              <div className="grid grid-cols-4 gap-4">
                {[['Total', total, 'text-gray-900'], ['No changes', unchanged, 'text-green-600'],
                  ['Changes detected', changed, 'text-orange-600'], ['Avg unchanged', `${avg}%`, 'text-blue-600']
                ].map(([label, val, cls]) => (
                  <div key={label} className="bg-white border border-gray-200 rounded-xl p-4">
                    <div className={`text-2xl font-semibold ${cls}`}>{val}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{label}</div>
                  </div>
                ))}
              </div>
            )}

            {loadingCandidates ? <div className="text-gray-400 text-sm">Loading candidates...</div>
            : candidates.length === 0 ? <div className="text-gray-400 text-sm text-center py-10">No candidates in this batch.</div>
            : (
              <div className="grid grid-cols-4 gap-4">
                {candidates.map(c => <CandidateCard key={c.id} candidate={c} />)}
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}