import { useNavigate } from 'react-router-dom'

function getScoreColor(score) {
  if (score >= 90) return { border: 'border-green-200', text: 'text-green-700', bar: 'bg-green-500' }
  if (score >= 70) return { border: 'border-yellow-200', text: 'text-yellow-700', bar: 'bg-yellow-500' }
  if (score >= 40) return { border: 'border-orange-200', text: 'text-orange-700', bar: 'bg-orange-500' }
  return { border: 'border-red-200', text: 'text-red-700', bar: 'bg-red-500' }
}

export default function CandidateCard({ candidate }) {
  const navigate = useNavigate()
  const score = candidate.change_score ?? 100
  const colors = getScoreColor(score)
  const parsed = candidate.parsed_cv_data || {}
  const currentRole = parsed.current_position || candidate.employment_history?.[0]?.position || '-'
  const currentCompany = parsed.current_company || candidate.employment_history?.[0]?.company_name || '-'

  return (
    <div onClick={() => navigate(`/candidate/${candidate.id}`)}
      className={`bg-white border ${colors.border} rounded-xl p-4 cursor-pointer hover:shadow-md transition-shadow flex flex-col gap-3`}>
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <span className={`text-xs font-semibold ${colors.text}`}>{score}% unchanged</span>
        </div>
        <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div className={`h-full ${colors.bar} rounded-full`} style={{ width: `${score}%` }} />
        </div>
      </div>
      <div>
        <h3 className="font-medium text-gray-900 text-sm truncate">{candidate.full_name}</h3>
        <p className="text-xs text-gray-500 truncate mt-0.5">{currentRole}</p>
        <p className="text-xs text-gray-400 truncate">{currentCompany}</p>
      </div>
      <div className="flex items-center justify-between pt-1 border-t border-gray-100">
        <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${
          candidate.verification_status === 'COMPLETED' ? 'bg-green-100 text-green-700'
          : candidate.verification_status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-700'
          : 'bg-gray-100 text-gray-500'}`}>
          {candidate.verification_status?.toLowerCase().replace('_', ' ')}
        </span>
        <span className="text-xs text-gray-400">{new Date(candidate.created_at).toLocaleDateString()}</span>
      </div>
    </div>
  )
}