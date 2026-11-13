import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import api from '../lib/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { Modal } from '../components/ui/Modal'
import { Plus, Zap, Play, Pause } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { formatDate } from '../lib/utils'

const TRIGGERS = [
  'lead_created', 'lead_status_changed', 'deal_stage_changed',
  'task_overdue', 'new_message', 'scheduled', 'webhook'
]

export default function Workflows() {
  const { orgId } = useAuthStore()
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm()

  const { data: workflows } = useQuery({
    queryKey: ['workflows', orgId],
    queryFn: () => api.get(`/workflows?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const createMutation = useMutation({
    mutationFn: (d: any) => api.post(`/workflows?org_id=${orgId}`, { ...d, steps: [] }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['workflows'] }); setShowCreate(false); reset() }
  })

  const toggleMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/workflows/${id}/toggle?org_id=${orgId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['workflows'] })
  })

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => setShowCreate(true)}><Plus size={16} />New Workflow</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {!workflows?.length && (
          <div className="col-span-full text-center py-12 text-gray-400 dark:text-gray-500">
            <Zap size={40} className="mx-auto mb-3 opacity-30" />
            <p>No workflows yet. Create your first automation!</p>
          </div>
        )}
        {workflows?.map((wf: any) => (
          <Card key={wf.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Zap size={18} className={wf.is_active ? 'text-yellow-500' : 'text-gray-400 dark:text-gray-500'} />
                  <h3 className="font-semibold text-gray-900 dark:text-white">{wf.name}</h3>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleMutation.mutate(wf.id)}
                >
                  {wf.is_active ? <Pause size={14} /> : <Play size={14} />}
                </Button>
              </div>
              {wf.description && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">{wf.description}</p>
              )}
              <div className="flex items-center gap-2">
                <Badge variant={wf.is_active ? 'success' : 'default'}>
                  {wf.is_active ? 'Active' : 'Paused'}
                </Badge>
                <Badge variant="info">{wf.trigger_type.replace('_', ' ')}</Badge>
              </div>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">{formatDate(wf.created_at)}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="New Workflow">
        <form onSubmit={handleSubmit(d => createMutation.mutate(d))} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Workflow Name *</label>
            <Input {...register('name', { required: true })} placeholder="Follow-up on new leads" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
            <Input {...register('description')} placeholder="What does this workflow do?" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Trigger *</label>
            <select {...register('trigger_type', { required: true })} className="w-full px-3 py-2 text-sm border rounded-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100">
              {TRIGGERS.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
            </select>
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" type="button" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" disabled={isSubmitting}>Create Workflow</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
