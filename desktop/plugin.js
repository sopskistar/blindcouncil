import { host, ROUTES_AREA, SIDEBAR_NAV_AREA, PALETTE_AREA, Button, Input, Textarea,
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
  useValue, useQuery, useMutation, useQueryClient } from '@hermes/plugin-sdk'
import { useState, useRef } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const labels = { pending: 'Pending', approved: 'Approved', rejected: 'Rejected', cancelled: 'Cancelled', expired: 'Expired' }
const durations = { '15m': '15 minutes', '1h': '1 hour', '24h': '24 hours', '3d': '3 days', '7d': '7 days' }
const css = `/* Hallmark · app screen · native Hermes theme · review pending · v2.0.0 */
/* Critique: real host captures and interaction verification pending. */
.blindcouncil { --bc-text:var(--ui-text-primary); --bc-muted:var(--ui-text-secondary); --bc-line:var(--ui-stroke-secondary); --bc-accent:var(--ui-accent); --bc-fill:var(--ui-bg-quaternary); --bc-fast:120ms; color:var(--bc-text); width:100%; max-width:1120px; margin:0 auto; padding:28px; min-width:0; overflow-x:clip; }
.blindcouncil * { box-sizing:border-box; }
.blindcouncil h1,.blindcouncil h2,.blindcouncil h3 { overflow-wrap:break-word; min-width:0; font-weight:600; margin:0; }
.blindcouncil h1 { font-size:22px; line-height:1.3; }
.blindcouncil h2 { font-size:18px; line-height:1.4; }
.blindcouncil h3 { font-size:14px; }
.blindcouncil p { line-height:1.6; margin:8px 0; max-width:70ch; }
.blindcouncil .bc-muted { color:var(--bc-muted); font-size:13px; }
.blindcouncil .bc-head,.blindcouncil .bc-actions { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
.blindcouncil .bc-actions { justify-content:flex-start; }
.blindcouncil .bc-head { padding-bottom:24px; border-bottom:1px solid var(--bc-line); }
.blindcouncil .bc-workspace { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.2fr); margin-top:24px; min-height:360px; }
.blindcouncil .bc-list { padding-right:24px; }
.blindcouncil .bc-detail { border-left:1px solid var(--bc-line); padding-left:28px; min-width:0; }
.blindcouncil .bc-filters { display:flex; gap:8px; margin-bottom:16px; }
.blindcouncil .bc-row { display:flex; align-items:flex-start; flex-direction:column; gap:6px; width:100%; min-height:76px; padding:14px 12px; white-space:normal; text-align:left; border-radius:4px; border-bottom:1px solid var(--bc-line); transition:background-color var(--bc-fast); }
.blindcouncil .bc-row[aria-pressed=true] { background:var(--bc-fill); }
.blindcouncil .bc-row-title { font-size:14px; font-weight:500; overflow-wrap:anywhere; }
.blindcouncil .bc-row-meta { display:flex; width:100%; justify-content:space-between; gap:12px; font-size:12px; color:var(--bc-muted); }
.blindcouncil .bc-state { font-size:13px; font-weight:600; }
.blindcouncil .bc-result { font-size:30px; line-height:1.2; margin:24px 0 12px; }
.blindcouncil .bc-facts { display:grid; grid-template-columns:auto minmax(0,1fr); gap:12px 20px; margin:24px 0; font-size:13px; }
.blindcouncil .bc-facts dt { color:var(--bc-muted); }
.blindcouncil .bc-facts dd { margin:0; overflow-wrap:anywhere; font-variant-numeric:tabular-nums; }
.blindcouncil .bc-create { padding:24px 0; border-bottom:1px solid var(--bc-line); max-width:680px; }
.blindcouncil .bc-field { display:flex; flex-direction:column; gap:8px; margin:16px 0; font-size:13px; }
.blindcouncil .bc-field input,.blindcouncil .bc-field textarea { width:100%; min-height:36px; font-size:14px; }
.blindcouncil .bc-error { border:1px solid var(--bc-line); padding:14px; margin:16px 0; }
.blindcouncil .bc-error a { text-decoration:underline; text-underline-offset:3px; }
.blindcouncil .bc-empty { padding:30px 0; }
.blindcouncil .bc-privacy { border-top:1px solid var(--bc-line); padding-top:20px; margin-top:28px; }
.blindcouncil .bc-note { white-space:pre-wrap; overflow-wrap:anywhere; }
.blindcouncil button,.blindcouncil summary { min-height:36px; }
.blindcouncil :focus-visible { outline:2px solid var(--bc-accent); outline-offset:3px; }
@media(max-width:720px) { .blindcouncil { padding:20px 16px; } .blindcouncil .bc-workspace { grid-template-columns:minmax(0,1fr); gap:28px; } .blindcouncil .bc-list { padding:0; } .blindcouncil .bc-detail { padding:24px 0 0; border-left:0; border-top:1px solid var(--bc-line); } .blindcouncil button { min-height:44px; } }
@media(prefers-reduced-motion:reduce) { .blindcouncil * { transition:none; animation:none; scroll-behavior:auto; } }
`

const button = (text, onClick, props = {}) => jsx(Button, { type: 'button', variant: 'secondary', onClick, ...props, children: text })
const stamp = value => value ? new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : 'Not recorded'
function currentScope() { return `${host.state.connectionId.get() || 'local'}:${host.state.profile.get()}` }
async function request(scope, action, params = {}) {
  if (scope !== currentScope()) throw new Error('The gateway changed. Reload this view.')
  const result = await host.request('plugin.blindcouncil.operator', { action, ...params })
  if (['error', 'blocked', 'denied'].includes(result.status)) throw new Error(result.message || 'This request is not authorized or ready.')
  return result
}

function CreateForm({ scope, onClose, onCreated }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [expires, setExpires] = useState('24h')
  const [errors, setErrors] = useState({})
  const summary = useRef(null)
  const create = useMutation({ mutationFn: () => request(scope, 'create', { title, description, expires }), retry: false,
    onSuccess: result => onCreated(result.decision.round_id) })
  function submit(event) {
    event.preventDefault()
    const found = {}
    if (!title.trim() || title.length > 200) found.title = 'Enter a clear title, up to 200 characters.'
    if (title.length + description.length > 3600) found.description = 'Shorten the request so it fits one Telegram message.'
    setErrors(found)
    if (Object.keys(found).length) { queueMicrotask(() => summary.current?.focus()); return }
    create.mutate()
  }
  return jsxs('form', { className: 'bc-create', onSubmit: submit, children: [
    jsx('h2', { children: 'New decision' }),
    jsx('p', { className: 'bc-muted', children: 'Your two configured accounts receive separate private requests. Both responses are required.' }),
    Object.keys(errors).length > 0 && jsxs('div', { className: 'bc-error', role: 'alert', tabIndex: -1, ref: summary, children: [
      jsx('strong', { children: 'Check the request' }),
      ...Object.entries(errors).map(([field, text]) => jsx('p', { children: jsx('a', { href: `#bc-${field}`, children: text }) }, field)) ] }),
    jsxs('div', { className: 'bc-field', children: [jsx('label', { htmlFor: 'bc-title', children: 'Decision title' }),
      jsx(Input, { id: 'bc-title', value: title, maxLength: 200, onChange: e => setTitle(e.target.value), 'aria-invalid': !!errors.title, 'aria-describedby': errors.title ? 'bc-title-error' : undefined, placeholder: 'What needs approval?' }),
      errors.title && jsx('span', { id: 'bc-title-error', children: errors.title }) ] }),
    jsxs('div', { className: 'bc-field', children: [jsx('label', { htmlFor: 'bc-description', children: 'Context (optional)' }),
      jsx(Textarea, { id: 'bc-description', rows: 3, value: description, maxLength: 3600, onChange: e => setDescription(e.target.value), 'aria-invalid': !!errors.description, 'aria-describedby': errors.description ? 'bc-description-error' : undefined, placeholder: 'Give both participants the information they need.' }),
      errors.description && jsx('span', { id: 'bc-description-error', children: errors.description }) ] }),
    jsxs('div', { className: 'bc-field', children: [jsx('label', { htmlFor: 'bc-expires', children: 'Response deadline' }),
      jsxs(Select, { value: expires, onValueChange: setExpires, children: [jsx(SelectTrigger, { id: 'bc-expires', children: jsx(SelectValue, {}) }),
        jsx(SelectContent, { children: Object.entries(durations).map(([value, text]) => jsx(SelectItem, { value, children: text }, value)) }) ] }) ] }),
    create.isError && jsx('p', { className: 'bc-error', role: 'alert', children: create.error.message }),
    jsxs('div', { className: 'bc-actions', children: [jsx(Button, { type: 'submit', loading: create.isPending, children: 'Send private requests' }), button('Discard draft', onClose, { disabled: create.isPending, variant: 'ghost' }) ] })
  ] })
}

function Detail({ scope, identifier, refreshBoard }) {
  const [confirmCancel, setConfirmCancel] = useState(false)
  const cache = useQueryClient()
  const key = ['blindcouncil', scope, 'detail', identifier]
  const query = useQuery({ queryKey: key, queryFn: () => request(scope, 'detail', { round_id: identifier }), refetchInterval: 5000, retry: 1 })
  const mutation = useMutation({ mutationFn: action => request(scope, action, { round_id: identifier }), retry: false,
    onSuccess: () => { setConfirmCancel(false); cache.invalidateQueries({ queryKey: key }); refreshBoard() } })
  if (query.isPending) return jsx('p', { role: 'status', children: 'Loading decision…' })
  if (query.isError) return jsxs('div', { role: 'alert', children: [jsx('p', { children: 'The decision could not be loaded.' }), button('Try again', () => query.refetch())] })
  const decision = query.data.decision
  if (!decision || decision.status === 'denied') return jsx('p', { role: 'alert', children: 'This decision is not available to the configured coordinator.' })
  const delivery = query.data.delivery
  const blocked = delivery?.notifications?.some(row => row.state === 'blocked')
  return jsxs('section', { 'aria-label': 'Decision detail', children: [
    jsx('h2', { children: decision.title }),
    decision.description && jsx('p', { className: 'bc-note', children: decision.description }),
    jsx('h3', { className: 'bc-result', 'aria-live': 'polite', children: labels[decision.status] || decision.status }),
    jsx('p', { className: 'bc-muted', children: decision.status === 'pending' ? `${decision.responded_count} of 2 responses recorded. Each account answers privately in Telegram.` : 'This decision is closed. Further button presses cannot add a response.' }),
    jsxs('dl', { className: 'bc-facts', children: [
      jsx('dt', { children: 'Policy' }), jsx('dd', { children: 'Two-person unanimity' }),
      jsx('dt', { children: 'Responses' }), jsx('dd', { children: `${decision.responded_count} of ${decision.participant_count}` }),
      jsx('dt', { children: 'Invitations bound' }), jsx('dd', { children: `${decision.bound_invitation_count} of 2` }),
      jsx('dt', { children: 'Deadline' }), jsx('dd', { children: jsx('time', { dateTime: decision.expires_utc, title: decision.expires_utc, children: stamp(decision.expires_utc) }) }),
      jsx('dt', { children: 'Exact UTC deadline' }), jsx('dd', { children: decision.expires_utc || 'Not recorded (legacy decision)' }),
      jsx('dt', { children: 'Decision ID' }), jsx('dd', { children: decision.round_id }) ] }),
    delivery && jsxs('section', { 'aria-label': 'Delivery status', children: [jsx('h3', { children: 'Notifications' }),
      jsx('ul', { children: delivery.notifications?.map(row => jsx('li', { children: `${row.kind === 'invite' ? 'Private invitations' : 'Aggregate results'}: ${row.state} (${row.count})` }, `${row.kind}:${row.state}`)) }),
      blocked && jsx('p', { className: 'bc-muted', children: 'Delivery needs attention. If a recipient blocked the bot, unblock it and press Start before retrying. Completed jobs are not queued again; closed invitations stay closed.' })] }),
    blocked && button('Retry blocked notifications', () => mutation.mutate('retry'), { loading: mutation.isPending }),
    decision.status === 'pending' && (confirmCancel ? jsxs('div', { className: 'bc-error', children: [
      jsx('p', { children: 'Cancel this decision? Existing responses stay in its history. This cannot be undone.' }),
      jsxs('div', { className: 'bc-actions', children: [button('Cancel decision', () => mutation.mutate('cancel'), { variant: 'destructive', loading: mutation.isPending }), button('Keep pending', () => setConfirmCancel(false), { disabled: mutation.isPending })] })
    ] }) : button('Cancel decision', () => setConfirmCancel(true), { variant: 'outline' })),
    mutation.isError && jsx('p', { role: 'alert', className: 'bc-error', children: mutation.error.message }),
    mutation.isSuccess && mutation.data?.retried !== undefined && jsx('p', { role: 'status', children: `${mutation.data.retried} blocked notification(s) queued for retry.` })
  ] })
}

function Workspace({ scope, gateway, profile }) {
  const [selected, setSelected] = useState(null)
  const [creating, setCreating] = useState(false)
  const [filter, setFilter] = useState('all')
  const query = useQuery({ queryKey: ['blindcouncil', scope, 'board'], queryFn: () => request(scope, 'board'), enabled: gateway === 'open', refetchInterval: gateway === 'open' ? 5000 : false, retry: 1 })
  const ready = query.data?.readiness.status !== 'BLOCKED' && !!query.data
  const rows = (query.data?.decisions || []).filter(row => filter === 'all' || row.status === 'pending')
  return jsxs('main', { className: 'blindcouncil', children: [jsx('style', { children: css }),
    jsxs('header', { className: 'bc-head', children: [jsxs('div', { children: [jsx('h1', { children: 'BlindCouncil' }), jsx('p', { className: 'bc-muted', children: 'Private decisions. Shared outcomes.' })] }),
      jsxs('div', { className: 'bc-actions', children: [jsx('span', { className: 'bc-muted', role: 'status', children: gateway === 'open' ? `Gateway connected (${profile})` : 'Gateway disconnected' }),
        button('New decision', () => setCreating(true), { variant: 'default', disabled: !ready || gateway !== 'open' || creating })] })] }),
    gateway !== 'open' && jsx('p', { className: 'bc-error', role: 'alert', children: 'Connect this Hermes window to your gateway to load decisions.' }),
    query.isPending && gateway === 'open' && jsx('p', { role: 'status', children: 'Loading your decision history…' }),
    query.isError && jsxs('div', { className: 'bc-error', role: 'alert', children: [jsx('p', { children: 'BlindCouncil could not be reached. Enable its Python plugin and use Hermes 0.23.1 or newer.' }), button('Try again', () => query.refetch())] }),
    query.data && !query.data.native_adapter_loaded && jsx('p', { className: 'bc-muted', children: 'The native Telegram adapter is not active on this gateway. Requests can queue, but delivery requires the configured bot gateway.' }),
    query.data?.readiness.status === 'BLOCKED' && jsxs('section', { className: 'bc-empty', children: [jsx('h2', { children: 'Connect your two accounts' }),
      jsx('p', { children: 'Configure one bot with an explicit allowlist, then have both accounts open that same bot and press Start.' }),
      jsx('ol', { children: [jsx('li', { children: jsx('code', { children: 'hermes gateway setup' }) }), jsx('li', { children: jsx('code', { children: 'hermes blindcouncil configure' }) }), jsx('li', { children: 'Keep one native Hermes gateway running.' })] }),
      jsx('ul', { children: query.data.readiness.issues.map(issue => jsx('li', { children: issue }, issue)) }),
      button('Check setup again', () => query.refetch())] }),
    creating && jsx(CreateForm, { scope, onClose: () => setCreating(false), onCreated: identifier => { setCreating(false); setSelected(identifier); query.refetch() } }),
    query.data && jsxs('div', { className: 'bc-workspace', children: [jsxs('section', { className: 'bc-list', 'aria-label': 'Decision history', children: [
      jsxs('div', { className: 'bc-filters', children: [button('All decisions', () => setFilter('all'), { 'aria-pressed': filter === 'all', variant: filter === 'all' ? 'secondary' : 'ghost' }), button('Pending', () => setFilter('pending'), { 'aria-pressed': filter === 'pending', variant: filter === 'pending' ? 'secondary' : 'ghost' })] }),
      rows.length ? rows.map(row => jsx(Button, { className: 'bc-row', type: 'button', variant: 'ghost', 'aria-pressed': row.round_id === selected, onClick: () => setSelected(row.round_id), children: [
        jsx('span', { className: 'bc-row-title', children: row.title }),
        jsxs('span', { className: 'bc-row-meta', children: [jsx('span', { children: labels[row.status] || row.status }), jsx('span', { children: `${row.responded_count} of 2 responses` })] })
      ] }, row.round_id)) : jsxs('div', { className: 'bc-empty', children: [jsx('h2', { children: filter === 'pending' ? 'Nothing awaiting a decision' : 'Your first shared decision' }), jsx('p', { className: 'bc-muted', children: 'Create a clear request. Each participant answers privately, and the policy determines the shared result.' })] })
    ] }), jsx('div', { className: 'bc-detail', children: selected ? jsx(Detail, { scope, identifier: selected, refreshBoard: () => query.refetch() }, selected) : jsxs('div', { className: 'bc-empty', children: [jsx('h2', { children: 'Decide with clarity' }), jsx('p', { children: 'Select a decision to see its policy, response progress, exact deadline and aggregate result.' }), jsx('p', { className: 'bc-muted', children: 'Both accounts approve for an approval. Any rejection prevents approval. Expiry and cancellation close the request.' })] }) })] }),
    jsx('footer', { className: 'bc-privacy', children: jsx('p', { className: 'bc-muted', children: 'Individual answers are not shown here. Aggregate results can permit inference, and the trusted gateway operator can access storage. BlindCouncil does not enforce other Hermes actions.' }) })
  ] })
}

function Page() {
  const gateway = useValue(host.state.gateway)
  const profile = useValue(host.state.profile)
  const connection = useValue(host.state.connectionId)
  const scope = `${connection || 'local'}:${profile}`
  return jsx(Workspace, { scope, gateway, profile }, scope)
}

export default {
  id: 'blindcouncil', name: 'BlindCouncil', defaultEnabled: false,
  register(ctx) {
    ctx.register({ id: 'page', area: ROUTES_AREA, data: { path: '/blindcouncil' }, render: () => jsx(Page, {}) })
    ctx.register({ id: 'navigation', area: SIDEBAR_NAV_AREA, data: { path: '/blindcouncil', label: 'BlindCouncil', codicon: 'shield' } })
    ctx.register({ id: 'open', area: PALETTE_AREA, data: { id: 'blindcouncil.open', label: 'Open BlindCouncil', run: () => host.navigate('/blindcouncil') } })
  }
}
