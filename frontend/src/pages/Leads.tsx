import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import api from '../lib/api'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { Modal } from '../components/ui/Modal'
import { Table, Thead, Tbody, Th, Tr, Td } from '../components/ui/Table'
import { Plus, Search, Flame, Thermometer, Snowflake, Bot } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { formatDate, getClassificationBadge } from '../lib/utils'

const statusColors: Record<string, 'default' | 'info' | 'success' | 'warning' | 'danger'> = {
  new: 'info', contacted: 'default', qualified: 'success', unqualified: 'warning', converted: 'success', lost: 'danger'
}

export default function Leads() {
  const { orgId } = useAuthStore()
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [showCreate, setShowCreate] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['leads', orgId, search],
    queryFn: () => api.get(`/leads?org_id=${orgId}&search=${search}`).then(r => r.data),
    enabled: !!orgId,
  })

  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm()

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post(`/leads?org_id=${orgId}`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['leads'] }); setShowCreate(false); reset() }
  })

  const ClassIcon = ({ c }: { c: string | null }) => {
    if (c === 'hot') return <Flame size={14} className="text-red-500" />
    if (c === 'warm') return <Thermometer size={14} className="text-yellow-500" />
    if (c === 'cold') return <Snowflake size={14} className="text-blue-500" />
    return null
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
          <Input className="pl-9" placeholder="Search leads…" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <Button onClick={() => setShowCreate(true)}><Plus size={16} />Add Lead</Button>
      </div>

      <Card>
        <Table>
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Company</Th>
              <Th>Status</Th>
              <Th>AI Score</Th>
              <Th>Source</Th>
              <Th>Created</Th>
            </Tr>
          </Thead>
          <Tbody>
            {isLoading && (
              <Tr><Td colSpan={6} className="text-center py-8 text-gray-400">Loading…</Td></Tr>
            )}
            {!isLoading && (!data?.items?.length) && (
              <Tr><Td colSpan={6} className="text-center py-8 text-gray-400 dark:text-gray-500">No leads yet. Add your first lead!</Td></Tr>
            )}
            {data?.items?.map((lead: any) => (
              <Tr key={lead.id}>
                <Td>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{lead.name}</p>
                    {lead.email && <p className="text-xs text-gray-500 dark:text-gray-400">{lead.email}</p>}
                  </div>
                </Td>
                <Td>{lead.company || '—'}</Td>
                <Td><Badge variant={statusColors[lead.status] || 'default'}>{lead.status}</Badge></Td>
                <Td>
                  <div className="flex items-center gap-1">
                    <ClassIcon c={lead.ai_classification} />
                    <span className="font-medium">{lead.lead_score}</span>
                    {lead.ai_classification && (
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${getClassificationBadge(lead.ai_classification)}`}>
                        {lead.ai_classification}
                      </span>
                    )}
                    {lead.ai_classification && <Bot size={12} className="text-gray-400 dark:text-gray-500 ml-1" aria-label="AI-scored" />}
                  </div>
                </Td>
                <Td>{lead.source}</Td>
                <Td>{formatDate(lead.created_at)}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Card>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add New Lead">
        <form onSubmit={handleSubmit(d => createMutation.mutate(d))} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
              <Input {...register('name', { required: true })} placeholder="John Doe" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
              <Input type="email" {...register('email')} placeholder="john@example.com" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone</label>
              <Input {...register('phone')} placeholder="+1 555 0100" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Company</label>
              <Input {...register('company')} placeholder="Acme Corp" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Industry</label>
              <Input {...register('industry')} placeholder="SaaS" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Country</label>
              <Input {...register('country')} placeholder="US" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Notes</label>
            <textarea
              {...register('notes')}
              className="w-full px-3 py-2 text-sm border rounded-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 h-20 resize-none"
              placeholder="Additional notes…"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" type="button" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Creating…' : 'Create Lead'}
            </Button>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <Bot size={12} /> AI will automatically score this lead in the background
          </p>
        </form>
      </Modal>
    </div>
  )
}
