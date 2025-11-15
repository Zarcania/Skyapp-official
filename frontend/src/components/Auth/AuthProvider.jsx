// Composant d'authentification avec Supabase
// src/components/Auth/AuthProvider.jsx

import React, { createContext, useContext, useEffect, useState } from 'react'
import { supabase, api } from '../../lib/supabase'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [userData, setUserData] = useState(null)
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Récupérer la session initiale
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      if (session?.user) {
        loadUserData(session.user.id)
      } else {
        setLoading(false)
      }
    })

    // Écouter les changements d'authentification
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      
      if (session?.user) {
        await loadUserData(session.user.id)
      } else {
        setUserData(null)
        setLoading(false)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  const loadUserData = async (userId) => {
    try {
      const { data, error } = await api.users.getCurrent()
      if (error) {
        console.error('Error loading user data:', error)
      } else {
        setUserData(data)
      }
    } catch (error) {
      console.error('Error loading user data:', error)
    } finally {
      setLoading(false)
    }
  }

  const signIn = async (email, password) => {
    try {
      setLoading(true)
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })
      
      if (error) {
        throw error
      }
      
      return { data, error: null }
    } catch (error) {
      console.error('Sign in error:', error)
      return { data: null, error }
    } finally {
      setLoading(false)
    }
  }

  const signUp = async (email, password, userData) => {
    try {
      setLoading(true)
      
      // Inscription avec Supabase Auth
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: userData
        }
      })
      
      if (error) {
        throw error
      }
      
      return { data, error: null }
    } catch (error) {
      console.error('Sign up error:', error)
      return { data: null, error }
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    try {
      setLoading(true)
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        throw error
      }
      
      setUser(null)
      setUserData(null)
      setSession(null)
      
      return { error: null }
    } catch (error) {
      console.error('Sign out error:', error)
      return { error }
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (updates) => {
    try {
      if (!userData?.id) {
        throw new Error('No user logged in')
      }

      const { data, error } = await supabase
        .from('users')
        .update(updates)
        .eq('id', userData.id)
        .select()
        .single()

      if (error) {
        throw error
      }

      setUserData(data)
      return { data, error: null }
    } catch (error) {
      console.error('Update profile error:', error)
      return { data: null, error }
    }
  }

  const value = {
    user: session?.user ?? null,
    userData,
    session,
    loading,
    signIn,
    signUp,
    signOut,
    updateProfile,
    isAuthenticated: !!session?.user,
    isAdmin: userData?.role === 'ADMIN',
    isBureau: userData?.role === 'BUREAU',
    isTechnicien: userData?.role === 'TECHNICIEN',
    companyId: userData?.company_id
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthProvider