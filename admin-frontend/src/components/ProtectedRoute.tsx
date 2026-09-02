import { Navigate, Outlet } from "react-router-dom"
import { useAuth } from "@/context/AuthContext"

export function ProtectedRoute() {
  const { authenticated } = useAuth()
  return authenticated ? <Outlet /> : <Navigate to="/login" replace />
}
