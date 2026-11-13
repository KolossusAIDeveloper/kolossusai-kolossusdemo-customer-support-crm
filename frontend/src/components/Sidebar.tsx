import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, TrendingUp, MessageSquare, CheckSquare,
  Zap, BarChart2, Settings, Plug, Building2
} from 'lucide-react'
import { cn } from '../lib/utils'

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/leads', icon: Users, label: 'Leads' },
  { to: '/deals', icon: TrendingUp, label: 'Deals' },
  { to: '/inbox', icon: MessageSquare, label: 'Inbox' },
  { to: '/tasks', icon: CheckSquare, label: 'Tasks' },
  { to: '/workflows', icon: Zap, label: 'Workflows' },
  { to: '/analytics', icon: BarChart2, label: 'Analytics' },
  { to: '/integrations', icon: Plug, label: 'Integrations' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar() {
  return (
    <aside className="w-60 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-screen fixed left-0 top-0 z-20">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <Building2 className="text-blue-600" size={22} />
          <span className="font-bold text-gray-900 dark:text-white text-sm">Customer CRM</span>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
              )
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
