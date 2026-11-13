import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

const titles: Record<string, string> = {
  '/': 'Dashboard',
  '/leads': 'Leads',
  '/deals': 'Deals Pipeline',
  '/inbox': 'Customer Inbox',
  '/tasks': 'Tasks',
  '/workflows': 'Workflow Automation',
  '/analytics': 'Analytics',
  '/integrations': 'Integrations',
  '/settings': 'Settings',
}

export function Layout() {
  const location = useLocation()
  const title = titles[location.pathname] || 'CRM'

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <div className="flex-1 ml-60 flex flex-col min-h-screen">
        <Header title={title} />
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
