import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { getPendingCandidates, getMyQueue, getStats, claimCandidate } from '../services/api'

export default function VerifierDashboard() {
  const navigate = useNavigate()
  const [pending, setPending] = useState([])
  const [myQueue, setMyQueue] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('queue')

  useEffect(() => { loadAll() }, [])

  const loadAll = async () => {
    try {
      const [p, q, s] = await Promise.all([
        getPendingCandidates(),
        getMyQueue(),
        getStats()
      ])
      setPending(p)
      setMyQueue(q)
      setStats(s)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const handleClaim = async (candidateId) => {
    try {
      await claimCandidate(candidateId)
      loadAll()
    } catch (e) { console.error(e) }
  }

  const candidates = tab === 'queue' ? myQueue : pending

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-xl font-semibold text-gray-900">Verification Queue</h1>

        {stats && (
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <div className="text-2xl font-semibold text-blue-600">{stats.available}</div>
              <div className="text-xs text-gray-500 mt-0.5">Available to claim</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <div className="text-2xl font-semibold text-orange-600">{stats.in_progress}</div>
              <div className="text-xs text-gray-500 mt-0.5">In my queue</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <div className="text-2xl font-semibold text-green-600">{stats.total_verified}</div>
              <div className="text-xs text-gray-500 mt-0.5">Completed</div>
            </div>
          </div>
        )}

        <div className="flex gap-2">
          {[['queue', `My queue (${myQueue.length})`], ['pending', `Available (${pending.length})`]].map(([key, label]) => (
            <button key={key} onClick={() => setTab(key)}
              className={`text-sm px-4 py-2 rounded-lg border transition-colors ${
                tab === key ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
              }`}>
              {label}
            </button>
          ))}
        </div>

        {loading ? <div className="text-gray-400 text-sm">Loading...</div>
        : candidates.length === 0 ? (
          <div className="text-center py-16 text-gray-400 text-sm">
            {tab === 'queue' ? 'No candidates in your queue. Claim some from Available tab.' : 'No candidates available.'}
          </div>
        ) : (
          <div className="space-y-3">
            {candidates.map(c => (
              <div key={c.id} className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between hover:border-gray-300 transition-colors">
                <div>
                  <div className="font-medium text-gray-900">{c.full_name}</div>
                  <div className="text-sm text-gray-500 mt-0.5">
                    {c.parsed_cv_data?.current_position || '-'}
                    {c.parsed_cv_data?.current_company ? ` at ${c.parsed_cv_data.current_company}` : ''}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    Uploaded {new Date(c.created_at).toLocaleDateString()}
                    {c.linkedin_url && <span className="ml-2 text-blue-500">LinkedIn available</span>}
                  </div>
                </div>
                <div className="flex gap-2">
                  {tab === 'pending' && (
                    <button onClick={() => handleClaim(c.id)}
                      className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors">
                      Claim
                    </button>
                  )}
                  <button onClick={() => navigate(`/candidate/${c.id}`)}
                    className="text-sm border border-gray-300 text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition-colors">
                    Open
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}