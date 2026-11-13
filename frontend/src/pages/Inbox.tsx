import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import api from '../lib/api'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'
import { Modal } from '../components/ui/Modal'
import { Plus, MessageSquare, Bot, Send, ThumbsUp } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { formatDate } from '../lib/utils'

export default function Inbox() {
  const { orgId } = useAuthStore()
  const qc = useQueryClient()
  const [selected, setSelected] = useState<any>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [aiSuggestion, setAiSuggestion] = useState<any>(null)
  const [replyText, setReplyText] = useState('')
  const { register, handleSubmit, reset } = useForm()

  const { data: conversations } = useQuery({
    queryKey: ['conversations', orgId],
    queryFn: () => api.get(`/conversations?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const { data: convDetail } = useQuery({
    queryKey: ['conversation', selected?.id],
    queryFn: () => api.get(`/conversations/${selected.id}?org_id=${orgId}`).then(r => r.data),
    enabled: !!selected,
  })

  const createMutation = useMutation({
    mutationFn: (d: any) => api.post(`/conversations?org_id=${orgId}`, d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['conversations'] }); setShowCreate(false); reset() }
  })

  const addMessageMutation = useMutation({
    mutationFn: ({ content }: { content: string }) =>
      api.post(`/conversations/${selected.id}/messages?org_id=${orgId}`, {
        content, sender_type: 'agent', is_sent: true
      }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['conversation'] }); setReplyText('') }
  })

  const aiSuggestMutation = useMutation({
    mutationFn: () => api.post(`/conversations/${selected.id}/ai-suggest?org_id=${orgId}`),
    onSuccess: (res) => setAiSuggestion(res.data)
  })

  return (
    <div className="flex gap-4 h-[calc(100vh-10rem)]">
      {/* Left: conversation list */}
      <div className="w-72 flex flex-col gap-3">
        <Button onClick={() => setShowCreate(true)} size="sm"><Plus size={14} />New Conversation</Button>
        <div className="flex-1 overflow-y-auto space-y-2">
          {!conversations?.length && (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">No conversations yet</p>
          )}
          {conversations?.map((conv: any) => (
            <div
              key={conv.id}
              onClick={() => setSelected(conv)}
              className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                selected?.id === conv.id
                  ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-700'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <MessageSquare size={14} className="text-blue-500" />
                <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {conv.subject || 'No subject'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <Badge variant="info">{conv.channel}</Badge>
                <span className="text-xs text-gray-400">{formatDate(conv.created_at)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right: conversation detail */}
      <div className="flex-1 flex flex-col bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        {!selected ? (
          <div className="flex-1 flex items-center justify-center text-gray-400 dark:text-gray-500">
            Select a conversation
          </div>
        ) : (
          <>
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">{convDetail?.subject || 'No subject'}</h3>
                {convDetail?.ai_summary && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 flex items-center gap-1">
                    <Bot size={12} />
                    <span className="italic">{convDetail.ai_summary}</span>
                  </p>
                )}
              </div>
              <Button variant="secondary" size="sm" onClick={() => aiSuggestMutation.mutate()}>
                <Bot size={14} />
                AI Suggest
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {convDetail?.messages?.map((msg: any) => (
                <div key={msg.id} className={`flex ${msg.sender_type === 'agent' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${
                    msg.sender_type === 'agent'
                      ? 'bg-blue-600 text-white'
                      : msg.sender_type === 'ai'
                      ? 'bg-purple-100 dark:bg-purple-900/40 text-purple-900 dark:text-purple-100 border border-purple-200 dark:border-purple-700'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                  }`}>
                    {msg.is_ai_suggested && (
                      <div className="flex items-center gap-1 text-xs opacity-75 mb-1">
                        <Bot size={10} />
                        <span>AI suggested</span>
                      </div>
                    )}
                    <p>{msg.content}</p>
                    <p className="text-xs opacity-60 mt-1">{formatDate(msg.created_at)}</p>
                  </div>
                </div>
              ))}
            </div>

            {aiSuggestion && (
              <div className="mx-4 mb-2 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-700">
                <div className="flex items-start gap-2">
                  <Bot size={14} className="text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-xs font-medium text-purple-700 dark:text-purple-300 mb-1">
                      AI Suggested Reply — requires your approval before sending
                    </p>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{aiSuggestion.suggested_reply}</p>
                    <div className="flex gap-2 mt-2">
                      <Button size="sm" onClick={() => { setReplyText(aiSuggestion.suggested_reply); setAiSuggestion(null) }}>
                        <ThumbsUp size={12} />Use this
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => setAiSuggestion(null)}>Dismiss</Button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex gap-2">
              <Input
                value={replyText}
                onChange={e => setReplyText(e.target.value)}
                placeholder="Type a reply…"
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && addMessageMutation.mutate({ content: replyText })}
              />
              <Button onClick={() => addMessageMutation.mutate({ content: replyText })} disabled={!replyText.trim()}>
                <Send size={14} />
              </Button>
            </div>
          </>
        )}
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="New Conversation">
        <form onSubmit={handleSubmit(d => createMutation.mutate(d))} className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Subject</label>
            <Input {...register('subject')} placeholder="Support request" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Channel</label>
            <select {...register('channel')} className="w-full px-3 py-2 text-sm border rounded-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100">
              <option value="email">Email</option>
              <option value="chat">Chat</option>
              <option value="form">Form</option>
              <option value="internal">Internal Note</option>
            </select>
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" type="button" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit">Create</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
