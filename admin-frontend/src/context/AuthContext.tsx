import { createContext, useContext, useState, type ReactNode } from "react"
import { login as apiLogin, logout as apiLogout, isAuthenticated } from "@/lib/api"

interface AuthContextValue {
  authenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authenticated, setAuthenticated] = useState(isAuthenticated())

  async function login(username: string, password: string) {
    await apiLogin(username, password)
    setAuthenticated(true)
  }

  function logout() {
    apiLogout()
    setAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ authenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth должен использоваться внутри AuthProvider")
  return ctx
}
