import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { Button } from '../ui/button'

export function ThemeDebug() {
  const { theme, setTheme, systemTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="fixed bottom-4 right-4 p-4 bg-card border border-border rounded-lg shadow-lg text-sm">
      <div className="font-bold mb-2">Theme Debug</div>
      <div>Current: {theme}</div>
      <div>System: {systemTheme}</div>
      <div>Resolved: {resolvedTheme}</div>
      <div>HTML classes: {document.documentElement.className}</div>
      <div className="mt-2 space-x-2">
        <Button 
          variant="default"
          size="sm"
          onClick={() => setTheme('light')}
        >
          Light
        </Button>
        <Button 
          variant="default"
          size="sm"
          onClick={() => setTheme('dark')}
        >
          Dark
        </Button>
      </div>
    </div>
  )
}