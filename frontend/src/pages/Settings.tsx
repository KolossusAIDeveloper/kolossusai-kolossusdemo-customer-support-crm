import { useAuthStore } from '../store/authStore'
import { useThemeStore } from '../store/themeStore'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { ThemeToggle } from '../components/ThemeToggle'
import { User, Building2, Shield } from 'lucide-react'

export default function Settings() {
  const { user, orgId } = useAuthStore()
  const { theme } = useThemeStore()

  return (
    <div className="space-y-6 max-w-2xl">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <User size={18} className="text-blue-600 dark:text-blue-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Profile</h3>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <label className="text-sm text-gray-500 dark:text-gray-400">Name</label>
            <p className="font-medium text-gray-900 dark:text-white">{user?.full_name}</p>
          </div>
          <div>
            <label className="text-sm text-gray-500 dark:text-gray-400">Email</label>
            <p className="font-medium text-gray-900 dark:text-white">{user?.email}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 size={18} className="text-blue-600 dark:text-blue-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Organization</h3>
          </div>
        </CardHeader>
        <CardContent>
          <div>
            <label className="text-sm text-gray-500 dark:text-gray-400">Organization ID</label>
            <p className="font-medium text-gray-900 dark:text-white font-mono text-sm">{orgId || 'None'}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Shield size={18} className="text-blue-600 dark:text-blue-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Appearance</h3>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900 dark:text-white">Theme</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Currently: {theme} mode</p>
            </div>
            <ThemeToggle />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
