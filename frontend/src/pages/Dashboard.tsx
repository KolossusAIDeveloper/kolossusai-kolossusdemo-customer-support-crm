import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import api from '../lib/api'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Users, TrendingUp, DollarSign, CheckSquare, Target, AlertTriangle } from 'lucide-react'
import { formatCurrency } from '../lib/utils'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'

export default function Dashboard() {
  const { orgId } = useAuthStore()

  const { data: stats } = useQuery({
    queryKey: ['dashboard', orgId],
    queryFn: () => api.get(`/analytics/dashboard?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const { data: pipeline } = useQuery({
    queryKey: ['pipeline-analytics', orgId],
    queryFn: () => api.get(`/analytics/pipeline?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const { data: leadScores } = useQuery({
    queryKey: ['lead-scores', orgId],
    queryFn: () => api.get(`/analytics/lead-scores?org_id=${orgId}`).then(r => r.data),
    enabled: !!orgId,
  })

  const pipelineData = pipeline ? Object.entries(pipeline).map(([stage, v]: [string, any]) => ({
    stage: stage.replace('_', ' '),
    count: v.count,
    value: v.value,
  })) : []

  const scoreData = leadScores ? [
    { name: 'Hot', value: leadScores.hot, color: '#ef4444' },
    { name: 'Warm', value: leadScores.warm, color: '#f59e0b' },
    { name: 'Cold', value: leadScores.cold, color: '#3b82f6' },
    { name: 'Unscored', value: leadScores.unscored, color: '#9ca3af' },
  ].filter(d => d.value > 0) : []

  const statCards = [
    { label: 'Total Leads', value: stats?.total_leads ?? 0, icon: Users, color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-900/20' },
    { label: 'New This Week', value: stats?.new_leads_week ?? 0, icon: TrendingUp, color: 'text-green-600 dark:text-green-400', bg: 'bg-green-50 dark:bg-green-900/20' },
    { label: 'Pipeline Value', value: formatCurrency(stats?.pipeline_value ?? 0), icon: DollarSign, color: 'text-purple-600 dark:text-purple-400', bg: 'bg-purple-50 dark:bg-purple-900/20' },
    { label: 'Won Deals', value: stats?.won_deals ?? 0, icon: Target, color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-900/20' },
    { label: 'Overdue Tasks', value: stats?.overdue_tasks ?? 0, icon: AlertTriangle, color: 'text-red-600 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-900/20' },
    { label: 'Conversion Rate', value: `${stats?.conversion_rate ?? 0}%`, icon: CheckSquare, color: 'text-indigo-600 dark:text-indigo-400', bg: 'bg-indigo-50 dark:bg-indigo-900/20' },
  ]

  if (!orgId) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-gray-500 dark:text-gray-400">No organization found. Please register with an organization name.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {statCards.map(({ label, value, icon: Icon, color, bg }) => (
          <Card key={label}>
            <CardContent className="p-4">
              <div className={`w-10 h-10 rounded-lg ${bg} flex items-center justify-center mb-3`}>
                <Icon className={color} size={20} />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-gray-900 dark:text-white">Sales Pipeline</h3>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={pipelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" className="text-gray-200 dark:text-gray-700" />
                <XAxis dataKey="stage" tick={{ fontSize: 11 }} className="text-gray-500 dark:text-gray-400" />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--tw-bg-opacity)', border: '1px solid #374151' }}
                  formatter={(v: number, name: string) => [name === 'value' ? formatCurrency(v) : v, name]}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Deals" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-semibold text-gray-900 dark:text-white">AI Lead Score Distribution</h3>
          </CardHeader>
          <CardContent className="flex items-center justify-center">
            {scoreData.length === 0 ? (
              <p className="text-gray-400 dark:text-gray-500 text-sm py-10">No scored leads yet</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={scoreData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                    {scoreData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                  </Pie>
                  <Legend />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Expected Revenue</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
              {formatCurrency(stats?.expected_revenue ?? 0)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Qualified Leads</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stats?.qualified_leads ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Lost Deals</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{stats?.lost_deals ?? 0}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
