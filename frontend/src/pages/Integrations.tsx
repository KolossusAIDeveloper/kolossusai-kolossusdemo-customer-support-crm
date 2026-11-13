import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import api from '../lib/api'
import { Card, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Plug, CheckCircle, XCircle, TestTube } from 'lucide-react'

const AVAILABLE_INTEGRATIONS = [
  { provider: 'gmail', name: 'Gmail', description: 'Connect Gmail for email sync' },
  { provider: 'outlook', name: 'Microsoft Outlook', description: 'Connect Outlook for email & calendar' },
  { provider: 'slack', name: 'Slack', description: 'Get notifications in Slack' },
  { provider: 'hubspot', name: 'HubSpot Import', description: 'Import contacts from HubSpot' },
  { provider: 'openai', name: 'OpenAI', description: 'Power AI features with GPT' },
  { provider: 'anthropic', name: 'Anthropic Claude', description: 'Power AI features with Claude' },
]

export default function Integrations() {
  const { orgId } = useAuthStore()
  const qc = useQueryClient()

  const { data: integrations } = useQuery({
    queryKey: ['integrations', orgId],
    queryFn: () => api.get(`/integrations?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const connectMutation = useMutation({
    mutationFn: ({ provider, name }: { provider: string; name: string }) =>
      api.post(`/integrations?org_id=${orgId}&provider=${provider}&name=${name}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['integrations'] })
  })

  const testMutation = useMutation({
    mutationFn: (id: string) => api.post(`/integrations/${id}/test?org_id=${orgId}`),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/integrations/${id}?org_id=${orgId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['integrations'] })
  })

  const connectedProviders = new Set(integrations?.map((i: any) => i.provider))

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {AVAILABLE_INTEGRATIONS.map(({ provider, name, description }) => {
          const connected = connectedProviders.has(provider)
          const integration = integrations?.find((i: any) => i.provider === provider)
          return (
            <Card key={provider}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                      <Plug size={20} className="text-gray-600 dark:text-gray-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">{name}</h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>
                    </div>
                  </div>
                  {connected ? (
                    <CheckCircle size={18} className="text-green-500 flex-shrink-0" />
                  ) : (
                    <XCircle size={18} className="text-gray-300 dark:text-gray-600 flex-shrink-0" />
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={connected ? 'success' : 'default'}>
                    {connected ? 'Connected' : 'Not connected'}
                  </Badge>
                </div>
                <div className="flex gap-2 mt-3">
                  {!connected ? (
                    <Button size="sm" onClick={() => connectMutation.mutate({ provider, name })}>
                      Connect
                    </Button>
                  ) : (
                    <>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => testMutation.mutate(integration.id)}
                      >
                        <TestTube size={12} />Test
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => deleteMutation.mutate(integration.id)}
                      >
                        Disconnect
                      </Button>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
