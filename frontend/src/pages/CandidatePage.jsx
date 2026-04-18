import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { getCandidate } from '../services/api'

const API_BASE = 'http://localhost:8000'

function Popup({ title, children, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
        </div>
        {children}
      </div>
    </div>
  )
}

function ClickableSection({ label, children, popupContent }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <div onClick={() => setOpen(true)}
        className="cursor-pointer hover:bg-blue-50 rounded-lg p-3 border border-transparent hover:border-blue-200 transition-all group">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{label}</span>
          <span className="text-xs text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity">View details</span>
        </div>
        {children}
      </div>
      {open && <Popup title={label} onClose={() => setOpen(false)}>{popupContent}</Popup>}
    </>
  )
}

export default function CandidatePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [candidate, setCandidate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showPdf, setShowPdf] = useState(false)

  useEffect(() => {
    getCandidate(id).then(setCandidate).catch(console.error).finally(() => setLoading(false))
  }, [id])

  if (loading) return <Layout><div className="text-gray-400 text-sm">Loading...</div></Layout>
  if (!candidate) return <Layout><div className="text-gray-400 text-sm">Candidate not found.</div></Layout>

  const parsed = candidate.parsed_cv_data || {}
  const employment = candidate.employment_history || []
  const education = candidate.education_history || []
  const skills = parsed.skills || []
  const score = candidate.change_score ?? 100
  const scoreColor = score >= 90 ? 'text-green-600' : score >= 70 ? 'text-yellow-600' : score >= 40 ? 'text-orange-600' : 'text-red-600'
  const token = localStorage.getItem('token')
  const pdfUrl = `${API_BASE}/api/candidates/pdf/${candidate.id}?token=${token}`

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <button onClick={() => navigate('/dashboard')} className="text-sm text-gray-500 hover:text-gray-900">- Back</button>
          <div className="flex items-center gap-3">
            <span className={`text-sm font-semibold border rounded-full px-3 py-1 ${scoreColor}`}>{score}% unchanged</span>
            {candidate.pdf_path && (
              <button onClick={() => setShowPdf(!showPdf)}
                className="text-sm border border-gray-300 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition-colors">
                {showPdf ? 'Hide PDF' : 'View original PDF'}
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 space-y-4">

            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
              <ClickableSection label="Personal Information" popupContent={
                <div className="space-y-3 text-sm">
                  <div><span className="text-gray-500">Name:</span> <span className="font-medium">{candidate.full_name}</span></div>
                  <div><span className="text-gray-500">Email:</span> <span>{candidate.email || '-'}</span></div>
                  <div><span className="text-gray-500">Phone:</span> <span>{candidate.phone || '-'}</span></div>
                  <div><span className="text-gray-500">LinkedIn:</span> {candidate.linkedin_url
                    ? <a href={candidate.linkedin_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{candidate.linkedin_url}</a>
                    : <span className="text-gray-400">Not provided</span>}
                  </div>
                </div>
              }>
                <div>
                  <div className="font-semibold text-gray-900 text-lg">{candidate.full_name}</div>
                  {parsed.current_position && <div className="text-sm text-gray-600">{parsed.current_position}{parsed.current_company ? ` at ${parsed.current_company}` : ''}</div>}
                  <div className="flex gap-4 mt-1 text-xs text-gray-400">
                    {candidate.email && <span>{candidate.email}</span>}
                    {candidate.phone && <span>{candidate.phone}</span>}
                  </div>
                </div>
              </ClickableSection>
            </div>

            {parsed.summary && (
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                <ClickableSection label="Summary" popupContent={<p className="text-sm text-gray-700 leading-relaxed">{parsed.summary}</p>}>
                  <p className="text-sm text-gray-600 line-clamp-3">{parsed.summary}</p>
                </ClickableSection>
              </div>
            )}

            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
              <ClickableSection label="Experience" popupContent={
                <div className="space-y-4">
                  {employment.length === 0 ? <p className="text-sm text-gray-400">No experience data extracted.</p>
                  : employment.map((emp, i) => (
                    <div key={i} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                      <div className="font-medium text-sm">{emp.position}</div>
                      <div className="text-sm text-gray-600">{emp.company_name}</div>
                      <div className="text-xs text-gray-400">{emp.start_date} - {emp.is_current ? 'Present' : (emp.end_date || '?')}</div>
                      {emp.description && <p className="text-xs text-gray-500 mt-2">{emp.description}</p>}
                    </div>
                  ))}
                </div>
              }>
                <div className="space-y-2">
                  {employment.slice(0, 3).map((emp, i) => (
                    <div key={i} className="flex items-start justify-between">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{emp.position}</div>
                        <div className="text-xs text-gray-500">{emp.company_name}</div>
                      </div>
                      <div className="text-xs text-gray-400 shrink-0 ml-4">{emp.start_date} - {emp.is_current ? 'Present' : (emp.end_date || '?')}</div>
                    </div>
                  ))}
                  {employment.length > 3 && <div className="text-xs text-gray-400">+{employment.length - 3} more</div>}
                  {employment.length === 0 && <div className="text-xs text-gray-400">No experience data extracted</div>}
                </div>
              </ClickableSection>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
              <ClickableSection label="Education" popupContent={
                <div className="space-y-4">
                  {education.length === 0 ? <p className="text-sm text-gray-400">No education data extracted.</p>
                  : education.map((edu, i) => (
                    <div key={i} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                      <div className="font-medium text-sm">{edu.institution}</div>
                      {edu.degree && <div className="text-sm text-gray-600">{edu.degree}{edu.field_of_study ? ` - ${edu.field_of_study}` : ''}</div>}
                      <div className="text-xs text-gray-400">{edu.start_date} - {edu.is_current ? 'Present' : (edu.end_date || '?')}</div>
                    </div>
                  ))}
                </div>
              }>
                <div className="space-y-2">
                  {education.map((edu, i) => (
                    <div key={i} className="flex items-start justify-between">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{edu.institution}</div>
                        {edu.degree && <div className="text-xs text-gray-500">{edu.degree}</div>}
                      </div>
                      <div className="text-xs text-gray-400 shrink-0 ml-4">{edu.end_date || edu.start_date || ''}</div>
                    </div>
                  ))}
                  {education.length === 0 && <div className="text-xs text-gray-400">No education data extracted</div>}
                </div>
              </ClickableSection>
            </div>

            {skills.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                <ClickableSection label="Skills" popupContent={
                  <div className="flex flex-wrap gap-2">
                    {skills.map((s, i) => <span key={i} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full">{s}</span>)}
                  </div>
                }>
                  <div className="flex flex-wrap gap-1.5">
                    {skills.slice(0, 8).map((s, i) => <span key={i} className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full">{s}</span>)}
                    {skills.length > 8 && <span className="text-xs text-gray-400">+{skills.length - 8} more</span>}
                  </div>
                </ClickableSection>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-3 text-sm">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-400">Details</h3>
              <div><div className="text-gray-400 text-xs">Uploaded</div><div className="text-gray-700">{new Date(candidate.created_at).toLocaleDateString()}</div></div>
              <div><div className="text-gray-400 text-xs">Status</div><div className="text-gray-700 capitalize">{candidate.verification_status?.toLowerCase().replace('_', ' ')}</div></div>
              <div><div className="text-gray-400 text-xs">LinkedIn</div>
                {candidate.linkedin_url
                  ? <a href={candidate.linkedin_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline text-xs break-all">View profile</a>
                  : <span className="text-gray-400 text-xs">Not found</span>}
              </div>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">LinkedIn Monitoring</h3>
              <p className="text-xs text-gray-400 italic">Automatic LinkedIn change detection coming in Phase 2.</p>
            </div>
          </div>
        </div>

        {showPdf && candidate.pdf_path && (
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-gray-100 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Original PDF</span>
              <button onClick={() => setShowPdf(false)} className="text-gray-400 hover:text-gray-600 text-sm">Hide</button>
            </div>
            <iframe src={pdfUrl} className="w-full h-screen" title="CV PDF" />
          </div>
        )}
      </div>
    </Layout>
  )
}