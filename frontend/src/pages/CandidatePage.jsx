import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { getCandidate, getSectionChecks, markSectionChecked, markSectionChanged, claimCandidate, completeVerification } from '../services/api'
import { useAuth } from '../context/AuthContext'

const API_BASE = 'http://localhost:8000'

function ChangeHistory({ history }) {
  const [index, setIndex] = useState(history.length - 1)
  if (!history || history.length === 0) return null
  const entry = history[index]
  return (
    <div className="mt-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-amber-700">Change history</span>
        <div className="flex items-center gap-2">
          <button onClick={() => setIndex(i => Math.max(0, i - 1))} disabled={index === 0}
            className="text-xs px-2 py-0.5 border border-amber-300 rounded disabled:opacity-30 hover:bg-amber-100">←</button>
          <span className="text-xs text-amber-600">{index + 1} / {history.length}</span>
          <button onClick={() => setIndex(i => Math.min(history.length - 1, i + 1))} disabled={index === history.length - 1}
            className="text-xs px-2 py-0.5 border border-amber-300 rounded disabled:opacity-30 hover:bg-amber-100">→</button>
        </div>
      </div>
      <div className="text-xs text-amber-600 mb-1">{new Date(entry.date).toLocaleDateString()} - {entry.checked_by}</div>
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-red-50 border border-red-200 rounded p-2">
          <div className="text-xs font-semibold text-red-500 mb-1">Before</div>
          <div className="text-xs text-gray-700 whitespace-pre-wrap">{entry.old_value || '-'}</div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded p-2">
          <div className="text-xs font-semibold text-green-600 mb-1">After</div>
          <div className="text-xs text-gray-700 whitespace-pre-wrap">{entry.new_value || '-'}</div>
        </div>
      </div>
      {entry.note && <div className="text-xs text-amber-700 mt-2 italic">Note: {entry.note}</div>}
    </div>
  )
}

function ChangeModal({ title, currentValue, onSave, onClose }) {
  const [oldValue, setOldValue] = useState(currentValue || '')
  const [newValue, setNewValue] = useState('')
  const [note, setNote] = useState('')
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Mark as changed - {title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-gray-500 block mb-1">What it says on CV (before)</label>
            <textarea value={oldValue} onChange={e => setOldValue(e.target.value)} rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 block mb-1">What LinkedIn shows now (after)</label>
            <textarea value={newValue} onChange={e => setNewValue(e.target.value)} rows={3}
              placeholder="Paste or type what you see on LinkedIn..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 block mb-1">Note (optional)</label>
            <input value={note} onChange={e => setNote(e.target.value)}
              placeholder="e.g. Role title changed, dates adjusted..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button onClick={onClose} className="flex-1 border border-gray-300 text-gray-700 text-sm px-4 py-2 rounded-lg hover:bg-gray-50">Cancel</button>
          <button onClick={() => onSave(oldValue, newValue, note)}
            className="flex-1 bg-amber-500 text-white text-sm px-4 py-2 rounded-lg hover:bg-amber-600">Save change</button>
        </div>
      </div>
    </div>
  )
}

function SectionBlock({ title, sectionType, sectionRefId, candidateId, check, canVerify, onRefresh, children }) {
  const [changeModal, setChangeModal] = useState(false)
  const [loading, setLoading] = useState(false)

  const status = check?.status || 'unchecked'
  const statusColors = {
    unchecked: 'border-gray-200',
    checked: 'border-green-300 bg-green-50/30',
    changed: 'border-amber-300 bg-amber-50/30'
  }
  const statusBadge = {
    unchecked: <span className="text-xs text-gray-400">Not checked</span>,
    checked: <span className="text-xs text-green-600 font-medium">Checked - {new Date(check.checked_at).toLocaleDateString()} by {check.checked_by}</span>,
    changed: <span className="text-xs text-amber-600 font-medium">Changed - {new Date(check.checked_at).toLocaleDateString()} by {check.checked_by}</span>
  }

  const handleCheck = async () => {
    setLoading(true)
    try {
      await markSectionChecked(candidateId, sectionType, sectionRefId, '')
      onRefresh()
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const handleSaveChange = async (oldVal, newVal, note) => {
    setLoading(true)
    try {
      await markSectionChanged(candidateId, sectionType, sectionRefId, oldVal, newVal, note)
      setChangeModal(false)
      onRefresh()
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  return (
    <div className={`bg-white border rounded-xl p-4 ${statusColors[status]}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{title}</span>
        <div className="flex items-center gap-2">
          {statusBadge[status]}
          {canVerify && (
            <div className="flex gap-1 ml-2">
              <button onClick={handleCheck} disabled={loading}
                className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors disabled:opacity-50">
                Mark checked
              </button>
              <button onClick={() => setChangeModal(true)} disabled={loading}
                className="text-xs px-2 py-1 bg-amber-100 text-amber-700 rounded-lg hover:bg-amber-200 transition-colors disabled:opacity-50">
                Mark changed
              </button>
            </div>
          )}
        </div>
      </div>
      {children}
      {check?.change_history?.length > 0 && <ChangeHistory history={check.change_history} />}
      {changeModal && (
        <ChangeModal title={title} currentValue="" onSave={handleSaveChange} onClose={() => setChangeModal(false)} />
      )}
    </div>
  )
}

function ScoreBadge({ score }) {
  const color = score >= 90 ? 'text-green-600 border-green-300'
    : score >= 70 ? 'text-yellow-600 border-yellow-300'
    : score >= 40 ? 'text-orange-600 border-orange-300'
    : 'text-red-600 border-red-300'
  return <span className={`text-sm font-semibold border rounded-full px-3 py-1 ${color}`}>{score}% unchanged</span>
}
export default function CandidatePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [candidate, setCandidate] = useState(null)
  const [checks, setChecks] = useState([])
  const [loading, setLoading] = useState(true)
  const [showPdf, setShowPdf] = useState(false)
  const [claiming, setClaiming] = useState(false)

  const canVerify = user?.role === 'verifier' || user?.role === 'admin'

  useEffect(() => { loadAll() }, [id])

  const loadAll = async () => {
    try {
      const [cand, sectionChecks] = await Promise.all([getCandidate(id), getSectionChecks(id)])
      setCandidate(cand)
      setChecks(sectionChecks)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const handleClaim = async () => {
    setClaiming(true)
    try { await claimCandidate(id); loadAll() } catch (e) { console.error(e) }
    setClaiming(false)
  }

  const handleComplete = async () => {
    try { await completeVerification(id); loadAll() } catch (e) { console.error(e) }
  }

  const getCheck = (sectionType, refId = null) =>
    checks.find(c => c.section_type === sectionType && c.section_ref_id === refId)

  if (loading) return <Layout><div className="text-gray-400 text-sm">Loading...</div></Layout>
  if (!candidate) return <Layout><div className="text-gray-400 text-sm">Candidate not found.</div></Layout>

  const parsed = candidate.parsed_cv_data || {}
  const employment = candidate.employment_history || []
  const education = candidate.education_history || []
  const skills = parsed.skills || []
  const token = localStorage.getItem('token')
  const pdfUrl = `${API_BASE}/api/candidates/pdf/${candidate.id}?token=${token}`
  const isPending = candidate.verification_status === 'PENDING'
  const isInProgress = candidate.verification_status === 'IN_PROGRESS'
  const isCompleted = candidate.verification_status === 'COMPLETED'

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-5">
        <div className="flex items-center justify-between">
          <button onClick={() => navigate(-1)}
            className="text-sm text-gray-600 hover:text-gray-900 border border-gray-200 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition-colors">
            ← Back
          </button>
          <div className="flex items-center gap-3">
            <ScoreBadge score={candidate.change_score ?? 100} />
            {candidate.pdf_path && (
              <button onClick={() => setShowPdf(!showPdf)}
                className="text-sm border border-gray-300 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition-colors">
                {showPdf ? 'Hide PDF' : 'View original PDF'}
              </button>
            )}
            {candidate.linkedin_url && (
              <a href={candidate.linkedin_url} target="_blank" rel="noreferrer"
                className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors">
                Open LinkedIn
              </a>
            )}
          </div>
        </div>

        {canVerify && (
          <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Status: <span className="font-medium capitalize">{candidate.verification_status.toLowerCase().replace('_', ' ')}</span>
            </div>
            <div className="flex gap-2">
              {isPending && (
                <button onClick={handleClaim} disabled={claiming}
                  className="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  {claiming ? 'Claiming...' : 'Claim & start verification'}
                </button>
              )}
              {isInProgress && (
                <button onClick={handleComplete}
                  className="text-sm bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                  Mark as completed
                </button>
              )}
              {isCompleted && <span className="text-sm text-green-600 font-medium">Verification completed</span>}
            </div>
          </div>
        )}

        <div className="grid grid-cols-3 gap-5">
          <div className="col-span-2 space-y-4">
            <SectionBlock title="Personal Information" sectionType="about" sectionRefId={null}
              candidateId={id} check={getCheck('about', null)} canVerify={canVerify} onRefresh={loadAll}>
              <div>
                <div className="font-semibold text-gray-900 text-lg">{candidate.full_name}</div>
                {parsed.current_position && (
                  <div className="text-sm text-gray-600">{parsed.current_position}{parsed.current_company ? ` at ${parsed.current_company}` : ''}</div>
                )}
                <div className="flex gap-4 mt-1 text-xs text-gray-400">
                  {candidate.email && <span>{candidate.email}</span>}
                  {candidate.phone && <span>{candidate.phone}</span>}
                </div>
              </div>
            </SectionBlock>

            {parsed.summary && (
              <SectionBlock title="About" sectionType="about" sectionRefId={-1}
                candidateId={id} check={getCheck('about', -1)} canVerify={canVerify} onRefresh={loadAll}>
                <p className="text-sm text-gray-700 leading-relaxed">{parsed.summary}</p>
              </SectionBlock>
            )}

            <div className="space-y-3">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide px-1">Experience</div>
              {employment.length === 0 && <div className="text-sm text-gray-400 px-1">No experience data extracted</div>}
              {employment.map((emp) => (
                <SectionBlock key={emp.id} title={`${emp.position} at ${emp.company_name}`}
                  sectionType="experience" sectionRefId={emp.id}
                  candidateId={id} check={getCheck('experience', emp.id)} canVerify={canVerify} onRefresh={loadAll}>
                  <div>
                    <div className="font-medium text-gray-900 text-sm">{emp.position}</div>
                    <div className="text-sm text-gray-600">{emp.company_name}</div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      {emp.start_date} - {emp.is_current ? 'Present' : (emp.end_date || '?')}
                    </div>
                    {emp.description && <p className="text-xs text-gray-500 mt-2 leading-relaxed">{emp.description}</p>}
                  </div>
                </SectionBlock>
              ))}
            </div>

            <div className="space-y-3">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide px-1">Education</div>
              {education.length === 0 && <div className="text-sm text-gray-400 px-1">No education data extracted</div>}
              {education.map((edu) => (
                <SectionBlock key={edu.id} title={edu.institution}
                  sectionType="education" sectionRefId={edu.id}
                  candidateId={id} check={getCheck('education', edu.id)} canVerify={canVerify} onRefresh={loadAll}>
                  <div>
                    <div className="font-medium text-gray-900 text-sm">{edu.institution}</div>
                    {edu.degree && <div className="text-sm text-gray-600">{edu.degree}{edu.field_of_study ? ` - ${edu.field_of_study}` : ''}</div>}
                    <div className="text-xs text-gray-400 mt-0.5">{edu.start_date} - {edu.is_current ? 'Present' : (edu.end_date || '?')}</div>
                  </div>
                </SectionBlock>
              ))}
            </div>

            {skills.length > 0 && (
              <SectionBlock title="Skills" sectionType="skills" sectionRefId={null}
                candidateId={id} check={getCheck('skills', null)} canVerify={canVerify} onRefresh={loadAll}>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {skills.map((s, i) => <span key={i} className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full">{s}</span>)}
                </div>
              </SectionBlock>
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
              <h3 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-3">Verification progress</h3>
              <div className="space-y-2 text-xs">
                {checks.length === 0 ? <div className="text-gray-400 italic">No sections checked yet</div> : (
                  <>
                    <div className="flex justify-between text-green-600"><span>Checked</span><span>{checks.filter(c => c.status === 'checked').length}</span></div>
                    <div className="flex justify-between text-amber-600"><span>Changed</span><span>{checks.filter(c => c.status === 'changed').length}</span></div>
                    <div className="flex justify-between text-gray-400"><span>Total</span><span>{checks.length}</span></div>
                  </>
                )}
              </div>
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