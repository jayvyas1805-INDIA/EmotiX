import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(() => {
        try { return JSON.parse(localStorage.getItem('emotix_user')) } catch { return null }
    })
    const [token, setToken] = useState(() => localStorage.getItem('emotix_token'))

    const login = (userData, accessToken) => {
        setUser(userData)
        setToken(accessToken)
        localStorage.setItem('emotix_user', JSON.stringify(userData))
        localStorage.setItem('emotix_token', accessToken)
    }

    const logout = () => {
        setUser(null)
        setToken(null)
        localStorage.removeItem('emotix_user')
        localStorage.removeItem('emotix_token')
    }

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
