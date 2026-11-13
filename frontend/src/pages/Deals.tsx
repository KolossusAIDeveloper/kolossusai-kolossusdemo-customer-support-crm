import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import api from '../lib/api'
import { Card, CardHeader, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Modal } from '../components/ui/Modal'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { Plus, DollarSign } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { formatCurrency } from '../lib/utils'

const STAGES = ['new', 'contacted', 'qualified', 'demo_scheduled', 'proposal_sent', 'negotiation', 'won', 'lost']
const STAGE_COLORS: Record<string, string> = {
  new: 'bg-gray-100 dark:bg-gray-700',
  contacted: 'bg-blue-50 dark:bg-blue-900/20',
  qualified: 'bg-indigo-50 dark:bg-indigo-900/20',
  demo_scheduled: 'bg-purple-50 dark:bg-purple-900/20',
  proposal_sent: 'bg-yellow-50 dark:bg-yellow-900/20',
  negotiation: 'bg-orange-50 dark:bg-orange-900/20',
  won: 'bg-green-50 dark:bg-green-900/20',
  lost: 'bg-red-50 dark:bg-red-900/20',
}

export default function Deals() {
  const { orgId } = useAuthStore()
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm()

  const { data } = useQuery({
    queryKey: ['deals', orgId],
    queryFn: () => api.get(`/deals?org_id=${orgId}&per_page=100`).then(r => r.data),
    enabled: !!orgId,
  })

  const createMutation = useMutation({
    mutationFn: (d: any) => api.post(`/deals?org_id=${orgId}`, { ...d, value: parseFloat(d.value) || 0 }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['deals'] }); setShowCreate(false); reset() }
  })

  const moveMutation = useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: string }) =>
      api.post(`/deals/${id}/move-stage?org_id=${orgId}`, { stage }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['deals'] })
  })

  const deals: any[] = data?.items || []

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => setShowCreate(true)}><Plus size={16} />New Deal</Button>
      </div>

      <div className="flex gap-3 overflow-x-auto pb-4">
        {STAGES.map(stage => {
          const stageDeals = deals.filter((d: any) => d.stage === stage)
          const stageValue = stageDeals.reduce((sum: number, d: any) => sum + d.value, 0)
          return (
            <div key={stage} className="flex-shrink-0 w-56">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
                  {stage.replace('_', ' ')}
                </span>
                <Badge variant="default">{stageDeals.length}</Badge>
              </div>
              <div className={`min-h-32 rounded-lg p-2 space-y-2 ${STAGE_COLORS[stage]}`}>
                {stageDeals.map((deal: any) => (
                  <div
                    key={deal.id}
                    className="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm border border-gray-200 dark:border-gray-700 cursor-pointer hover:shadow-md transition-shadow"
                  >
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{deal.name}</p>
                    {deal.company && <p className="text-xs text-gray-500 dark:text-gray-400">{deal.company}</p>}
                    <div className="flex items-center gap-1 mt-2">
                      <DollarSign size={12} className="text-green-600 dark:text-green-400" />
                      <span className="text-xs font-medium text-green-600 dark:text-green-400">
                        {formatCurrency(deal.value, deal.currency)}
                      </span>
                    </div>
                    <div className="flex gap-1 mt-2 flex-wrap">
                      {STAGES.filter(s => s !== stage).slice(0, 2).map(s => (
                        <button
                          key={s}
                          onClick={() => moveMutation.mutate({ id: deal.id, stage: s })}
                          className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          → {s.replace('_', ' ')}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              {stageValue > 0 && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 text-center">
                  {formatCurrency(stageValue)}
                </p>
              )}
            </div>
          )
        })}
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="New Deal">
        <form onSubmit={handleSubmit(d => createMutation.mutate(d))} className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deal Name *</label>
            <Input {...register('name', { required: true })} placeholder="Enterprise Contract" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Company</label>
              <Input {...register('company')} placeholder="Acme Corp" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Value ($)</label>
              <Input type="number" {...register('value')} placeholder="10000" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Probability %</label>
              <Input type="number" {...register('probability')} placeholder="50" defaultValue={50} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Stage</label>
              <select {...register('stage')} className="w-full px-3 py-2 text-sm border rounded-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100">
                {STAGES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
              </select>
            </div>
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" type="button" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Creating…' : 'Create'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
