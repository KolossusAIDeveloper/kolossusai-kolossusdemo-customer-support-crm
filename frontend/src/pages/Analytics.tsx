import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import api from '../lib/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { formatCurrency } from '../lib/utils'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line
} from 'recharts'

const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

export default function Analytics() {
  const { orgId } = useAuthStore()

  const { data: dashboard } = useQuery({
    queryKey: ['analytics-dashboard', orgId],
    queryFn: () => api.get(`/analytics/dashboard?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const { data: pipeline } = useQuery({
    queryKey: ['analytics-pipeline', orgId],
    queryFn: () => api.get(`/analytics/pipeline?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const { data: leadScores } = useQuery({
    queryKey: ['analytics-scores', orgId],
    queryFn: () => api.get(`/analytics/lead-scores?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const pipelineChartData = pipeline ? Object.entries(pipeline).map(([stage, v]: [string, any]) => ({
    name: stage.replace('_', ' '),
    deals: v.count,
    value: Math.round(v.value),
  })) : []

  const scoreChartData = leadScores ? [
    { name: 'Hot', value: leadScores.hot },
    { name: 'Warm', value: leadScores.warm },
    { name: 'Cold', value: leadScores.cold },
    { name: 'Unscored', value: leadScores.unscored },
  ] : []

  const kpis = [
    { label: 'Total Leads', value: dashboard?.total_leads ?? 0 },
    { label: 'Qualified Leads', value: dashboard?.qualified_leads ?? 0 },
    { label: 'Won Deals', value: dashboard?.won_deals ?? 0 },
    { label: 'Lost Deals', value: dashboard?.lost_deals ?? 0 },
    { label: 'Pipeline Value', value: formatCurrency(dashboard?.pipeline_value ?? 0) },
    { label: 'Expected Revenue', value: formatCurrency(dashboard?.expected_revenue ?? 0) },
    { label: 'Conversion Rate', value: `${dashboard?.conversion_rate ?? 0}%` },
    { label: 'Overdue Tasks', value: dashboard?.overdue_tasks ?? 0 },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map(({ label, value }) => (
          <Card key={label}>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card>
          <CardHeader><h3 className="font-semibold text-gray-900 dark:text-white">Pipeline by Stage</h3></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={pipelineChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number, n: string) => [n === 'value' ? formatCurrency(v) : v, n]} />
                <Bar yAxisId="left" dataKey="deals" fill="#3b82f6" radius={[4,4,0,0]} name="Deals" />
                <Bar yAxisId="right" dataKey="value" fill="#10b981" radius={[4,4,0,0]} name="Value" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><h3 className="font-semibold text-gray-900 dark:text-white">AI Lead Scoring</h3></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={scoreChartData.filter(d => d.value > 0)}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {scoreChartData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
