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
import { Plus, CheckCircle } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { formatDate } from '../lib/utils'

const statusColors: Record<string, any> = {
  todo: 'info', in_progress: 'warning', blocked: 'danger', completed: 'success', cancelled: 'default'
}

export default function Tasks() {
  const { orgId } = useAuthStore()
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm()

  const { data: tasks } = useQuery({
    queryKey: ['tasks', orgId],
    queryFn: () => api.get(`/tasks?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const createMutation = useMutation({
    mutationFn: (d: any) => api.post(`/tasks?org_id=${orgId}`, d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['tasks'] }); setShowCreate(false); reset() }
  })

  const completeMutation = useMutation({
    mutationFn: (id: string) => api.patch(`/tasks/${id}?org_id=${orgId}`, { status: 'completed' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks'] })
  })

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => setShowCreate(true)}><Plus size={16} />New Task</Button>
      </div>
      <Card>
        <Table>
          <Thead>
            <Tr>
              <Th>Title</Th>
              <Th>Status</Th>
              <Th>Priority</Th>
              <Th>Due Date</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {!tasks?.length && (
              <Tr><Td colSpan={5} className="text-center py-8 text-gray-400 dark:text-gray-500">No tasks yet</Td></Tr>
            )}
            {tasks?.map((task: any) => (
              <Tr key={task.id}>
                <Td>
                  <p className="font-medium text-gray-900 dark:text-white">{task.title}</p>
                  {task.description && <p className="text-xs text-gray-500 dark:text-gray-400">{task.description}</p>}
                </Td>
                <Td><Badge variant={statusColors[task.status]}>{task.status.replace('_', ' ')}</Badge></Td>
                <Td><Badge variant={task.priority === 'urgent' ? 'danger' : task.priority === 'high' ? 'warning' : 'default'}>{task.priority}</Badge></Td>
                <Td>{task.due_date ? formatDate(task.due_date) : '—'}</Td>
                <Td>
                  {task.status !== 'completed' && (
                    <Button variant="ghost" size="sm" onClick={() => completeMutation.mutate(task.id)}>
                      <CheckCircle size={14} />Complete
                    </Button>
                  )}
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Card>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="New Task">
        <form onSubmit={handleSubmit(d => createMutation.mutate(d))} className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title *</label>
            <Input {...register('title', { required: true })} placeholder="Follow up with lead" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
            <Input {...register('description')} placeholder="Details…" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label>
              <select {...register('priority')} className="w-full px-3 py-2 text-sm border rounded-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Due Date</label>
              <Input type="datetime-local" {...register('due_date')} />
            </div>
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" type="button" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" disabled={isSubmitting}>Create Task</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
