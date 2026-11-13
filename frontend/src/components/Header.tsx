import { Bell, LogOut, User } from 'lucide-react'
import { ThemeToggle } from './ThemeToggle'
import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'

interface HeaderProps {
  title: string
}

export function Header({ title }: HeaderProps) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 sticky top-0 z-10">
      <h1 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h1>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        <button className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <Bell size={18} />
        </button>
        <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <User size={16} />
          <span>{user?.full_name || user?.email}</span>
        </div>
        <button
          onClick={handleLogout}
          className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          title="Logout"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  )
}
