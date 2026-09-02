import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import { AuthProvider } from "@/context/AuthContext"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { LoginPage } from "@/pages/LoginPage"
import { SitesPage } from "@/pages/SitesPage"

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/sites" element={<SitesPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/sites" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
