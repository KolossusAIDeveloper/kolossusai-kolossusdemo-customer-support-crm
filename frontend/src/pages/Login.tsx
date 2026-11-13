import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import { ThemeToggle } from '../components/ThemeToggle'
import api from '../lib/api'
import { useState } from 'react'
import { Building2 } from 'lucide-react'

const schema = z.object({
  username: z.string().email(),
  password: z.string().min(1),
})

type Form = z.infer<typeof schema>

export default function Login() {
  const navigate = useNavigate()
  const { setAuth, setOrgId } = useAuthStore()
  const [error, setError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<Form>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: Form) => {
    setError('')
    try {
      const form = new FormData()
      form.append('username', data.username)
      form.append('password', data.password)
      const res = await api.post('/auth/login', form)
      const meRes = await api.get('/auth/me', { headers: { Authorization: `Bearer ${res.data.access_token}` } })
      setAuth(res.data.access_token, meRes.data)

      const orgsRes = await api.get('/auth/organizations', { headers: { Authorization: `Bearer ${res.data.access_token}` } })
      if (orgsRes.data.length > 0) {
        setOrgId(orgsRes.data[0].id)
      }
      navigate('/')
    } catch {
      setError('Invalid email or password')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
      <div className="absolute top-4 right-4"><ThemeToggle /></div>
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <div className="flex items-center gap-3 mb-8">
            <Building2 className="text-blue-600" size={32} />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Customer CRM</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Sign in to your account</p>
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
              <Input type="email" placeholder="you@example.com" {...register('username')} />
              {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password</label>
              <Input type="password" placeholder="••••••••" {...register('password')} />
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>

          <p className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
            Don't have an account?{' '}
            <Link to="/register" className="text-blue-600 dark:text-blue-400 hover:underline">Register</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
